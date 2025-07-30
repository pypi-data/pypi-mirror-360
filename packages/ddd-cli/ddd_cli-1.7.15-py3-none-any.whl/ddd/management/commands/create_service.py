from .utils import *
from colorama import Fore, Style

class CreateServiceCommand:
    def __init__(self, subparsers):
        parser = subparsers.add_parser("create-service", help='Create a new service')
        parser.add_argument("app_path", type=str, help='The relative path of the app within the project (for example, "apps/app1")')
        parser.add_argument("entity_name", type=str, help='The name of the entity')
        parser.add_argument("--class-format", action="store_true", help="Create a file with class format")   
        parser.add_argument("--split", action="store_true", help='Create a separate file for this service')
        parser.set_defaults(func=self.execute)         

    def execute(self, args):
        self.create_service(args.app_path, args.entity_name, args.class_format, args.split)

    def create_service(self, app_path, entity_name="Entity", class_format=False, split=False, **kwargs):
        """Crea un nuevo servicio"""
        services_dir = os.path.join(app_path, 'domain') if not split else os.path.join(app_path, 'domain', 'services')
        services_path = os.path.join(services_dir, 'services.py') if not split else os.path.join(services_dir, entity_name.lower() + '_service.py')

        # Crear directorios si no existen
        try:
            os.makedirs(services_dir, exist_ok=True)

            # Crear archivos __init__.py
            create__init__files(services_dir)
        except OSError as e:
            print(Fore.RED + f"Failed to create directory '{services_dir}': {e}" + Style.RESET_ALL)
            return
        
        #si split y ya existe el archivo mostrar error
        if split and os.path.exists(services_path):
            print(Fore.RED + f"The file '{services_path}' already exists. A separate file cannot be created" + Style.RESET_ALL)
            return

        # Escribir imports en el archivo 
        # si no existe el archivo template_imports
        if not os.path.exists(services_path):
            #renderizar imports
            rendered_content_imports = renderTemplate(templateName = 'service', fileName='imports.py', render_params={'entity_name':entity_name})

            # Escribir imports en el archivo
            with open(services_path, 'w') as f:
                f.write(rendered_content_imports + '\n')
            print(f"Imports of Service for '{entity_name}' created at {services_path}")

        if class_format:
            #renderizar class con crud
            rendered_content_class = renderTemplate(templateName = 'service', fileName='class_crud.py', render_params={'entity_name':entity_name})

        else:
            #renderizar funcion con crud
            rendered_content_class = renderTemplate(templateName = 'service', fileName='function_crud.py', render_params={'entity_name':entity_name})
      

        # Escribir class en el archivo
        with open(services_path, 'a') as f:
            f.write('\n' + rendered_content_class + '\n')
        print(f"Class of Service for '{entity_name}' created at {services_path}")        