Name:           scx-tools
Version:        1.1.3
Release:        1%{?dist}
Summary:        sched_ext loader (D-Bus service for managing scx schedulers)

License:        GPL-2.0-only
URL:            https://github.com/sched-ext/scx-loader
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/scx-loader-%{version}.tar.gz

ExclusiveArch:  x86_64 aarch64

BuildRequires:  gcc
BuildRequires:  git
BuildRequires:  python3
BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  clang >= 17
BuildRequires:  llvm >= 17
BuildRequires:  lld >= 17
BuildRequires:  systemd
BuildRequires:  bpftool
BuildRequires:  libseccomp-devel

Requires:       scx-scheds

Obsoletes:      scxctl < %{version}-%{release}
Provides:       scxctl = %{version}-%{release}
Conflicts:      scx-tools-git

%description
scx_loader exposes a D-Bus interface for managing sched_ext schedulers.
The companion scxctl CLI uses that interface to start, stop, and switch
between scx scheduler implementations at runtime.

%prep
%autosetup -n scx-loader-%{version}

%build
export CARGO_HOME=%{_builddir}/.cargo
cargo fetch --locked
cargo build --release --frozen --all-features --workspace

%install
find target/release \
    -maxdepth 1 -type f -executable ! -name '*.so' ! -name 'xtask' \
    -exec install -Dm755 -t %{buildroot}%{_bindir} {} +

# Systemd units, D-Bus services, polkit rules, sample configs
./target/release/xtask install --destdir %{buildroot}

%files
%{_bindir}/*
%{_unitdir}/scx_loader.service
%{_datadir}/dbus-1/system-services/org.scx.Loader.service
%{_datadir}/dbus-1/system.d/org.scx.Loader.conf
%{_datadir}/dbus-1/interfaces/org.scx.Loader.xml
%{_datadir}/polkit-1/actions/org.scx.Loader.policy
%{_datadir}/scx_loader/config.toml

%changelog
* Sat Sep 05 2026 Automated Update <github-actions@github.com> - 1.1.3-1
- Update to version 1.1.3
* Sun Jul 05 2026 Automated Update <github-actions@github.com> - 1.1.2-1
- Update to version 1.1.2
* Tue May 19 2026 Automated Update <github-actions@github.com> - 1.1.1-1
- Update to version 1.1.1
* Tue May 05 2026 Kristián Kekeš <gamerix2006@gmail.com> - 1.1.0-1
- Initial package, adapted from CachyOS COPR (bieszczaders/kernel-cachyos-addons)
