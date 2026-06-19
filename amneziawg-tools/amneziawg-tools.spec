%global commit 61e741780e8465a67a7d7fb6cffe14a8a15d624a
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global commitdate 20260619

Name:           amneziawg-tools
Version:        1.0.%{commitdate}git%{shortcommit}
Release:        1%{?dist}
URL:            https://github.com/amnezia-vpn/amneziawg-tools
Summary:        AmneziaWG VPN userspace tools
License:        GPL-2.0-only

Source0:        https://github.com/amnezia-vpn/amneziawg-tools/archive/%{commit}/amneziawg-tools-%{shortcommit}.tar.gz

%{?systemd_requires}
BuildRequires:  make
BuildRequires:  systemd
BuildRequires:  gcc

%description
AmneziaWG is a contemporary version of the popular VPN protocol WireGuard.
It's a fork of WireGuard and offers protection against detection by Deep Packet
Inspection (DPI) systems. AmneziaWG modifies packet headers to make them
indistinguishable from regular web traffic, helping to bypass censorship in
restrictive networks.

This package provides the awg binary for controlling AmneziaWG and awg-quick
for managing AmneziaWG interfaces.

%prep
%autosetup -p1 -n amneziawg-tools-%{commit}

%build
%set_build_flags

%make_build RUNSTATEDIR=%{_rundir} -C src

%install
%make_install BINDIR=%{_bindir} MANDIR=%{_mandir} RUNSTATEDIR=%{_rundir} \
WITH_BASHCOMPLETION=yes WITH_WGQUICK=yes WITH_SYSTEMDUNITS=yes -C src

%files
%doc README.md contrib
%license COPYING
%{_bindir}/awg
%{_bindir}/awg-quick
%{_sysconfdir}/amnezia/amneziawg/
%{_datadir}/bash-completion/completions/awg
%{_datadir}/bash-completion/completions/awg-quick
%{_unitdir}/awg-quick@.service
%{_unitdir}/awg-quick.target
%{_mandir}/man8/awg.8*
%{_mandir}/man8/awg-quick.8*

%changelog
* Fri Jun 19 2026 Automated Update <github-actions@github.com> - 1.0.20260619git61e7417-1
- Update to git commit 61e7417
* Thu Apr 30 2026 Kristián Kekeš <gamerix2006@gmail.com> - 1.0.20260403git5d6179a-1
- Use SPDX license identifier
- Drop DNS Hatchet block (only triggered on Fedora <33 / RHEL <9)
* Fri Apr 03 2026 Automated Update <github-actions@github.com> - 1.0.20260403git5d6179a-1
- Update to git commit 5d6179a
* Fri Apr 04 2025 Automated Update <github-actions@github.com> - 1.0.20260403git5d6179a-1
- Initial automated tracking from git commit 5d6179a
