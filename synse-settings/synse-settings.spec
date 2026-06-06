%global commit      1b1b2cab051c585f73eb95fc98ec869a4a29777c
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global commitdate  20260606

Name:           synse-settings
Version:        1.0.%{commitdate}git%{shortcommit}
Release:        1%{?dist}
Summary:        Personal CachyOS-settings fork: system tuning configs for Fedora (AMD-focused)

License:        GPL-3.0-or-later
URL:            https://github.com/synsejse/synse-settings
Source0:        %{url}/archive/%{commit}/synse-settings-%{shortcommit}.tar.gz

BuildArch:      noarch

Requires:       zram-generator
Provides:       zram-generator-defaults
Conflicts:      zram-generator-defaults
Requires:       ntsync-autoload

%description
synse-settings is a personal fork of CachyOS-settings, trimmed for Fedora on AMD
hardware. It is a collection of drop-in system configuration files: sysctl tuning,
udev I/O-scheduler and device rules, modprobe options, systemd manager and service
drop-ins, tmpfiles entries, a NetworkManager DNS snippet, an X11 touchpad profile,
and PAM audio limits. No support or stability is implied.

%prep
%autosetup -p1 -n %{name}-%{commit}

%build

%install
if [ -f usr/lib/modprobe.d/nvidia.conf ]; then
    mv usr/lib/modprobe.d/nvidia.conf usr/lib/modprobe.d/nvidia_synse.conf
fi
mkdir -p %{buildroot}
cp -a etc usr %{buildroot}/

%files
%license LICENSE.md
%doc README.md
%config(noreplace) %{_sysconfdir}/security/limits.d/*
%{_prefix}/lib/*
%dir %{_datadir}/X11
%{_datadir}/X11/xorg.conf.d

%changelog
* Sat Jun 06 2026 Kristián Kekeš <gamerix2006@gmail.com> - 1.0.20260606git1b1b2ca-1
- Initial package (CachyOS-settings fork @ 1b1b2ca)
- Drop ntsync.conf; depend on ntsync-autoload instead
- Rename nvidia.conf to nvidia_synse.conf to avoid nvidia-driver file conflict
- Provide/Conflict zram-generator-defaults (ship CachyOS zram-generator.conf)
