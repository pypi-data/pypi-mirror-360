
from django.urls import path

from . import entity1_views

app_name = "app1"

urlpatterns = [

    path('', entity1_views.entity1_list, name="index"),  # ← Esta es la URL por defecto    
    path('entity1-list/', entity1_views.entity1_list, name="entity1_list"),
    path('entity1-create/', entity1_views.entity1_create, name="entity1_create"),
    path('entity1-edit/<int:id>', entity1_views.entity1_edit, name="entity1_edit"),
    path('entity1-detail/<int:id>', entity1_views.entity1_detail, name="entity1_detail"),
    path('entity1-delete/<int:id>', entity1_views.entity1_delete, name="entity1_delete"),    

]
