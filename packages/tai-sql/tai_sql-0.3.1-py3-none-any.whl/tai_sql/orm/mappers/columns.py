# -*- coding: utf-8 -*-
"""
Declarative models for SQLAlchemy.
This module provides the base classes and utilities to define
models using SQLAlchemy's declarative system.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import (
    Any,
    List,
    Dict,
    Optional,
    Union,
    TYPE_CHECKING,
)
from enum import Enum

from sqlalchemy import (
    Integer, String, Text, Boolean, DateTime, 
    Date, Time, Float, Numeric, LargeBinary,
    BigInteger,
    Column as SQLAlchemyColumn,
    Enum as SQLAlchemyEnum
)

if TYPE_CHECKING:
    from .table import Table


@dataclass
class Column:
    # Valores por defecto de la clase (definido primero)
    _DEFAULT_VALUES = {
        'primary_key': False,
        'unique': False,
        'default': None,
        'index': False,
        'autoincrement': False
    }
    
    # Atributos que obtienen sus valores del diccionario
    name: str = None
    type: Any = None
    user_defined_sqlalchemy_type: Any = None
    model: Optional[Table] = None
    options: Optional[List[Any]] = None
    nullable: bool = False
    is_foreign_key: bool = False
    server_now: bool = False
    encrypt: bool = False
    primary_key: bool = field(default_factory=lambda: Column._DEFAULT_VALUES['primary_key'])
    unique: bool = field(default_factory=lambda: Column._DEFAULT_VALUES['unique'])
    default: Any = field(default_factory=lambda: Column._DEFAULT_VALUES['default'])
    index: bool = field(default_factory=lambda: Column._DEFAULT_VALUES['index'])
    autoincrement: bool = field(default_factory=lambda: Column._DEFAULT_VALUES['autoincrement'])
    
    def info(self) -> Dict[str, Any]:
        """
        Devuelve un diccionario con la información de la columna.
        """
        return {
            'name': self.name,
            'type': self.type,
            'user_defined_sqlalchemy_type': self.user_defined_sqlalchemy_type,
            'options': self.options,
            'nullable': self.nullable,
            'is_foreign_key': self.is_foreign_key,
            'default': self.args.get('default', self.default),
            'encrypt': self.encrypt,
            'args': self.args,
            'no_args': self.no_args
        }
    
    @property
    def sqlalchemy_type_mapping(self) -> Dict[str, Any]:
        return {
            'int': Integer,
            'BigInteger': BigInteger,
            'str': String,
            'bool': Boolean,
            'datetime': DateTime,
            'date': Date,
            'time': Time,
            'float': Float,
            'Numeric': Numeric,
            'LargeBinary': LargeBinary,
            'Enum': SQLAlchemyEnum,
        }
    
    def to_sqlalchemy_column(self) -> SQLAlchemyColumn:
        """Convierte la definición de columna a SQLAlchemy Column"""
       
        # Obtener tipo SQLAlchemy
        sqlalchemy_type = self.sqlalchemy_type_mapping.get(self.type)

        if sqlalchemy_type is None:
            raise ValueError(f"Tipo de dato '{self.type}' no soportado para la columna '{self.name}'")
        
        if self.server_now:
            from sqlalchemy.sql.functions import now
            server_default = now()
        else:
            server_default = None

        # Crear columna SQLAlchemy
        return SQLAlchemyColumn(
            self.name,
            sqlalchemy_type,
            nullable=self.nullable,
            **self.args,
            server_default=server_default
        )

    @property
    def no_args(self) -> bool:
        """
        Verifica si la columna se puede definir solo con su tipo de dato.
        
        Returns:
            bool: True si es una columna simple, False en caso contrario
        """
        return all(getattr(self, attr) == default for attr, default in self._DEFAULT_VALUES.items())

    @property
    def args(self) -> Dict[str, Union[str, bool, Any]]:
        """
        Devuelve un diccionario con los argumentos de la columna que son
        diferentes de los valores por defecto.
        """
        args = {}
        
        # Comparar con los valores por defecto y añadir solo los diferentes
        for attr_name, default_value in self._DEFAULT_VALUES.items():
            
            current_value = getattr(self, attr_name)
            
            if current_value != default_value:
                # Manejar casos especiales para el valor por defecto
                if attr_name == 'default' and current_value is not None:
                    # Manejar datetime.now especialmente
                    if isinstance(current_value, Enum):
                        args[attr_name] = current_value.value

                    elif hasattr(current_value, '__name__') and current_value.__name__ == 'now':
                        if hasattr(current_value, '__self__') and current_value.__self__.__name__ == 'datetime':
                            args[attr_name] = 'datetime.now'
                        else:
                            args[attr_name] = str(current_value)
                    else:
                        args[attr_name] = current_value
                else:
                    args[attr_name] = current_value
            
            args['autoincrement'] = self.autoincrement

        return args
    
    def save(self) -> None:
        """
        Guarda la columna en el modelo.
        Esta función se utiliza para registrar la columna en el modelo
        y establecer las propiedades necesarias.
        """
        if self.model is None:
            raise ValueError("El modelo de la columna no puede ser None")
        
        if self.name in (None, ''):
            raise ValueError("El nombre de la columna no puede ser None o vacío")
        
        if self.type is None:
            raise ValueError("El tipo de la columna no puede ser None")
        
        self.model.columns[self.name] = self

        if getattr(self.model, self.name, None) is None:
            setattr(self.model, self.name, self)

def column(
    primary_key=False,
    unique=False,
    default=None,
    server_now=False,
    index=False,
    autoincrement=False,
    encrypt=False
):
    """
    Configurador para añadir metadatos a las columnas definidas por tipado.
    
    Ejemplo:
        id: int = column(primary_key=True, autoincrement=True)
        name: str = column(length=100)
        password: str = column(encrypt=True)
    """
    return Column(
        primary_key=primary_key,
        unique=unique,
        default=default,
        server_now=server_now,
        index=index,
        autoincrement=autoincrement,
        encrypt=encrypt
    )
