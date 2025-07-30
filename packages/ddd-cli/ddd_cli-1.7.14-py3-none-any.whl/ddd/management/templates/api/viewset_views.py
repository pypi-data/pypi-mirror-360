from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.permissions import IsAuthenticated

# importar serializers
from serializers import [[ entity_name.capitalize() ]]Serializer

# importar excepciones especificas de dominio
from [[ app_name.lower() ]].domain.exceptions import EntityNotFoundError

# importar servicios específicos del dominio
from [[ app_name.lower() ]].domain.services import (
    list_[[ entity_name.lower() ]],
    create_[[ entity_name.lower() ]],
    retrieve_[[ entity_name.lower() ]],
    update_[[ entity_name.lower() ]],
    delete_[[ entity_name.lower() ]],
)

# Importar repositorios específicos de la infraestructura
from [[ app_name.lower() ]].infrastructure.[[ entity_name.lower() ]]_repository import [[ entity_name.capitalize() ]]Repository

class [[ entity_name.capitalize() ]]ViewSet(ViewSet):
    """
    ViewSet para manejar operaciones CRUD relacionadas con [[ entity_name.lower() ]].
    
    Este ViewSet interactúa con:
    - Los servicios del dominio para manejar la lógica de negocio.
    - Los repositorios para acceder a la capa de persistencia.
    """

    # Definición de permisos y autenticación
    # permission_classes = [IsAuthenticated]
    # authentication_classes = [TokenAuthentication]

    # Definición de métodos HTTP permitidos
    # http_method_names = ['get', 'post', 'put', 'delete']


    @swagger_auto_schema(
        operation_summary="Retrieve a list or a specific [[ entity_name.lower() ]]",
        operation_description="Retrieve a list of all [[ entity_name.lower() ]] or a specific one by ID",
        responses={
            200: [[ entity_name.capitalize() ]]Serializer,
            404: "Not Found",
            400: "Bad Request"
        },
        tags=["[[ entity_name.lower() ]]"]
    )
    def list(self, request):
        """
        Endpoint para obtener una lista de todos los [[ entity_name.lower() ]].
        
        - Se valida y adapta la solicitud.
        - Se utiliza el servicio `list_[[ entity_name.lower() ]]` para manejar la lógica.
        """
        try:
            # Llamar al servicio para recuperar todos los registros
            repository = [[ entity_name.capitalize() ]]Repository()
            [[ entity_name.lower() ]]List = list_[[ entity_name.lower() ]](repository=repository)

            # Serializar la lista de registros
            response_serializer_list = [[ entity_name.capitalize() ]]Serializer([[ entity_name.lower() ]]List, many=True)
            response_serializer_list.is_valid(raise_exception=True)            

            # Retornar los datos serializados con un estado HTTP 200 OK
            return Response(response_serializer_list.data, status=status.HTTP_200_OK)

        except (ValueError, EntityNotFoundError) as e:
            # Manejar errores de lógica de negocio
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)


    @swagger_auto_schema(
        operation_summary="Retrieve a specific [[ entity_name.lower() ]] by ID",
        operation_description="Retrieve a specific [[ entity_name.lower() ]] by its ID",
        responses={
            200: [[ entity_name.capitalize() ]]Serializer,
            404: "Not Found",
            400: "Bad Request"
        },
        tags=["[[ entity_name.lower() ]]"]
    )
    def retrieve(self, request, pk=None):
        """
        Endpoint para obtener un [[ entity_name.lower() ]] específico por su ID (pk).
        
        - Valida y adapta la solicitud al dominio.
        - Utiliza el servicio `retrieve_[[ entity_name.lower() ]]` para manejar la lógica.
        """
        try:
            # Llamar al servicio para recuperar un registro específico
            repository = [[ entity_name.capitalize() ]]Repository()
            [[ entity_name.lower() ]] = retrieve_[[ entity_name.lower() ]](repository=repository, entity_id=pk)

            # Serializar el registro recuperado
            response_serializer = [[ entity_name.capitalize() ]]Serializer([[ entity_name.lower() ]])
            response_serializer.is_valid(raise_exception=True)            

            # Retornar el resultado con un estado HTTP 200 OK
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except (ValueError, EntityNotFoundError) as e:
            # Manejar errores si el registro no existe
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)


    @swagger_auto_schema(
        operation_summary="Create a new [[ entity_name.lower() ]]",
        operation_description="Create a new [[ entity_name.lower() ]] with the provided data",
        request_body=[[ entity_name.capitalize() ]]Serializer,
        responses={
            201: [[ entity_name.capitalize() ]]Serializer,
            400: "Bad Request"
        },
        tags=["[[ entity_name.lower() ]]"]
    )
    def create(self, request):
        """
        Endpoint para crear un nuevo [[ entity_name.lower() ]].
        
        - Valida y adapta los datos entrantes.
        - Llama al servicio `create_[[ entity_name.lower() ]]` para manejar la creación.
        """
        
        # Datos enviados en el cuerpo de la solicitud
        serializer = [[ entity_name.capitalize() ]]Serializer(data=request.data)
        if not serializer.is_valid():
            # Si la validación falla, retornar un error 400 BAD REQUEST
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Obtener el ID de la entidad relacionada si existe
        parent_id = request.data.get('parent_id', None)

        try:
            # Llamar al servicio para crear el registro
            repository = [[ entity_name.capitalize() ]]Repository()
            [[ entity_name.lower() ]] = create_[[ entity_name.lower() ]](repository=repository, parent_id=parent_id,data=serializer.validated_data)

            # Serializar el nuevo registro creado
            response_serializer = [[ entity_name.capitalize() ]]Serializer([[ entity_name.lower() ]])
            response_serializer.is_valid(raise_exception=True)            

            # Retornar el resultado con un estado HTTP 201 CREATED
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except (ValueError, EntityNotFoundError) as e:
            # Manejar errores en las reglas de negocio o validación
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(
        operation_summary="Update an existing [[ entity_name.lower() ]]",
        operation_description="Update an existing [[ entity_name.lower() ]] with the provided ID and data",
        request_body=[[ entity_name.capitalize() ]]Serializer,
        responses={
            200: [[ entity_name.capitalize() ]]Serializer,
            400: "Bad Request",
            404: "Not Found"
        },
        tags=["[[ entity_name.lower() ]]"]
    )
    def update(self, request, pk=None):
        """
        Endpoint para actualizar un [[ entity_name.lower() ]] existente.
        
        - Valida y adapta los datos entrantes.
        - Llama al servicio `update_[[ entity_name.lower() ]]` para manejar la actualización.
        """

        # Datos enviados en el cuerpo de la solicitud
        serializer = [[ entity_name.capitalize() ]]Serializer(data=request.data) 
        if not serializer.is_valid():
            # Si la validación falla, retornar un error 400 BAD REQUEST
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Llamar al servicio para actualizar el registro
            repository = [[ entity_name.capitalize() ]]Repository()
            [[ entity_name.lower() ]] = update_[[ entity_name.lower() ]](repository=repository, entity_id=pk, data=serializer.validated_data)

            # Serializar el registro actualizado
            response_serializer = [[ entity_name.capitalize() ]]Serializer([[ entity_name.lower() ]])
            response_serializer.is_valid(raise_exception=True)            

            # Retornar el resultado con un estado HTTP 200 OK
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except (ValueError, EntityNotFoundError) as e:
            # Manejar errores en las reglas de negocio o validación
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(
        operation_summary="Delete an existing [[ entity_name.lower() ]]",
        operation_description="Delete an existing [[ entity_name.lower() ]] with the provided ID",
        responses={
            204: "No Content",
            400: "Bad Request",
            404: "Not Found"
        },
        tags=["[[ entity_name.lower() ]]"]
    )
    def destroy(self, request, pk=None):
        """
        Endpoint para eliminar un [[ entity_name.lower() ]] existente.
        
        - Valida y adapta la solicitud.
        - Llama al servicio `delete_[[ entity_name.lower() ]]` para manejar la eliminación.
        """
        try:
            # Llamar al servicio para eliminar el registro
            repository = [[ entity_name.capitalize() ]]Repository()
            [[ entity_name.lower() ]] = delete_[[ entity_name.lower() ]](repository=repository, entity_id=pk)

            # Retornar un estado HTTP 204 NO CONTENT para confirmar la eliminación
            return Response(status=status.HTTP_204_NO_CONTENT)

        except (ValueError, EntityNotFoundError) as e:
            # Manejar errores si el registro no existe o no se puede eliminar
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

