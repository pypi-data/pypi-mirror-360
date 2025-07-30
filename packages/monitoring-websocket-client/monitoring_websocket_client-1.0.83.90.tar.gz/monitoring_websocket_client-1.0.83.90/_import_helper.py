"""
Module d'aide pour garantir l'import de la configuration depuis tout contexte.

Ce module résout les problèmes d'import en important directement le module config
et en rendant ses attributs disponibles globalement.
"""

import monitoring_config

# Rend tous les attributs de monitoring_config disponibles globalement
# Cela permet d'utiliser les constantes de configuration comme si elles
# étaient définies directement dans ce module
# Note: Cette approche est utilisée pour simplifier l'import des constantes
# pylint: disable=global-statement
config_dict = getattr(monitoring_config, '__dict__', {})
globals().update({k: v for k, v in config_dict.items() if not k.startswith('_')})