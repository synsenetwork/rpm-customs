%global commit e59165a8881ad747119b2f57a187f832440bbc66
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global commitdate 20260619

Name:           synse-settings
Version:        1.0.%{commitdate}git%{shortcommit}
Release:        1%{?dist}
Summary:        Personal CachyOS-settings fork: system tuning configs for Fedora (AMD-focused)

License:        GPL-3.0-or-later
URL:            https://github.com/synsenetwork/synse-settings
Source0:        %{url}/archive/%{commit}/synse-settings-%{shortcommit}.tar.gz

BuildArch:      noarch

Requires:       zram-generator
Provides:       zram-generator-defaults
Conflicts:      zram-generator-defaults
Requires:       ntsync-autoload

Recommends:     tuned
Recommends:     tuned-ppd

%description
synse-settings is a personal fork of CachyOS-settings, trimmed for Fedora on AMD
hardware. It is a collection of drop-in system configuration files: sysctl tuning,
udev I/O-scheduler and device rules, modprobe options, systemd manager and service
drop-ins, tmpfiles entries, NetworkManager DNS snippet, and PAM audio limits.
No support or stability is implied.

%prep
%autosetup -p1 -n %{name}-%{commit}

%build

%install
mkdir -p %{buildroot}
cp -a etc usr %{buildroot}/

%files
%license LICENSE.md
%doc README.md
%config(noreplace) %{_sysconfdir}/security/limits.d/*
%dir %{_sysconfdir}/tuned/profiles/throughput-performance
%config(noreplace) %{_sysconfdir}/tuned/profiles/throughput-performance/tuned.conf
%{_prefix}/lib/modprobe.d/*
%{_prefix}/lib/NetworkManager/conf.d/*
%{_prefix}/lib/sysctl.d/*
%{_prefix}/lib/systemd/**
%{_prefix}/lib/tmpfiles.d/*
%{_prefix}/lib/udev/rules.d/*

%changelog
* Fri Jun 19 2026 Automated Update <github-actions@github.com> - 1.0.20260619gite59165a-1
- Update to git commit e59165a
* Wed Jun 10 2026 Kristián Kekeš <gamerix2006@gmail.com> - 1.0.20260610gitd110023-1
- Ship /etc/tuned throughput-performance shadow profile (stop tuned-ppd
  clobbering sysctl.d VM tuning)
- Rename 70-cachyos-settings.conf to 70-synse-settings.conf
- Add gaming sysctls: split_lock_mitigate=0, compaction_proactiveness=0,
  BBR+fq, TCP fast open
- Enable THP=always (pairs with existing THP shrinker tuning)
- Drop NVIDIA modprobe/udev configs and legacy GCN amdgpu.conf (all-AMD,
  RDNA2+ machines)

* Wed Jun 10 2026 Automated Update <github-actions@github.com> - 1.0.20260610gitd110023-1
- Update to git commit d110023
* Tue Jun 09 2026 Kristián Kekeš <gamerix2006@gmail.com> - 1.0.20260609gitf006980-1
- Move RAPL permissions to tmpfiles.conf
- Remove X11/Xorg input configuration (Wayland-only system assumption)
- Drop legacy xorg.conf.d touchpad InputClass rules
- Clean packaging metadata to reflect Wayland-native setup

* Sat Jun 06 2026 Kristián Kekeš <gamerix2006@gmail.com> - 1.0.20260606gitbc5d0bc-1
- Initial package (CachyOS-settings fork @ bc5d0bc)
- Depend on ntsync-autoload instead of shipping ntsync.conf
- Rename nvidia.conf to nvidia_synse.conf to avoid nvidia-driver file conflict
- Provide/Conflict zram-generator-defaults (ship CachyOS zram-generator.conf)
