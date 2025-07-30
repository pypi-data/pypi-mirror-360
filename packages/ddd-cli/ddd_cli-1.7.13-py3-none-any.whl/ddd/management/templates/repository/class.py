from typing import List, Optional
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.forms import ValidationError

# importa las entidades utilizadas aqui
from ..models import [[ entity_name.capitalize() ]]
from .mappers import Mapper
from ..domain.entities import [[ entity_name.capitalize() ]]Entity
from ..domain.exceptions import EntityNotFoundError


class [[ entity_name.capitalize() ]]Repository:
    """
    Repositorio para manejar la persistencia de datos de la entidad: [[ entity_name.lower() ]].
    
    Este repositorio incluye:
    - Validación de existencia de registros.
    - Control de unicidad.
    - Métodos básicos.
    """

    @staticmethod
    def get_all(filters: Optional[dict] = None) -> List[ [[ entity_name.capitalize() ]]Entity ]:
        """
        Obtiene todos los registros de la entidad.
        :return: Lista de registros de la entidad.
        """

        instance_list = [[ entity_name.capitalize() ]].objects.all()    

        # Aplicar filtros si se proporcionan
        if filters:
            if "nombre" in filters and filters["nombre"] != "":
                instance_list = instance_list.filter(nombre__icontains=filters["nombre"])        

        # Convertir a entidades usando el Mapper genérico
        return [Mapper.model_to_entity(instance, [[ entity_name.capitalize() ]]Entity) for instance in instance_list]        


    @staticmethod
    def get_by_id(id) -> Optional[ [[ entity_name.capitalize() ]]Entity ]:
        """
        Obtiene un registro por su ID.
        
        :param id: ID del registro a recuperar.
        :return: El entidad encontrada o None si no existe.
        """

        try:
            instance = [[ entity_name.capitalize() ]].objects.get(id=id)
            return Mapper.model_to_entity(instance, [[ entity_name.capitalize() ]]Entity)

        except [[ entity_name.capitalize() ]].DoesNotExist:
            return None


    @staticmethod
    def exists_by_field(field_name, value) -> bool:
        """
        Verifica si existe un registro con un valor específico para un campo dado.

        :param field_name: Nombre del campo a buscar.
        :param value: Valor del campo a verificar.
        :return: True si existe un registro con el valor dado, False en caso contrario.
        """

        return [[ entity_name.capitalize() ]].objects.filter(**{field_name: value}).exists()


    @staticmethod
    def count_all(filters: Optional[dict] = None) -> int:
        """
        Cuenta registros que cumplen con ciertas condiciones.

        :param conditions: Condiciones de filtro como clave-valor.
        :return: Número de registros que cumplen las condiciones.
        """

        instance_list = [[ entity_name.capitalize() ]].objects.all()    

        # Aplicar filtros si se proporcionan
        if filters:
            if "nombre" in filters and filters["nombre"] != "":
                instance_list = instance_list.filter(nombre__icontains=filters["nombre"])            

        return instance_list.count()            


    @staticmethod
    def create(entity: [[ entity_name.capitalize() ]]Entity, parent_id: Optional[int]) -> [[ entity_name.capitalize() ]]Entity:
        """
        Crea un nuevo registro.

        :param entity: Entidad con los datos necesarios para crear el registro.
        :param parent_id: ID del padre si es necesario (opcional).
        :return: La entidad creada.
        :raises ValueError: Si los datos no son válidos.
        """
        #convertir a dict
        data = entity.to_dict()        

        # Eliminar las claves 'id' y 'uuid' si existen en el diccionario
        data.pop('id', None)
        data.pop('uuid', None)        

        # Si se proporciona un ID de otra entidad, agregarlo al diccionario
        # django crea el campo 'parent_id' automáticamente si la relación es ForeignKey => otherEntity
        if parent_id is not None:
            data['parent_id'] = parent_id

        # Crear el registro
        instance = [[ entity_name.capitalize() ]](**data)

        # Validar y guardar
        try:
            instance.full_clean()  # Validaciones del modelo
            instance.save()

        except ValueError as e:
            raise ValueError(f"An error occurred while processing the value: {e}")
        
        return Mapper.model_to_entity(instance, [[ entity_name.capitalize() ]]Entity)


    @staticmethod
    def save(entity: [[ entity_name.capitalize() ]]Entity) -> [[ entity_name.capitalize() ]]Entity:
        """
        Guarda los cambios en una entidad existente.

        :param entity: Entidad con los datos a actualizar (debe traer el id en los campos).
        :return: La entidad guardada.
        :raises EntityNotFoundError: Si no existe el registro con el ID dado.
        :raises ValueError: Si los datos no son válidos.
        """

        try:
            # Recuperar el modelo existente basado en el ID de la entidad
            instance = [[ entity_name.capitalize() ]].objects.get(id=entity.id)

            # Actualizar cada campo de la entidad en el modelo
            for key, value in entity.to_dict().items():
                if hasattr(instance, key):
                    if key != 'id' and key != 'uuid': # No actualizar campos especiales
                        # Los campos especiales son aquellos que nunca cambian como: id, uuid, created_at, updated_at, etc.
                        # o aquellos que tienen una forma especial de ser guardados como: photo, password, etc.
                        setattr(instance, key, value)

            # Validar y guardar
            instance.full_clean()  # Validaciones del modelo Django
            instance.save()
            
            # Convertir el modelo actualizado de vuelta a una entidad
            return Mapper.model_to_entity(instance, [[ entity_name.capitalize() ]]Entity)

        except [[ entity_name.capitalize() ]].DoesNotExist:
            raise EntityNotFoundError(f"No [[ entity_name.lower() ]] found with ID {id}")

        except ValidationError as e:
            raise ValueError(f"Validation error occurred: {e.message_dict}")


    @staticmethod
    def delete(id) -> bool:
        """
        Elimina un registro por su ID.

        :param id: ID del registro a eliminar.
        :raises EntityNotFoundError: Si no existe el registro con el ID dado.
        """

        try:
            instance = [[ entity_name.capitalize() ]].objects.get(id=id)
            instance.delete()
            return True

        except [[ entity_name.capitalize() ]].DoesNotExist:
            raise EntityNotFoundError(f"No [[ entity_name.lower() ]] found with ID {id}")


