%define package_name mesa
%bcond_without patented_video_codecs
%global _default_patch_fuzz 2
#global __meson_auto_features disabled

%global build_repo https://gitlab.freedesktop.org/mesa/mesa
%define version_string 26.2.0
%global version_major %(ver=%{version_string}; echo ${ver%.*.*})

%define commit 80e6b468f435aea09c085b14efff9e70c32ec4dd
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global commit_date 20260501.12
%global gitrel .%{commit_date}.%{shortcommit}

%global hw_video_codecs_free vc1dec,av1dec,av1enc,vp9dec
%global hw_video_codecs_patented ,h264dec,h264enc,h265dec,h265enc

# Intel ray-tracing fails to build on 32-bit, see
# https://gitlab.freedesktop.org/mesa/mesa/-/issues/10629
%ifarch x86_64
%global with_intel_vk_rt 1
%endif

%bcond_without valgrind

%global vulkan_layers device-select,anti-lag,screenshot,vram-report-limit,overlay
%global vulkan_drivers swrast,amd,intel,intel_hasvk,nouveau,virtio

Name:           %{package_name}
Summary:        Mesa 3D Graphics Library, git version
Version:        %{version_string}
Release:        0.46%{?gitrel}%{?dist}

License:        MIT
URL:            http://www.mesa3d.org
ExclusiveArch:  %{ix86} x86_64

Source0:        %{build_repo}/-/archive/%{commit}.tar.gz#/mesa-%{commit}.tar.gz

BuildRequires:  meson >= 1.3.0
BuildRequires:  cbindgen
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  gettext
BuildRequires:  kernel-headers
BuildRequires:  pkgconfig(libdrm) >= 2.4.133
BuildRequires:  pkgconfig(libunwind)
BuildRequires:  pkgconfig(expat)
BuildRequires:  pkgconfig(libpng)
BuildRequires:  pkgconfig(zlib) >= 1.2.3
BuildRequires:  pkgconfig(libzstd)
BuildRequires:  pkgconfig(libdisplay-info)
BuildRequires:  pkgconfig(wayland-scanner)
BuildRequires:  pkgconfig(wayland-protocols) >= 1.8
BuildRequires:  pkgconfig(wayland-client) >= 1.11
BuildRequires:  pkgconfig(wayland-server) >= 1.11
BuildRequires:  pkgconfig(wayland-egl-backend) >= 3
BuildRequires:  pkgconfig(x11)
BuildRequires:  pkgconfig(xext)
BuildRequires:  pkgconfig(xdamage) >= 1.1
BuildRequires:  pkgconfig(xfixes)
BuildRequires:  pkgconfig(xcb-glx) >= 1.8.1
BuildRequires:  pkgconfig(xxf86vm)
BuildRequires:  pkgconfig(xcb)
BuildRequires:  pkgconfig(x11-xcb)
BuildRequires:  pkgconfig(xcb-dri2) >= 1.8
BuildRequires:  pkgconfig(xcb-dri3)
BuildRequires:  pkgconfig(xcb-present)
BuildRequires:  pkgconfig(xcb-sync)
BuildRequires:  pkgconfig(xshmfence) >= 1.1
BuildRequires:  pkgconfig(dri2proto) >= 2.8
BuildRequires:  pkgconfig(glproto) >= 1.4.14
BuildRequires:  pkgconfig(xcb-xfixes)
BuildRequires:  pkgconfig(xcb-randr)
BuildRequires:  pkgconfig(xrandr) >= 1.3
BuildRequires:  python3-pycparser
BuildRequires:  bison
BuildRequires:  flex
BuildRequires:  lm_sensors-devel
BuildRequires:  pkgconfig(libva) >= 0.38.0
BuildRequires:  pkgconfig(libelf)
BuildRequires:  pkgconfig(libglvnd) >= 1.3.2
BuildRequires:  llvm-devel >= 7.0.0
BuildRequires:  clang-devel
BuildRequires:  bindgen
BuildRequires:  rustfmt
BuildRequires:  rust-packaging
BuildRequires:  pkgconfig(libclc)
BuildRequires:  pkgconfig(SPIRV-Tools)
BuildRequires:  pkgconfig(LLVMSPIRVLib)
BuildRequires:  (crate(paste/default) >= 1.0.0 with crate(paste/default) < 2.0.0~)
BuildRequires:  (crate(proc-macro2) >= 1.0.56 with crate(proc-macro2) < 2)
BuildRequires:  (crate(quote) >= 1.0.25 with crate(quote) < 2)
BuildRequires:  (crate(syn/clone-impls) >= 2.0.15 with crate(syn/clone-impls) < 3)
BuildRequires:  (crate(unicode-ident) >= 1.0.6 with crate(unicode-ident) < 2)
BuildRequires:  (crate(rustc-hash) >= 2.0.0 with crate(rustc-hash) < 3)
%if %{with valgrind}
BuildRequires:  pkgconfig(valgrind)
%endif
BuildRequires:  python3-devel
BuildRequires:  python3-yaml
BuildRequires:  python3-mako
BuildRequires:  vulkan-headers
BuildRequires:  glslang
BuildRequires:  pkgconfig(vulkan)


%description
%{summary}.

%package filesystem
Summary:        Mesa driver filesystem
Provides:       mesa-dri-filesystem = %{?epoch:%{epoch}:}%{version}-%{release}
Obsoletes:      mesa-omx-drivers < %{?epoch:%{epoch}:}%{version}-%{release}
Obsoletes:      mesa-libglapi < %{?epoch:%{epoch}:}%{version}-%{release}
Obsoletes:      mesa-libxatracker < %{?epoch:%{epoch}:}%{version}-%{release}
Obsoletes:      mesa-libxatracker-devel < %{?epoch:%{epoch}:}%{version}-%{release}


%description filesystem
%{summary}.

%package libGL
Summary:        Mesa libGL runtime libraries
Requires:       libglvnd-glx%{?_isa} >= 1:1.3.2
Recommends:     %{name}-dri-drivers%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}

%description libGL
%{summary}.

%package libGL-devel
Summary:        Mesa libGL development package
Requires:       %{name}-libGL%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Requires:       libglvnd-devel%{?_isa} >= 1:1.3.2
Provides:       libGL-devel
Provides:       libGL-devel%{?_isa}

%description libGL-devel
%{summary}.

%package libEGL
Summary:        Mesa libEGL runtime libraries
Requires:       libglvnd-egl%{?_isa} >= 1:1.3.2
Requires:       %{name}-libgbm%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Recommends:     %{name}-dri-drivers%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Obsoletes:      egl-icd < %{?epoch:%{epoch}:}%{version}-%{release}
Obsoletes:      libOSMesa < %{?epoch:%{epoch}:}%{version}-%{release}

%description libEGL
%{summary}.

%package libEGL-devel
Summary:        Mesa libEGL development package
Requires:       %{name}-libEGL%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Requires:       libglvnd-devel%{?_isa} >= 1:1.3.2
Requires:       %{name}-khr-devel%{?_isa}
Provides:       libEGL-devel
Provides:       libEGL-devel%{?_isa}
Obsoletes:      libOSMesa-devel < %{?epoch:%{epoch}:}%{version}-%{release}


%description libEGL-devel
%{summary}.

%package dri-drivers
Summary:        Mesa-based DRI drivers
Requires:       %{name}-filesystem%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Recommends:     %{name}-va-drivers%{?_isa}

%description dri-drivers
%{summary}.

%package        va-drivers
Summary:        Mesa-based VA-API video acceleration drivers
Requires:       %{name}-filesystem%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Obsoletes:      %{name}-vaapi-drivers < %{?epoch:%{epoch}:}%{version}-%{release}
Obsoletes:      %{name}-vdpau-drivers < %{?epoch:%{epoch}:}%{version}-%{release}
Provides:       %{name}-vdpau-drivers = %{?epoch:%{epoch}:}%{version}-%{release}

%description va-drivers
%{summary}.

%package libgbm
Summary:        Mesa gbm runtime library
Provides:       libgbm
Provides:       libgbm%{?_isa}
Recommends:     %{name}-dri-drivers%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}

%description libgbm
%{summary}.

%package libgbm-devel
Summary:        Mesa libgbm development package
Requires:       %{name}-libgbm%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Provides:       libgbm-devel
Provides:       libgbm-devel%{?_isa}

%description libgbm-devel
%{summary}.

%package libOpenCL
Summary:        Mesa OpenCL runtime library
Requires:       ocl-icd%{?_isa}
Requires:       libclc%{?_isa}
Requires:       %{name}-libgbm%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Requires:       opencl-filesystem

%description libOpenCL
%{summary}.

%package libOpenCL-devel
Summary:        Mesa OpenCL development package
Requires:       %{name}-libOpenCL%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}

%description libOpenCL-devel
%{summary}.


%package vulkan-drivers
Summary:        Mesa Vulkan drivers
Requires:       vulkan%{_isa}
Obsoletes:      mesa-vulkan-devel < %{?epoch:%{epoch}:}%{version}-%{release}

%description vulkan-drivers
The drivers with support for the Vulkan API.


%prep
%setup -q -c
%autosetup -n mesa-%{commit} -p1

%build
# ensure standard Rust compiler flags are set
export RUSTFLAGS="%build_rustflags"

export MESON_PACKAGE_CACHE_DIR="%{cargo_registry}/"
# So... Meson can't actually find them without tweaks

%define inst_crate_nameversion() %( \
  found_dir=$(find %{cargo_registry} -maxdepth 1 -type d -name '%{1}-*' 2>/dev/null | head -n1); \
  if [ -n "$found_dir" ]; then basename "$found_dir"; fi \
)

%define rewrite_wrap_file() \
  wrapfile=$(find subprojects -maxdepth 1 -name '%{1}*.wrap' | head -n1) && \
  if [ -z "$wrapfile" ]; then \
    echo "ERROR: .wrap file not found for crate %{1}" >&2; exit 1; \
  fi && \
  crate_dir="%{expand:%%inst_crate_nameversion %{1}}" && \
  if [ -z "$crate_dir" ]; then \
    echo "ERROR: Crate directory not found in %{cargo_registry} for %{1}" >&2; exit 1; \
  fi && \
  echo "→ Rewriting $wrapfile to use directory = $crate_dir" && \
  sed -i -e '/^source_/d' -e "s|^directory = .*|directory = ${crate_dir}|" "$wrapfile"


%rewrite_wrap_file paste
%rewrite_wrap_file proc-macro2
%rewrite_wrap_file quote
%rewrite_wrap_file syn
%rewrite_wrap_file unicode-ident

# We've gotten a report that enabling LTO for mesa breaks some games. See
# https://bugzilla.redhat.com/show_bug.cgi?id=1862771 for details.
# Disable LTO for now
%define _lto_cflags %{nil}

%meson \
  -Dplatforms=x11,wayland \
  -Dgallium-drivers=llvmpipe,softpipe,virgl,nouveau,r300,crocus,i915,iris,svga,radeonsi,r600,zink \
  -Dgallium-extra-hud=true \
  -Dgallium-mediafoundation=disabled \
  -Dgallium-va=enabled \
  -Dgallium-rusticl=true \
  -Dvulkan-drivers=%{?vulkan_drivers} \
  -Dvulkan-layers=%{?vulkan_layers} \
  -Dgles1=disabled \
  -Dgles2=enabled \
  -Dopengl=true \
  -Dgbm=enabled \
  -Dglx=dri \
  -Degl=enabled \
  -Dglvnd=enabled \
  -Dintel-rt=%{?with_intel_vk_rt:enabled}%{!?with_intel_vk_rt:disabled} \
  -Dmicrosoft-clc=disabled \
  -Dllvm=enabled \
  -Dshared-llvm=enabled \
  -Db_ndebug=true \
  -Dvalgrind=%{?with_valgrind:enabled}%{!?with_valgrind:disabled} \
  -Dbuild-tests=false \
  -Dandroid-libbacktrace=disabled \
%ifarch %{ix86}
  -Dglx-read-only-text=true \
%endif
  -Dvideo-codecs=%{?hw_video_codecs_free}%{?with_patented_video_codecs:%{hw_video_codecs_patented}} \
  %{nil}
%meson_build

%install
%meson_install

# glvnd opens the versioned name, don't bother including the unversioned
rm -vf %{buildroot}%{_libdir}/libGLX_mesa.so
rm -vf %{buildroot}%{_libdir}/libEGL_mesa.so
# XXX can we just not build this
rm -vf %{buildroot}%{_libdir}/libGLES*

# glvnd needs a default provider for indirect rendering where it cannot
# determine the vendor
ln -s %{_libdir}/libGLX_mesa.so.0 %{buildroot}%{_libdir}/libGLX_system.so.0

# this keeps breaking, check it early.  note that the exit from eu-ftr is odd.
pushd %{buildroot}%{_libdir}
for i in libGL*.so ; do
    sleep 1
    eu-findtextrel $i && exit 1
done
popd

%files filesystem
%dir %{_libdir}/dri

%files libGL
%{_libdir}/libGLX_mesa.so.0*
%{_libdir}/libGLX_system.so.0*
%files libGL-devel
%{_includedir}/GL/*
%{_libdir}/pkgconfig/dri.pc


%files libEGL
%{_datadir}/glvnd/egl_vendor.d/50_mesa*.json
%{_libdir}/libEGL_mesa.so.0*
%files libEGL-devel
%dir %{_includedir}/EGL
%{_includedir}/EGL/*.h

%files libgbm
%{_libdir}/gbm/dri_gbm.so
%{_libdir}/libgbm.so.1
%{_libdir}/libgbm.so.1.*
%{_includedir}/gbm_backend_abi.h

%files libgbm-devel
%{_libdir}/libgbm.so
%{_includedir}/gbm.h
%{_libdir}/pkgconfig/gbm.pc


%files libOpenCL
%{_libdir}/libRusticlOpenCL.so.*
%{_sysconfdir}/OpenCL/vendors/rusticl.icd

%files libOpenCL-devel
%{_libdir}/libRusticlOpenCL.so

%files dri-drivers
%dir %{_datadir}/drirc.d
%{_datadir}/drirc.d/*.conf
%{_libdir}/dri/kms_swrast_dri.so
%{_libdir}/dri/swrast_dri.so
%{_libdir}/dri/virtio_gpu_dri.so

%{_libdir}/dri/r300_dri.so
%{_libdir}/dri/r600_dri.so
%{_libdir}/dri/radeonsi_dri.so

%{_libdir}/dri/crocus_dri.so
%{_libdir}/dri/i915_dri.so
%{_libdir}/dri/iris_dri.so

# kmsro drivers
%{_libdir}/dri/hdlcd_dri.so
%{_libdir}/dri/apple_dri.so
%{_libdir}/dri/ingenic-drm_dri.so
%{_libdir}/dri/imx-drm_dri.so
%{_libdir}/dri/imx-lcdif_dri.so
%{_libdir}/dri/kirin_dri.so
%{_libdir}/dri/komeda_dri.so
%{_libdir}/dri/mali-dp_dri.so
%{_libdir}/dri/mcde_dri.so
%{_libdir}/dri/mxsfb-drm_dri.so
%{_libdir}/dri/panel-mipi-dbi_dri.so
%{_libdir}/dri/rcar-du_dri.so
%{_libdir}/dri/sti_dri.so
%{_libdir}/dri/stm_dri.so
# old kmsro drivers
%{_libdir}/dri/armada-drm_dri.so
%{_libdir}/dri/exynos_dri.so
%{_libdir}/dri/gm12u320_dri.so
%{_libdir}/dri/hx8357d_dri.so
%{_libdir}/dri/ili9163_dri.so
%{_libdir}/dri/ili9225_dri.so
%{_libdir}/dri/ili9341_dri.so
%{_libdir}/dri/ili9486_dri.so
%{_libdir}/dri/imx-dcss_dri.so
%{_libdir}/dri/mediatek_dri.so
%{_libdir}/dri/meson_dri.so
%{_libdir}/dri/mi0283qt_dri.so
%{_libdir}/dri/pl111_dri.so
%{_libdir}/dri/repaper_dri.so
%{_libdir}/dri/rockchip_dri.so
%{_libdir}/dri/rzg2l-du_dri.so
%{_libdir}/dri/ssd130x_dri.so
%{_libdir}/dri/st7586_dri.so
%{_libdir}/dri/st7735r_dri.so
%{_libdir}/dri/sun4i-drm_dri.so
%{_libdir}/dri/udl_dri.so
%{_libdir}/dri/vkms_dri.so
%{_libdir}/dri/zynqmp-dpsub_dri.so

%{_libdir}/dri/nouveau_dri.so
%{_libdir}/dri/vmwgfx_dri.so

%{_libdir}/dri/libdril_dri.so
%{_libdir}/libgallium-*.so

%{_libdir}/dri/zink_dri.so

%files va-drivers
%{_libdir}/dri/nouveau_drv_video.so
%{_libdir}/dri/r600_drv_video.so
%{_libdir}/dri/radeonsi_drv_video.so
%{_libdir}/dri/virtio_gpu_drv_video.so

%files vulkan-drivers
%{_libdir}/libvulkan_lvp.so
%{_datadir}/vulkan/icd.d/lvp_icd.*.json
%{_bindir}/mesa-*-control.py
%{_libdir}/libVkLayer_MESA_*.so
%{_datadir}/vulkan/explicit_layer.d/VkLayer_MESA_*.json
%{_datadir}/vulkan/implicit_layer.d/VkLayer_MESA_*.json

%{_libdir}/libvulkan_radeon.so
%{_datadir}/vulkan/icd.d/radeon_icd.*.json
%{_libdir}/libvulkan_nouveau.so
%{_datadir}/vulkan/icd.d/nouveau_icd.*.json
%{_libdir}/libvulkan_intel.so
%{_libdir}/libvulkan_intel_hasvk.so
%{_datadir}/vulkan/icd.d/intel_icd.*.json
%{_datadir}/vulkan/icd.d/intel_hasvk_icd.*.json
%{_libdir}/libvulkan_virtio.so
%{_datadir}/vulkan/icd.d/virtio_icd.*.json

%changelog
* Thu Apr 30 2026 Kristián Kekeš <gamerix2006@gmail.com>
  Tune build options:
  - Disable -Dgles1 (OpenGL ES 1.x is effectively unused)
  - Set -Dgbm=enabled explicitly (we ship libgbm subpackages)
  - Add 'virtio' Vulkan driver for VM guests (venus)

* Thu Apr 30 2026 Kristián Kekeš <gamerix2006@gmail.com>
  Bump pkgconfig(libdrm) BuildRequires to >= 2.4.133 to match
  upstream amdgpu driver requirement.

* Thu Apr 30 2026 Kristián Kekeš <gamerix2006@gmail.com>
  Restore i686 (32-bit) support for multilib builds:
  - Allow ExclusiveArch %{ix86} x86_64
  - Gate intel-rt back behind x86_64 (still broken on 32-bit)
  - Re-add -Dglx-read-only-text=true on i686

* Thu Apr 30 2026 Kristián Kekeš <gamerix2006@gmail.com>
  Treat the spec as Fedora x86_64 only:
  - Add ExclusiveArch x86_64
  - Drop unreachable RHEL/s390x/i686/aarch64 conditionals and globals
  - Drop dead commented patches and unused build_branch global

* Thu Apr 30 2026 Kristián Kekeš <gamerix2006@gmail.com>
  Enable b_ndebug=true to drop assertions from hot paths,
  matching CachyOS PKGBUILD defaults

* Fri Apr 10 2026 Kristián Kekeš <gamerix2006@gmail.com>
  Enable gallium-extra-hud and additional Mesa Vulkan utility layers
  based on current CachyOS PKGBUILD defaults

* Wed Sep 17 2025 Mihai Vultur <xanto@egaming.ro>
  Disable compiling of ARM specific drivers in x86_64 builds

* Thu Sep 11 2025 Mihai Vultur <xanto@egaming.ro>
  Remove 'gallium-vdpau' option after:
  https://gitlab.freedesktop.org/mesa/mesa/-/merge_requests/36632

* Fri Aug 08 2025 Mihai Vultur <xanto@egaming.ro>
  Remove 'intel-clc' option after:
  https://gitlab.freedesktop.org/mesa/mesa/-/merge_requests/36625

* Thu Aug 07 2025 Mihai Vultur <xanto@egaming.ro>
  Modify 'rewrite_wrap_file' define to also modify the directory = directive in meson wrap.
  Because it seems that meson can't reliably use those by default.

* Sun May 25 2025 Mihai Vultur <xanto@egaming.ro>
  Don't use 'gallium-xa' anymore.
  Explicitely set -Dgallium-mediafoundation=disabled
  https://gitlab.freedesktop.org/mesa/mesa/-/merge_requests/35113

* Wed May 21 2025 Mihai Vultur <xanto@egaming.ro>
  Add 'rustc-hash' dependency required for building nvk.
  https://gitlab.freedesktop.org/mesa/mesa/-/merge_requests/34865

* Thu Apr 17 2025 Mihai Vultur <xanto@egaming.ro>
  Remove 'gallium-opencl' now that clover was removed.
  https://gitlab.freedesktop.org/mesa/mesa/-/merge_requests/19385

* Fri Apr 11 2025 Mihai Vultur <xanto@egaming.ro>
  support building with system libgbm
  https://gitlab.freedesktop.org/mesa/mesa/-/merge_requests/33890

* Sat Mar 29 2025 Mihai Vultur <xanto@egaming.ro>
  swrast has been removed in favor of softpipe+llvmpipe:
  https://gitlab.freedesktop.org/mesa/mesa/-/merge_requests/34217

* Thu Mar 06 2025 Mihai Vultur <xanto@egaming.ro>
  Remove references to osmesa as it has been removed after:
  https://gitlab.freedesktop.org/mesa/mesa/-/merge_requests/33836

* Fri Jan 24 2025 Mihai Vultur <xanto@egaming.ro>
  Remove references to libglapi as it is no longer generated by mesa after:
  https://gitlab.freedesktop.org/mesa/mesa/-/merge_requests/32789

* Fri Sep 20 2024 Mihai Vultur <xanto@egaming.ro>
  New dri_gbm.so after: https://gitlab.freedesktop.org/mesa/mesa/-/merge_requests/31074

* Fri Sep 13 2024 Mihai Vultur <xanto@egaming.ro>
  libgallium_drv_video and libvdpau_gallium are no longer being generated.

* Tue Sep 10 2024 Mihai Vultur <xanto@egaming.ro>
  Remove references to OMX as it was removed from mesa.

* Fri Aug 02 2024 Mihai Vultur <xanto@egaming.ro>
  Compile mesa without patented codecs, as per COPR System Team request.

* Fri Aug 02 2024 Mihai Vultur <xanto@egaming.ro>
  Remove kmsro option after: https://gitlab.freedesktop.org/mesa/mesa/-/merge_requests/30463

* Wed Jul 24 2024 Mihai Vultur <xanto@egaming.ro>
  Enable 'intel-rt' for x64 bit targets.

* Mon Jul 22 2024 Mihai Vultur <xanto@egaming.ro>
  'rustfmt' has become a build dependency.

* Fri Jul 19 2024 Mihai Vultur <xanto@egaming.ro>
  Adaptations for commit d5ec3a89

* Fri Jul 19 2024 Mihai Vultur <xanto@egaming.ro>
  Commit d709b421 removed zink_dri.so

* Tue Apr 09 2024 Mihai Vultur <xanto@egaming.ro>
  NVK depends on cbindgen and rust-paste now. Adjust dependencies.

* Thu Feb 29 2024 Mihai Vultur <xanto@egaming.ro>
  NVK got vulkan conformance, 'nouveau-experimental', becomes 'nouveou' now.

* Mon Feb 19 2024 Mihai Vultur <xanto@egaming.ro>
  Disable intel-rt until the issue with 32bit compilation is fixed.
  Bugzilla: https://gitlab.freedesktop.org/mesa/mesa/-/issues/10629

* Tue Feb 13 2024 Mihai Vultur <xanto@egaming.ro>
  https://gitlab.freedesktop.org/mesa/mesa/-/merge_requests/27593
  If we do a native build, regardless of the host architecture and we
  build Anv or Iris, we need intel-clc. So force building that tool.

* Sun Feb 04 2024 Mihai Vultur <xanto@egaming.ro>
  Enable imagination-experimental (PowerVR) Vulkan Driver.
  Enable nouveau-experimental for Nvidia Drivers. For Kernel 6.7+

* Sat Jan 27 2024 Mihai Vultur <xanto@egaming.ro>
  Add ssd130x to the list of kmsro drivers
  https://gitlab.freedesktop.org/mesa/mesa/-/merge_requests/27135

* Sun Jan 21 2024 Mihai Vultur <xanto@egaming.ro>
  Enable av1 dec/enc and vp9 dec codecs.

* Mon Nov 27 2023 José Expósitojexposit@redhat.com>
  Set glx-read-only-text on i386
  An update on the linker will now refuse to create binaries with a loadable
  memory segment that has read, write and execute permissions set.
  mesa creates one unless "glx-read-only-text" is enabled.

* Sat Nov 11 2023 Mihai Vultur <mihaivultur7@gmail.com>
  Add new drivers to the list: https://gitlab.freedesktop.org/mesa/mesa/-/merge_requests/26129

* Wed Oct 25 2023 Mihai Vultur <mihaivultur7@gmail.com>
  Various modifications and adjustments to more closely follow the official spec.
  + hdlcd_dri.so

* Tue Feb 28 2023 Mihai Vultur <mihaivultur7@gmail.com>
  According to https://gitlab.freedesktop.org/mesa/mesa/-/commit/a06ab9849db7fdf8f5194412f0c5a15abd8ece9b
  Vdpau support for r300 has been dropped.

* Tue Feb 28 2023 Fabio Valentini <decathorpe@gmail.com>
  Ensure standard Rust compiler flags are set.

* Thu Jan 12 2023 Mihai Vultur <mihaivultur7@gmail.com>
  Introduce 'with_opencl_rust' and temporary disable rust opencl.

* Thu Jan 12 2023 Peter Robinson <pbrobinson@fedoraproject.org>
   Enable rusticl as an optional OpenCL engine

* Sat Dec 17 2022 Mihai Vultur <mihaivultur7@gmail.com>
  Use official freedesktop gitlab url for downloading source archive.
  .. for some reason it seems like mirroring to github is not working.

* Mon Dec 12 2022 Mihai Vultur <mihaivultur7@gmail.com>
  Use '-Dxmlconfig=enabled' otherwise drirc config files won't be generated..

* Wed Nov 16 2022 Mihai Vultur <mihaivultur7@gmail.com>
  Use '-Dcpp_std=gnu++17' to unbreak the build.

* Thu Oct 06 2022 Ibrahim Ansari <retrixe@users.noreply.github.com>
- The Intel ANV Vulkan driver no longer supports Gen7/8 integrated graphics,
  instead, the Vulkan support for these GPUs has been moved into a new "HASVK" driver.
- Enable 'intel_hasvk'.

* Thu Oct 06 2022 Mihai Vultur <xanto@egaming.ro>
- Carry over and adapt some patches from upstream:
 60b9e9d Rename mesa-vaapi-drivers to mesa-va-drivers
 07e1e0b mesa: split out vaapi drivers into separate package
 8a2edad Recommend mesa-dri-drivers from libGL, libEGL, and libgbm subpackages (rhbz#1900633)
 8d117d9 Remove old obsoletes

* Mon Aug 15 2022 Mihai Vultur <xanto@egaming.ro>
- Adjust specfile after eglextchromium.h removal
- MR https://gitlab.freedesktop.org/mesa/mesa/-/merge_requests/17815

* Sat Apr 30 2022 Mikhail Gavrilov <mikhail.v.gavrilov@gmail.com>
- Reenabling all hw implementations of video codecs which was disabled by
- MR https://gitlab.freedesktop.org/mesa/mesa/-/merge_requests/15258.

* Wed Mar 02 2022 Mihai Vultur <mihaivultur7@gmail.com>
- Also include 00-radv-defaults.conf in the list of bundled files.

* Thu Dec 16 2021 Mihai Vultur <mihaivultur7@gmail.com>
- Adjustments after dri-drivers deprecation in mesa 22

* Tue Jun 15 2021 Mihai Vultur <xanto@egaming.ro>
- Partially revert the modifications done in Apr 11:
- Regenerate vulkan-devel package but with no files
- This provides a lean upgrade path

* Wed May 05 2021 Mihai Vultur <xanto@egaming.ro>
- After https://gitlab.freedesktop.org/mesa/mesa/-/merge_requests/10554
- also consider i830_dri.so

* Sun Apr 11 2021 Mihai Vultur <xanto@egaming.ro>
- Don't generate a separate vulkan-devel package anymore
- Since upstream commit:
-    commit 5e6db1916860ec217eac60903e0a9d10189d1c53
-    Author: Chad Versace <chad@kiwitree.net>
-    Message:
-       anv: Remove vkCreateDmaBufINTEL (v4)

* Fri Mar 26 2021 Mihai Vultur <xanto@egaming.ro>
- Set vulkan-layers=device-select,overlay since upstream commit 54fe5b04

* Fri Dec 11 2020 Mihai Vultur <xanto@egaming.ro>
- Set osmesa=true since upstream commit ee802372180a2b4460cc7abb53438e45c6b6f1e4

* Wed Nov 25 2020 Mihai Vultur <xanto@egaming.ro>
- meson: __meson_auto_features default to disabled
- Issue: https://gitlab.freedesktop.org/mesa/mesa/-/issues/3873

* Mon Nov 23 2020 Mihai Vultur <xanto@egaming.ro>
- meson: drop deprecated EGL platform build options.
- Consequence of MR: https://gitlab.freedesktop.org/mesa/mesa/-/merge_requests/5844

* Mon Apr 20 2020 Mihai Vultur <xanto@egaming.ro>
- Enable vulkan-device-select-layer.

* Sun Feb 09 2020 Mihai Vultur <xanto@egaming.ro>
- Enable zink.

* Sat Feb 08 2020 Mikhail Gavrilov <mikhail.v.gavrilov@gmail.com>
- Prevent radeonsi crashing when compiled with GCC10 on Rawhide.

* Thu Jan 23 2020 Tom Stellard <tstellar@redhat.com>
- Link against libclang-cpp.so
- https://fedoraproject.org/wiki/Changes/Stop-Shipping-Individual-Component-Libraries-In-clang-lib-Package

* Sat Dec 14 2019 Mihai Vultur <xanto@egaming.ro>
- new mesa-overlay-control.py script added to the install list

* Sun Nov 03 2019 Peter Robinson <pbrobinson@gmail.com>
- adjust mesa-khr-devel requires now provided by libglvnd

* Sun Oct 06 2019 Mihai Vultur <xanto@egaming.ro>
- Architecture specific builds might run asynchronous.
- This might cause that same package build for x86_64 will be different when
-  built for i686. This is problematic when we want to install multilib packages.
- Convert the specfile to template and use it to generate the actual script.
- This will prevent the random failues and mismatch between arch versions.

* Sun Sep 08 2019 Mihai Vultur <xanto@egaming.ro>
- Merge the two implementations.

* Sun Jul 07 2019 Mihai Vultur <xanto@egaming.ro>
- Implement some version autodetection to reduce maintenance work.

* Thu Jul 04 2019 Mihai Vultur <xanto@egaming.ro>
- Modified to point to Valve's Radeon ACO compiler patches from https://github.com/daniel-schuermann/mesa.

* Mon Oct 10 2016 Rudolf Kastl <rudolf@redhat.com>
- Synced with Leighs spec.
