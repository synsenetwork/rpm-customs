# rpm should not strip the bundled Electron binaries or generate a
# debug subpackage (this is a binary repackager — no source compiled).
%global debug_package %{nil}
%global __os_install_post %{nil}
%global __strip /bin/true

%global claude_version 1.37937.3

# The .deb payload is arch-specific; map the RPM arch to the Debian
# arch used in the pool filename.
%ifarch x86_64
%global debarch amd64
%endif
%ifarch aarch64
%global debarch arm64
%endif

# The .desktop file is named for the app's reverse-DNS id (its basename must
# match the Wayland app_id / X11 WM_CLASS in StartupWMClass for window
# grouping). Anthropic renamed it from claude-desktop.desktop at 1.20186.x;
# the icons and /usr/bin symlink stay claude-desktop.
%global desktop_file com.anthropic.Claude.desktop

Name:           claude-desktop
# Epoch 1: the package switched from Anthropic's Windows Squirrel feed
# (last packaged 1.19367.0) to the official Linux apt channel, whose
# version numbering lags the Windows one — without the epoch the first
# deb-based build would sort as a downgrade.
Epoch:          1
Version:        %{claude_version}
Release:        2%{?dist}
Summary:        Claude Desktop for Linux
License:        LicenseRef-Anthropic
URL:            https://claude.com/download/

# Official Linux .deb from Anthropic's apt repository (Linux beta since
# 2026-06-30). Available versions are listed in the repo's Packages
# index at dists/stable/main/binary-%{debarch}/Packages under the same
# prefix.
Source0:        https://downloads.claude.ai/claude-desktop/apt/stable/pool/main/c/claude-desktop/claude-desktop_%{claude_version}_%{debarch}.deb

ExclusiveArch:  aarch64 x86_64
AutoReqProv:    no

BuildRequires:  bsdtar
BuildRequires:  desktop-file-utils

# Translated from the .deb's Depends; glibc/libuuid/libxcb are baseline
# on any Fedora desktop and not spelled out.
Requires:       gtk3
Requires:       nss
Requires:       libnotify
Requires:       libsecret
Requires:       libdrm
Requires:       mesa-libgbm
Requires:       libXtst
Requires:       at-spi2-core
Requires:       alsa-lib
Requires:       xdg-utils
Requires:       xdg-desktop-portal

# Cowork runs tasks in a local KVM virtual machine (mirrors the .deb's
# Recommends: qemu-system-x86, ovmf, virtiofsd).
Recommends:     virtiofsd
%ifarch x86_64
Recommends:     qemu-system-x86-core
Recommends:     edk2-ovmf
%endif
%ifarch aarch64
Recommends:     qemu-system-aarch64-core
Recommends:     edk2-aarch64
%endif

%description
Claude Desktop for Linux, repackaged from the official Debian package in
Anthropic's apt repository. Ships Anthropic's native Linux Electron build
unmodified — including Linux builds of @ant/claude-native and node-pty —
so nothing is patched or stubbed. The Debian postinst's AppArmor userns
profile and apt source registration are intentionally not carried over:
Fedora uses SELinux, and updates come through this package instead.

%prep
cd %{_builddir}
rm -rf usr data.tar.* control.tar.* debian-binary
# .deb = ar archive of control.tar.* + data.tar.*; bsdtar reads both
# layers. Only the data tree is wanted — the maintainer scripts are
# Debian-specific (AppArmor profile, apt repo registration).
bsdtar -xf %{SOURCE0}
bsdtar -xf data.tar.*

%build

%install
cd %{_builddir}
# The payload is already FHS-shaped: usr/lib/claude-desktop (Electron +
# app.asar), usr/bin/claude-desktop symlink, desktop file, hicolor
# icons. Drop the Debian-only doc/lintian trees and copy the rest
# through verbatim.
rm -rf usr/share/doc usr/share/lintian
install -d %{buildroot}%{_prefix}
cp -a usr/* %{buildroot}%{_prefix}/

# tar extraction as an unprivileged build user drops the setuid bit the
# .deb ships on the sandbox helper; restore it (Electron falls back to
# the SUID sandbox when user namespaces are unavailable).
chmod 4755 %{buildroot}%{_prefix}/lib/%{name}/chrome-sandbox

desktop-file-validate %{buildroot}%{_datadir}/applications/%{desktop_file}

%files
# /usr/bin/claude-desktop -> ../lib/claude-desktop/claude-desktop
%{_bindir}/claude-desktop
%{_prefix}/lib/%{name}/
%{_datadir}/applications/%{desktop_file}
%{_datadir}/icons/hicolor/*/apps/%{name}.png

%post
gtk-update-icon-cache -f -t %{_datadir}/icons/hicolor || :
touch -h %{_datadir}/icons/hicolor >/dev/null 2>&1 || :
update-desktop-database %{_datadir}/applications || :

%postun
if [ $1 -eq 0 ]; then
    gtk-update-icon-cache -f -t %{_datadir}/icons/hicolor || :
    update-desktop-database %{_datadir}/applications || :
fi

%changelog
* Thu Aug 27 2026 Automated Update <github-actions@github.com> - 1:1.37937.3-1
- Update to Claude Desktop 1.37937.3
* Sun Aug 23 2026 Automated Update <github-actions@github.com> - 1:1.34493.1-1
- Update to Claude Desktop 1.34493.1
* Wed Aug 19 2026 Automated Update <github-actions@github.com> - 1:1.32885.1-1
- Update to Claude Desktop 1.32885.1
* Sat Aug 15 2026 Automated Update <github-actions@github.com> - 1:1.30096.1-1
- Update to Claude Desktop 1.30096.1
* Thu Aug 13 2026 Automated Update <github-actions@github.com> - 1:1.28929.0-1
- Update to Claude Desktop 1.28929.0
* Sun Aug 09 2026 Automated Update <github-actions@github.com> - 1:1.26832.0-1
- Update to Claude Desktop 1.26832.0
* Wed Aug 05 2026 Automated Update <github-actions@github.com> - 1:1.24012.11-1
- Update to Claude Desktop 1.24012.11
* Sat Jul 25 2026 Automated Update <github-actions@github.com> - 1:1.24012.9-1
- Update to Claude Desktop 1.24012.9
* Thu Jul 23 2026 Automated Update <github-actions@github.com> - 1:1.24012.0-1
- Update to Claude Desktop 1.24012.0
* Tue Jul 14 2026 Kristián Kekeš <gamerix2006@gmail.com> - 1:1.20186.1-2
- Install the desktop file under its upstream name
  com.anthropic.Claude.desktop. Anthropic renamed it from
  claude-desktop.desktop at 1.20186.x (StartupWMClass is now
  com.anthropic.Claude), which broke the %%install desktop-file-validate
  and %%files. Icons and the /usr/bin symlink are still claude-desktop.
* Mon Jul 13 2026 Automated Update <github-actions@github.com> - 1:1.20186.1-1
- Update to Claude Desktop 1.20186.1
* Wed Jul 08 2026 Kristián Kekeš <gamerix2006@gmail.com> - 1:1.18286.2-1
- Switch to repackaging the official Linux .deb from Anthropic's apt
  repository (Linux beta released 2026-06-30). Drops the entire Windows
  .nupkg pipeline: no more asar patching, @ant/claude-native stub,
  npm-vendored Electron, or icon extraction from claude.exe — the deb
  ships a native Linux Electron build, real Linux native modules,
  official desktop file and icons.
- Add Epoch 1: the Linux apt channel's version numbering lags the
  Windows Squirrel feed this package previously tracked.
- App now lives in /usr/lib/claude-desktop (upstream layout) instead of
  %%{_libdir}/claude-desktop; chrome-sandbox is installed setuid as the
  deb ships it. Skip the Debian postinst's AppArmor profile and apt
  repo registration on purpose.
- Requires translated from the deb's Depends (adds libnotify, libsecret,
  libdrm, libXtst, at-spi2-core, xdg-utils, xdg-desktop-portal); new
  Recommends for Cowork's KVM workspace (qemu, edk2-ovmf, virtiofsd).
* Tue Jul 07 2026 Automated Update <github-actions@github.com> - 1.19367.0-1
- Update to Claude Desktop 1.19367.0
* Fri Jul 03 2026 Automated Update <github-actions@github.com> - 1.18286.0-1
- Update to Claude Desktop 1.18286.0
* Wed Jul 01 2026 Automated Update <github-actions@github.com> - 1.17377.1-1
- Update to Claude Desktop 1.17377.1
* Sat Jun 27 2026 Automated Update <github-actions@github.com> - 1.15962.1-1
- Update to Claude Desktop 1.15962.1
* Thu Jun 25 2026 Automated Update <github-actions@github.com> - 1.15200.0-1
- Update to Claude Desktop 1.15200.0
* Fri Jun 19 2026 Automated Update <github-actions@github.com> - 1.14271.0-1
- Update to Claude Desktop 1.14271.0
* Wed Jun 17 2026 Automated Update <github-actions@github.com> - 1.13576.0-1
- Update to Claude Desktop 1.13576.0
* Sat Jun 13 2026 Automated Update <github-actions@github.com> - 1.12603.1-1
- Update to Claude Desktop 1.12603.1
* Thu Jun 11 2026 Automated Update <github-actions@github.com> - 1.12603.0-1
- Update to Claude Desktop 1.12603.0
* Wed Jun 10 2026 Automated Update <github-actions@github.com> - 1.11847.5-1
- Update to Claude Desktop 1.11847.5
* Sat Jun 06 2026 Automated Update <github-actions@github.com> - 1.11187.4-1
- Update to Claude Desktop 1.11187.4
* Wed Jun 03 2026 Automated Update <github-actions@github.com> - 1.10628.0-1
- Update to Claude Desktop 1.10628.0
* Fri May 29 2026 Automated Update <github-actions@github.com> - 1.9659.2-1
- Update to Claude Desktop 1.9659.2
* Wed May 27 2026 Automated Update <github-actions@github.com> - 1.9255.2-1
- Update to Claude Desktop 1.9255.2
* Mon May 25 2026 Kristián Kekeš <gamerix2006@gmail.com> - 1.8555.2-3
- Verified the spec by actually unpacking the 1.8555.2 .nupkg and
  walking each step. Three of the four reference-spec sed lines turned
  out to be no-ops against current bundles because the minified
  identifiers renamed (e->A, Ln->mo, Jr->ui); rewrote them with
  capturing groups so they survive future renames.
- Stop packing Tray icons / i18n JSON / fonts into the asar — the
  bundle's ryt() helper resolves these via process.resourcesPath, so
  they must live alongside app.asar in Electron's resources/ dir, not
  inside the asar.
- Ship the previously-missed lib/net45/resources/ion-dist/ payload at
  process.resourcesPath/ion-dist (new in 1.x, not in 1.1.x).
- Move app.asar + app.asar.unpacked into %%{_libdir}/claude-desktop/
  electron/resources/ to follow Electron's canonical app layout, drop
  the default_app.asar welcome screen, and simplify the launcher to
  `exec electron` (Electron auto-discovers resources/app.asar).
- Make the claude-ssh install block tolerant of the subdir being
  absent — gone from .nupkg by 1.8555.x.

* Mon May 25 2026 Kristián Kekeš <gamerix2006@gmail.com> - 1.8555.2-1
- Initial RPM package, adapted from christian-korneck/claude-desktop-rpm.
  Downloads the .nupkg directly from Anthropic's Squirrel feed instead
  of the outer Claude-<hash>.exe wrapper, since the .nupkg URL is
  derivable from the public RELEASES manifest while the .exe hash is
  not.
