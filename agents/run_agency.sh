#!/bin/bash
# MORPHIC Content Agency — Full Pipeline Runner
# Genera una settimana completa: trend → strategia → contenuti → video

cd "$(dirname "$0")/.."
source backend/venv/bin/activate
python3 agents/orchestrator.py
