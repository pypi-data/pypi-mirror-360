from .utils import *
from colorama import Fore, Style

class CreateRepositoryCommand:
    def __init__(self, subparsers):
        parser = subparsers.add_parser("create-repository", help='Create a new repository')
        parser.add_argument('app_path', type=str, help='The relative path of the app within the project (for example, "apps/app1")')
        parser.add_argument('entity_name', type=str, help='The name of the entity')
        parser.set_defaults(func=self.execute)

    def execute(self, args):
        self.create_repository(args.app_path, args.entity_name)

    def create_repository(self, app_path, entity_name, **kwargs):
            """Crea un nuevo repositorio"""
            repository_dir = os.path.join(app_path, 'infrastructure')
            repository_path = os.path.join(repository_dir, entity_name.lower() + '_repository.py')
            mappers_path = os.path.join(repository_dir, 'mappers.py')

            # decodficar app_path
            app_name, last_app_name, app_route, relative_app_path = decodeAppPath(app_path)

            # Crear directorios si no existen
            try:
                os.makedirs(repository_dir, exist_ok=True)

                # Crear archivos __init__.py
                create__init__files(repository_dir)

            except OSError as e:
                print(Fore.RED + f"Failed to create directory '{repository_dir}': {e}" + Style.RESET_ALL)
                return    
            
            #si ya existe el archivo mostrar error
            if os.path.exists(repository_path):
                print(Fore.RED + f"The file '{repository_path}' already exists" + Style.RESET_ALL)
                return
            
            # Crear archivo de mappers.py        
            readWriteTemplate(templateName = 'repository', fileName='mappers.py', render_params={}, repository_path=mappers_path, failIfError=False)
            
            #renderizar class
            readWriteTemplate(templateName = 'repository', fileName='class.py', render_params={'entity_name':entity_name, 'app_name':app_name}, repository_path=repository_path, failIfError=True)

            # # Escribir class en el archivo
            # with open(repository_path, 'w') as f:
            #     f.write('\n' + rendered_content_class + '\n')
            print(f"Class Repository of Entity '{entity_name}' created at {repository_path}")
