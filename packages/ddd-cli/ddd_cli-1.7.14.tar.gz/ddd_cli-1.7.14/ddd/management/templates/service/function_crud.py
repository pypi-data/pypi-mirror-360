
def list_[[ entity_name.lower() ]](repository: [[ entity_name.capitalize() ]]Repository, filters: Optional[dict] = None) -> List[dict]:
    """
    Lista instancias de [[ entity_name.lower() ]].

    :param repository: Repositorio que maneja la persistencia de [[ entity_name.lower() ]].
    :return: Lista de la entidad.
    :raises ValueError: Si las reglas de negocio no se cumplen.
    """

    entity_list = repository.get_all(filters)

    return [entity.to_dict() for entity in entity_list]  


def create_[[ entity_name.lower() ]](repository: [[ entity_name.capitalize() ]]Repository, parent_id: Optional[int], data) -> dict:
    """
    Crea una nueva instancia de [[ entity_name.lower() ]].

    :param repository: Repositorio que maneja la persistencia de [[ entity_name.lower() ]].
    :param data: Diccionario o DTO con los datos necesarios para crear la instancia.
    :return: La entidad creada.
    :raises ValueError: Si las reglas de negocio no se cumplen.
    """
    # Validación de reglas de negocio (opcional)
    if repository.exists_by_field("attributeName", data['attributeName']):
        raise ValueError("An instance with this attributeName already exists")

    #crear y validar la entidad
    entity = [[ entity_name.capitalize() ]]Entity.from_dict(data)
    entity.validate()

    # Guardar en el repositorio
    saved_entity = repository.create(entity=entity, parent_id=parent_id)

    return saved_entity.to_dict()


def retrieve_[[ entity_name.lower() ]](repository: [[ entity_name.capitalize() ]]Repository, entity_id: int) -> dict:
    """
    Recupera una instancia de [[ entity_name.lower() ]] por su ID.

    :param repository: Repositorio que maneja la persistencia de [[ entity_name.lower() ]].
    :param entity_id: ID de la instancia a recuperar.
    :return: La entidad recuperada.
    :raises ValueError: Si no se encuentra la instancia.
    """
    entity = repository.get_by_id(entity_id)
    if not entity:
        raise ValueError(f"No [[ entity_name.lower() ]] found with ID {entity_id}")

    return entity.to_dict()


def update_[[ entity_name.lower() ]](repository: [[ entity_name.capitalize() ]]Repository, entity_id: int, data) -> dict:
    """
    Actualiza una instancia existente de [[ entity_name.lower() ]].

    :param repository: Repositorio que maneja la persistencia de [[ entity_name.lower() ]].
    :param entity_id: ID de la instancia a actualizar.
    :param data: Diccionario o DTO con los datos a actualizar.
    :return: La entidad actualizada.
    :raises ValueError: Si no se encuentra la instancia o las reglas de negocio no se cumplen.
    """
    # Recuperar la entidad
    entity = repository.get_by_id(entity_id)
    if not entity:
        raise ValueError(f"No [[ entity_name.lower() ]] found with ID {entity_id}")

    # actualizar la instancia y validar
    entity.update(data)     
    entity.validate()   

    # Guardar en el repositorio
    updated_entity = repository.save(entity)
    
    return updated_entity.to_dict()


def delete_[[ entity_name.lower() ]](repository: [[ entity_name.capitalize() ]]Repository, entity_id: int) -> bool:
    """
    Elimina una instancia de [[ entity_name.lower() ]].

    :param repository: Repositorio que maneja la persistencia de [[ entity_name.lower() ]].
    :param entity_id: ID de la instancia a eliminar.
    :return: True/False (depende del exito de la operacion)
    :raises ValueError: Si no se encuentra la instancia.
    """
    # Recuperar la entidad
    entity = repository.get_by_id(entity_id)
    if not entity:
        raise ValueError(f"No [[ entity_name.lower() ]] found with ID {entity_id}")

    # Eliminación en el repositorio
    repository.delete(entity_id)

    return True