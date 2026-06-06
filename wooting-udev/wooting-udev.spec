Name:           wooting-udev
Version:        1.0.0
Release:        1%{?dist}
Summary:        udev rules granting user access to Wooting keyboards

License:        MIT
URL:            https://github.com/synsenetwork/rpm-customs
BuildArch:      noarch

Source0:        70-wooting.rules

Requires:       systemd-udev

%description
Installs /etc/udev/rules.d/70-wooting.rules so non-root users can talk to
Wooting keyboards (Wooting One, Wooting Two, and generic Wooting devices,
including their bootloader/update-mode product IDs) via hidraw and usb.

The rules attach the uaccess tag, which grants the local logged-in user
read/write access through systemd-logind without needing a custom group.

%prep

%build

%install
install -Dpm0644 %{SOURCE0} %{buildroot}%{_sysconfdir}/udev/rules.d/70-wooting.rules

%files
%config(noreplace) %{_sysconfdir}/udev/rules.d/70-wooting.rules

%post
if [ -x /usr/bin/udevadm ]; then
    /usr/bin/udevadm control --reload-rules || :
    /usr/bin/udevadm trigger || :
fi

%postun
if [ $1 -eq 0 ] && [ -x /usr/bin/udevadm ]; then
    /usr/bin/udevadm control --reload-rules || :
    /usr/bin/udevadm trigger || :
fi

%changelog
* Sat May 02 2026 Kristián Kekeš <gamerix2006@gmail.com> - 1.0.0-1
- Initial package
