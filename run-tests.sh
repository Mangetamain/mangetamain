#!/bin/bash

# Script pour exécuter les tests avec Docker Compose
# Usage: ./run-tests.sh [options]

set -e

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 MangeTaMain - Script de tests Docker${NC}"
echo "========================================"

# Fonction d'aide
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help           Afficher cette aide"
    echo "  -u, --unit           Exécuter seulement les tests unitaires"
    echo "  -i, --integration    Exécuter seulement les tests d'intégration"
    echo "  -p, --performance    Exécuter seulement les tests de performance"
    echo "  -c, --coverage       Générer le rapport de couverture uniquement"
    echo "  -d, --dev           Mode développement interactif"
    echo "  -b, --build         Forcer la reconstruction de l'image"
    echo "  -v, --verbose       Mode verbose"
    echo "  --clean             Nettoyer les volumes et images de test"
    echo ""
    echo "Exemples:"
    echo "  $0                  # Exécuter tous les tests"
    echo "  $0 -u               # Tests unitaires seulement"
    echo "  $0 -i               # Tests d'intégration seulement"
    echo "  $0 -p               # Tests de performance seulement"
    echo "  $0 -c               # Générer le rapport de couverture"
    echo "  $0 -d               # Mode développement interactif"
    echo "  $0 --clean          # Nettoyer l'environnement de test"
}

# Variables par défaut
TEST_TYPE="all"
BUILD_FLAG=""
VERBOSE_FLAG=""
COVERAGE_ONLY=false
DEV_MODE=false
CLEAN_MODE=false

# Parser les arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -u|--unit)
            TEST_TYPE="unit"
            shift
            ;;
        -i|--integration)
            TEST_TYPE="integration"
            shift
            ;;
        -p|--performance)
            TEST_TYPE="performance"
            shift
            ;;
        -c|--coverage)
            COVERAGE_ONLY=true
            shift
            ;;
        -d|--dev)
            DEV_MODE=true
            shift
            ;;
        -b|--build)
            BUILD_FLAG="--build"
            shift
            ;;
        -v|--verbose)
            VERBOSE_FLAG="-v"
            shift
            ;;
        --clean)
            CLEAN_MODE=true
            shift
            ;;
        *)
            echo -e "${RED}❌ Option inconnue: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Fonction de nettoyage
cleanup() {
    echo -e "\n${YELLOW}🧹 Nettoyage de l'environnement de test...${NC}"
    docker-compose --profile testing down -v
    docker-compose --profile testing rm -f
    docker volume prune -f
    docker system prune -f
    echo -e "${GREEN}✅ Nettoyage terminé${NC}"
}

# Mode nettoyage
if [ "$CLEAN_MODE" = true ]; then
    cleanup
    exit 0
fi

# Vérifier que Docker est disponible
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ docker-compose n'est pas installé${NC}"
    exit 1
fi

# Mode développement interactif
if [ "$DEV_MODE" = true ]; then
    echo -e "${BLUE}🔧 Démarrage du mode développement interactif...${NC}"
    echo -e "${YELLOW}Commands disponibles dans le container:${NC}"
    echo "  poetry run pytest tests/unit/           # Tests unitaires"
    echo "  poetry run pytest tests/integration/    # Tests d'intégration"
    echo "  poetry run pytest tests/performance/    # Tests de performance"
    echo "  poetry run pytest --cov=src            # Tests avec couverture"
    echo "  poetry run coverage html               # Générer rapport HTML"
    echo "  exit                                    # Quitter"
    echo ""
    
    docker-compose --profile testing up $BUILD_FLAG -d preprocessing
    docker-compose --profile testing run --rm tests-dev
    exit 0
fi

# Construire la commande pytest selon le type de test
PYTEST_CMD="poetry run pytest"

case $TEST_TYPE in
    "unit")
        PYTEST_CMD="$PYTEST_CMD tests/unit/"
        echo -e "${BLUE}🔬 Exécution des tests unitaires...${NC}"
        ;;
    "integration")
        PYTEST_CMD="$PYTEST_CMD tests/integration/"
        echo -e "${BLUE}🔗 Exécution des tests d'intégration...${NC}"
        ;;
    "performance")
        PYTEST_CMD="$PYTEST_CMD tests/performance/"
        echo -e "${BLUE}⚡ Exécution des tests de performance...${NC}"
        ;;
    "all")
        PYTEST_CMD="$PYTEST_CMD tests/"
        echo -e "${BLUE}🧪 Exécution de tous les tests...${NC}"
        ;;
esac

# Ajouter les options de couverture
if [ "$COVERAGE_ONLY" = true ]; then
    echo -e "${BLUE}📊 Génération du rapport de couverture...${NC}"
    PYTEST_CMD="$PYTEST_CMD --cov=src --cov-report=html:/app/test-reports/htmlcov --cov-report=xml:/app/test-reports/coverage.xml --cov-report=term-missing"
else
    PYTEST_CMD="$PYTEST_CMD --cov=src --cov-report=html:/app/test-reports/htmlcov --cov-report=xml:/app/test-reports/coverage.xml --cov-report=term-missing --junit-xml=/app/test-reports/junit.xml"
fi

# Ajouter le flag verbose si demandé
if [ -n "$VERBOSE_FLAG" ]; then
    PYTEST_CMD="$PYTEST_CMD -v"
fi

# Fonction pour exécuter les tests
run_tests() {
    echo -e "${YELLOW}📦 Démarrage des services de test...${NC}"
    
    # Démarrer le preprocessing d'abord
    docker-compose --profile testing up $BUILD_FLAG -d preprocessing
    
    # Attendre que le preprocessing soit prêt
    echo -e "${YELLOW}⏳ Attente du preprocessing...${NC}"
    sleep 5
    
    # Exécuter les tests
    echo -e "${BLUE}🚀 Exécution: $PYTEST_CMD${NC}"
    docker-compose --profile testing run --rm tests bash -c "poetry install --with dev && $PYTEST_CMD"
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✅ Tests terminés avec succès!${NC}"
        echo -e "${BLUE}📊 Rapports disponibles dans le volume test_reports${NC}"
        echo -e "${YELLOW}💡 Pour voir les rapports: docker-compose --profile testing exec tests ls -la /app/test-reports/${NC}"
    else
        echo -e "${RED}❌ Les tests ont échoué!${NC}"
    fi
    
    return $exit_code
}

# Exécution normale
run_tests
exit $?