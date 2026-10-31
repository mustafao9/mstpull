#!/bin/bash

# 1. Mevcut en son Git tag'ini al
CURRENT_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v1.0.2")

# 2. Versiyon numarasını otomatik 1 artır (örnek: v1.0.2 -> v1.0.3)
VERSION_BODY=${CURRENT_TAG#v}
MAJOR=$(echo $VERSION_BODY | awk -F. '{print $1}')
MINOR=$(echo $VERSION_BODY | awk -F. '{print $2}')
PATCH=$(echo $VERSION_BODY | awk -F. '{print $3}')
NEW_PATCH=$((PATCH + 1))
NEW_TAG="v${MAJOR}.${MINOR}.${NEW_PATCH}"

echo "========================================"
echo "📌 Mevcut Sürüm: $CURRENT_TAG"
echo "🚀 Yeni Sürüm  : $NEW_TAG"
echo "========================================"

# 3. Değişiklik açıklamasını Türkçe olarak al
read -p "Türkçe Sürüm Açıklamasını Girin: " msg
if [ -z "$msg" ]; then
  msg="Windows kilitlenme, konsol penceresi ve thread bellek sızıntıları düzeltildi"
fi

# 4. PyInstaller ile derleme yap (eğer sistemde kuruluysa)
if [ -f "main.py" ] && command -v pyinstaller &> /dev/null; then
    echo "📦 Executable paket derleniyor..."
    pyinstaller --noconfirm --onedir --windowed --name "MstPull" main.py
fi

COMMIT_MSG="release($NEW_TAG): $msg"

# 5. Git adımlarını çalıştır
git add .
git commit -m "$COMMIT_MSG"
git tag -a "$NEW_TAG" -m "$msg"
git push origin main --tags

echo "========================================"
echo "✅ Sürüm $NEW_TAG ve Türkçe güncellemeler GitHub'a başarıyla gönderildi!"
echo "========================================"
