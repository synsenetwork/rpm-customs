%global debug_package %{nil}
%global appdir /opt/Wootility
%global appimage Wootility-%{version}.AppImage

Name:           wootility
Version:        5.3.0
Release:        1%{?dist}
Summary:        Utility for configuring Wooting keyboards

License:        LicenseRef-Wooting-EULA
URL:            https://wooting.io/wootility
Source0:        https://wootility-updates.ams3.cdn.digitaloceanspaces.com/wootility-linux/Wootility-%{version}.AppImage

ExclusiveArch:  x86_64

Requires:       fuse-libs
Requires:       hicolor-icon-theme
Requires:       zlib
Requires:       wooting-udev

%description
Wootility is the official configuration utility for Wooting keyboards
(Wooting One, Wooting Two, Wooting 60HE, etc.). Upstream distributes it
as an AppImage; this package wraps that AppImage, installs a desktop
entry plus icons extracted from it, and provides a /usr/bin/wootility
launcher.

%prep
%setup -q -c -T
cp -p %{SOURCE0} ./%{appimage}
chmod +x ./%{appimage}
./%{appimage} --appimage-extract %{name}.desktop
./%{appimage} --appimage-extract usr/share/icons
sed -i -E 's|^Exec=AppRun|Exec=env DESKTOPINTEGRATION=false /usr/bin/%{name}|' \
    squashfs-root/%{name}.desktop
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
* Sat May 02 2026 Kristián Kekeš <gamerix2006@gmail.com> - 5.3.0-1
- Initial RPM package wrapping the upstream Wootility AppImage
