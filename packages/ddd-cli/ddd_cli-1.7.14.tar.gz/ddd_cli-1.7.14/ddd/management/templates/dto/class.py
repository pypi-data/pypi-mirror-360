@dataclass
class [[ dto_name.capitalize() ]]Dto:
    """
    Data Transfer Object para [[ dto_name.lower() ]].

    Este DTO se utiliza para transferir datos entre capas del sistema, 
    como entre la capa de dominio y la capa de infraestructura o vistas.
    """

    # Atributos de ID
    id: Optional[int] = None  # ID es opcional al crear un nuevo objeto

    # Atributos del DTO
    attributeName: str  # Atributo obligatorio
    attributeEmail: Optional[str] = None  # Atributo opcional

    def __post_init__(self):
        self.validate()       

    def validate(self) -> None:
        """
        Valida los datos del DTO.
        Transporte y validación básica de datos
        - Validaciones centradas en un conjunto específico de datos (integridad de datos)
        - Ejemplo: campos no nulos, longitud mínima
        """

    def to_dict(self) -> dict:
        """
        Convierte el DTO a un diccionario.
        Ideal para serialización.
        """
        return self.__dict__

    @staticmethod
    def from_dict(data: dict) -> "[[ dto_name.capitalize() ]]Dto":
        """
        Crea una instancia del DTO a partir de un diccionario.
        """
        return [[ dto_name.capitalize() ]]Dto(**data)


    '''Ejemplos de campos adicionales:

    name: str  # Nombre obligatorio
    email: Optional[str] = None  # Email opcional
    external_id: Optional[str] = None  # Identificador externo, o un UUID público
    slug: Optional[str] = None  # Identificador único legible para URLs
    title: str  # Título de la entidad
    content: Optional[str] = None  # Contenido detallado o descripción extensa
    price: Optional[float] = None  # Precio o valor numérico
    quantity: Optional[int] = None  # Cantidad disponible o asociada
    rating: Optional[float] = None  # Valoración media (ej. 4.5 estrellas)
    is_active: bool = True  # Estado activo/inactivo
    is_featured: Optional[bool] = None  # Si es destacado/promocionado
    updated_at: Optional[str] = None  # Fecha de última modificación (ISO 8601)
    deleted_at: Optional[str] = None  # Fecha de eliminación o "soft delete"
    parent_id: Optional[int] = None  # Llave foránea hacia una entidad padre
    owner_id: Optional[int] = None  # Llave foránea hacia el usuario propietario
    tags: Optional[List[str]] = None  # Lista de etiquetas (relación Many-to-Many)
    image: Optional[str] = None  # URL hacia una imagen asociada
    video: Optional[str] = None  # URL hacia un video asociado
    latitude: Optional[float] = None  # Coordenada de latitud
    longitude: Optional[float] = None  # Coordenada de longitud
    location_name: Optional[str] = None  # Nombre del lugar (dirección o ciudad)
    created_by: Optional[int] = None  # Usuario que creó la entidad
    updated_by: Optional[int] = None  # Usuario que actualizó la entidad
    order_status: Optional[str] = None  # Estado de la orden (e.g., "PENDING", "COMPLETED")
    total_price: Optional[float] = None  # Precio total de la orden
    items: Optional[List[Dict]] = None  # Lista de artículos asociados    
        
    '''