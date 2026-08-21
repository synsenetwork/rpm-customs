%global debug_package %{nil}
%global appdir /opt/%{name}

Name:           jetbrains-toolbox
Version:        3.7.2.87231
Release:        1%{?dist}
Summary:        Manage all your JetBrains projects and tools

License:        LicenseRef-JetBrains-User-Agreement
URL:            https://www.jetbrains.com/toolbox/
Source0:        https://download.jetbrains.com/toolbox/%{name}-%{version}.tar.gz
Source1:        %{name}.desktop
Source2:        icon.svg
Source3:        LICENSE

ExclusiveArch:  x86_64

Requires:       xdg-utils

%description
JetBrains Toolbox helps you install, manage, and update JetBrains IDEs and
related tools from one desktop application.

%prep
%setup -q -n %{name}-%{version}

%build

%install
install -dm0755 %{buildroot}%{_bindir}
install -dm0755 %{buildroot}%{appdir}
install -dm0755 %{buildroot}%{_datadir}/applications
install -dm0755 %{buildroot}%{_datadir}/pixmaps

cp -a bin/* %{buildroot}%{appdir}/

install -m0644 %{SOURCE1} %{buildroot}%{_datadir}/applications/%{name}.desktop
install -m0644 %{SOURCE2} %{buildroot}%{_datadir}/pixmaps/%{name}.svg
install -Dm0644 %{SOURCE3} %{buildroot}%{_licensedir}/%{name}/LICENSE.txt

ln -s ../../opt/%{name}/%{name} %{buildroot}%{_bindir}/%{name}

%files
%license %{_licensedir}/%{name}/LICENSE.txt
%{_bindir}/%{name}
%{appdir}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/pixmaps/%{name}.svg

%changelog
* Fri Aug 21 2026 Automated Update <github-actions@github.com> - 3.7.2.87231-1
- Update to version 3.7.2.87231
* Wed Aug 19 2026 Automated Update <github-actions@github.com> - 3.7.0.87111-1
- Update to version 3.7.0.87111
* Wed Aug 05 2026 Automated Update <github-actions@github.com> - 3.6.4.86641-1
- Update to version 3.6.4.86641
* Wed Jul 29 2026 Automated Update <github-actions@github.com> - 3.6.3.86383-1
- Update to version 3.6.3.86383
* Thu Jul 23 2026 Automated Update <github-actions@github.com> - 3.6.2.85969-1
- Update to version 3.6.2.85969
* Sun Jul 05 2026 Automated Update <github-actions@github.com> - 3.6.1.85592-1
- Update to version 3.6.1.85592
* Fri Jul 03 2026 Automated Update <github-actions@github.com> - 3.6.0.85549-1
- Update to version 3.6.0.85549
* Wed Jun 03 2026 Automated Update <github-actions@github.com> - 3.5.0.84344-1
- Update to version 3.5.0.84344
* Mon Apr 27 2026 Kristián Kekeš <gamerix2006@gmail.com> - 3.4.3.81140-1
- Initial RPM package from the upstream JetBrains Toolbox binary release
