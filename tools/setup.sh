#!/bin/sh
# Everything immollimma needs, from nothing. Safe to run again: done steps are skipped.
#
#   sh tools/setup.sh            libraries into libs/ (≈ 4.4 GB; .git folders removed), Python packages,
#                                checks bin/libsfizz.so (prebuilt, x86-64, glibc ≥ 2.39 — Ubuntu 24.04)
#   sh tools/setup.sh --keep-git keep the .git folders of the libraries (≈ 8 GB)
#   sh tools/setup.sh --build-sfizz   build libsfizz from source even if the prebuilt one loads
#   sh tools/setup.sh --no-sso   skip Sonatina (VSCO only)
#
# A Claude session runs it in ~5–10 minutes (most of it the 3 GB VSCO clone).
set -e
cd "$(dirname "$0")/.."
ROOT=$PWD
LIBS=${IMMOLLIMMA_LIBS:-$ROOT/libs}
KEEP_GIT=0; BUILD=0; SSO=1
for a in "$@"; do
  case $a in --keep-git) KEEP_GIT=1;; --build-sfizz) BUILD=1;; --no-sso) SSO=0;; esac
done
mkdir -p "$LIBS"

echo "== Python packages"
python3 -c "import numpy, scipy, soundfile, librosa, mido, music21, matplotlib" 2>/dev/null || \
  pip install -q --break-system-packages numpy scipy soundfile librosa mido music21 matplotlib 2>&1 | tail -1

echo "== system tools (ffmpeg required; LilyPond for PDF scores)"
command -v ffmpeg >/dev/null || (apt-get install -y -qq ffmpeg >/dev/null 2>&1 || echo "  ffmpeg missing — install it")
command -v lilypond >/dev/null || (apt-get install -y -qq lilypond >/dev/null 2>&1 || echo "  LilyPond missing — no PDF scores (MIDI/MusicXML still made)")

echo "== VSCO-2 Community Edition (CC0)"
if [ ! -d "$LIBS/VSCO-2-CE/Strings" ]; then
  git clone -q --depth 1 https://github.com/sgossner/VSCO-2-CE "$LIBS/VSCO-2-CE"
  [ $KEEP_GIT = 1 ] || rm -rf "$LIBS/VSCO-2-CE/.git"
fi

echo "== VSCO SFZ files (branch SFZ, only the .sfz)"
if [ ! -f "$LIBS/vsco-sfz/Harp.sfz" ]; then
  rm -rf "$LIBS/vsco-sfz-src"
  git clone -q --filter=blob:none --no-checkout --depth 1 --branch SFZ https://github.com/sgossner/VSCO-2-CE "$LIBS/vsco-sfz-src"
  (cd "$LIBS/vsco-sfz-src" && git sparse-checkout set --no-cone '*.sfz' && git checkout -q SFZ)
  mkdir -p "$LIBS/vsco-sfz" && cp "$LIBS/vsco-sfz-src"/*.sfz "$LIBS/vsco-sfz/" && rm -rf "$LIBS/vsco-sfz-src"
  for d in Brass Keys Percussion Strings Woodwinds "VSCO 1 Percussion" "Miscellania Raw"; do
    ln -sfn "../VSCO-2-CE/$d" "$LIBS/vsco-sfz/$d"
  done
fi

if [ $SSO = 1 ]; then
  echo "== Sonatina Symphonic Orchestra (CC Sampling Plus 1.0 — not for advertising)"
  if [ ! -d "$LIBS/sso/Sonatina Symphonic Orchestra/Samples" ]; then
    git clone -q --depth 1 https://github.com/peastman/sso "$LIBS/sso"
    [ $KEEP_GIT = 1 ] || rm -rf "$LIBS/sso/.git"
  fi
fi

echo "== sfizz"
LOADS=0
python3 -c "import ctypes; ctypes.CDLL('$ROOT/bin/libsfizz.so')" 2>/dev/null && LOADS=1
if [ $LOADS = 0 ] || [ $BUILD = 1 ]; then
  echo "  building libsfizz from source (≈ 10 min on 2 cores; needs cmake, g++, libsndfile1-dev)"
  command -v cmake >/dev/null || apt-get install -y -qq cmake g++ libsndfile1-dev >/dev/null 2>&1 || true
  B=${TMPDIR:-/tmp}/sfizz-build
  [ -d "$B/sfizz" ] || git clone -q --depth 1 --recurse-submodules --shallow-submodules https://github.com/sfztools/sfizz "$B/sfizz"
  mkdir -p "$B/sfizz/bs" && cd "$B/sfizz/bs"
  cmake .. -DCMAKE_BUILD_TYPE=Release -DSFIZZ_JACK=OFF -DSFIZZ_RENDER=OFF -DSFIZZ_SHARED=ON \
           -DSFIZZ_LV2=OFF -DSFIZZ_VST=OFF -DENABLE_LTO=OFF > /dev/null
  make -j"$(nproc)" sfizz_shared 2>&1 | tail -1
  cp library/lib/libsfizz.so "$ROOT/bin/libsfizz.so" && strip "$ROOT/bin/libsfizz.so"
  cd "$ROOT"
fi

echo "== check"
python3 -m kit check
