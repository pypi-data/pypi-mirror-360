import os
from pathlib import Path

def creer_fichier(chemin, contenu):
    """Crée un fichier avec le contenu spécifié"""
    chemin = Path(chemin)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with open(chemin, 'w', encoding='utf-8') as f:
        f.write(contenu)

def copier_dossier(source, destination):
    """Copie récursivement un dossier"""
    source = Path(source)
    destination = Path(destination)
    
    destination.mkdir(parents=True, exist_ok=True)
    
    for item in source.iterdir():
        dest_item = destination / item.name
        if item.is_dir():
            copier_dossier(item, dest_item)
        else:
            with open(item, 'r', encoding='utf-8') as src_file:
                creer_fichier(dest_item, src_file.read())