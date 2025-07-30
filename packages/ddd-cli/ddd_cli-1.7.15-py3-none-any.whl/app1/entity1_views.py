
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse

# Importar excepciones específicas de dominio
from app1.domain.exceptions import EntityNotFoundError

# Importar formularios específicos de la entidad
from app1.entity1_forms import Entity1CreateForm, Entity1EditGetForm, Entity1EditPostForm, Entity1ViewForm

# Importar servicios específicos del dominio
from app1.domain.services import (
    list_entity1,
    create_entity1,
    retrieve_entity1,
    update_entity1,
    delete_entity1,
)

# Importar repositorios específicos de la infraestructura
from app1.infrastructure.entity1_repository import Entity1Repository


def entity1_list(request):
    """
    Vista genérica para mostrar una lista de todas las instancias de entity1.
    """

    entity1List = [] #inicialize list

    # Obtener la lista del repositorio
    try:
        repository = Entity1Repository()
        entity1List = list_entity1(repository=repository)

    except (ValueError, EntityNotFoundError) as e:
        # Manejo de errores específicos del dominio
        messages.error(request,  str(e))

    # Renderizar la plantilla con la lista
    return render(request, 'app1/entity1_web_list.html', {
        'entity1List': entity1List
    })


def entity1_create(request):
    """
    Vista genérica para crear una nueva instancia de entity1 utilizando un servicio.
    """

    if request.method == "POST":

        # Validar los datos del formulario
        form = Entity1CreateForm(request.POST)

        if form.is_valid():
            form_data = form.cleaned_data
            repository = Entity1Repository()

            # Obtener el ID de la entidad relacionada si existe
            external_id = request.POST.get('external_id', None)

            try:
                # LLamar al servicio de creación
                create_entity1(repository=repository, external_id=external_id, data=form_data)

                # Mostrar mensaje de éxito y redirigir
                messages.success(request, f"Successfully created entity1")
                return redirect('app1:entity1_list')

            except (ValueError, EntityNotFoundError) as e:
                # Manejar errores específicos del dominio
                form.add_error(None, str(e))
        else:
            messages.error(request, "There were errors in the form. Please correct them")
    else:
        # Formulario vacío para solicitudes GET
        form = Entity1CreateForm()

    # Renderizar la plantilla con el formulario
    return render(request, 'app1/entity1_web_create.html', {'form': form}) 


def entity1_edit(request, id=None):
    """
    Vista genérica para editar una instancia existente de entity1 utilizando un servicio.
    """

    if id is None:
        # Redireccion si no se proporciona un ID
        return redirect('app1:entity1_list')

    repository = Entity1Repository()

    try:
        # Obtener los datos de la entidad desde el servicio
        entity1 = retrieve_entity1(repository=repository, entity_id=id)

    except (ValueError, EntityNotFoundError) as e:
        # Manejar errores específicos del dominio
        messages.error(request,  str(e))
        return redirect('app1:entity1_list')

    if request.method == "POST":

        # Validar los datos del formulario
        form = Entity1EditPostForm(request.POST)

        if form.is_valid():
            form_data = form.cleaned_data

            try:
                # obtenemos del request los campos especiales del formulario
                # ejemplo: password = request.POST.get('password', None)
                # ejemplo: photo = request.FILES.get('photo', None)
                # y los enviamos como parametros al servicio de actualizacion

                # LLamar al servicio de actualización
                update_entity1(repository=repository, entity_id=id, data=form_data)

                # Mostrar mensaje de éxito
                messages.success(request, f"Successfully updated entity1")

                # Redireccionar a la lista de entity1s
                return redirect('app1:entity1_list')

            except (ValueError, EntityNotFoundError) as e:
                form.add_error(None, str(e))

        else:
            messages.error(request, "There were errors in the form. Please correct them")

    # request.method == "GET":
    else:  
        # Initialize the form with existing data
        form = Entity1EditGetForm(initial={
            'id': entity1['id'],            
            'attributeName': entity1['attributeName'],
            'attributeEmail': entity1['attributeEmail']
        })

    # Renderizar la plantilla con el formulario
    return render(request, 'app1/entity1_web_edit.html', {'form': form})


def entity1_detail(request, id=None):
    """
    Vista genérica para mostrar los detalles de una instancia específica de entity1.
    """
    if id is None:
        return redirect('app1:entity1_list')

    repository = Entity1Repository()
    try:
        # Obtener los datos de la entidad desde el servicio
        entity1 = retrieve_entity1(repository=repository, entity_id=id)

    except (ValueError, EntityNotFoundError) as e:
        # Manejar errores específicos del dominio
        messages.error(request,  str(e))
        return redirect('app1:entity1_list')

    # Renderizar la plantilla con el formulario de vista
    form = Entity1ViewForm(initial={
        'attributeName': entity1['attributeName'],
        'attributeEmail': entity1['attributeEmail']
    })

    return render(request, 'app1/entity1_web_detail.html', {'form': form})


def entity1_delete(request, id=None):
    """
    Vista genérica para eliminar una instancia existente de entity1 utilizando un servicio.
    """
    if id is None:
        messages.error(request, "Non Valid id to delete")
        return redirect('app1:entity1_list')

    repository = Entity1Repository()
    try:
        # LLamar al servicio de eliminación
        delete_entity1(repository=repository, entity_id=id)
        messages.success(request, f"Successfully deleted entity1")
        
    except (ValueError, EntityNotFoundError) as e:
        # Manejar errores específicos del dominio
        messages.error(request,  str(e))

    return redirect('app1:entity1_list')

