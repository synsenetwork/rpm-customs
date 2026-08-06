%undefine _auto_set_build_flags
%global debug_package %{nil}
%global autovirt_commit dd88bea77b85070f44e5f948eed485422e8a8b5b
# Pinned tip of https://github.com/synsenetwork/edk2-shadow/tree/intel
%global edk2_commit 86ff5df7b2a8797439c3d012c88cf8f3fcd1c0e0
%global openssl_version 3.5.7
%global jansson_version 2.13.1
%global dtc_version 1.7.0

Name:           edk2-shadow-intel
Version:        20260508
Release:        1%{?dist}
Epoch:          1
Summary:        AutoVirt-patched OVMF replacement for Intel hosts

License:        Apache-2.0 AND (BSD-2-Clause OR GPL-2.0-or-later) AND BSD-2-Clause-Patent AND BSD-4-Clause AND ISC AND MIT AND LicenseRef-Fedora-Public-Domain
URL:            https://github.com/synsenetwork/edk2-shadow
Source1:        https://github.com/openssl/openssl/releases/download/openssl-%{openssl_version}/openssl-%{openssl_version}.tar.gz
Source2:        https://github.com/akheron/jansson/releases/download/v%{jansson_version}/jansson-%{jansson_version}.tar.bz2
Source3:        https://mirrors.edge.kernel.org/pub/software/utils/dtc/dtc-%{dtc_version}.tar.xz
Source20:       40-edk2-shadow-intel-x64.json

ExclusiveArch:  x86_64

BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  git
BuildRequires:  make
BuildRequires:  nasm
BuildRequires:  acpica-tools
BuildRequires:  libuuid-devel
BuildRequires:  python3
BuildRequires:  python3-virt-firmware
BuildRequires:  perl(File::Compare)
BuildRequires:  perl(File::Copy)
BuildRequires:  perl(FindBin)
BuildRequires:  perl(IPC::Cmd)
BuildRequires:  perl(JSON)
BuildRequires:  perl(Time::Piece)

Provides:       bundled(openssl) = %{openssl_version}
Provides:       edk2-ovmf = %{epoch}:%{version}-%{release}
Provides:       OVMF = %{epoch}:%{version}-%{release}
Obsoletes:      edk2-ovmf < %{epoch}:%{version}-%{release}
Obsoletes:      OVMF < %{epoch}:%{version}-%{release}
Conflicts:      edk2-ovmf < %{epoch}:%{version}-%{release}
Conflicts:      OVMF < %{epoch}:%{version}-%{release}
Conflicts:      edk2-shadow-amd

%description
edk2-shadow-intel provides a compact OVMF build carrying AutoVirt's Intel firmware
spoofing patch from commit %{autovirt_commit}. It installs the standard Fedora
OVMF paths and libvirt firmware metadata, and intentionally replaces
edk2-ovmf. It is mutually exclusive with edk2-shadow-amd.

The firmware supports Secure Boot and SMM, but its packaged variable-store
template is intentionally empty. Enroll keys into a per-VM copy rather than
embedding build-host keys in a reproducible RPM.

%prep
%setup -q -T -c -n edk2-shadow-%{edk2_commit}
git init .
git remote add origin %{url}
git fetch --depth 1 origin %{edk2_commit}
git checkout --detach FETCH_HEAD
test "$(git rev-parse HEAD)" = "%{edk2_commit}"

mkdir -p CryptoPkg/Library/OpensslLib/openssl
mkdir -p RedfishPkg/Library/JsonLib/jansson
mkdir -p MdePkg/Library/BaseFdtLib/libfdt
tar -xf %{SOURCE1} --strip-components=1 \
    --directory CryptoPkg/Library/OpensslLib/openssl
tar -xf %{SOURCE2} --strip-components=1 \
    --directory RedfishPkg/Library/JsonLib/jansson
tar -xf %{SOURCE3} --strip-components=1 \
    --directory MdePkg/Library/BaseFdtLib/libfdt

# Package parsers require these unused submodule include paths to exist.
mkdir -p MdePkg/Library/MipiSysTLib/mipisyst/library/include
mkdir -p CryptoPkg/Library/MbedTlsLib/mbedtls/include/mbedtls
mkdir -p CryptoPkg/Library/MbedTlsLib/mbedtls/library
mkdir -p SecurityPkg/DeviceSecurity/SpdmLib/libspdm/include

%build
export WORKSPACE="$PWD"
export EDK_TOOLS_PATH="$WORKSPACE/BaseTools"
export CONF_PATH="$WORKSPACE/Conf"
export PYTHON_COMMAND=python3

make -C BaseTools -j%{_smp_build_ncpus}
. ./edksetup.sh
python3 CryptoPkg/Library/OpensslLib/configure.py
build -p OvmfPkg/OvmfPkgX64.dsc \
    -a X64 -t GCC -b RELEASE -n %{_smp_build_ncpus} -s \
    -D SECURE_BOOT_ENABLE=TRUE \
    -D SMM_REQUIRE=TRUE \
    -D TPM1_ENABLE=TRUE \
    -D TPM2_ENABLE=TRUE

%install
install -Dm0644 Build/OvmfX64/RELEASE_GCC/FV/OVMF_CODE.fd \
    %{buildroot}%{_datadir}/edk2/ovmf/OVMF_CODE.fd
install -Dm0644 Build/OvmfX64/RELEASE_GCC/FV/OVMF_VARS.fd \
    %{buildroot}%{_datadir}/edk2/ovmf/OVMF_VARS.fd

mkdir -p %{buildroot}%{_datadir}/OVMF
ln -s ../edk2/ovmf/OVMF_CODE.fd \
    %{buildroot}%{_datadir}/OVMF/OVMF_CODE.fd
ln -s ../edk2/ovmf/OVMF_VARS.fd \
    %{buildroot}%{_datadir}/OVMF/OVMF_VARS.fd

install -Dm0644 %{SOURCE20} \
    %{buildroot}%{_datadir}/qemu/firmware/40-edk2-shadow-intel-x64.json

%check
test -s %{buildroot}%{_datadir}/edk2/ovmf/OVMF_CODE.fd
test -s %{buildroot}%{_datadir}/edk2/ovmf/OVMF_VARS.fd
virt-fw-vars --input \
    %{buildroot}%{_datadir}/edk2/ovmf/OVMF_VARS.fd --print >/dev/null

%files
%license License.txt
%license CryptoPkg/Library/OpensslLib/openssl/LICENSE.txt
%doc OvmfPkg/README
%dir %{_datadir}/edk2
%dir %{_datadir}/edk2/ovmf
%{_datadir}/edk2/ovmf/OVMF_CODE.fd
%{_datadir}/edk2/ovmf/OVMF_VARS.fd
%dir %{_datadir}/OVMF
%{_datadir}/OVMF/OVMF_CODE.fd
%{_datadir}/OVMF/OVMF_VARS.fd
%dir %{_datadir}/qemu
%dir %{_datadir}/qemu/firmware
%{_datadir}/qemu/firmware/40-edk2-shadow-intel-x64.json

%changelog
* Thu Aug 06 2026 Kristián Kekeš <gamerix2006@gmail.com> - 1:20260508-1
- Build from the pinned Intel branch of synsenetwork/edk2-shadow
- Carry the AutoVirt EDK2 changes from commit dd88bea
- Replace Fedora edk2-ovmf while keeping standard firmware paths
