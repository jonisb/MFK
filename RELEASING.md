# Releasing M.F.K.

Releases are driven by pushing a `v`-prefixed Git tag. The tag is the source of truth for the release version.

## Release procedure

1. Check out `master` and make sure it is clean, up to date, and pushed. Cut the tag from the tip of `master` and leave that branch unchanged until the release finishes.
2. Create and push a version tag:

   ```bash
   git tag v0.0.2
   git push origin v0.0.2
   ```

3. Pushing a tag matching `v*` triggers `.github/workflows/release.yml`. The workflow:
   - checks out `master` and validates the tag as a leading `v` followed by a stable numeric version (`v0.0.2` -> `0.0.2`),
   - updates `plugin.video.mfk/addon.xml`, then commits only that file and pushes the bump to `master` (skipping the commit and push if the version is already set),
   - builds `plugin.video.mfk-<version>.zip` using the committed `addon.xml`, with `plugin.video.mfk/` as the top-level folder,
   - creates or updates the GitHub Release for that tag and attaches the zip as a release asset.

The tag is not moved: it points to the commit **before** the automated bump, so GitHub's tagged source archive does not include that bump. Install the attached addon zip, not the tagged source archive. The workflow needs permission to push to `master`; branch protections or a concurrent push can prevent the bump and stop the release.

## Local build without CI

Build using the version currently in `plugin.video.mfk/addon.xml`:

```bash
python3 tools/build_release.py
```

Tag overrides and local pre-release version overrides both update the working-tree `plugin.video.mfk/addon.xml` by default before building the zip:

```bash
python3 tools/build_release.py --tag v0.0.2
python3 tools/build_release.py --version 0.0.2~beta1 --outdir dist
```

For a dry run that still builds a versioned zip but leaves the working-tree file unchanged, pass `--no-write-addon-xml`:

```bash
python3 tools/build_release.py --version 0.0.2~beta1 --no-write-addon-xml --outdir dist
```

Without `--outdir`, the zip is written to the repository root. The old `--write-addon-xml` flag still works but is no longer needed. CI uses `--update-addon-xml-only` to update and commit the version before creating the zip.

## Version-format rules (Kodi)

Kodi addon versions are **not** SemVer:

- Allowed characters are **only** `A-Za-z0-9.+_@~`.
- Hyphens (`-`) are **invalid** and break Kodi version comparison — never tag `v0.0.2-rc1` or `v1.0.0-alpha`.
- Use `~` for pre-releases: `1.0.0 > 1.0.0~beta2 > 1.0.0~beta1 > 1.0.0~alpha`.
- Examples of Kodi-compatible versions: `0.0.2`, `1.2.3`, `0.0.2~alpha`, `0.0.2~beta`, `0.0.2~beta2`.
- Tags are **stable numeric versions only**, such as `v0.0.2` or `v1.0`. Pre-releases are built locally with `python3 tools/build_release.py --version 0.0.2~beta1 --outdir dist` and are not tag-published. Git does not allow `~` in tag names, so `git tag v0.0.2~alpha` fails.

## Kodi repository status

There is **no Kodi repository yet** (no `repository.*` addon, no `addons.xml`, no `addons.xml.md5`). That work is intentionally deferred; for now, users install the release zip directly from GitHub Releases via Kodi's "Install from zip file".
