from __future__ import annotations
from typing import Any, Dict, ClassVar, List, Type
from enum import Enum as BaseEnum, EnumMeta
from tai_sql import pm


class EnumRegistryMeta(EnumMeta):
    """
    Metaclass que registra automáticamente los Enums cuando se crean.
    """
    
    # Registro global de todos los Enums definidos
    registry: ClassVar[List[Type[BaseEnum]]] = []
    
    def __new__(metacls, name, bases, namespace, **kwargs):
        # Crear la clase Enum normalmente
        enum_class = super().__new__(metacls, name, bases, namespace, **kwargs)
        
        # Solo registrar si es una subclase de Enum y no es la clase base
        if (issubclass(enum_class, BaseEnum) and 
            enum_class is not BaseEnum and 
            name != 'Enum'):  # Evitar registrar nuestra clase base
            
            EnumRegistryMeta.registry.append(enum_class)
            print(f"✅ Enum registrado: {enum_class.__name__}")
        
        return enum_class


class Enum(BaseEnum, metaclass=EnumRegistryMeta):
    """
    Clase base para definir enumeraciones que serán utilizadas en columnas de base de datos.
    Los Enums se registran automáticamente al definirlos.
    """
    
    @classmethod
    def get_registered_enums(cls) -> List[Type[BaseEnum]]:
        """
        Obtiene todos los Enums registrados.
        
        Returns:
            List[Type[BaseEnum]]: Lista de clases Enum registradas
        """
        return EnumRegistryMeta.registry.copy()
    
    @classmethod
    def clear_registry(cls) -> None:
        """
        Limpia el registro de Enums (útil para testing).
        """
        EnumRegistryMeta.registry.clear()
    
    @classmethod
    def info(cls) -> Dict[str, Any]:
        """
        Obtiene información sobre el Enum.
        
        Returns:
            Dict[str, Any]: Información del Enum
        """
        return {
            'name': cls.__name__.lower(),
            'values': [item.value for item in cls]
        }