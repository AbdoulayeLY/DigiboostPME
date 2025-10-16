#!/bin/bash
# Script pour demarrer le serveur FastAPI sans interference d'Anaconda

# Desactiver conda
if command -v conda &> /dev/null; then
    conda deactivate 2>/dev/null || true
fi

# Nettoyer le PATH d'Anaconda
export PATH=$(echo $PATH | tr ':' '\n' | grep -v anaconda | tr '\n' ':' | sed 's/:$//')

# Definir explicitement le Python du venv
export PYTHONPATH=""
export PYTHONHOME=""

# Aller dans le repertoire backend
cd "$(dirname "$0")"

# Lancer uvicorn avec le Python du venv
./venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
