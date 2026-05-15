# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository purpose

A collection of RPM spec files (Fedora-style) for software the maintainer packages personally. Each top-level directory is one package. There is no top-level build system — `rpmbuild` operates on a single `.spec` at a time.

## Layout

Each package lives in its own directory and is self-contained:

- `<package>/<package>.spec` — the spec file (always present)
- Optional companion files used as local `SourceN:` entries (e.g. `jetbrains-toolbox/{icon.svg,jetbrains-toolbox.desktop,LICENSE}`, `cachyos-default-kernel/99-default`)

There is **no shared tooling, no Makefile, no top-level build script**. Don't invent one.

Packages currently tracked: `amneziawg-dkms`, `amneziawg-tools`, `cachyos-default-kernel`, `gamescope`, `jetbrains-toolbox`, `kernel-cachyos`, `mesa-git`, `scx-manager`, `scx-scheds`, `scx-tools`, `wooting-udev`, `wootility-beta`, `zed`.

The three `scx-*` packages are adapted from CachyOS's Fedora COPR (`bieszczaders/kernel-cachyos-addons`). `scx-scheds` requires `scx-tools` (the `scx_loader` D-Bus service + `scxctl` CLI) at runtime, and `scx-manager` requires both — install/build them together. Sources track upstream release tags from `sched-ext/scx`, `sched-ext/scx-loader`, and `CachyOS/scx-manager`.

## Building a package locally

The `.gitignore` is set up to expect rpmbuild to operate from the repo root with `_topdir` pointed here, dropping `BUILD/`, `BUILDROOT/`, `RPMS/`, `SOURCES/`, `SPECS/`, `SRPMS/` alongside the package dirs. Typical flow for one package:

```bash
# Stage spec + local sources where rpmbuild expects them
mkdir -p SPECS SOURCES
cp <pkg>/<pkg>.spec SPECS/
cp <pkg>/* SOURCES/                         # any companion Source files
spectool -g -R --directory SOURCES SPECS/<pkg>.spec   # download Source0..N
sudo dnf builddep SPECS/<pkg>.spec
rpmbuild --define "_topdir $PWD" -ba SPECS/<pkg>.spec
```

Built RPMs land in `RPMS/<arch>/`; SRPMs in `SRPMS/`. Both are gitignored.

## Spec conventions in this repo

Two distinct spec styles coexist — preserve the style of whichever package you're editing:

1. **Binary repackagers** — `jetbrains-toolbox`, `wootility-beta`, `zed`. Pull an upstream prebuilt tarball/`.deb`/AppImage, unpack, and reinstall into the buildroot. These all set `%global debug_package %{nil}`, declare `ExclusiveArch: x86_64`, have an empty `%build`, and their `%install` is `install`/`cp` plus symlinks. Don't add compilation steps to these.
2. **Source builds** — `amneziawg-dkms`, `amneziawg-tools`, `gamescope`, `mesa-git`, `kernel-cachyos`, `scx-scheds`, `scx-tools`, `scx-manager`. Real `BuildRequires`, real compilation. The two `amneziawg-*` packages, `mesa-git`, and `gamescope` track an upstream **git commit** (not a release tag); the three `scx-*` packages track upstream release tags. See versioning below.

`gamescope` is a personal fork at `github.com/synsejse/gamescope-synse` and the spec is a slimmed-down adaptation of Fedora's `gamescope.spec` — same `BuildRequires`, same companion patches (`0001-cstdint.patch`, `Allow-to-use-system-wlroots.patch`, `Use-system-stb-glm.patch`), same bundled `stb.pc` and pinned `reshade`/`vkroots` sources — only `Source0`, `URL`, `Version`/`Release`, and the `%setup -n` line differ. Keep that intentional. When upstream Fedora bumps `reshade_commit` or `vkroots_commit` we should sync those too.

Versioning idioms used by the auto-updater (preserve these exactly — the workflow's `sed` patterns depend on them):

- Pinned upstream release: `Version: <semver>` (jetbrains-toolbox, scx-scheds, scx-tools, scx-manager).
- Prerelease: `%global upstream_version` + `%global prerelease`; `Version: %{upstream_version}~%{prerelease}` (zed, wootility-beta).
- Git snapshot: `%global commit <sha>` + `%global commitdate <YYYYMMDD>`; `Version: 1.0.%{commitdate}git%{shortcommit}` (amneziawg-dkms, amneziawg-tools).
- Mesa-git snapshot uses `%define commit` + `%define version_string` + `%global commit_date` and bumps the numeric `Release: 0.<N>%{?dist}` field on each update — `version_string` comes from the upstream `VERSION` file at that commit (with `-devel` stripped).
- Gamescope snapshot keeps `Version:` pinned to whichever upstream tag the fork is roughly based on (currently `3.16.23`) and encodes the fork commit in `Release: 0.<N>.<commitdate>git<shortcommit>%{?dist}`. The numeric `0.<N>` counter bumps on every update; `%global commit` / `%global commitdate` carry the fork SHA + date.
- CachyOS kernel tag: three `%define` macros — `_upstream_base` (`X.Y`), `_upstream_stable` (`Z`), `_upstream_rel` (`N`) — yielding the upstream tag `cachyos-X.Y.Z-N`. `_pkgrel` (the Fedora respin counter) resets to `1` on every upstream bump.

`cachyos-default-kernel` is hand-maintained and does **not** participate in the auto-update workflow — it ships a `/etc/kernel/postinst.d/99-default` hook that re-pins the latest CachyOS kernel as the grub default after kernel installs.

## Auto-update workflow (`.github/workflows/update-all-packages.yml`)

Runs daily at 12:00 UTC and on `workflow_dispatch`. Architecture to keep in mind when editing:

- One job, sequential per-package blocks. Each block is a triple of steps gated on the same `id`'s `update_needed` output: **check** → **update spec (sed)** → **commit**.
- Each per-package commit is made locally; a final `git push` at the end pushes them all together. There is **no PR flow** — commits land directly on `main` as `github-actions[bot]`.
- Commit message convention: `chore(<package>): update to <something>` (matches the manual commit history style — see `git log`).
- Changelog entries are inserted with `sed -i "/^%changelog/a ..."` so the newest entry is always immediately after the `%changelog` line. The format is `* <date> Automated Update <github-actions@github.com> - <evr>` followed by a `- Update to ...` line. Mesa-git is the exception: it bumps `Release` but does not append a changelog entry.
- Upstream version sources (memorize where to look when adding a package): GitHub Releases API (zed prereleases, scx-scheds via `sched-ext/scx`), GitHub Tags API (scx-tools via `sched-ext/scx-loader`, scx-manager via `CachyOS/scx-manager` — neither publishes proper Releases), GitHub matching-refs/tags API filtered to `cachyos-X.Y.Z-N` and sorted with `sort -V` (kernel-cachyos via `CachyOS/linux`), GitHub Commits API (both amneziawg-*, gamescope via `synsejse/gamescope-synse` master), JetBrains `data.services.jetbrains.com/products/releases?code=TBA` (jetbrains-toolbox), GitLab repo commits API + raw `VERSION` file at that commit (mesa-git), `api.wooting.io/public/wootility/download?os=linux&channel=beta` redirect Location header (wootility-beta).

When adding a new package to the workflow, follow the same three-step block pattern and grep/sed against the same fields the spec exposes — don't invent a new convention.

## Things to be careful about

- The `sed` patterns in the workflow are tightly coupled to the exact field names in each spec (`%global upstream_version`, `%global commit`, `%define commit`, `Version:`, `Release:`, etc.). Renaming or reformatting these in a spec will silently break its auto-updater step.
- Don't edit `%changelog` entries that were inserted by `Automated Update <github-actions@github.com>` — they're regenerated whenever the workflow runs and will fight you.
- `cachyos-default-kernel`'s `URL:` points at `github.com/synsejse/rpm-customs` (this repo). The git remote is `git@github.com:synsejse/rpm-customs.git`.
