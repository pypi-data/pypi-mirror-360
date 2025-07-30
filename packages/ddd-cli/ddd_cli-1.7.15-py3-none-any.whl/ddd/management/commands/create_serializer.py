from .utils import *
from colorama import Fore, Style

class CreateSerializerCommand:
    def __init__(self, subparsers):
        parser = subparsers.add_parser('create-serializer', help='Create a new Serializer')
        parser.add_argument('app_path', type=str, help='The relative path of the app within the project (for example, "apps/app1")')
        parser.add_argument('serializer_name', type=str, help='The name of the Serializer')
        parser.add_argument(
            '--split', action='store_true', help='Create a separate file for this Serializer'
        )        
        parser.set_defaults(func=self.execute) 

    def execute(self, args):
        self.create_serializer(args.app_path, args.serializer_name, args.split)
        
    def create_serializer(self, app_path, serializer_name, split=False, **kwargs):
        """Crea un nuevo Serializer"""
        serializers_dir = app_path if not split else os.path.join(app_path, 'serializers')
        serializers_path = os.path.join(serializers_dir, 'serializers.py') if not split else os.path.join(serializers_dir, serializer_name.lower() + '_serializer.py')

        # Crear directorios si no existen
        try:
            os.makedirs(serializers_dir, exist_ok=True)

            # Crear archivos __init__.py
            create__init__files(serializers_dir)
        except OSError as e:
            print(Fore.RED + f"Failed to create directory '{serializers_dir}': {e}" + Style.RESET_ALL)
            return
        
        #si split y ya existe el archivo mostrar error
        if split and os.path.exists(serializers_path):
            print(Fore.RED + f"File '{serializers_path}' already exists. Cannot create separate file" + Style.RESET_ALL)
            return

        # Escribir imports en el archivo 
        # si no existe el archivo template_imports
        if not os.path.exists(serializers_path):
            #renderizar imports
            rendered_content_imports = renderTemplate(templateName = 'serializer', fileName='imports.py', render_params={'serializer_name':serializer_name})

            # Escribir imports en el archivo
            with open(serializers_path, 'w') as f:
                f.write(rendered_content_imports + '\n')
            print(f"Imports of Serializer '{serializer_name}' created at {serializers_path}")

        #renderizar class
        rendered_content_class = renderTemplate(templateName = 'serializer', fileName='class.py', render_params={'serializer_name':serializer_name})

        # Escribir class en el archivo
        with open(serializers_path, 'a') as f:
            f.write('\n' + rendered_content_class + '\n')
        print(f"Class of Serializer '{serializer_name}' created at {serializers_path}")        