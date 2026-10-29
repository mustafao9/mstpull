#!/bin/bash
set -e

echo "🚀 MstPull İkon Düzeltmeli Paketleme..."

BUILD_DIR="build_out"
DEB_DIR="$BUILD_DIR/deb/mstpull_1.0.1_amd64"

rm -rf "$BUILD_DIR"
mkdir -p "$DEB_DIR/DEBIAN"
mkdir -p "$DEB_DIR/usr/bin"
mkdir -p "$DEB_DIR/usr/share/mstpull"
mkdir -p "$DEB_DIR/usr/share/applications"
mkdir -p "$DEB_DIR/usr/share/pixmaps"
mkdir -p "$DEB_DIR/usr/share/icons/hicolor/256x256/apps"

cp -r main.py src config assets locales "$DEB_DIR/usr/share/mstpull/" 2>/dev/null || cp -r main.py src config assets "$DEB_DIR/usr/share/mstpull/"
rsync -a --exclude='__pycache__' --exclude='*.pyc' .venv "$DEB_DIR/usr/share/mstpull/" 2>/dev/null || cp -r .venv "$DEB_DIR/usr/share/mstpull/"
find "$DEB_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

chmod -R 755 "$DEB_DIR/usr/share/mstpull/"

# İkonları hem pixmaps hem de hicolor altına kopyala (Cinnamon uyumu için)
if [ -f "assets/icons/app.png" ]; then
    cp assets/icons/app.png "$DEB_DIR/usr/share/pixmaps/mstpull.png"
    cp assets/icons/app.png "$DEB_DIR/usr/share/icons/hicolor/256x256/apps/mstpull.png"
fi

cat << 'LAUNCHER' > "$DEB_DIR/usr/bin/mstpull"
#!/bin/bash
cd /usr/share/mstpull
source .venv/bin/activate
exec python3 main.py "$@"
LAUNCHER
chmod +x "$DEB_DIR/usr/bin/mstpull"

cat << 'DESKTOP' > "$DEB_DIR/usr/share/applications/mstpull.desktop"
[Desktop Entry]
Name=MstPull
Comment=Profesyonel Linux Video ve Ses İndirme Yöneticisi
Exec=/usr/bin/mstpull
Icon=mstpull
Terminal=false
Type=Application
Categories=Network;AudioVideo;
StartupWMClass=mstpull
Keywords=download;youtube;mp3;video;mstpull;
DESKTOP

cat << 'CONTROL' > "$DEB_DIR/DEBIAN/control"
Package: mstpull
Version: 1.0.1
Architecture: amd64
Maintainer: Mustafa Satılmış <mustafao9>
Description: MstPull Video & Audio Downloader for Linux
 IDM kalitesinde hızlı, eşzamanlı ve sistem tepsisi destekli indirme yöneticisi.
CONTROL

dpkg-deb --build "$DEB_DIR" "$BUILD_DIR/mstpull_1.0.1_amd64.deb"
echo "✅ DEB paketi ikonlarla güncellendi."
