#!/usr/bin/env python3
"""Build an installable Kodi addon zip."""

import argparse
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ADDON_DIR = REPO_ROOT / "plugin.video.mfk"


def read_addon(addon_dir):
    addon_xml = addon_dir / "addon.xml"
    root = ET.parse(addon_xml).getroot()
    if root.tag != "addon":
        raise ValueError(f"{addon_xml}: root element must be <addon>")
    try:
        return root.attrib["id"], root.attrib["version"]
    except KeyError as exc:
        raise ValueError(f"{addon_xml}: missing required attribute {exc}") from exc


def validate_version(version, source):
    if not version:
        raise ValueError(f"{source} produced an empty version")
    invalid = sorted(set(re.sub(r"[A-Za-z0-9.+_@~]", "", version)))
    if invalid:
        raise ValueError(
            f"invalid {source} {version!r}: invalid character(s) "
            f"{' '.join(repr(char) for char in invalid)}; allowed characters are "
            "A-Za-z0-9.+_@~ (hyphen '-' is not allowed)"
        )
    return version


def validate_tag(tag):
    version = tag[1:] if tag.startswith("v") else tag
    if not re.fullmatch(r"[0-9]+(?:\.[0-9]+)*", version):
        raise ValueError(
            f"invalid tag {tag!r}: tags must be stable numeric versions; "
            "pre-releases must be built locally with --version, for example: "
            "python3 tools/build_release.py --version 0.0.2~beta1 --outdir dist"
        )
    return version


def is_excluded(relative_path):
    excluded_suffixes = (".pyc", ".pyo", ".bak", ".orig", ".rej")
    return any(
        part == "__pycache__"
        or part.startswith(".git")
        or part.endswith(excluded_suffixes)
        for part in relative_path.parts
    )


VERSION_ATTR_RE = re.compile(
    r'(<addon\b[^>]*?\bversion\s*=\s*)(["\'])[^"\']*\2', re.DOTALL
)


def rewrite_addon_xml_version(xml_text, version):
    updated, replacements = VERSION_ATTR_RE.subn(
        lambda match: match.group(1) + match.group(2) + version + match.group(2),
        xml_text,
        count=1,
    )
    if replacements != 1:
        raise ValueError("could not replace the addon version attribute")
    return updated


def build_zip(addon_dir, addon_id, version, outdir, write_addon_xml=False):
    outdir.mkdir(parents=True, exist_ok=True)
    output = outdir / f"{addon_id}-{version}.zip"
    files = []
    excluded_count = 0
    for path in sorted(addon_dir.rglob("*")):
        if not path.is_file():
            continue
        relative_path = path.relative_to(addon_dir)
        if is_excluded(relative_path):
            excluded_count += 1
        else:
            files.append(path)
    addon_xml_path = addon_dir / "addon.xml"
    with addon_xml_path.open("r", encoding="utf-8", newline="") as handle:
        original_addon_xml = handle.read()
    updated_addon_xml = rewrite_addon_xml_version(original_addon_xml, version)
    if write_addon_xml:
        with addon_xml_path.open("w", encoding="utf-8", newline="") as handle:
            handle.write(updated_addon_xml)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            relative = path.relative_to(addon_dir).as_posix()
            archive_name = f"{addon_id}/{relative}"
            if relative == "addon.xml":
                archive.writestr(archive_name, updated_addon_xml.encode("utf-8"))
            else:
                archive.write(path, archive_name)
    return output, len(files), excluded_count


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    version_group = parser.add_mutually_exclusive_group()
    version_group.add_argument("--version", help="Kodi addon version override")
    version_group.add_argument(
        "--tag", help="git tag override (one leading 'v' is stripped)"
    )
    parser.add_argument("--outdir", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--write-addon-xml",
        action="store_true",
        help="also rewrite the version attribute in working-tree addon.xml",
    )
    args = parser.parse_args(argv)
    try:
        addon_id, version = read_addon(ADDON_DIR)
        source = "addon.xml version"
        if args.tag is not None:
            version = validate_tag(args.tag)
        else:
            if args.version is not None:
                version = args.version
                source = "version"
            validate_version(version, source)
        output, file_count, excluded_count = build_zip(
            ADDON_DIR,
            addon_id,
            version,
            args.outdir,
            write_addon_xml=args.write_addon_xml,
        )
    except (OSError, KeyError, ValueError, ET.ParseError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"Version: {version}")
    print(f"Source: {ADDON_DIR}")
    print(f"Output: {output}")
    print(f"Files: {file_count}")
    print(f"Excluded files: {excluded_count}")
    if args.write_addon_xml:
        print(f"Updated working-tree addon.xml: {ADDON_DIR / 'addon.xml'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
