Name:           scx-scheds
Version:        1.1.1
Release:        1%{?dist}
Summary:        sched_ext schedulers and support utilities

License:        GPL-2.0-only
URL:            https://github.com/sched-ext/scx
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/scx-%{version}.tar.gz

ExclusiveArch:  x86_64 aarch64

BuildRequires:  gcc
BuildRequires:  git
BuildRequires:  python3
BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  clang >= 17
BuildRequires:  llvm >= 17
BuildRequires:  lld >= 17
BuildRequires:  elfutils-libelf-devel
BuildRequires:  zlib-devel
BuildRequires:  jq
BuildRequires:  jq-devel
BuildRequires:  systemd
BuildRequires:  bpftool
BuildRequires:  protobuf-compiler
BuildRequires:  libseccomp-devel

Requires:       elfutils-libelf
Requires:       libseccomp
Requires:       protobuf
Requires:       zlib
Requires:       jq
Requires:       scx-tools

Conflicts:      scx-scheds-git
Conflicts:      scx_layered
Conflicts:      scx_rustland
Conflicts:      scx_rusty
Conflicts:      rust-scx_utils-devel

Provides:       scx_layered
Provides:       scx_rustland
Provides:       scx_rusty
Provides:       rust-scx_utils-devel

%description
sched_ext is a Linux kernel feature which enables implementing kernel
thread schedulers in BPF and dynamically loading them. This package
contains the upstream sched_ext scheduler implementations.

%prep
%autosetup -n scx-%{version}

%build
export CARGO_HOME=%{_builddir}/.cargo
cargo fetch --locked
cargo build \
    --release \
    --frozen \
    --all-features \
    --workspace \
    --exclude scx_rlfifo \
    --exclude scx_mitosis \
    --exclude scx_wd40 \
    --exclude xtask \
    --exclude scxcash \
    --exclude vmlinux_docify \
    --exclude scx_arena_selftests

%install
find target/release \
    -maxdepth 1 -type f -executable ! -name '*.so' \
    -exec install -Dm755 -t %{buildroot}%{_bindir} {} +

%files
%{_bindir}/*

%changelog
* Fri May 15 2026 Automated Update <github-actions@github.com> - 1.1.1-1
- Update to version 1.1.1
* Tue May 05 2026 Kristián Kekeš <gamerix2006@gmail.com> - 1.1.0-1
- Initial package, adapted from CachyOS COPR (bieszczaders/kernel-cachyos-addons)
