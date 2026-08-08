%global debug_package %{nil}
%global _lto_cflags %{nil}
%global autovirt_commit dd88bea77b85070f44e5f948eed485422e8a8b5b
# Pinned tip of https://github.com/synsenetwork/qemu-shadow/tree/amd
%global qemu_commit 9db0d1a363563f7366cb2dde971f5b01e4ad2f2f

Name:           qemu-shadow-amd
Version:        11.0.3
Release:        2%{?dist}
Epoch:          3
Summary:        AutoVirt-patched QEMU replacement for AMD hosts

License:        Apache-2.0 AND BSD-2-Clause AND BSD-3-Clause AND FSFAP AND GPL-1.0-or-later AND GPL-2.0-only AND GPL-2.0-or-later AND GPL-2.0-or-later WITH GCC-exception-2.0 AND LGPL-2.0-only AND LGPL-2.0-or-later AND LGPL-2.1-only AND LGPL-2.1-or-later AND MIT AND LicenseRef-Fedora-Public-Domain AND CC-BY-3.0
URL:            https://github.com/synsenetwork/qemu-shadow
Source11:       bridge.conf
Source12:       qemu.sysusers

ExclusiveArch:  x86_64

BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  git-core
BuildRequires:  make
BuildRequires:  meson >= 1.5.0
BuildRequires:  ninja-build
BuildRequires:  python3
BuildRequires:  python3-pip
BuildRequires:  python3-qemu-qmp
BuildRequires:  python3-setuptools
BuildRequires:  python3-wheel
BuildRequires:  systemd-rpm-macros
BuildRequires:  pkgconfig(alsa)
BuildRequires:  pkgconfig(gio-2.0)
BuildRequires:  pkgconfig(gnutls)
BuildRequires:  pkgconfig(libcap-ng)
BuildRequires:  pkgconfig(libcurl)
BuildRequires:  pkgconfig(libseccomp)
BuildRequires:  pkgconfig(slirp)
BuildRequires:  pkgconfig(libusb-1.0)
BuildRequires:  pkgconfig(libudev)
BuildRequires:  pkgconfig(liburing)
BuildRequires:  pkgconfig(libzstd)
BuildRequires:  pkgconfig(pixman-1)
BuildRequires:  pkgconfig(libpipewire-0.3)
BuildRequires:  pkgconfig(libpulse)
BuildRequires:  pkgconfig(sdl2)
BuildRequires:  pkgconfig(spice-protocol)
BuildRequires:  pkgconfig(spice-server)
BuildRequires:  pkgconfig(libusbredirparser-0.5)
BuildRequires:  pkgconfig(xkbcommon)
BuildRequires:  libaio-devel
BuildRequires:  libepoxy-devel
BuildRequires:  libfdt-devel
BuildRequires:  numactl-devel

Requires:       edk2-shadow-amd
Requires:       seabios-bin
Requires:       seavgabios-bin

# Epoch 3 is intentionally higher than Fedora QEMU's epoch 2.  These virtual
# provides and versioned conflicts let DNF --allowerasing replace the
# incompatible split Fedora stack without considering the other Shadow vendor
# variant as another candidate to obsolete the same packages.
Provides:       qemu = %{epoch}:%{version}-%{release}
Provides:       qemu-common = %{epoch}:%{version}-%{release}
Provides:       qemu-img = %{epoch}:%{version}-%{release}
Provides:       qemu-kvm = %{epoch}:%{version}-%{release}
Provides:       qemu-kvm-core = %{epoch}:%{version}-%{release}
Provides:       qemu-pr-helper = %{epoch}:%{version}-%{release}
Provides:       qemu-system-x86 = %{epoch}:%{version}-%{release}
Provides:       qemu-system-x86-core = %{epoch}:%{version}-%{release}
Provides:       qemu-tools = %{epoch}:%{version}-%{release}

Conflicts:      qemu < %{epoch}:%{version}-%{release}
Conflicts:      qemu-common < %{epoch}:%{version}-%{release}
Conflicts:      qemu-img < %{epoch}:%{version}-%{release}
Conflicts:      qemu-kvm < %{epoch}:%{version}-%{release}
Conflicts:      qemu-kvm-core < %{epoch}:%{version}-%{release}
Conflicts:      qemu-pr-helper < %{epoch}:%{version}-%{release}
Conflicts:      qemu-system-x86 < %{epoch}:%{version}-%{release}
Conflicts:      qemu-system-x86-core < %{epoch}:%{version}-%{release}
Conflicts:      qemu-tools < %{epoch}:%{version}-%{release}
Conflicts:      qemu-shadow-intel

%description
qemu-shadow-amd is a compact, KVM-only x86_64 QEMU build carrying the AMD
hardware-spoofing patch from AutoVirt commit %{autovirt_commit}. It installs
the normal system QEMU executable names and intentionally replaces Fedora's
split QEMU packages. It is mutually exclusive with qemu-shadow-intel.

%prep
%setup -q -T -c -n qemu-shadow-%{qemu_commit}
git init .
git remote add origin %{url}
git fetch --depth 1 origin %{qemu_commit}
git checkout --detach FETCH_HEAD
test "$(git rev-parse HEAD)" = "%{qemu_commit}"

%build
./configure \
    --target-list=x86_64-softmmu \
    --prefix=%{_prefix} \
    --libdir=%{_libdir} \
    --datadir=%{_datadir} \
    --sysconfdir=%{_sysconfdir} \
    --libexecdir=%{_libexecdir} \
    --with-suffix=%{name} \
    --with-pkgversion=%{name}-%{version}-%{release} \
    --firmwarepath=%{_datadir}/qemu-firmware:%{_datadir}/ipxe/qemu:%{_datadir}/seavgabios:%{_datadir}/seabios:%{_datadir}/edk2/ovmf:%{_datadir}/OVMF \
    --without-default-features \
    --enable-system \
    --enable-kvm \
    --enable-linux-aio \
    --enable-linux-io-uring \
    --enable-pixman \
    --enable-opengl \
    --enable-sdl \
    --enable-spice \
    --enable-spice-protocol \
    --enable-libusb \
    --enable-usb-redir \
    --enable-libudev \
    --enable-pipewire \
    --enable-pa \
    --enable-alsa \
    --audio-drv-list=pipewire,pa,alsa,sdl \
    --enable-tpm \
    --enable-numa \
    --enable-seccomp \
    --enable-zstd \
    --enable-cap-ng \
    --enable-slirp \
    --enable-gnutls \
    --enable-curl \
    --enable-fdt=system \
    --enable-vhost-kernel \
    --enable-vhost-net \
    --enable-vhost-user \
    --enable-tools \
    --enable-xkbcommon \
    --enable-pie \
    --disable-modules \
    --disable-docs \
    --disable-guest-agent \
    --disable-linux-user \
    --disable-bsd-user \
    --disable-tcg \
    --disable-werror \
    --extra-cflags="%{optflags}" \
    --extra-ldflags="%{build_ldflags}"

%ninja_build -C build

%install
build/pyvenv/bin/meson install -C build --no-rebuild \
    --destdir %{buildroot}
ln -s qemu-system-x86_64 %{buildroot}%{_bindir}/qemu-kvm

# The Shadow build is intentionally CLI/libvirt focused.
rm -rf %{buildroot}%{_datadir}/applications
rm -rf %{buildroot}%{_datadir}/icons
rm -rf %{buildroot}%{_datadir}/locale

# Do not ship QEMU's generic EDK2 blobs beside the vendor-patched firmware.
# libvirt and QEMU must resolve OVMF from the required edk2-shadow-amd RPM.
rm -f %{buildroot}%{_datadir}/%{name}/edk2-*.fd
rm -f %{buildroot}%{_datadir}/%{name}/edk2-licenses.txt
rm -rf %{buildroot}%{_datadir}/%{name}/firmware

install -Dm0644 %{SOURCE11} \
    %{buildroot}%{_sysconfdir}/%{name}/bridge.conf
install -Dm0644 %{SOURCE12} \
    %{buildroot}%{_sysusersdir}/qemu.conf

%check
%{buildroot}%{_bindir}/qemu-system-x86_64 --version | grep -F '%{version}'

%files
%license COPYING COPYING.LIB LICENSE
%doc README.rst
%{_bindir}/qemu-*
%{_bindir}/elf2dmp
%attr(4755,root,root) %{_libexecdir}/qemu-bridge-helper
%dir %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/bridge.conf
%{_sysusersdir}/qemu.conf
%{_datadir}/%{name}/

%changelog
* Sat Aug 08 2026 Kristián Kekeš <gamerix2006@gmail.com> - 3:11.0.3-2
- Replace Fedora QEMU through solver-safe Provides/Conflicts metadata
- Provide and conflict with Fedora's separate qemu-pr-helper package

* Thu Aug 06 2026 Kristián Kekeš <gamerix2006@gmail.com> - 3:11.0.3-1
- Build from the pinned AMD branch of synsenetwork/qemu-shadow
- Carry the AutoVirt QEMU changes from commit dd88bea
- Replace Fedora's split QEMU stack with a compact KVM-only x86_64 build
