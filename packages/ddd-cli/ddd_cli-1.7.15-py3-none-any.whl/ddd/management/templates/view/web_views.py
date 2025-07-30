from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse

# Importar excepciones específicas de dominio
from [[ app_name.lower() ]].domain.exceptions import EntityNotFoundError

# Importar formularios específicos de la entidad
from [[ app_name.lower() ]].[[ entity_name.lower() ]]_forms import [[ entity_name.capitalize() ]]CreateForm, [[ entity_name.capitalize() ]]EditGetForm, [[ entity_name.capitalize() ]]EditPostForm, [[ entity_name.capitalize() ]]ViewForm

# Importar servicios específicos del dominio
from [[ app_name.lower() ]].domain.services import (
    list_[[ entity_name.lower() ]],
    create_[[ entity_name.lower() ]],
    retrieve_[[ entity_name.lower() ]],
    update_[[ entity_name.lower() ]],
    delete_[[ entity_name.lower() ]],
)

# Importar repositorios específicos de la infraestructura
from [[ app_name.lower() ]].infrastructure.[[ entity_name.lower() ]]_repository import [[ entity_name.capitalize() ]]Repository


def [[ entity_name.lower() ]]_list(request):
    """
    Vista genérica para mostrar una lista de todas las instancias de [[ entity_name.lower() ]].
    """

    [[ entity_name.lower() ]]List = [] #inicialize list

    # Obtener la lista del repositorio
    try:
        repository = [[ entity_name.capitalize() ]]Repository()
        [[ entity_name.lower() ]]List = list_[[ entity_name.lower() ]](repository=repository)

    except (ValueError, EntityNotFoundError) as e:
        # Manejo de errores específicos del dominio
        messages.error(request,  str(e))

    # Renderizar la plantilla con la lista
    return render(request, '[[ relative_app_path.lower() ]]/[[ entity_name.lower() ]]_web_list.html', {
        '[[ entity_name.lower() ]]List': [[ entity_name.lower() ]]List
    })


def [[ entity_name.lower() ]]_create(request):
    """
    Vista genérica para crear una nueva instancia de [[ entity_name.lower() ]] utilizando un servicio.
    """

    if request.method == "POST":

        # Validar los datos del formulario
        form = [[ entity_name.capitalize() ]]CreateForm(request.POST)

        if form.is_valid():
            form_data = form.cleaned_data
            repository = [[ entity_name.capitalize() ]]Repository()

            # Obtener el ID de la entidad relacionada si existe
            external_id = request.POST.get('external_id', None)

            try:
                # LLamar al servicio de creación
                create_[[ entity_name.lower() ]](repository=repository, external_id=external_id, data=form_data)

                # Mostrar mensaje de éxito y redirigir
                messages.success(request, f"Successfully created [[ entity_name.lower() ]]")
                return redirect('[[ app_route.lower() ]]:[[ entity_name.lower() ]]_list')

            except (ValueError, EntityNotFoundError) as e:
                # Manejar errores específicos del dominio
                form.add_error(None, str(e))
        else:
            messages.error(request, "There were errors in the form. Please correct them")
    else:
        # Formulario vacío para solicitudes GET
        form = [[ entity_name.capitalize() ]]CreateForm()

    # Renderizar la plantilla con el formulario
    return render(request, '[[ relative_app_path.lower() ]]/[[ entity_name.lower() ]]_web_create.html', {'form': form}) 


def [[ entity_name.lower() ]]_edit(request, id=None):
    """
    Vista genérica para editar una instancia existente de [[ entity_name.lower() ]] utilizando un servicio.
    """

    if id is None:
        # Redireccion si no se proporciona un ID
        return redirect('[[ app_route.lower() ]]:[[ entity_name.lower() ]]_list')

    repository = [[ entity_name.capitalize() ]]Repository()

    try:
        # Obtener los datos de la entidad desde el servicio
        [[ entity_name.lower() ]] = retrieve_[[ entity_name.lower() ]](repository=repository, entity_id=id)

    except (ValueError, EntityNotFoundError) as e:
        # Manejar errores específicos del dominio
        messages.error(request,  str(e))
        return redirect('[[ app_route.lower() ]]:[[ entity_name.lower() ]]_list')

    if request.method == "POST":

        # Validar los datos del formulario
        form = [[ entity_name.capitalize() ]]EditPostForm(request.POST)

        if form.is_valid():
            form_data = form.cleaned_data

            try:
                # obtenemos del request los campos especiales del formulario
                # ejemplo: password = request.POST.get('password', None)
                # ejemplo: photo = request.FILES.get('photo', None)
                # y los enviamos como parametros al servicio de actualizacion

                # LLamar al servicio de actualización
                update_[[ entity_name.lower() ]](repository=repository, entity_id=id, data=form_data)

                # Mostrar mensaje de éxito
                messages.success(request, f"Successfully updated [[ entity_name.lower() ]]")

                # Redireccionar a la lista de [[ entity_name.lower() ]]s
                return redirect('[[ app_route.lower() ]]:[[ entity_name.lower() ]]_list')

            except (ValueError, EntityNotFoundError) as e:
                form.add_error(None, str(e))

        else:
            messages.error(request, "There were errors in the form. Please correct them")

    # request.method == "GET":
    else:  
        # Initialize the form with existing data
        form = [[ entity_name.capitalize() ]]EditGetForm(initial={
            'id': [[ entity_name.lower() ]]['id'],            
            'attributeName': [[ entity_name.lower() ]]['attributeName'],
            'attributeEmail': [[ entity_name.lower() ]]['attributeEmail']
        })

    # Renderizar la plantilla con el formulario
    return render(request, '[[ relative_app_path.lower() ]]/[[ entity_name.lower() ]]_web_edit.html', {'form': form})


def [[ entity_name.lower() ]]_detail(request, id=None):
    """
    Vista genérica para mostrar los detalles de una instancia específica de [[ entity_name.lower() ]].
    """
    if id is None:
        return redirect('[[ app_route.lower() ]]:[[ entity_name.lower() ]]_list')

    repository = [[ entity_name.capitalize() ]]Repository()
    try:
        # Obtener los datos de la entidad desde el servicio
        [[ entity_name.lower() ]] = retrieve_[[ entity_name.lower() ]](repository=repository, entity_id=id)

    except (ValueError, EntityNotFoundError) as e:
        # Manejar errores específicos del dominio
        messages.error(request,  str(e))
        return redirect('[[ app_route.lower() ]]:[[ entity_name.lower() ]]_list')

    # Renderizar la plantilla con el formulario de vista
    form = [[ entity_name.capitalize() ]]ViewForm(initial={
        'attributeName': [[ entity_name.lower() ]]['attributeName'],
        'attributeEmail': [[ entity_name.lower() ]]['attributeEmail']
    })

    return render(request, '[[ relative_app_path.lower() ]]/[[ entity_name.lower() ]]_web_detail.html', {'form': form})


def [[ entity_name.lower() ]]_delete(request, id=None):
    """
    Vista genérica para eliminar una instancia existente de [[ entity_name.lower() ]] utilizando un servicio.
    """
    if id is None:
        messages.error(request, "Non Valid id to delete")
        return redirect('[[ app_route.lower() ]]:[[ entity_name.lower() ]]_list')

    repository = [[ entity_name.capitalize() ]]Repository()
    try:
        # LLamar al servicio de eliminación
        delete_[[ entity_name.lower() ]](repository=repository, entity_id=id)
        messages.success(request, f"Successfully deleted [[ entity_name.lower() ]]")
        
    except (ValueError, EntityNotFoundError) as e:
        # Manejar errores específicos del dominio
        messages.error(request,  str(e))

    return redirect('[[ app_route.lower() ]]:[[ entity_name.lower() ]]_list')

