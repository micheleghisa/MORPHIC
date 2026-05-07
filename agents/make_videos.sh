#!/bin/bash
# MORPHIC Video Maker — Genera video TikTok faceless
# Uso: bash agents/make_videos.sh 2026-W18

cd "$(dirname "$0")/.."
source backend/venv/bin/activate
python3 agents/video_maker.py "$1"
