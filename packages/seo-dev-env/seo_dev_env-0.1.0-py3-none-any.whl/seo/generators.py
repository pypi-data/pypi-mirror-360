import os
import subprocess
import sys
import shutil
from pathlib import Path
from .utils import creer_fichier, copier_dossier

class EnvironnementGenerator:
    """Classe de base pour générer des environnements"""
    
    def __init__(self, niveau: str, type_app: str, chemin: str):
        self.niveau = niveau
        self.type_app = type_app
        self.chemin_projet = Path(chemin).resolve()
        self.packages = []
        self.template_dir = Path(__file__).parent / 'templates' / niveau
        
    def _installer_dependances(self):
        """Installe les packages nécessaires"""
        if self.packages:
            print(f"🔧 Installation des packages: {', '.join(self.packages)}")
            subprocess.run([sys.executable, '-m', 'pip', 'install'] + self.packages)
        
    def _copier_template(self):
        """Copie les fichiers du template"""
        if self.template_dir.exists():
            copier_dossier(self.template_dir, self.chemin_projet)
        else:
            print(f"⚠️ Avertissement: Template {self.niveau} non trouvé, création de base")
            self._creer_structure_base()
    
    def _creer_structure_base(self):
        """Crée une structure de base si le template est manquant"""
        creer_fichier(self.chemin_projet / 'app.py', "# Votre application Flask")
        (self.chemin_projet / 'templates').mkdir(exist_ok=True)
        creer_fichier(self.chemin_projet / 'templates/index.html', "<h1>Bienvenue</h1>")
        
    def _post_creation(self):
        """Actions supplémentaires après création"""
        pass
        
    def generer(self):
        """Méthode principale pour générer l'environnement"""
        self.chemin_projet.mkdir(exist_ok=True, parents=True)
        print(f"🏗️ Création de l'environnement {self.niveau} ({self.type_app})...")
        
        self._copier_template()
        self._creer_structure()
        self._installer_dependances()
        self._post_creation()
        
        print(f"✅ Environnement créé avec succès dans {self.chemin_projet}")
        print("👉 Pour démarrer: cd " + str(self.chemin_projet))

class DebutantWebGenerator(EnvironnementGenerator):
    """Générateur pour débutants - Site web simple"""
    
    def __init__(self, chemin):
        super().__init__('debutant', 'web', chemin)
        self.packages = ['flask', 'python-dotenv']
    
    def _creer_structure(self):
        # Personnalisation supplémentaire
        creer_fichier(
            self.chemin_projet / 'README.md',
            f"# Mon Premier Projet Flask\n\nCe projet a été créé avec SEO pour les débutants!"
        )

class IntermediaireWebGenerator(EnvironnementGenerator):
    """Générateur intermédiaire - Applications web complètes"""
    
    def __init__(self, chemin):
        super().__init__('intermediaire', 'web', chemin)
        self.packages = [
            'flask',
            'flask-sqlalchemy',
            'flask-wtf',
            'flask-login',
            'flask-migrate',
            'python-dotenv'
        ]
    
    def _creer_structure(self):
        # Création de la base de données
        db_path = self.chemin_projet / 'app.db'
        if not db_path.exists():
            with open(db_path, 'w') as f:
                f.write("")
        
        # Création du fichier requirements
        creer_fichier(
            self.chemin_projet / 'requirements.txt',
            "\n".join(self.packages)
        )

class ProWebGenerator(EnvironnementGenerator):
    """Générateur pro - Applications professionnelles"""
    
    def __init__(self, chemin):
        super().__init__('pro', 'web', chemin)
        self.packages = [
            'flask',
            'flask-restx',
            'flask-cors',
            'flask-sqlalchemy',
            'flask-migrate',
            'flask-jwt-extended',
            'python-dotenv',
            'gunicorn',
            'psycopg2-binary'
        ]
    
    def _post_creation(self):
        # Initialiser un dépôt Git
        try:
            subprocess.run(['git', 'init', str(self.chemin_projet)], check=True)
            print("📦 Dépôt Git initialisé")
        except:
            print("⚠️ Git non installé, ignore l'initialisation du dépôt")

# Interface simplifiée
def creer_environnement(niveau, type_app='web', chemin='.'):
    """
    Crée un environnement de développement adapté
    
    Args:
        niveau: 'debutant', 'intermediaire' ou 'pro'
        type_app: 'web' ou 'mobile' (défaut: 'web')
        chemin: Chemin où créer le projet (défaut: dossier actuel)
    """
    generators = {
        'debutant': DebutantWebGenerator,
        'intermediaire': IntermediaireWebGenerator,
        'pro': ProWebGenerator
    }
    
    if niveau not in generators:
        raise ValueError(f"🚫 Niveau non supporté: {niveau}")
    
    generator = generators[niveau](chemin)
    generator.generer()
    
    # Ajout des instructions spécifiques
    if niveau == 'debutant':
        print("\n🚀 Pour démarrer votre application:")
        print(f"cd {chemin}")
        print("python app.py")
    elif niveau == 'intermediaire':
        print("\n🚀 Pour initialiser la base de données:")
        print(f"cd {chemin}")
        print("flask db init")
        print("flask db migrate")
        print("flask db upgrade")
        print("flask run")
    else:
        print("\n🚀 Pour démarrer avec Docker:")
        print(f"cd {chemin}")
        print("docker-compose up --build")

# Alias pour une utilisation plus simple
creer_projet = creer_environnement