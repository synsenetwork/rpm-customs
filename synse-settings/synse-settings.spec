%global commit      79e615e0cbc8ca97c3e591cf1f3be44afadfb819
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global commitdate  20260606

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
if [ -f usr/lib/modprobe.d/nvidia.conf ]; then
    mv usr/lib/modprobe.d/nvidia.conf usr/lib/modprobe.d/nvidia_synse.conf
fi
mkdir -p %{buildroot}
cp -a etc usr %{buildroot}/

%files
%license LICENSE.md
%doc README.md
%config(noreplace) %{_sysconfdir}/security/limits.d/*
%{_prefix}/lib/modprobe.d/*
%{_prefix}/lib/NetworkManager/conf.d/*
%{_prefix}/lib/sysctl.d/*
%{_prefix}/lib/systemd/**
%{_prefix}/lib/tmpfiles.d/*
%{_prefix}/lib/udev/rules.d/*

%changelog
* Tue Jun 09 2026 Kristián Kekeš <gamerix2006@gmail.com> - 1.0.20260609git79e615e-1
- Remove X11/Xorg input configuration (Wayland-only system assumption)
- Drop legacy xorg.conf.d touchpad InputClass rules
- Clean packaging metadata to reflect Wayland-native setup

* Sat Jun 06 2026 Kristián Kekeš <gamerix2006@gmail.com> - 1.0.20260606gitbc5d0bc-1
- Initial package (CachyOS-settings fork @ bc5d0bc)
- Depend on ntsync-autoload instead of shipping ntsync.conf
- Rename nvidia.conf to nvidia_synse.conf to avoid nvidia-driver file conflict
- Provide/Conflict zram-generator-defaults (ship CachyOS zram-generator.conf)
