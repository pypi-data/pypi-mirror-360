
from django import forms
from django.core import validators
from django.core.validators import (
    MinLengthValidator,
    MaxLengthValidator,
    RegexValidator,
    EmailValidator,
    MinValueValidator,
    MaxValueValidator,
)


class Entity1BaseForm(forms.Form):
    """
    Formulario base para la entidad entity1.
    """

    # Campo de texto y numeros (Nombre)
    attributeName = forms.CharField(
        label="Name",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your full name',
            'minlength': '3',  # HTML5 validación
            'maxlength': '100',  # HTML5 validación
            'pattern': r'^[A-Za-z0-9ñÑáéíóúÁÉÍÓÚ ]*$',  # Expresión regular en el navegador
            'title': 'The name must only contain letters, numbers, and spaces.'  # Mensaje de ayuda                          
        }),
        validators=[
            MinLengthValidator(3, "The name must be at least 3 characters"),
            MaxLengthValidator(100, "The name must not exceed 100 characters"),
            RegexValidator(r'^[A-Za-z0-9ñÑáéíóúÁÉÍÓÚ ]*$', 'The name must only contain letters, numbers, and spaces.'),
        ]
    )

    # Campo de texto (Category)
    attributeCategory = forms.CharField(
        label='Category',
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'minlength': '4',  # Mínima longitud en el navegador
            'maxlength': '250',  # Máxima longitud en el navegador      
            'pattern': r'^[A-Za-z\s]*$',  # Expresión regular en el navegador           
            'title': 'The name can only contain letters and spaces.'
        }),
        validators=[
            MinLengthValidator(4, "The name must be at least 4 characters"),
            MaxLengthValidator(250, "The name must not exceed 250 characters"),
            RegexValidator(r'^[A-Za-z\s]*$', "The name can only contain letters and spaces"),
        ]          
    ) 

    # Campo de correo electrónico
    attributeEmail = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
        }),
        validators=[
            EmailValidator("Please enter a valid email address"),
        ]
    )

    # Campo de contraseña
    attributePassword = forms.CharField(
        label="Password",
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create a password',
            'minlength': '8',
        }),
        validators=[
            MinLengthValidator(8, "Password must be at least 8 characters long"),
        ]
    )

    # Campo numérico
    attributeAge = forms.IntegerField(
        label="Age",
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '18',  # HTML5 validación
            'max': '100',  # HTML5 validación
            'placeholder': 'Enter your age',
        }),
        validators=[
            MinValueValidator(18, "You must be at least 18 years old"),
            MaxValueValidator(100, "The age must not exceed 100"),
        ]
    )

    # Campo de fecha
    attributeBirthDate = forms.DateField(
        label="Birth Date",
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',  # HTML5 tipo fecha
        })
    )

    # Selección desplegable
    attributeCountry = forms.ChoiceField(
        label="Country",
        required=True,
        choices=[
            ('', 'Select your country'),
            ('us', 'United States'),
            ('es', 'Spain'),
            ('mx', 'Mexico'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control form-select',
        })  
    )

    # Opciones de radio
    attributeGender = forms.ChoiceField(
        label="Gender",
        required=True,
        choices=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other'),
        ],
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input',
        })
    )

    # Casillas de verificación
    attributeTerms = forms.BooleanField(
        label="I accept the terms and conditions",
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        }),
        error_messages={
            'required': "You must accept the terms and conditions to proceed",
        }
    )

    def clean_attributeName(self):
        '''
        Esta validacion es solo para el campo 'attributeName'
        '''    
        attributeName = self.cleaned_data.get('attributeName')
        if len(attributeName) < 3:
            raise forms.ValidationError("The name must be at least 3 characters long")
        return attributeName

    def clean_attributeEmail(self):
        '''
        Esta validacion es solo para el campo 'attributeEmail'
        '''
        attributeEmail = self.cleaned_data.get('attributeEmail')
        if attributeEmail.endswith('@example.com'):
            raise forms.ValidationError("Emails from example.com are not allowed")
        return attributeEmail

    def clean(self):
        '''
        Aqui podemos hacer validaciones que involucren a varios campos
        '''
        cleaned_data = super().clean()
        attributePassword = cleaned_data.get('attributePassword')
        attributePassword_confirm = cleaned_data.get('attributePassword_confirm')

        if attributePassword != attributePassword_confirm:
            raise forms.ValidationError("Passwords do not match")


class Entity1CreateForm(Entity1BaseForm):
    """
    Formulario para crear una nueva instancia de entity1. Sin modificaciones adicionales.
    """
    #Permitimos que el attributeEmail sea editable
    Entity1BaseForm.base_fields['attributeEmail'].widget.attrs.update({
        'readonly': False,
    })

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)        

        # Aqui podemos agregar validaciones adicionales o modificar el comportamiento del formulario


class Entity1EditGetForm(Entity1BaseForm):
    """
    Formulario para editar mediante GET una instancia de entity1. 
    """
    #Agregamos un campo adicional para 'id' Oculto para el Formulario
    id = forms.IntegerField(
        label='ID',
        required=False,
        widget=forms.HiddenInput()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)     

        # Aqui podemos agregar validaciones adicionales o modificar el comportamiento del formulario

        #impedimos que el attributeEmail sea editable 
        self.attributeEmail.widget.attrs.update({
            'readonly': 'True'
        })


class Entity1EditPostForm(Entity1BaseForm):
    """
    Formulario para editar mediante POST una instancia de entity1. 
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)     

        # Aqui podemos agregar validaciones adicionales o modificar el comportamiento del formulario

        # Eliminamos los campos que no se deben guardar de la forma tradicional
        for field in ['attributePassword', 'attributePhoto']:
            if field in self.fields:
                del self.fields[field]      


class Entity1ViewForm(Entity1BaseForm):
    """
    Formulario de solo lectura para Visualizar una instancia de entity1
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Aqui podemos agregar validaciones adicionales o modificar el comportamiento del formulario

        # Hacer todos los campos no editables
        for field in self.fields.values():
            field.widget.attrs['disabled'] = True








            
'''
Flujo de Validación en Django Forms

Cuando se llama al método is_valid() de un formulario, Django realiza las siguientes acciones de manera secuencial:

1. Limpiar los datos de entrada crudos
    Antes de cualquier validación, Django toma los datos enviados ( o  en formularios de tipo GET) y los procesa en el objeto . 
    Esto incluye convertir los valores en tipos de datos que Django pueda interpretar.

2. Validación de los campos individuales
    Django valida cada campo del formulario según las reglas especificadas en el formulario o en el modelo asociado. 
    Este proceso incluye:
    
    Validadores básicos del campo:
    - Validación de tipo: Por ejemplo, un campo 'forms.integerField' asegura que el valor sea un entero.
    - Validación de valores requeridos: Si el campo tiene 'required=True' y no se proporciona ningún valor, se genera un error.
    - Validación de longitud: En campos como 'CharField', 'max_length' y 'min_length' son comprobados.
    - Validación de opciones: En campos como 'Choice_Field', el valor debe ser una de las opciones definidas

    Validadores específicos: Los validadores personalizados definidos en el propio campo o como funciones adicionales se ejecutan

3. Métodos 'clean_<nombr_campo>'
    Django busca métodos personalizados para los campos del formulario, siguiendo la convención 'clean_<nombr_campo>'. 
    Si existen, estos métodos se ejecutan después de las validaciones básicas del campo.

    Ejemplo:

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email.endswith("@example.com"):
            raise forms.ValidationError("Only example.com emails are allowed")
        return email

    Los errores generados por estos métodos se almacenan en el atributo 'form.field_name.errors'.

4. Método 'clean()' general
    Una vez que todos los campos han sido validados individualmente, Django llama al método 'clean()'  general del formulario. 
    Este método es útil para validar dependencias entre múltiples campos.
    Por ejemplo:

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password != password_confirm:
            raise forms.ValidationError("Passwords do not match")

    Los errores de este método se almacenan en 'form.errors' como errores globales, no asociados a un campo específico.

5. Almacenar los datos validados
    Si no hay errores, los valores procesados y validados se almacenan en el atributo 'form.cleaned_data', 
    que es un diccionario con los datos del formulario que pasaron la validación.

'''
