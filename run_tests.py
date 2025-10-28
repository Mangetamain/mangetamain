#!/usr/bin/env python3
"""
Script unifié pour exécuter les tests avec Docker Compose ou Python direct.
Combine les fonctionnalités de run-tests.sh et run_tests.py pour une cohérence maximale.

Usage: 
    ./run_tests.py [options]
    python run_tests.py [options]
"""
import argparse
import subprocess
import sys
import os
import platform
import time
from pathlib import Path
from typing import List, Optional, Dict, Any


# Couleurs pour l'affichage terminal
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    NC = '\033[0m'  # No Color
    
    @classmethod
    def colorize(cls, text: str, color: str) -> str:
        """Ajoute de la couleur au texte si le terminal le supporte."""
        if os.getenv('NO_COLOR') or platform.system() == 'Windows':
            return text
        return f"{color}{text}{cls.NC}"


def print_header(title: str):
    """Affiche un en-tête coloré."""
    print(Colors.colorize(f"\n🧪 {title}", Colors.BLUE))
    print(Colors.colorize("=" * (len(title) + 4), Colors.BLUE))


def print_success(message: str):
    """Affiche un message de succès."""
    print(Colors.colorize(f"✅ {message}", Colors.GREEN))


def print_error(message: str):
    """Affiche un message d'erreur."""
    print(Colors.colorize(f"❌ {message}", Colors.RED))


def print_warning(message: str):
    """Affiche un avertissement."""
    print(Colors.colorize(f"⚠️  {message}", Colors.YELLOW))


def print_info(message: str):
    """Affiche une information."""
    print(Colors.colorize(f"ℹ️  {message}", Colors.CYAN))


class TestRunner:
    """Gestionnaire principal pour l'exécution des tests."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.is_docker_available = self._check_docker()
        self.is_python_available = self._check_python()
        
    def _check_docker(self) -> bool:
        """Vérifie si Docker et Docker Compose sont disponibles."""
        try:
            subprocess.run(['docker', '--version'], 
                         check=True, capture_output=True, text=True)
            subprocess.run(['docker-compose', '--version'], 
                         check=True, capture_output=True, text=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _check_python(self) -> bool:
        """Vérifie si Python et les dépendances sont disponibles."""
        try:
            subprocess.run([sys.executable, '-m', 'pytest', '--version'], 
                         check=True, capture_output=True, text=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def run_docker_tests(self, test_type: str = "all", **kwargs) -> bool:
        """Exécute les tests avec Docker Compose."""
        print_header(f"Exécution des tests Docker - {test_type}")
        
        # Préparation des commandes Docker
        build_flag = "--build" if kwargs.get('build', False) else ""
        verbose_flag = "-v" if kwargs.get('verbose', False) else ""
        
        try:
            # Démarrer le preprocessing d'abord
            print_info("Démarrage des services de preprocessing...")
            subprocess.run([
                'docker-compose', '--profile', 'testing', 'up', 
                build_flag, '-d', 'preprocessing'
            ].filter(None), check=True, cwd=self.project_root)
            
            # Attendre que le preprocessing soit prêt
            print_info("Attente du preprocessing...")
            time.sleep(5)
            
            # Construire la commande pytest
            pytest_cmd = self._build_pytest_command(test_type, "docker", **kwargs)
            
            # Exécuter les tests
            print_info(f"Exécution: {' '.join(pytest_cmd)}")
            result = subprocess.run([
                'docker-compose', '--profile', 'testing', 'run', '--rm', 'tests',
                'bash', '-c', f"poetry install --with dev && {' '.join(pytest_cmd)}"
            ], cwd=self.project_root)
            
            if result.returncode == 0:
                print_success("Tests Docker terminés avec succès!")
                self._show_reports_info("docker")
                return True
            else:
                print_error("Les tests Docker ont échoué!")
                return False
                
        except subprocess.CalledProcessError as e:
            print_error(f"Erreur lors de l'exécution des tests Docker: {e}")
            return False
        except FileNotFoundError:
            print_error("Docker Compose non trouvé. Installez Docker et Docker Compose.")
            return False
    
    def run_python_tests(self, test_type: str = "all", **kwargs) -> bool:
        """Exécute les tests directement avec Python."""
        print_header(f"Exécution des tests Python - {test_type}")
        
        # S'assurer qu'on est dans le bon répertoire
        os.chdir(self.project_root)
        
        # Construire la commande pytest
        pytest_cmd = self._build_pytest_command(test_type, "python", **kwargs)
        
        success = True
        
        if test_type == "all":
            # Exécuter par catégories pour une meilleure organisation
            categories = [
                ("unitaires", "tests/unit/"),
                ("intégration", "tests/integration/"),
                ("performance", "tests/performance/")
            ]
            
            for i, (cat_name, cat_path) in enumerate(categories, 1):
                print(f"\n🔬 Tests {cat_name} ({i}/{len(categories)})")
                print("-" * 40)
                
                cat_cmd = pytest_cmd.copy()
                cat_cmd[cat_cmd.index("tests/")] = cat_path
                
                if not self._run_single_pytest_command(cat_cmd, cat_name):
                    success = False
                    
        else:
            success = self._run_single_pytest_command(pytest_cmd, test_type)
        
        # Rapport final si tous les tests ont été exécutés
        if success and test_type == "all":
            success = self._generate_final_coverage_report()
        
        return success
    
    def _build_pytest_command(self, test_type: str, runner: str, **kwargs) -> List[str]:
        """Construit la commande pytest selon les paramètres."""
        cmd = [sys.executable, "-m", "pytest"] if runner == "python" else ["poetry", "run", "pytest"]
        
        # Dossier de tests selon le type
        test_paths = {
            "unit": "tests/unit/",
            "integration": "tests/integration/", 
            "performance": "tests/performance/",
            "all": "tests/"
        }
        cmd.append(test_paths.get(test_type, "tests/"))
        
        # Options de couverture
        if not kwargs.get('no_coverage', False):
            cmd.extend([
                "--cov=preprocessing",
                "--cov=streamlit_poetry_docker",
                "--cov-report=term-missing",
                "--cov-report=html:htmlcov/" + test_type,
            ])
            
            if test_type != "all":
                cmd.append("--cov-append")
        
        # Options additionnelles
        if kwargs.get('verbose', False):
            cmd.append("-v")
            
        if kwargs.get('markers'):
            cmd.extend(["-m", kwargs['markers']])
            
        if kwargs.get('durations'):
            cmd.extend(["--durations", str(kwargs['durations'])])
            
        # Seuil de couverture pour le rapport final
        if test_type == "all" and not kwargs.get('no_coverage', False):
            cmd.extend(["--cov-fail-under=80"])
        
        return cmd
    
    def _run_single_pytest_command(self, cmd: List[str], test_name: str) -> bool:
        """Exécute une commande pytest unique."""
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print_warning(f"Warnings: {result.stderr}")
            return True
            
        except subprocess.CalledProcessError as e:
            print_error(f"Échec des tests {test_name}")
            print("STDOUT:", e.stdout)
            print("STDERR:", e.stderr)
            return False
            
        except FileNotFoundError:
            print_error("Pytest non trouvé. Installez avec: pip install pytest pytest-cov")
            return False
    
    def _generate_final_coverage_report(self) -> bool:
        """Génère le rapport de couverture final."""
        print_info("Génération du rapport de couverture final...")
        
        final_cmd = [
            sys.executable, "-m", "pytest", 
            "tests/",
            "--cov=preprocessing",
            "--cov=streamlit_poetry_docker",
            "--cov-report=html:htmlcov/final",
            "--cov-report=term-missing",
            "--cov-report=xml:coverage.xml",
            "--cov-fail-under=80",
            "--tb=no",
            "-q"
        ]
        
        try:
            result = subprocess.run(final_cmd, check=True, capture_output=True, text=True)
            print(result.stdout)
            
            print_success("Rapport de couverture généré!")
            print_info("📁 Rapport HTML: htmlcov/final/index.html")
            print_info("📄 Rapport XML: coverage.xml")
            return True
            
        except subprocess.CalledProcessError as e:
            print_warning("Couverture insuffisante (< 80%)")
            print(e.stdout)
            return False
    
    def _show_reports_info(self, runner: str):
        """Affiche les informations sur les rapports générés."""
        if runner == "docker":
            print_info("📊 Rapports disponibles dans le volume test_reports")
            print_info("💡 Voir: docker-compose --profile testing exec tests ls -la /app/test-reports/")
        else:
            print_info("📊 Rapports HTML disponibles dans htmlcov/")
            print_info("📄 Rapport XML disponible: coverage.xml")
    
    def run_development_mode(self):
        """Lance le mode développement interactif."""
        print_header("Mode Développement Interactif")
        
        if not self.is_docker_available:
            print_error("Docker non disponible pour le mode développement")
            return False
        
        print_info("Commands disponibles dans le container:")
        print("  poetry run pytest tests/unit/           # Tests unitaires")
        print("  poetry run pytest tests/integration/    # Tests d'intégration")
        print("  poetry run pytest --cov=src            # Tests avec couverture")
        print("  poetry run coverage html               # Générer rapport HTML")
        print("  exit                                    # Quitter")
        print()
        
        try:
            subprocess.run([
                'docker-compose', '--profile', 'testing', 'up', '-d', 'preprocessing'
            ], check=True, cwd=self.project_root)
            
            subprocess.run([
                'docker-compose', '--profile', 'testing', 'run', '--rm', 'tests-dev'
            ], cwd=self.project_root)
            
            return True
            
        except subprocess.CalledProcessError as e:
            print_error(f"Erreur en mode développement: {e}")
            return False
    
    def cleanup_environment(self):
        """Nettoie l'environnement de test."""
        print_header("Nettoyage de l'environnement de test")
        
        if not self.is_docker_available:
            print_warning("Docker non disponible pour le nettoyage")
            return
        
        try:
            print_info("Arrêt des services de test...")
            subprocess.run([
                'docker-compose', '--profile', 'testing', 'down', '-v'
            ], cwd=self.project_root)
            
            print_info("Suppression des containers...")
            subprocess.run([
                'docker-compose', '--profile', 'testing', 'rm', '-f'
            ], cwd=self.project_root)
            
            print_info("Nettoyage des volumes...")
            subprocess.run(['docker', 'volume', 'prune', '-f'])
            
            print_info("Nettoyage du système...")
            subprocess.run(['docker', 'system', 'prune', '-f'])
            
            print_success("Nettoyage terminé")
            
        except subprocess.CalledProcessError as e:
            print_error(f"Erreur lors du nettoyage: {e}")
    
    def check_coverage_only(self):
        """Vérifie uniquement la couverture existante."""
        print_header("Vérification de la couverture existante")
        
        try:
            cmd = [sys.executable, "-m", "coverage", "report", "--show-missing"]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(result.stdout)
            return True
        except subprocess.CalledProcessError:
            print_error("Aucune donnée de couverture trouvée. Exécutez d'abord les tests.")
            return False
        except FileNotFoundError:
            print_error("Module coverage non trouvé. Installez-le avec: pip install coverage")
            return False


def create_parser() -> argparse.ArgumentParser:
    """Crée le parser d'arguments."""
    parser = argparse.ArgumentParser(
        description="Script unifié pour exécuter les tests MangeTaMain",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  %(prog)s                    # Exécuter tous les tests (auto-détection Docker/Python)
  %(prog)s -u                 # Tests unitaires seulement
  %(prog)s -i                 # Tests d'intégration seulement
  %(prog)s -p                 # Tests de performance seulement
  %(prog)s -c                 # Vérifier couverture existante
  %(prog)s -d                 # Mode développement interactif
  %(prog)s --docker           # Forcer l'utilisation de Docker
  %(prog)s --python           # Forcer l'utilisation de Python direct
  %(prog)s --clean            # Nettoyer l'environnement Docker
        """
    )
    
    # Type de tests
    test_group = parser.add_mutually_exclusive_group()
    test_group.add_argument('-u', '--unit', action='store_true',
                           help='Exécuter seulement les tests unitaires')
    test_group.add_argument('-i', '--integration', action='store_true',
                           help='Exécuter seulement les tests d\'intégration')
    test_group.add_argument('-p', '--performance', action='store_true',
                           help='Exécuter seulement les tests de performance')
    test_group.add_argument('-c', '--coverage', action='store_true',
                           help='Vérifier la couverture existante uniquement')
    
    # Mode d'exécution
    runner_group = parser.add_mutually_exclusive_group()
    runner_group.add_argument('--docker', action='store_true',
                             help='Forcer l\'utilisation de Docker')
    runner_group.add_argument('--python', action='store_true',
                             help='Forcer l\'utilisation de Python direct')
    
    # Modes spéciaux
    parser.add_argument('-d', '--dev', action='store_true',
                       help='Mode développement interactif (Docker)')
    parser.add_argument('--clean', action='store_true',
                       help='Nettoyer l\'environnement Docker')
    
    # Options de test
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Mode verbose')
    parser.add_argument('-b', '--build', action='store_true',
                       help='Forcer la reconstruction des images Docker')
    parser.add_argument('--no-coverage', action='store_true',
                       help='Désactiver la mesure de couverture')
    parser.add_argument('-m', '--markers', type=str,
                       help='Filtrer par marqueurs pytest (ex: "unit and not slow")')
    parser.add_argument('--durations', type=int, default=10,
                       help='Afficher les N tests les plus lents (défaut: 10)')
    
    return parser


def main():
    """Fonction principale."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Affichage de l'en-tête
    print_header("MangeTaMain - Suite de Tests Unifiée")
    
    runner = TestRunner()
    
    # Modes spéciaux
    if args.clean:
        runner.cleanup_environment()
        return
    
    if args.dev:
        success = runner.run_development_mode()
        sys.exit(0 if success else 1)
    
    if args.coverage:
        success = runner.check_coverage_only()
        sys.exit(0 if success else 1)
    
    # Déterminer le type de test
    if args.unit:
        test_type = "unit"
    elif args.integration:
        test_type = "integration"
    elif args.performance:
        test_type = "performance"
    else:
        test_type = "all"
    
    # Déterminer le runner (Docker vs Python)
    use_docker = False
    if args.docker:
        use_docker = True
        if not runner.is_docker_available:
            print_error("Docker demandé mais non disponible!")
            sys.exit(1)
    elif args.python:
        use_docker = False
        if not runner.is_python_available:
            print_error("Python/pytest demandé mais non disponible!")
            sys.exit(1)
    else:
        # Auto-détection: préférer Docker si disponible
        use_docker = runner.is_docker_available
        if not use_docker and not runner.is_python_available:
            print_error("Ni Docker ni Python/pytest ne sont disponibles!")
            sys.exit(1)
    
    # Afficher la méthode choisie
    method = "Docker Compose" if use_docker else "Python direct"
    print_info(f"Méthode d'exécution: {method}")
    
    # Exécuter les tests
    kwargs = {
        'verbose': args.verbose,
        'build': args.build,
        'no_coverage': args.no_coverage,
        'markers': args.markers,
        'durations': args.durations
    }
    
    if use_docker:
        success = runner.run_docker_tests(test_type, **kwargs)
    else:
        success = runner.run_python_tests(test_type, **kwargs)
    
    # Résultat final
    if success:
        print_success("\n🎉 Tests terminés avec succès!")
        if test_type == "all" and not args.no_coverage:
            print_success("🎯 Objectif de couverture 80% vérifié!")
    else:
        print_error("\n⚠️  Certains tests ont échoué ou couverture insuffisante.")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()