# Release profile strips symbols (see upstream Cargo.toml), so there is no
# debuginfo to extract — skip the debug package entirely.
%global debug_package %{nil}

Name:           scx-synse-manager
Version:        0.2.3
Release:        1%{?dist}
Summary:        GTK4 / libadwaita GUI for managing sched_ext schedulers via scx_loader

License:        GPL-2.0-or-later
URL:            https://github.com/synsenetwork/scx-synse-manager
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/scx-synse-manager-%{version}.tar.gz

ExclusiveArch:  x86_64 aarch64

BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  gcc
BuildRequires:  meson
BuildRequires:  ninja-build
BuildRequires:  pkgconf-pkg-config
BuildRequires:  gtk4-devel
BuildRequires:  libadwaita-devel
BuildRequires:  glib2-devel
BuildRequires:  libxml2

Requires:       scx-tools
Requires:       scx-scheds
Requires:       polkit

%description
scx-synse-manager is a friendly GTK4 / libadwaita application for managing
sched_ext schedulers through the scx_loader D-Bus service. It provides
plain-language scheduler descriptions, a hardware-based "recommended" hint,
and a single long-lived privileged helper so the user authenticates only
once per session rather than once per change.

%prep
%autosetup -n %{name}-%{version}

%build
# meson drives `cargo build --release` via a custom target. Pre-populate the
# crate cache from the committed Cargo.lock and force cargo offline so the
# meson-invoked build does not reach the network.
export CARGO_HOME=%{_builddir}/.cargo
cargo fetch --locked
export CARGO_NET_OFFLINE=true
%meson
%meson_build

%install
%meson_install

%files
%license LICENSE
%doc README.md
%{_bindir}/scx-synse-manager
%{_libexecdir}/scx-synse-helper
%{_datadir}/applications/com.synsenetwork.scx-synse-manager.desktop
%{_datadir}/metainfo/com.synsenetwork.scx-synse-manager.metainfo.xml
%{_datadir}/icons/hicolor/scalable/apps/com.synsenetwork.scx-synse-manager.svg
%{_datadir}/polkit-1/actions/com.synsenetwork.scx-synse-manager.policy

%changelog
* Sun May 31 2026 Kristián Kekeš <gamerix2006@gmail.com> - 0.2.3-1
- Update to 0.2.3 (silence meson configure_file warnings)
* Sun May 31 2026 Kristián Kekeš <gamerix2006@gmail.com> - 0.2.2-1
- Update to 0.2.2 (header status pill replaces the banner)
* Sun May 31 2026 Kristián Kekeš <gamerix2006@gmail.com> - 0.2.1-1
- Update to 0.2.1 (rkyv helper protocol)
* Sun May 31 2026 Kristián Kekeš <gamerix2006@gmail.com> - 0.2.0-1
- Initial package (app id com.synsenetwork.scx-synse-manager)
