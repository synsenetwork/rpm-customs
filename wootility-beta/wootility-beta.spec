%global debug_package %{nil}
%global __os_install_post %{nil}
%global __strip /bin/true

%global upstream_version 5.4.0
%global prerelease       beta.0

%global appdir /opt/Wootility-Beta
%global appimage Wootility-%{upstream_version}-%{prerelease}.AppImage

Name:           wootility-beta
Version:        %{upstream_version}~%{prerelease}
Release:        2%{?dist}
Summary:        Beta channel of the Wooting keyboard configuration utility

License:        LicenseRef-Wooting-EULA
URL:            https://wooting.io/wootility
Source0:        https://wootility-updates.ams3.cdn.digitaloceanspaces.com/wootility-linux/Wootility-%{upstream_version}-%{prerelease}.AppImage

ExclusiveArch:  x86_64

Requires:       fuse-libs
Requires:       hicolor-icon-theme
Requires:       zlib
Requires:       wooting-udev

%description
Beta-channel build of Wootility, the official configuration utility for
Wooting keyboards. Installs alongside the stable wootility package under
/opt/Wootility-Beta and exposes a /usr/bin/wootility-beta launcher plus
a "Wootility Beta" desktop entry with renamed icons.

%prep
%setup -q -c -T
cp -p %{SOURCE0} ./%{appimage}
chmod +x ./%{appimage}
./%{appimage} --appimage-extract wootility.desktop
./%{appimage} --appimage-extract usr/share/icons

# Differentiate the beta from the stable: rewrite Exec to our wrapper
# (passing --class so the bundled Electron app sets WM_CLASS=WootilityBeta
# and isn't grouped with a running stable Wootility), point Icon at the
# renamed beta icon, set StartupWMClass to match the new WM_CLASS, append
# " Beta" to all Name= keys (including locale variants), and rename the
# .desktop file itself.
sed -i -E 's|^Exec=AppRun|Exec=env DESKTOPINTEGRATION=false /usr/bin/%{name} --class=WootilityBeta|' \
    squashfs-root/wootility.desktop
sed -i -E 's|^Icon=.*|Icon=%{name}|' squashfs-root/wootility.desktop
sed -i -E 's|^StartupWMClass=.*|StartupWMClass=WootilityBeta|' squashfs-root/wootility.desktop
sed -i -E 's|^(Name(\[[^]]+\])?=)(.*)$|\1\3 Beta|' squashfs-root/wootility.desktop
mv squashfs-root/wootility.desktop squashfs-root/%{name}.desktop

# Rename every wootility.<ext> icon under the extracted icons tree to
# wootility-beta.<ext> so we don't collide with the stable package.
find squashfs-root/usr/share/icons -name 'wootility.*' | while read -r f; do
    dir=$(dirname "$f")
    ext=${f##*.}
    mv "$f" "$dir/%{name}.$ext"
done

# AppImage extracts directories as 0700 — fix perms before we ship them.
chmod -R a-x+rX squashfs-root/usr

%build

%install
install -dm0755 %{buildroot}%{appdir}
install -dm0755 %{buildroot}%{_bindir}
install -m0755 %{SOURCE0} %{buildroot}%{appdir}/%{appimage}
ln -s %{appdir}/%{appimage} %{buildroot}%{_bindir}/%{name}

install -Dm0644 squashfs-root/%{name}.desktop \
    %{buildroot}%{_datadir}/applications/%{name}.desktop

mkdir -p %{buildroot}%{_datadir}/icons
cp -a squashfs-root/usr/share/icons/. %{buildroot}%{_datadir}/icons/

%files
%dir %{appdir}
%{appdir}/%{appimage}
%{_bindir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}.*

%changelog
* Sat May 02 2026 Kristián Kekeš <gamerix2006@gmail.com> - 5.4.0~beta.0-2
- Pass --class=WootilityBeta to the bundled Electron app and set the
  matching StartupWMClass so window managers don't group the beta with
  a running stable Wootility
* Sat May 02 2026 Kristián Kekeš <gamerix2006@gmail.com> - 5.4.0~beta.0-1
- Initial RPM package wrapping the upstream Wootility beta AppImage
