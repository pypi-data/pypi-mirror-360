# utils/mappers.py
from dataclasses import asdict, fields
from typing import Type, TypeVar, Any
from django.db import models

T = TypeVar("T")

class Mapper:
    
    @staticmethod
    def model_to_entity(model_instance: models.Model, entity_class: Type[T]) -> T:
        """
        Convierte una instancia de modelo Django a una entidad basada solo en los campos de la entidad.

        Conversión según el tipo de propiedad de Django Model:
            CharField -> (str).
            TextField -> (str).
            IntegerField -> (int).
            FloatField -> (float)
            BooleanField -> (bool)
            DateField -> (datetime.date)
            DateTimeField -> (datetime.time)
            ForeignKey -> (int/str)
            ManyToManyField -> lista o Queryset de objetos
            DecimalField -> (decimal.Decimal)
            UUIDField -> uuid.UUID
            JSONField -> (dict o list)
            FileField o ImageField -> ruta de archivo(str)
            EmailField -> (str)
            SlugField -> (str)
            AutoField (ID auto-generado) -> (int)
        """

        # Obtener los nombres de los campos definidos en la entidad
        entity_fields = {field.name for field in fields(entity_class)}

        # Crear un diccionario filtrado solo con los campos de la entidad
        data = {field: getattr(model_instance, field) for field in entity_fields if hasattr(model_instance, field)}
        
        # Crear y devolver la entidad usando los datos filtrados
        return entity_class(**data)
    
    @staticmethod
    def entity_to_dict(entity_instance: Any) -> dict:
        """Convierte una entidad en un diccionario que contiene solo sus propios campos"""
        # Convertir la entidad a diccionario directamente con asdict (solo los campos de la entidad)
        return asdict(entity_instance)
    
    @staticmethod
    def model_to_dict(model_instance: models.Model) -> dict:
        """Convierte una instancia de modelo Django en un diccionario que contiene solo sus propios campos"""
        # Convertir la instancia de modelo a diccionario directamente con asdict (solo los campos del modelo)
        return asdict(model_instance)
    
