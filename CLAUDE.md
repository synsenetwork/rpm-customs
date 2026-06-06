# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository purpose

A collection of RPM spec files (Fedora-style) for software the maintainer packages personally. Each top-level directory is one package. There is no top-level build system — `rpmbuild` operates on a single `.spec` at a time.

## Layout

Each package lives in its own directory and is self-contained:

- `<package>/<package>.spec` — the spec file (always present)
- Optional companion files used as local `SourceN:` entries (e.g. `jetbrains-toolbox/{icon.svg,jetbrains-toolbox.desktop,LICENSE}`, `wooting-udev/70-wooting.rules`)

There is **no shared tooling, no Makefile, no top-level build script**. Don't invent one.

Packages currently tracked: `amneziawg-dkms`, `amneziawg-tools`, `claude-desktop`, `jetbrains-toolbox`, `mesa-git`, `scrcpy`, `scx-scheds`, `scx-synse-manager`, `scx-tools`, `synse-settings`, `wooting-udev`, `wootility-beta`, `zed`.

The `scx-scheds` and `scx-tools` packages are adapted from CachyOS's Fedora COPR (`bieszczaders/kernel-cachyos-addons`). `scx-scheds` requires `scx-tools` (the `scx_loader` D-Bus service + `scxctl` CLI) at runtime — install/build them together. Sources track upstream release tags from `sched-ext/scx` and `sched-ext/scx-loader`. `scx-synse-manager` is the maintainer's own GTK4 / libadwaita scx GUI (Rust, meson-driven cargo build); it likewise requires `scx-tools` + `scx-scheds` and tracks release tags from `synsenetwork/scx-synse-manager`.

`synse-settings` is the maintainer's personal fork of CachyOS-settings (`synsenetwork/synse-settings`), trimmed for Fedora on AMD hardware. It is the repo's only **config-only** package — a `noarch` filesystem tree (`etc/` + `usr/`) of drop-in configs (sysctl, udev, modprobe, systemd `*.conf.d`, tmpfiles, PAM limits) with no compilation. It tracks the upstream **master git commit** (no release tags) and is modeled on CachyOS's own Fedora COPR spec: `Requires: zram-generator` + `ntsync-autoload`, `Provides`/`Conflicts: zram-generator-defaults`, and renames `nvidia.conf` → `nvidia_synse.conf` to dodge the nvidia-driver file conflict.

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

Three distinct spec styles coexist — preserve the style of whichever package you're editing:

1. **Binary repackagers** — `claude-desktop`, `jetbrains-toolbox`, `wootility-beta`, `zed`. Pull an upstream prebuilt tarball/`.deb`/AppImage/`.nupkg`, unpack, and reinstall into the buildroot. These all set `%global debug_package %{nil}`, declare `ExclusiveArch: x86_64` (or `aarch64 x86_64` for claude-desktop), have an empty `%build`, and their `%install` is `install`/`cp` plus symlinks. Don't add compilation steps to these. `claude-desktop` is the odd one — it patches the Windows installer's `app.asar` in `%prep` to enable native window decorations on Linux and ships a vendored Electron runtime via npm; that's an explicit exception to the "no compilation in repackagers" rule because asar repacking happens entirely at `%prep` time.
2. **Source builds** — `amneziawg-dkms`, `amneziawg-tools`, `mesa-git`, `scrcpy`, `scx-scheds`, `scx-tools`, `scx-synse-manager`. Real `BuildRequires`, real compilation. The two `amneziawg-*` packages and `mesa-git` track an upstream **git commit** (not a release tag); the `scx-*` packages and `scrcpy` track upstream release tags. `scrcpy` is meson + ninja and uses the prebuilt server JAR shipped per upstream release (`-Dprebuilt_server=%{SOURCE1}`) so the buildroot doesn't pull Java + Android SDK. `scx-synse-manager` is the other meson-driven build — `%build` runs `cargo fetch --locked` then `%meson`/`%meson_build` (meson's custom target invokes `cargo build --release`), with `CARGO_NET_OFFLINE=true` so the meson-invoked build stays offline. See versioning below.
3. **Config mirrors** — `synse-settings`. A `noarch` package that ships a filesystem tree (`etc/` + `usr/`) of drop-in config files verbatim: no `BuildRequires`, empty `%build`, and an `%install` that is just `cp -a etc usr %{buildroot}/` (plus a couple of targeted `rm`/`mv` lines for conflict avoidance). `%files` uses broad globs (`%{_prefix}/lib/*`) rather than an explicit list so the package survives upstream adding/removing configs between snapshots. Sets `BuildArch: noarch` (which is why it needs no `%global debug_package %{nil}`). Don't add compilation steps to this style.

Versioning idioms used by the auto-updater (preserve these exactly — the workflow's `sed` patterns depend on them):

- Pinned upstream release: `Version: <semver>` (claude-desktop, jetbrains-toolbox, scrcpy, scx-scheds, scx-tools, scx-synse-manager).
- Prerelease: `%global upstream_version` + `%global prerelease`; `Version: %{upstream_version}~%{prerelease}` (zed, wootility-beta).
- Git snapshot: `%global commit <sha>` + `%global commitdate <YYYYMMDD>`; `Version: 1.0.%{commitdate}git%{shortcommit}` (amneziawg-dkms, amneziawg-tools, synse-settings).
- Mesa-git snapshot uses `%define commit` + `%define version_string` + `%global commit_date` and bumps the numeric `Release: 0.<N>%{?dist}` field on each update — `version_string` comes from the upstream `VERSION` file at that commit (with `-devel` stripped).

## Auto-update workflow (`.github/workflows/update-all-packages.yml`)

Runs every 2 days at 12:00 UTC (cron `'0 12 */2 * *'`) and on `workflow_dispatch`. Architecture to keep in mind when editing:

- One job, sequential per-package blocks. Each block is a triple of steps gated on the same `id`'s `update_needed` output: **check** → **update spec (sed)** → **commit**.
- Each per-package commit is made locally; a final `git push` at the end pushes them all together. There is **no PR flow** — commits land directly on `main` as `github-actions[bot]`.
- Commit message convention: `chore(<package>): update to <something>` (matches the manual commit history style — see `git log`).
- Changelog entries are inserted with `sed -i "/^%changelog/a ..."` so the newest entry is always immediately after the `%changelog` line. The format is `* <date> Automated Update <github-actions@github.com> - <evr>` followed by a `- Update to ...` line. Mesa-git is the exception: it bumps `Release` but does not append a changelog entry.
- Upstream version sources (memorize where to look when adding a package): GitHub Releases API (zed prereleases, scx-scheds via `sched-ext/scx`, scrcpy via `Genymobile/scrcpy`), GitHub Tags API (scx-tools via `sched-ext/scx-loader`, scx-synse-manager via `synsenetwork/scx-synse-manager` — none publish proper Releases), GitHub Commits API (both amneziawg-*, and synse-settings via `synsenetwork/synse-settings`), JetBrains `data.services.jetbrains.com/products/releases?code=TBA` (jetbrains-toolbox), GitLab repo commits API + raw `VERSION` file at that commit (mesa-git), `api.wooting.io/public/wootility/download?os=linux&channel=beta` redirect Location header (wootility-beta), Anthropic's Squirrel `RELEASES` manifest at `downloads.claude.ai/releases/win32/arm64/RELEASES` parsed for the highest `AnthropicClaude-X.Y.Z-full.nupkg` entry via `sort -V` (claude-desktop).

When adding a new package to the workflow, follow the same three-step block pattern and grep/sed against the same fields the spec exposes — don't invent a new convention.

## Things to be careful about

- The `sed` patterns in the workflow are tightly coupled to the exact field names in each spec (`%global upstream_version`, `%global commit`, `%define commit`, `Version:`, `Release:`, etc.). Renaming or reformatting these in a spec will silently break its auto-updater step.
- Don't edit `%changelog` entries that were inserted by `Automated Update <github-actions@github.com>` — they're regenerated whenever the workflow runs and will fight you.
- The git remote is `git@github.com:synsenetwork/rpm-customs.git`.
