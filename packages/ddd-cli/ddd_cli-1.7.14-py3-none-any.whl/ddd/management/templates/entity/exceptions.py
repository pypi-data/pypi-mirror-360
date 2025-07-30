# domain/exceptions.py

class EntityNotFoundError(Exception):
    """Excepción personalizada para cuando una entidad no es encontrada"""
    def __init__(self, entity_name: str, entity_id: int):
        self.entity_name = entity_name
        self.entity_id = entity_id
        super().__init__(f"{entity_name} with ID {entity_id} was not found")