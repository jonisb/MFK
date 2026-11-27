# Releasing M.F.K.

Releases are driven by pushing a `v`-prefixed Git tag. The tag is the source of truth for the release version.

## Release procedure

1. Make sure `master` is clean and pushed.
2. Create and push a version tag:

   ```bash
   git tag v0.0.2
   git push origin v0.0.2
   ```

3. Pushing a tag matching `v*` triggers `.github/workflows/release.yml`:
   - strips one leading `v` from the tag (`v0.0.2` -> `0.0.2`) and validates that it is a stable numeric version,
   - writes the release version into `plugin.video.mfk/addon.xml` inside the archive only,
   - builds `plugin.video.mfk-<version>.zip` with `plugin.video.mfk/` as the top-level folder inside the zip,
   - creates or updates the GitHub Release for that tag and attaches the zip as a release asset.

## Local build without CI

Build using the version currently in `plugin.video.mfk/addon.xml`:

```bash
python3 tools/build_release.py
```

Build for a specific tag or version override without modifying the working-tree `addon.xml`:

```bash
python3 tools/build_release.py --tag v0.0.2
python3 tools/build_release.py --version 0.0.2~beta1 --outdir dist
```

By default the zip is written to the repository root and working-tree `plugin.video.mfk/addon.xml` is left untouched. Pass `--write-addon-xml` only if you intentionally want to rewrite `plugin.video.mfk/addon.xml` in place.

## Version-format rules (Kodi)

Kodi addon versions are **not** SemVer:

- Allowed characters are **only** `A-Za-z0-9.+_@~`.
- Hyphens (`-`) are **invalid** and break Kodi version comparison — never tag `v0.0.2-rc1` or `v1.0.0-alpha`.
- Use `~` for pre-releases: `1.0.0 > 1.0.0~beta2 > 1.0.0~beta1 > 1.0.0~alpha`.
- Examples of Kodi-compatible versions: `0.0.2`, `1.2.3`, `0.0.2~alpha`, `0.0.2~beta`, `0.0.2~beta2`.
- Tags are **stable numeric versions only**, such as `v0.0.2` or `v1.0`. Pre-releases are built locally with `python3 tools/build_release.py --version 0.0.2~beta1 --outdir dist` and are not tag-published. Git does not allow `~` in tag names, so `git tag v0.0.2~alpha` fails.

## Kodi repository status

There is **no Kodi repository yet** (no `repository.*` addon, no `addons.xml`, no `addons.xml.md5`). That work is intentionally deferred; for now, users install the release zip directly from GitHub Releases via Kodi's "Install from zip file".
