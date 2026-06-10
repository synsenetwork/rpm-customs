# rpm should not strip the bundled Electron binaries or generate a
# debug subpackage (this is a binary repackager — no source compiled).
%global debug_package %{nil}
%global __os_install_post %{nil}
%global __strip /bin/true

%global claude_version 1.11847.5
%global electron_ver   40.4.1

Name:           claude-desktop
Version:        %{claude_version}
Release:        3%{?dist}
Summary:        Claude Desktop for Linux
License:        LicenseRef-Anthropic
URL:            https://claude.com/download/

# Direct .nupkg from Anthropic's Squirrel feed — discoverable via the
# RELEASES manifest at the same path. The .exe wrapper used by the
# upstream christian-korneck/claude-desktop-rpm spec only adds an outer
# 7z layer to strip; the .nupkg inside is the actual payload.
Source0:        https://downloads.claude.ai/releases/win32/arm64/AnthropicClaude-%{claude_version}-full.nupkg

ExclusiveArch:  aarch64 x86_64
AutoReqProv:    no

BuildRequires:  p7zip-plugins
BuildRequires:  icoutils
BuildRequires:  nodejs >= 22
BuildRequires:  npm
BuildRequires:  desktop-file-utils

Requires:       gtk3
Requires:       nss
Requires:       alsa-lib
Requires:       cups-libs
Requires:       dbus-libs
Requires:       mesa-libgbm

%description
Claude Desktop for Linux. Repackaged from Anthropic's Windows installer
with the upstream christian-korneck/claude-desktop-rpm transforms: the
asar payload is patched to enable native window decorations on Linux,
add the linux-arm64/linux-x64 platform branch for Claude Code, relax
the file:// origin check, and quit on window close when the tray menu
is disabled. Bundles a current Electron runtime via npm.

%prep
# --- npm install asar + electron locally ---------------------------------
mkdir -p %{_builddir}/_tools
cd %{_builddir}/_tools
npm install --no-save @electron/asar electron@%{electron_ver}
export PATH="%{_builddir}/_tools/node_modules/.bin:$PATH"

# --- extract the .nupkg payload ------------------------------------------
cd %{_builddir}
cp %{SOURCE0} AnthropicClaude-%{claude_version}-full.nupkg
7z x -y AnthropicClaude-%{claude_version}-full.nupkg

# --- extract icons from the bundled Windows binary -----------------------
wrestool -x -t 14 lib/net45/claude.exe -o claude.ico
icotool -x claude.ico

# --- extract and patch app.asar ------------------------------------------
asar extract lib/net45/resources/app.asar app.asar.contents
cp -r lib/net45/resources/app.asar.unpacked .

# External resources (Tray*, i18n, ion-dist, fonts, *.png) are NOT packed
# into the asar — the bundle's ryt() helper returns process.resourcesPath
# (Electron's outer resources/ dir) when app.isPackaged is true. They are
# installed alongside app.asar in %install instead.

# native module stub (the Windows native .node binary is unusable on Linux)
mkdir -p app.asar.contents/node_modules/@ant/claude-native
cat > app.asar.contents/node_modules/@ant/claude-native/index.js << 'STUB'
const KeyboardKey = {
  Backspace: 43, Tab: 280, Enter: 261, Shift: 272, Control: 61,
  Alt: 40, CapsLock: 56, Escape: 85, Space: 276, PageUp: 251,
  PageDown: 250, End: 83, Home: 154, LeftArrow: 175, UpArrow: 282,
  RightArrow: 262, DownArrow: 81, Delete: 79, Meta: 187
};
Object.freeze(KeyboardKey);
class AuthRequest {
  static isAvailable() { return false; }
  start() { return Promise.reject(new Error("Not available")); }
  cancel() {}
}
module.exports = {
  getWindowsVersion: () => "10.0.0",
  getWindowsElevationType: () => "default",
  getCurrentPackageFamilyName: () => "",
  getActiveWindowHandle: () => null,
  getAppInfoForFile: () => null,
  focusWindow: () => {},
  setWindowEffect: () => {},
  removeWindowEffect: () => {},
  getIsMaximized: () => false,
  flashFrame: () => {},
  clearFlashFrame: () => {},
  showNotification: () => {},
  setProgressBar: () => {},
  clearProgressBar: () => {},
  setOverlayIcon: () => {},
  clearOverlayIcon: () => {},
  readCfPrefValue: () => null,
  readPlistValue: () => null,
  readRegistryValues: () => [],
  writeRegistryValue: () => {},
  writeRegistryDword: () => {},
  closeOfficeDocument: () => {},
  focusOfficeDocument: () => false,
  getWindowAbove: () => null,
  isHardwareVirtEnabled: () => true,
  isProcessRunning: () => Promise.resolve(false),
  moveWindowBehind: () => {},
  enableWindowsOptionalFeature: () => Promise.resolve({ success: false }),
  AuthRequest,
  KeyboardKey
};
STUB

# --- sed patches on index.js ---------------------------------------------
# Patterns use captured groups for short minified identifiers (parameter
# names, variable names) because those rename across Claude releases.
# Verified against 1.8555.2 — three of the four reference-spec sed lines
# would have been no-ops with the upstream-hardcoded identifiers (e, Ln,
# Jr); the bundle now uses A, mo, ui at those sites.
_idx=app.asar.contents/.vite/build/index.js

# native window decorations
sed -i 's/titleBarStyle:"hidden"/titleBarStyle:"default"/g'      "$_idx"
sed -i 's/titleBarStyle:"hiddenInset"/titleBarStyle:"default"/g' "$_idx"

# Linux platform detection for Claude Code
sed -i -E 's/if\(process\.platform==="darwin"\)return ([a-zA-Z_$]+)==="arm64"\?"darwin-arm64":"darwin-x64";if\(process\.platform==="win32"\)return \1==="arm64"\?"win32-arm64":"win32-x64";throw new Error/if(process.platform==="darwin")return \1==="arm64"?"darwin-arm64":"darwin-x64";if(process.platform==="win32")return \1==="arm64"?"win32-arm64":"win32-x64";if(process.platform==="linux")return \1==="arm64"?"linux-arm64":"linux-x64";throw new Error/g' "$_idx"

# file:// origin validation
sed -i -E 's/([a-zA-Z_$]+)\.protocol==="file:"&&[a-zA-Z_$]+\.app\.isPackaged===!0/\1.protocol==="file:"/g' "$_idx"

# quit on window close when tray is disabled (upstream only checks win32)
sed -i -E 's/if\(([a-zA-Z_$]+)&&!([a-zA-Z_$]+)\("menuBarEnabled"\)\)/if((\1||process.platform==="linux")\&\&!\2("menuBarEnabled"))/' "$_idx"

# repack
asar pack app.asar.contents app.asar

%build

%install
export PATH="%{_builddir}/_tools/node_modules/.bin:$PATH"

_elecdir=%{_builddir}/_tools/node_modules/electron/dist
_dest=%{buildroot}%{_libdir}/%{name}
_resdir="$_dest"/electron/resources

# --- electron runtime ----------------------------------------------------
mkdir -p "$_dest"/electron
cp -r "$_elecdir"/* "$_dest"/electron/
# strip non-en-US locales (~41 MB)
find "$_dest"/electron/locales -type f ! -name 'en-US.pak' -delete
# remove chromium license blob (~15 MB)
rm -f "$_dest"/electron/LICENSES.chromium.html
# drop Electron's default welcome-screen asar so it doesn't shadow ours
rm -f "$_resdir"/default_app.asar

# --- app.asar + app.asar.unpacked (canonical Electron layout) ------------
# Electron's main process auto-loads ./resources/app.asar when no path arg
# is passed; that path also makes process.resourcesPath resolve to
# ./resources/, which is where the bundle's ryt() looks for Tray icons,
# i18n JSON, ion-dist, fonts, etc.
install -Dm644 %{_builddir}/app.asar "$_resdir"/app.asar
cp -r %{_builddir}/app.asar.unpacked "$_resdir"/
# native stub overlay so the unpacked @ant/claude-native is the Linux
# stub rather than the Windows .node binary
mkdir -p "$_resdir"/app.asar.unpacked/node_modules/@ant/claude-native
cp %{_builddir}/app.asar.contents/node_modules/@ant/claude-native/index.js \
   "$_resdir"/app.asar.unpacked/node_modules/@ant/claude-native/index.js
rm -f "$_resdir"/app.asar.unpacked/node_modules/@ant/claude-native/claude-native-binding.node

# --- external resources at process.resourcesPath ------------------------
# Tray icons, i18n JSON, ion-dist app, fonts, screen-capture PNGs. These
# live OUTSIDE the asar because ryt() returns process.resourcesPath.
_src=%{_builddir}/lib/net45/resources
cp "$_src"/Tray*.png "$_src"/Tray*.ico "$_resdir"/ 2>/dev/null || :
mkdir -p "$_resdir"/i18n
cp "$_src"/*.json "$_resdir"/i18n/ 2>/dev/null || :
[ -d "$_src"/fonts ]    && cp -r "$_src"/fonts    "$_resdir"/
[ -d "$_src"/ion-dist ] && cp -r "$_src"/ion-dist "$_resdir"/
cp "$_src"/claude-screen*.png "$_resdir"/ 2>/dev/null || :

# --- claude-ssh binaries (SSH remote feature) ----------------------------
# Anthropic ships this subdir intermittently — present 1.1.3770-1.1.x,
# absent by 1.8555.x. Skip when missing rather than fail the build.
_sshsrc="$_src"/claude-ssh
if [ -d "$_sshsrc" ]; then
    [ -f "$_sshsrc/claude-ssh-linux-arm64" ] && install -Dm755 "$_sshsrc/claude-ssh-linux-arm64" "$_resdir"/claude-ssh/claude-ssh-linux-arm64
    [ -f "$_sshsrc/claude-ssh-linux-amd64" ] && install -Dm755 "$_sshsrc/claude-ssh-linux-amd64" "$_resdir"/claude-ssh/claude-ssh-linux-amd64
    [ -f "$_sshsrc/version.txt" ]            && install -Dm644 "$_sshsrc/version.txt"            "$_resdir"/claude-ssh/version.txt
fi

# --- launcher script -----------------------------------------------------
# No path arg — Electron auto-discovers resources/app.asar next to its
# executable.
mkdir -p %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/claude-desktop << 'LAUNCHER'
#!/bin/bash
exec %{_libdir}/claude-desktop/electron/electron "$@"
LAUNCHER
chmod 0755 %{buildroot}%{_bindir}/claude-desktop

# --- desktop file --------------------------------------------------------
mkdir -p %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/claude-desktop.desktop << 'DESKTOP'
[Desktop Entry]
Name=Claude
Exec=claude-desktop %u
Icon=claude-desktop
Type=Application
Terminal=false
Categories=Office;Utility;
MimeType=x-scheme-handler/claude;
StartupWMClass=claude
DESKTOP
desktop-file-install \
    --dir=%{buildroot}%{_datadir}/applications \
    %{buildroot}%{_datadir}/applications/claude-desktop.desktop

# --- icons ---------------------------------------------------------------
for size in 16 24 32 48 64 256; do
    _icon=$(ls %{_builddir}/claude_*_${size}x${size}x32.png 2>/dev/null | head -1)
    if [ -n "$_icon" ]; then
        install -Dm644 "$_icon" \
            %{buildroot}%{_datadir}/icons/hicolor/${size}x${size}/apps/claude-desktop.png
    fi
done

%files
%{_bindir}/claude-desktop
%{_libdir}/%{name}
%{_datadir}/applications/claude-desktop.desktop
%{_datadir}/icons/hicolor/*/apps/claude-desktop.png

%post
gtk-update-icon-cache -f -t %{_datadir}/icons/hicolor || :
touch -h %{_datadir}/icons/hicolor >/dev/null 2>&1 || :
update-desktop-database %{_datadir}/applications || :

%postun
if [ $1 -eq 0 ]; then
    gtk-update-icon-cache -f -t %{_datadir}/icons/hicolor || :
    update-desktop-database %{_datadir}/applications || :
fi

%changelog
* Wed Jun 10 2026 Automated Update <github-actions@github.com> - 1.11847.5-1
- Update to Claude Desktop 1.11847.5
* Sat Jun 06 2026 Automated Update <github-actions@github.com> - 1.11187.4-1
- Update to Claude Desktop 1.11187.4
* Wed Jun 03 2026 Automated Update <github-actions@github.com> - 1.10628.0-1
- Update to Claude Desktop 1.10628.0
* Fri May 29 2026 Automated Update <github-actions@github.com> - 1.9659.2-1
- Update to Claude Desktop 1.9659.2
* Wed May 27 2026 Automated Update <github-actions@github.com> - 1.9255.2-1
- Update to Claude Desktop 1.9255.2
* Mon May 25 2026 Kristián Kekeš <gamerix2006@gmail.com> - 1.8555.2-3
- Verified the spec by actually unpacking the 1.8555.2 .nupkg and
  walking each step. Three of the four reference-spec sed lines turned
  out to be no-ops against current bundles because the minified
  identifiers renamed (e->A, Ln->mo, Jr->ui); rewrote them with
  capturing groups so they survive future renames.
- Stop packing Tray icons / i18n JSON / fonts into the asar — the
  bundle's ryt() helper resolves these via process.resourcesPath, so
  they must live alongside app.asar in Electron's resources/ dir, not
  inside the asar.
- Ship the previously-missed lib/net45/resources/ion-dist/ payload at
  process.resourcesPath/ion-dist (new in 1.x, not in 1.1.x).
- Move app.asar + app.asar.unpacked into %{_libdir}/claude-desktop/
  electron/resources/ to follow Electron's canonical app layout, drop
  the default_app.asar welcome screen, and simplify the launcher to
  `exec electron` (Electron auto-discovers resources/app.asar).
- Make the claude-ssh install block tolerant of the subdir being
  absent — gone from .nupkg by 1.8555.x.

* Mon May 25 2026 Kristián Kekeš <gamerix2006@gmail.com> - 1.8555.2-1
- Initial RPM package, adapted from christian-korneck/claude-desktop-rpm.
  Downloads the .nupkg directly from Anthropic's Squirrel feed instead
  of the outer Claude-<hash>.exe wrapper, since the .nupkg URL is
  derivable from the public RELEASES manifest while the .exe hash is
  not.
