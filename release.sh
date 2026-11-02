#!/bin/bash
set -e

if [ -z "$1" ]; then
  echo "Kullanım: ./release.sh v1.0.5"
  exit 1
fi

VERSION=$1

echo "Sürüm etiketleniyor: $VERSION"
git tag -a "$VERSION" -m "Release $VERSION"
git push origin "$VERSION"

echo "Sürüm $VERSION başarıyla GitHub'a gönderildi!"
