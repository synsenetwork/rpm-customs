%global upstream_version 1.8.0
%global prerelease     pre
%global appid          dev.zed.Zed-Preview
%global appdir         %{_libdir}/%{name}
%global bundledir      %{appdir}/zed-preview.app
%global debug_package  %{nil}

Name:           zed
Version:        %{upstream_version}~%{prerelease}
Release:        1%{?dist}
Summary:        Prebuilt prerelease build of the Zed code editor

License:        GPL-3.0-or-later AND AGPL-3.0-or-later AND Apache-2.0
URL:            https://zed.dev
Source0:        https://github.com/zed-industries/zed/releases/download/v%{upstream_version}-%{prerelease}/zed-linux-x86_64.tar.gz

ExclusiveArch:  x86_64

Obsoletes:      zed-editor < %{version}-%{release}
Provides:       zed-editor = %{version}-%{release}

%description
Zed is a high-performance, multiplayer code editor from the creators of Atom
and Tree-sitter. This package repackages the upstream Linux prerelease bundle
instead of building Zed from source.

%prep
%setup -q -c -T
tar -xzf %{SOURCE0}

%build

%install
install -dm0755 %{buildroot}%{appdir}
cp -a zed-preview.app %{buildroot}%{appdir}/
chmod 0644 %{buildroot}%{bundledir}/share/applications/%{appid}.desktop

install -dm0755 %{buildroot}%{_bindir}
ln -s ../lib64/zed/zed-preview.app/bin/zed %{buildroot}%{_bindir}/zed
ln -s ../lib64/zed/zed-preview.app/bin/zed %{buildroot}%{_bindir}/zeditor

install -dm0755 %{buildroot}%{_datadir}/applications
install -dm0755 %{buildroot}%{_datadir}/icons/hicolor/512x512/apps
install -dm0755 %{buildroot}%{_datadir}/icons/hicolor/1024x1024/apps
install -m0644 zed-preview.app/share/applications/%{appid}.desktop \
    %{buildroot}%{_datadir}/applications/%{appid}.desktop
install -m0644 zed-preview.app/share/icons/hicolor/512x512/apps/zed.png \
    %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/zed.png
install -m0644 zed-preview.app/share/icons/hicolor/1024x1024/apps/zed.png \
    %{buildroot}%{_datadir}/icons/hicolor/1024x1024/apps/zed.png

%files
%license %{bundledir}/licenses.md
%{_bindir}/zed
%{_bindir}/zeditor
%exclude %{bundledir}/licenses.md
%{appdir}
%{_datadir}/applications/%{appid}.desktop
%{_datadir}/icons/hicolor/512x512/apps/zed.png
%{_datadir}/icons/hicolor/1024x1024/apps/zed.png

%changelog
* Fri Jun 19 2026 Automated Update <github-actions@github.com> - 1.8.0~pre-1
- Update to prerelease 1.8.0-pre
* Sat Jun 13 2026 Automated Update <github-actions@github.com> - 1.7.2~pre-1
- Update to prerelease 1.7.2-pre
* Thu Jun 11 2026 Automated Update <github-actions@github.com> - 1.7.1~pre-1
- Update to prerelease 1.7.1-pre
* Wed Jun 10 2026 Automated Update <github-actions@github.com> - 1.6.3~pre-1
- Update to prerelease 1.6.3-pre
* Sat Jun 06 2026 Automated Update <github-actions@github.com> - 1.6.1~pre-1
- Update to prerelease 1.6.1-pre
* Fri May 29 2026 Automated Update <github-actions@github.com> - 1.5.3~pre-1
- Update to prerelease 1.5.3-pre
* Tue May 26 2026 Automated Update <github-actions@github.com> - 1.4.2~pre-1
- Update to prerelease 1.4.2-pre
* Fri May 22 2026 Automated Update <github-actions@github.com> - 1.4.1~pre-1
- Update to prerelease 1.4.1-pre
* Thu May 21 2026 Automated Update <github-actions@github.com> - 1.4.0~pre-1
- Update to prerelease 1.4.0-pre
* Wed May 20 2026 Automated Update <github-actions@github.com> - 1.3.5~pre-1
- Update to prerelease 1.3.5-pre
* Tue May 19 2026 Automated Update <github-actions@github.com> - 1.3.4~pre-1
- Update to prerelease 1.3.4-pre
* Sat May 16 2026 Automated Update <github-actions@github.com> - 1.3.3~pre-1
- Update to prerelease 1.3.3-pre
* Fri May 15 2026 Automated Update <github-actions@github.com> - 1.3.2~pre-1
- Update to prerelease 1.3.2-pre
* Thu May 14 2026 Automated Update <github-actions@github.com> - 1.3.0~pre-1
- Update to prerelease 1.3.0-pre
* Wed May 13 2026 Automated Update <github-actions@github.com> - 1.2.3~pre-1
- Update to prerelease 1.2.3-pre
* Sat May 09 2026 Automated Update <github-actions@github.com> - 1.2.2~pre-1
- Update to prerelease 1.2.2-pre
* Thu May 07 2026 Automated Update <github-actions@github.com> - 1.2.1~pre-1
- Update to prerelease 1.2.1-pre
* Wed May 06 2026 Automated Update <github-actions@github.com> - 1.1.5~pre-1
- Update to prerelease 1.1.5-pre
* Mon May 04 2026 Automated Update <github-actions@github.com> - 1.1.3~pre-1
- Update to prerelease 1.1.3-pre
* Thu Apr 30 2026 Automated Update <github-actions@github.com> - 1.1.2~pre-1
- Update to prerelease 1.1.2-pre
* Sat Apr 25 2026 Automated Update <github-actions@github.com> - 0.234.6~pre-1
- Update to prerelease 0.234.6-pre
* Fri Apr 24 2026 Automated Update <github-actions@github.com> - 0.234.5~pre-1
- Update to prerelease 0.234.5-pre
* Thu Apr 23 2026 Automated Update <github-actions@github.com> - 0.234.3~pre-1
- Update to prerelease 0.234.3-pre
* Wed Apr 22 2026 Automated Update <github-actions@github.com> - 0.233.5~pre-1
- Update to prerelease 0.233.5-pre
* Tue Apr 21 2026 Automated Update <github-actions@github.com> - 0.233.4~pre-1
- Update to prerelease 0.233.4-pre
* Sat Apr 18 2026 Automated Update <github-actions@github.com> - 0.233.2~pre-1
- Update to prerelease 0.233.2-pre
* Fri Apr 17 2026 Automated Update <github-actions@github.com> - 0.233.1~pre-1
- Update to prerelease 0.233.1-pre
* Thu Apr 16 2026 Automated Update <github-actions@github.com> - 0.233.0~pre-1
- Update to prerelease 0.233.0-pre
* Mon Apr 13 2026 Kristián Kekeš <gamerix2006@gmail.com> - 0.232.2~pre-1
- Repackage the upstream Zed prerelease binary bundle
