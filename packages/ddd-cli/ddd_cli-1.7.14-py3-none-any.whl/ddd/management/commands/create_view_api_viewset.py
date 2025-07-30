
from .utils import *
from colorama import Fore, Style
import os
from .create_serializer import CreateSerializerCommand

class CreateViewApiViewSetCommand:
    def __init__(self, subparsers):
        parser = subparsers.add_parser('create-view-api-viewset', help='Create a view for api based on ViewSet')
        parser.add_argument('app_path', type=str, help='The relative path of the app within the project (for example, "apps/app1")')
        parser.add_argument('entity_name', type=str, help='The name of the entity')  
        parser.set_defaults(func=self.execute)    

        # guardar el subparser para usarlo en el comando
        self.subparsers = subparsers                      

    def execute(self, args):
        self.create_view_api_viewset(args.app_path, args.entity_name)

    def create_view_api_viewset(self, app_path, entity_name, **kwargs):
        """Crea una view para api basada en ApiViewSet"""
        views_dir = app_path
        urls_path = os.path.join(views_dir, entity_name.lower() + '_urls.py')        
        views_path = os.path.join(views_dir, entity_name.lower() + '_views.py')

        # Crear directorios si no existen
        try:
            os.makedirs(views_dir, exist_ok=True)

            # Crear archivos __init__.py
            create__init__files(views_dir)
        except OSError as e:
            print(Fore.RED + f"Failed to create directory '{views_dir}': {e}" + Style.RESET_ALL)
            return    
        
        #si ya existe el archivo mostrar error
        if os.path.exists(views_path):
            print(Fore.RED + f"The file '{views_path}' already exists" + Style.RESET_ALL)
            return
        
        # decodficar app_path
        app_name, last_app_name, app_route, relative_app_path = decodeAppPath(app_path)

        #renderizar urls
        readWriteTemplate(templateName='routers', fileName='api_viewset_urls.py',  render_params={'entity_name':entity_name}, repository_path=urls_path, failIfError=True)
        print(f"ViewSet Urls of Entity '{entity_name}' created at {urls_path}")     

        # Crear serializer
        serializer_command = CreateSerializerCommand(subparsers=self.subparsers)
        serializer_command.create_serializer(app_path, entity_name)                   

        #renderizar view
        rendered_content_class = renderTemplate(templateName = 'api', fileName='viewset_views.py', render_params={'app_name':app_name, 'entity_name':entity_name})
        # Escribir class en el archivo
        with open(views_path, 'w') as f:
            f.write('\n' + rendered_content_class + '\n')
        print(f"Class View ApiViewSet of Entity '{entity_name}' created at {views_path}")