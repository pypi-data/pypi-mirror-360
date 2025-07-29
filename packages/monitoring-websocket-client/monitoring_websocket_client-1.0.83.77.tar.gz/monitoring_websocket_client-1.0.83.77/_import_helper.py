"""
Module d'aide pour garantir l'import de la configuration depuis tout contexte.

Ce module résout les problèmes d'import en ajoutant le répertoire racine
du projet au chemin Python, permettant l'import direct du module config
depuis n'importe quel emplacement dans la hiérarchie du projet.
"""

import os
import sys

# Ajoute le répertoire racine du projet au chemin Python
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Maintenant config peut être importé directement
import config

# Rend tous les attributs de config disponibles globalement
# Cela permet d'utiliser les constantes de configuration comme si elles
# étaient définies directement dans ce module
# Note: Cette approche est utilisée pour simplifier l'import des constantes
# pylint: disable=global-statement
config_dict = getattr(config, '__dict__', {})
globals().update({k: v for k, v in config_dict.items() if not k.startswith('_')})