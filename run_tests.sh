#!/bin/bash
# Script wrapper pour run_tests_unified.py
# Compatible Unix/Linux/macOS et Windows via Git Bash/WSL

set -e

# Détection de l'OS
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    PYTHON_CMD="python"
else
    PYTHON_CMD="python3"
fi

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 MangeTaMain - Script de tests unifié${NC}"
echo "========================================"

# Vérifier que Python est disponible
if ! command -v $PYTHON_CMD &> /dev/null; then
    echo -e "${RED}❌ Python n'est pas disponible dans le PATH${NC}"
    echo "Installez Python 3.9+ ou utilisez 'python' au lieu de 'python3'"
    exit 1
fi

# Vérifier que le script Python existe
SCRIPT_PATH="$(dirname "$0")/run_tests_unified.py"
if [[ ! -f "$SCRIPT_PATH" ]]; then
    echo -e "${RED}❌ Script run_tests_unified.py non trouvé${NC}"
    exit 1
fi

# Passer tous les arguments au script Python
echo -e "${YELLOW}🚀 Lancement du script Python unifié...${NC}"
exec $PYTHON_CMD "$SCRIPT_PATH" "$@"