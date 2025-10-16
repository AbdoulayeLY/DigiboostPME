#!/bin/bash
# Script pour desactiver conda dans .zshrc

echo "=== Correction de l'erreur Anaconda ==="
echo ""

# Backup du .zshrc
cp ~/.zshrc ~/.zshrc.backup.$(date +%Y%m%d_%H%M%S)
echo "✓ Backup cree: ~/.zshrc.backup.$(date +%Y%m%d_%H%M%S)"

# Commenter le bloc conda initialize
sed -i.bak '/# >>> conda initialize >>>/,/# <<< conda initialize <<</s/^/# DISABLED BY DIGIBOOST: /' ~/.zshrc

echo "✓ Bloc conda commente dans ~/.zshrc"
echo ""
echo "IMPORTANT:"
echo "1. Fermez ce terminal"
echo "2. Ouvrez un NOUVEAU terminal"
echo "3. Allez dans le dossier backend"
echo "4. Lancez: ./run_server.sh"
echo ""
echo "Pour reactiver Anaconda plus tard:"
echo "  cp ~/.zshrc.backup.XXXXXX ~/.zshrc"
