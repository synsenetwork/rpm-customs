%global libliftoff_minver 0.5.0
%global reshade_commit 696b14cd6006ae9ca174e6164450619ace043283
%global reshade_shortcommit %(c=%{reshade_commit}; echo ${c:0:7})
%global vkroots_commit 5106d8a0df95de66cc58dc1ea37e69c99afc9540
%global vkroots_shortcommit %(c=%{vkroots_commit}; echo ${c:0:7})

# Personal fork of gamescope tracked by commit (no upstream tag).
%global commit 6a9097fbaf64b08b15be9c3e06039166c8599a3b
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global commitdate 20260428

Name:           gamescope
Version:        3.16.23
Release:        0.3.%{commitdate}git%{shortcommit}%{?dist}
Epoch:          1
Summary:        Micro-compositor for video games on Wayland (synse fork)

License:        LicenseRef-Callaway-BSD
URL:            https://github.com/synsejse/gamescope-synse
# luajit is not available on ppc64le:
# https://bugzilla.redhat.com/show_bug.cgi?id=2339416
ExcludeArch:    ppc64le

Source0:        %{url}/archive/%{commit}/gamescope-synse-%{shortcommit}.tar.gz
# Create stb.pc to satisfy dependency('stb')
Source1:        stb.pc
Source2:        https://github.com/misyltoad/reshade/archive/%{reshade_commit}/reshade-%{reshade_shortcommit}.tar.gz
Source3:        https://github.com/misyltoad/vkroots/archive/%{vkroots_commit}/vkroots-%{vkroots_shortcommit}.tar.gz

# https://github.com/misyltoad/reshade/pull/1:
Patch:          0001-cstdint.patch
# Allow to use system wlroots
# We use/package rest from the forks, I've tried to verify that wlroots match relevant commits
# We'll hold on rebases of gamescope if tags diverge in the future
Patch:          Allow-to-use-system-wlroots.patch
Patch:          Use-system-stb-glm.patch

BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  git-core
BuildRequires:  glm-devel
BuildRequires:  google-benchmark-devel
BuildRequires:  libXcursor-devel
BuildRequires:  libXmu-devel
BuildRequires:  meson >= 0.54.0
BuildRequires:  ninja-build
BuildRequires:  pkgconfig(hwdata)
BuildRequires:  pkgconfig(libavif)
BuildRequires:  pkgconfig(libcap)
BuildRequires:  pkgconfig(libdecor-0)
BuildRequires:  pkgconfig(libdisplay-info)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libeis-1.0)
BuildRequires:  (pkgconfig(libliftoff) >= %{libliftoff_minver} with pkgconfig(libliftoff) < 0.6)
BuildRequires:  pkgconfig(libpipewire-0.3)
BuildRequires:  pkgconfig(libudev)
BuildRequires:  pkgconfig(luajit)
BuildRequires:  pkgconfig(openvr) >= 2.12
BuildRequires:  pkgconfig(sdl2)
BuildRequires:  pkgconfig(vulkan)
BuildRequires:  pkgconfig(wayland-protocols) >= 1.17
BuildRequires:  pkgconfig(wayland-scanner)
BuildRequires:  pkgconfig(wayland-server)
BuildRequires:  pkgconfig(wlroots-0.18)
BuildRequires:  pkgconfig(x11)
BuildRequires:  pkgconfig(xcomposite)
BuildRequires:  pkgconfig(xdamage)
BuildRequires:  pkgconfig(xext)
BuildRequires:  pkgconfig(xfixes)
BuildRequires:  pkgconfig(xkbcommon)
BuildRequires:  pkgconfig(xrender)
BuildRequires:  pkgconfig(xres)
BuildRequires:  pkgconfig(xtst)
BuildRequires:  pkgconfig(xxf86vm)
BuildRequires:  spirv-headers-devel
# Enforce the the minimum EVR to contain fixes for all of:
# CVE-2021-28021 CVE-2021-42715 CVE-2021-42716 CVE-2022-28041 CVE-2023-43898
# CVE-2023-45661 CVE-2023-45662 CVE-2023-45663 CVE-2023-45664 CVE-2023-45666
# CVE-2023-45667, upstream issues #1860, #1861
BuildRequires:  stb_image-devel >= 2.30^20251025gitf1c79c0-2
# Header-only library: -static is for tracking per guidelines
BuildRequires:  stb_image-static
BuildRequires:  stb_image_resize-devel
BuildRequires:  stb_image_resize-static
BuildRequires:  stb_image_write-devel
BuildRequires:  stb_image_write-static
BuildRequires:  /usr/bin/glslangValidator

Provides:       bundled(vkroots) = 0^20240429git5106d8a

# libliftoff hasn't bumped soname, but API/ABI has changed for 0.2.0 release
Requires:       libliftoff%{?_isa} >= %{libliftoff_minver}
Requires:       xorg-x11-server-Xwayland
Recommends:     mesa-dri-drivers
Recommends:     mesa-vulkan-drivers

%description
%{name} is the micro-compositor optimized for running video games on Wayland.
This package is built from a personal fork at %{url}.

%prep
%autosetup -p1 -N -n gamescope-synse-%{commit}
# Install stub pkgconfig file
mkdir -p pkgconfig
cp %{SOURCE1} pkgconfig/stb.pc

# Replace spirv-headers include with the system directory
sed -i 's^../thirdparty/SPIRV-Headers/include/spirv/^/usr/include/spirv/^' src/meson.build

# Push in reshade and vkroots from sources instead of submodule
tar -xzf %{SOURCE2} --strip-components=1 -C src/reshade
tar -xzf %{SOURCE3} --strip-components=1 -C subprojects/vkroots

%autopatch -p1

%build
export PKG_CONFIG_PATH=pkgconfig
%meson \
    -Davif_screenshots=enabled \
    -Dbenchmark=enabled \
    -Ddrm_backend=enabled \
    -Denable_gamescope=true \
    -Denable_gamescope_wsi_layer=true \
    -Denable_openvr_support=true \
    -Denable_tests=false \
    -Dforce_fallback_for=[] \
    -Dinput_emulation=enabled \
    -Dpipewire=enabled \
    -Drt_cap=enabled \
    -Dsdl2_backend=enabled
%meson_build

%install
%meson_install --skip-subprojects

%files
%license LICENSE
%doc README.md
%{_bindir}/gamescope
%{_bindir}/gamescopectl
%{_bindir}/gamescopereaper
%{_bindir}/gamescopestream
%{_bindir}/gamescope-type
%{_datadir}/gamescope
%{_libdir}/libVkLayer_FROG_gamescope_wsi_*.so
%{_datadir}/vulkan/implicit_layer.d/VkLayer_FROG_gamescope_wsi.*.json

%changelog
* Sat May 16 2026 Kristián Kekeš <gamerix2006@gmail.com> - 1:3.16.23-0.3.20260428git6a9097f
- Set Epoch: 1 so this fork always supersedes stock Fedora gamescope,
  regardless of how dnf compares the snapshot Release against Fedora's
  conventional Release counter

* Sat May 16 2026 Kristián Kekeš <gamerix2006@gmail.com> - 3.16.23-0.2.20260428git6a9097f
- Disable the upstream test build (-Denable_tests=false) so the spec
  does not require catch2-with-main, which isn't in the buildroot
* Fri May 15 2026 Kristián Kekeš <gamerix2006@gmail.com> - 3.16.23-0.1.20260428git6a9097f
- Initial RPM package built from the synsejse/gamescope-synse fork
