"""Classe de base abstraite pour tous les moniteurs système.

Ce module définit l'interface commune que tous les moniteurs doivent
implémenter, ainsi que les fonctionnalités partagées pour la gestion
des erreurs, de l'état et du cycle de vie des moniteurs.

Classes:
    BaseMonitor: Classe abstraite définissant l'interface des moniteurs
"""

import time
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict
from datetime import datetime

from ..core.exceptions import MonitorInitializationError, DataCollectionError


class BaseMonitor(ABC):
    """Classe abstraite de base pour tous les moniteurs système.
    
    Cette classe définit l'interface commune et fournit les fonctionnalités
    de base partagées par tous les moniteurs, incluant la gestion d'état,
    le comptage d'erreurs et le cycle de vie d'initialisation.
    
    Attributes:
        _name: Nom du moniteur
        _initialized: État d'initialisation du moniteur
        _last_update: Timestamp de la dernière collecte de données
        _error_count: Nombre d'erreurs rencontrées
        _max_errors: Nombre maximum d'erreurs autorisées avant défaillance
    
    Methods:
        initialize: Initialise le moniteur
        get_data: Collecte les données avec gestion d'erreur
        reset_errors: Réinitialise le compteur d'erreurs
        is_healthy: Vérifie l'état de santé du moniteur
        get_status: Retourne le statut détaillé
        _do_initialize: Méthode abstraite d'initialisation à implémenter
        _collect_data: Méthode abstraite de collecte à implémenter
    """

    def __init__(self, name: str) -> None:
        """Initialise le moniteur de base.

        Args:
            name: Nom unique identifiant le moniteur.
        """
        self._name: str = name
        self._initialized: bool = False
        self._last_update: Optional[float] = None
        self._error_count: int = 0
        self._max_errors: int = 10

    @property
    def name(self) -> str:
        """Retourne le nom du moniteur.

        Returns:
            str: Nom unique du moniteur.
        """
        return self._name

    @property
    def initialized(self) -> bool:
        """Indique si le moniteur est initialisé.

        Returns:
            bool: True si le moniteur est prêt à collecter des données,
                False sinon.
        """
        return self._initialized

    @property
    def last_update(self) -> Optional[float]:
        """Retourne le timestamp de la dernière mise à jour.

        Returns:
            Optional[float]: Timestamp Unix de la dernière collecte réussie,
                ou None si aucune collecte n'a encore été effectuée.
        """
        return self._last_update

    @property
    def error_count(self) -> int:
        """Retourne le nombre d'erreurs rencontrées.

        Returns:
            int: Nombre total d'erreurs depuis l'initialisation ou la
                dernière réinitialisation.
        """
        return self._error_count

    @property
    def max_errors(self) -> int:
        """Retourne le nombre maximum d'erreurs autorisées.

        Returns:
            int: Seuil d'erreurs au-delà duquel le moniteur est
                considéré comme défaillant.
        """
        return self._max_errors

    @max_errors.setter
    def max_errors(self, value: int) -> None:
        """Définit le nombre maximum d'erreurs autorisées.

        Args:
            value: Nouveau seuil d'erreurs (doit être positif).
            
        Raises:
            ValueError: Si la valeur est négative.
        """
        if value < 0:
            raise ValueError("Le nombre maximum d'erreurs doit être positif")
        self._max_errors = value

    def initialize(self) -> None:
        """Initialise le moniteur.
        
        Appelle la méthode _do_initialize() spécifique à chaque implémentation
        et met à jour l'état interne du moniteur.
        
        Raises:
            MonitorInitializationError: Si l'initialisation échoue.
        """
        try:
            self._do_initialize()
            self._initialized = True
            self._error_count = 0
        except Exception as e:
            raise MonitorInitializationError(f"Erreur lors de l'initialisation du moniteur {self._name}: {e}")

    def get_data(self) -> Any:
        """Récupère les données du moniteur avec gestion d'erreur.

        Initialise automatiquement le moniteur si nécessaire, appelle
        _collect_data() et gère le comptage d'erreurs.

        Returns:
            Any: Données collectées spécifiques à chaque type de moniteur.

        Raises:
            DataCollectionError: Si la collecte échoue ou si le nombre
                maximum d'erreurs est atteint.
        """
        if not self._initialized:
            self.initialize()

        try:
            data = self._collect_data()
            self._last_update = time.time()
            return data
        except Exception as e:
            # Limite error_count avec modulo pour éviter overflow
            self._error_count = (self._error_count + 1) % 1000000
            if self._error_count >= self._max_errors:
                raise DataCollectionError(f"Trop d'erreurs dans le moniteur {self._name} ({self._error_count}): {e}")
            raise DataCollectionError(f"Erreur de collecte dans {self._name}: {e}")

    def reset_errors(self) -> None:
        """Remet à zéro le compteur d'erreurs.
        
        Utile pour réinitialiser un moniteur après une période de
        dysfonctionnement temporaire.
        """
        self._error_count = 0

    def is_healthy(self) -> bool:
        """Vérifie si le moniteur est en bonne santé.

        Un moniteur est considéré sain s'il est initialisé, n'a pas
        dépassé le seuil d'erreurs et a effectué au moins une collecte.

        Returns:
            bool: True si le moniteur fonctionne correctement, False sinon.
        """
        return (self._initialized and 
                self._error_count < self._max_errors and
                self._last_update is not None)

    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut détaillé du moniteur.

        Returns:
            Dict[str, Any]: Dictionnaire contenant le nom, l'état
                d'initialisation, la santé, le nombre d'erreurs et
                les informations de dernière mise à jour.
        """
        return {
            "name": self._name,
            "initialized": self._initialized,
            "healthy": self.is_healthy(),
            "error_count": self._error_count,
            "max_errors": self._max_errors,
            "last_update": self._last_update,
            "last_update_datetime": datetime.fromtimestamp(self._last_update) if self._last_update else None
        }

    @abstractmethod
    def _do_initialize(self) -> None:
        """Méthode d'initialisation spécifique à implémenter.
        
        Cette méthode doit être implémentée par chaque moniteur concret
        pour effectuer son initialisation spécifique.
        
        Raises:
            Exception: En cas d'erreur pendant l'initialisation.
        """
        pass

    @abstractmethod
    def _collect_data(self) -> Any:
        """Méthode de collecte de données spécifique à implémenter.

        Cette méthode doit être implémentée par chaque moniteur concret
        pour collecter ses données spécifiques.

        Returns:
            Any: Données collectées dans le format approprié au moniteur.

        Raises:
            Exception: En cas d'erreur pendant la collecte de données.
        """
        pass

    def __str__(self) -> str:
        """Retourne une représentation textuelle du moniteur.

        Returns:
            str: Chaîne descriptive incluant le type, le nom et l'état
                de santé du moniteur.
        """
        return f"{self.__class__.__name__}(name='{self._name}', healthy={self.is_healthy()})"

    def __repr__(self) -> str:
        """Retourne une représentation technique du moniteur.

        Returns:
            str: Chaîne technique incluant le type, le nom, l'état
                d'initialisation et le nombre d'erreurs.
        """
        return (f"{self.__class__.__name__}(name='{self._name}', "
                f"initialized={self._initialized}, errors={self._error_count})")
