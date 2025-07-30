from .utils import *
from colorama import Fore, Style

class CreateDTOCommand:
    def __init__(self, subparsers):
        parser = subparsers.add_parser('create-dto', help='Create a new DTO')
        parser.add_argument('app_path', type=str, help='The relative path of the app within the project (for example, "apps/app1")')
        parser.add_argument('dto_name', type=str, help='The name of the DTO')
        parser.add_argument(
            '--split', action='store_true', help='Create a separate file for this DTO'
        )        
        parser.set_defaults(func=self.execute) 

    def execute(self, args):
        self.create_dto(args.app_path, args.dto_name, args.split)
        
    def create_dto(self, app_path, dto_name, split=False, **kwargs):
        """Crea un nuevo DTO"""
        dtos_dir = app_path if not split else os.path.join(app_path, 'dtos')
        dtos_path = os.path.join(dtos_dir, 'dtos.py') if not split else os.path.join(dtos_dir, dto_name.lower() + '_dto.py')

        # Crear directorios si no existen
        try:
            os.makedirs(dtos_dir, exist_ok=True)

            # Crear archivos __init__.py
            create__init__files(dtos_dir)
        except OSError as e:
            print(Fore.RED + f"Failed to create directory '{dtos_dir}': {e}" + Style.RESET_ALL)
            return
        
        #si split y ya existe el archivo mostrar error
        if split and os.path.exists(dtos_path):
            print(Fore.RED + f"File '{dtos_path}' already exists. Cannot create separate file" + Style.RESET_ALL)
            return

        # Escribir imports en el archivo 
        # si no existe el archivo template_imports
        if not os.path.exists(dtos_path):
            #renderizar imports
            rendered_content_imports = renderTemplate(templateName = 'dto', fileName='imports.py', render_params={'dto_name':dto_name})

            # Escribir imports en el archivo
            with open(dtos_path, 'w') as f:
                f.write(rendered_content_imports + '\n')
            print(f"Imports of Dto '{dto_name}' created at {dtos_path}")

        #renderizar class
        rendered_content_class = renderTemplate(templateName = 'dto', fileName='class.py', render_params={'dto_name':dto_name})

        # Escribir class en el archivo
        with open(dtos_path, 'a') as f:
            f.write('\n' + rendered_content_class + '\n')
        print(f"Class of Dto '{dto_name}' created at {dtos_path}")        