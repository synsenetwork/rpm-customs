Name:           scrcpy
Version:        4.0
Release:        1%{?dist}
Summary:        Display and control Android devices over USB or TCP/IP

License:        Apache-2.0
URL:            https://github.com/Genymobile/scrcpy

# Client source.
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

# Prebuilt server JAR — built with the Android SDK by upstream and published
# per release. Using this avoids pulling Java + Android SDK + Gradle into the
# buildroot just to recompile a small jar whose hashes upstream documents.
Source1:        %{url}/releases/download/v%{version}/scrcpy-server-v%{version}

ExclusiveArch:  x86_64 aarch64

BuildRequires:  meson >= 0.60.0
BuildRequires:  ninja-build
BuildRequires:  gcc
BuildRequires:  pkgconfig(sdl3)
BuildRequires:  pkgconfig(libavformat) >= 60
BuildRequires:  pkgconfig(libavcodec) >= 60
BuildRequires:  pkgconfig(libavutil) >= 58
BuildRequires:  pkgconfig(libavdevice) >= 60
BuildRequires:  pkgconfig(libusb-1.0)

Requires:       android-tools

%description
scrcpy displays and controls Android devices connected over USB or via
TCP/IP. It does not require root access, works on Linux/Windows/macOS,
and provides low-latency mirroring (typically 35-70 ms), high resolution
(up to 1920x1080+) and 30-120 fps. This package ships the prebuilt
upstream server JAR rather than rebuilding it from sources, which would
require Java and the Android SDK in the buildroot.

%prep
%autosetup -p1

%build
%meson \
    -Dcompile_server=false \
    -Dprebuilt_server=%{SOURCE1} \
    -Db_lto=true
%meson_build

%install
%meson_install

%files
%license LICENSE
%doc README.md FAQ.md doc/
%{_bindir}/scrcpy
%{_datadir}/scrcpy/
%{_datadir}/bash-completion/completions/scrcpy
%{_datadir}/zsh/site-functions/_scrcpy
%{_datadir}/icons/hicolor/256x256/apps/scrcpy.png
%{_datadir}/applications/scrcpy.desktop
%{_datadir}/applications/scrcpy-console.desktop
%{_mandir}/man1/scrcpy.1*

%changelog
* Mon Jun 01 2026 Kristián Kekeš <gamerix2006@gmail.com> - 4.0-1
- Initial RPM package, built from the upstream meson tree with the
  prebuilt server JAR from the matching release (no Java/Android SDK
  in the buildroot)
