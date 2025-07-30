import os
from pathlib import Path
from jinja2 import Environment, Template, FileSystemLoader

def create__init__file(path):
    """Crea un archivo __init__.py en el directorio especificado"""
    with open(os.path.join(path, '__init__.py'), 'w') as f:
        pass


def create__init__files(path):
    """Crea un archivo __init__.py en el directorio especificado 
    y en todos los directorios padres hasta el directorio raíz 
    o hasta encontrar un archivo __init__.py"""
    while True:
        if os.path.exists(os.path.join(path, '__init__.py')):
            break
        create__init__file(path)
        path = os.path.dirname(path)
        if path == '' or path == '/':
            break

# def renderTemplate(templateName: str, fileName:str, render_params: dict) -> str:
#     """
#     Renderiza una plantilla con los parámetros proporcionados.
#     """
#     # Construir la ruta absoluta de la plantilla
#     templates_dir = Path(__file__).resolve().parent.parent / "templates" / templateName
#     template_path = templates_dir / fileName

#     # Verificar si el archivo existe
#     if not template_path.exists():
#         raise FileNotFoundError(f"Template file {template_path} not found")

#     # Cargar la plantilla imports
#     template_imports = os.path.join(templates_dir, fileName)
#     with open(template_imports, 'r') as template_file:
#         template_content = template_file.read()

#     # Renderizar la plantilla imports
#     return Template(template_content).render(**render_params)

def renderTemplate(templateName: str, fileName: str, render_params: dict) -> str:
    """
    Renderiza una plantilla con los delimitadores específicos y los parámetros proporcionados.
    """
    # Construir la ruta absoluta de la plantilla
    templates_dir = Path(__file__).resolve().parent.parent / "templates" / templateName
    template_path = templates_dir / fileName

    # Verificar si el archivo existe
    if not template_path.exists():
        raise FileNotFoundError(f"Template file {template_path} not found")

    # Cargar el contenido de la plantilla
    with open(template_path, 'r') as template_file:
        template_content = template_file.read()

    # Configurar un entorno Jinja2 con delimitadores personalizados
    env = Environment(
        block_start_string='[%',   # Delimitador de inicio de bloque
        block_end_string='%]',     # Delimitador de fin de bloque
        variable_start_string='[[', # Delimitador de inicio de variable
        variable_end_string=']]'    # Delimitador de fin de variable
    )

    # Renderizar la plantilla usando el entorno personalizado
    template = env.from_string(template_content)
    return template.render(**render_params)

def readWriteTemplate(templateName: str, fileName:str, render_params: dict, repository_path: str, failIfError:bool= False):
    """
    Renderiza una plantilla con los parámetros proporcionados y escribe el archivo en repository_path
    """
    try:
        # Renderizar la plantilla
        rendered_content = renderTemplate(templateName = templateName, fileName=fileName, render_params=render_params)

        # Escribir en el archivo
        with open(repository_path, 'w') as f:
            f.write('\n' + rendered_content + '\n') 

    except Exception as e:
        if failIfError:
            raise Exception(e.args)
        
def decodeAppPath(app_path: str) -> tuple:
    """
    Convierte una ruta de aplicación (ej: apps/manager/app1) a:
    1. nombre de aplicación (ej: apps.manager.app1)
    2. ultimo nombre de la aplicación (ej: app1)
    3. ruta de la aplicación (ej: apps:manager:app1)
    4. path relativo de la aplicación (ej: manager/app1) quitando el primer prefijo.
    """

    # Convertir app_path a path relativo
    relative_app_path = app_path.split('/', 1)[-1] if '/' in app_path else app_path

    # Convertir app_path a app_name
    app_name = app_path.replace('/', '.').replace('\\', '.').replace('..', '.')
    relative_app_name = relative_app_path.replace('/', '.').replace('\\', '.').replace('..', '.')
    
    # Obtener el último nombre de la aplicación
    last_app_name = app_name.split('.')[-1]

    # Convertir app_path a ruta de aplicación
    app_route = relative_app_name.replace('.', ':')

    return app_name, last_app_name, app_route, relative_app_path