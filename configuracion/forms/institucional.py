from django import forms

from core.models import Institucion, Localidad, Municipio, Provincia
from legajos.models import (
    InscriptoActividad,
    PersonalInstitucion,
    PlanFortalecimiento,
    StaffActividad,
)
from legajos.models_programas import Programa

# Alias para compatibilidad
DispositivoRed = Institucion


class ProvinciaForm(forms.ModelForm):
    class Meta:
        model = Provincia
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Ingrese el nombre de la provincia'
            })
        }


class MunicipioForm(forms.ModelForm):
    class Meta:
        model = Municipio
        fields = ['nombre', 'provincia']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Ingrese el nombre del municipio'
            }),
            'provincia': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            })
        }


class LocalidadForm(forms.ModelForm):
    class Meta:
        model = Localidad
        fields = ['nombre', 'municipio']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Ingrese el nombre de la localidad'
            }),
            'municipio': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            })
        }


class InstitucionForm(forms.ModelForm):
    class Meta:
        model = Institucion
        fields = [
            'tipo', 'nombre', 'provincia', 'municipio', 'localidad', 'direccion', 
            'telefono', 'email', 'activo', 'descripcion', 'estado_registro',
            'tipo_personeria', 'nro_personeria', 'fecha_personeria', 'cuit',
            'presta_asistencia', 'convenio_obras_sociales', 'nro_sss'
        ]
        widgets = {
            'tipo': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Ingrese el nombre de la institución'
            }),
            'provincia': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'municipio': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'localidad': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Ingrese la dirección'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Ingrese el teléfono'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Ingrese el email'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Descripción de la institución'
            }),
            'estado_registro': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'tipo_personeria': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'nro_personeria': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Número de personería jurídica'
            }),
            'fecha_personeria': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'date'
            }),
            'cuit': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'CUIT (XX-XXXXXXXX-X)'
            }),
            'nro_sss': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Número SSS'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            }),
            'presta_asistencia': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            }),
            'convenio_obras_sociales': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            })
        }


# Alias para compatibilidad
DispositivoForm = InstitucionForm


class PersonalInstitucionForm(forms.ModelForm):
    class Meta:
        model = PersonalInstitucion
        fields = ['nombre', 'apellido', 'dni', 'tipo', 'titulo_profesional', 'matricula']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500',
                'placeholder': 'Nombre'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500',
                'placeholder': 'Apellido'
            }),
            'dni': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500',
                'placeholder': 'DNI'
            }),
            'tipo': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500'
            }),
            'titulo_profesional': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500',
                'placeholder': 'Título profesional (opcional)'
            }),
            'matricula': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500',
                'placeholder': 'Matrícula (opcional)'
            })
        }


class StaffActividadForm(forms.ModelForm):
    OPCIONES_PERSONAL = [
        ('existente', 'Seleccionar personal existente'),
        ('nuevo', 'Crear nuevo personal')
    ]
    
    tipo_asignacion = forms.ChoiceField(
        choices=OPCIONES_PERSONAL,
        widget=forms.RadioSelect(attrs={
            'class': 'form-radio text-purple-600'
        }),
        initial='existente'
    )
    
    buscar_personal = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500',
            'placeholder': 'Buscar por nombre, apellido o DNI...'
        })
    )
    
    class Meta:
        model = StaffActividad
        fields = ['personal', 'rol_en_actividad', 'activo']
        widgets = {
            'personal': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500'
            }),
            'rol_en_actividad': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500',
                'placeholder': 'Ej: Coordinador, Terapeuta, Operador'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded'
            })
        }
    
    def __init__(self, *args, **kwargs):
        legajo_institucional = kwargs.pop('legajo_institucional', None)
        super().__init__(*args, **kwargs)
        
        self.fields['personal'].required = False
        
        if legajo_institucional:
            self.fields['personal'].queryset = PersonalInstitucion.objects.filter(
                legajo_institucional=legajo_institucional,
                activo=True
            ).order_by('apellido', 'nombre')
            self.fields['personal'].label_from_instance = lambda obj: f"{obj.apellido}, {obj.nombre} - DNI: {obj.dni}"
    
    def clean(self):
        cleaned_data = super().clean()
        tipo_asignacion = cleaned_data.get('tipo_asignacion')
        personal = cleaned_data.get('personal')
        
        if tipo_asignacion == 'existente' and not personal:
            raise forms.ValidationError('Debe seleccionar un personal existente.')
        
        return cleaned_data


class PlanFortalecimientoForm(forms.ModelForm):
    class Meta:
        model = PlanFortalecimiento
        fields = [
            'nombre', 'tipo', 'subtipo', 'descripcion',
            'cupo_ciudadanos', 'fecha_inicio', 'fecha_fin', 'estado',
            'tipo_acceso', 'programa_requerido',
        ]
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'type': 'date'
            }),
            'fecha_fin': forms.DateInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'type': 'date'
            }),
            'tipo_acceso': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500',
                'x-model': 'tipoAcceso',
            }),
            'programa_requerido': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['programa_requerido'].queryset = Programa.objects.filter(
            estado='ACTIVO'
        ).order_by('nombre')
        self.fields['programa_requerido'].required = False
        self.fields['programa_requerido'].empty_label = 'Seleccionar programa...'

    def clean(self):
        cleaned_data = super().clean()
        tipo_acceso = cleaned_data.get('tipo_acceso')
        programa_requerido = cleaned_data.get('programa_requerido')

        if tipo_acceso == PlanFortalecimiento.TipoAcceso.LIBRE:
            cleaned_data['programa_requerido'] = None
        elif tipo_acceso == PlanFortalecimiento.TipoAcceso.REQUIERE_PROGRAMA and not programa_requerido:
            self.add_error('programa_requerido', 'Debe seleccionar un programa cuando el tipo de acceso lo requiere.')

        return cleaned_data


class InscriptoEstadoForm(forms.ModelForm):
    class Meta:
        model = InscriptoActividad
        fields = ["estado", "observaciones"]
        widgets = {
            "estado": forms.Select(
                attrs={
                    "class": "w-full p-3 border border-gray-300 rounded-lg",
                }
            ),
            "observaciones": forms.Textarea(
                attrs={
                    "class": "w-full p-3 border border-gray-300 rounded-lg",
                    "rows": 4,
                    "placeholder": "Agregar observaciones sobre el cambio de estado...",
                }
            ),
        }


class ActividadEditarForm(forms.ModelForm):
    class Meta:
        model = PlanFortalecimiento
        fields = [
            "nombre",
            "descripcion",
            "cupo_ciudadanos",
            "fecha_inicio",
            "fecha_fin",
            "estado",
            "tipo_acceso",
            "programa_requerido",
        ]
        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "class": "w-full p-3 border border-gray-300 rounded-lg",
                    "placeholder": "Nombre de la actividad",
                }
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "class": "w-full p-3 border border-gray-300 rounded-lg",
                    "rows": 4,
                }
            ),
            "cupo_ciudadanos": forms.NumberInput(
                attrs={
                    "class": "w-full p-3 border border-gray-300 rounded-lg",
                    "min": 0,
                }
            ),
            "fecha_inicio": forms.DateInput(
                attrs={
                    "class": "w-full p-3 border border-gray-300 rounded-lg",
                    "type": "date",
                }
            ),
            "fecha_fin": forms.DateInput(
                attrs={
                    "class": "w-full p-3 border border-gray-300 rounded-lg",
                    "type": "date",
                }
            ),
            "estado": forms.Select(
                attrs={
                    "class": "w-full p-3 border border-gray-300 rounded-lg",
                }
            ),
            "tipo_acceso": forms.Select(
                attrs={
                    "class": "w-full p-3 border border-gray-300 rounded-lg",
                    "x-model": "tipoAcceso",
                }
            ),
            "programa_requerido": forms.Select(
                attrs={
                    "class": "w-full p-3 border border-gray-300 rounded-lg",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['programa_requerido'].queryset = Programa.objects.filter(
            estado='ACTIVO'
        ).order_by('nombre')
        self.fields['programa_requerido'].required = False
        self.fields['programa_requerido'].empty_label = 'Seleccionar programa...'

    def clean(self):
        cleaned_data = super().clean()
        tipo_acceso = cleaned_data.get('tipo_acceso')
        programa_requerido = cleaned_data.get('programa_requerido')

        if tipo_acceso == PlanFortalecimiento.TipoAcceso.LIBRE:
            cleaned_data['programa_requerido'] = None
        elif tipo_acceso == PlanFortalecimiento.TipoAcceso.REQUIERE_PROGRAMA and not programa_requerido:
            self.add_error('programa_requerido', 'Debe seleccionar un programa cuando el tipo de acceso lo requiere.')

        return cleaned_data


class StaffActividadUpdateForm(forms.ModelForm):
    class Meta:
        model = StaffActividad
        fields = ["rol_en_actividad", "activo"]
        widgets = {
            "rol_en_actividad": forms.TextInput(
                attrs={
                    "class": "w-full p-3 border border-gray-300 rounded-lg",
                    "placeholder": "Ej: Coordinador, Terapeuta, Operador",
                }
            ),
            "activo": forms.CheckboxInput(
                attrs={
                    "class": "h-4 w-4 text-blue-600 border-gray-300 rounded",
                }
            ),
        }


class InscripcionDirectaForm(forms.Form):
    ciudadano_dni = forms.CharField(
        label='DNI del ciudadano',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'w-full p-3 border border-gray-300 rounded-lg',
            'placeholder': 'Ingrese el DNI del ciudadano',
            'autofocus': True,
        }),
    )
    observaciones = forms.CharField(
        label='Observaciones',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full p-3 border border-gray-300 rounded-lg',
            'rows': 2,
            'placeholder': 'Observaciones opcionales...',
        }),
    )

    def clean_ciudadano_dni(self):
        from legajos.models import Ciudadano

        dni = self.cleaned_data.get('ciudadano_dni', '').strip()
        try:
            ciudadano = Ciudadano.objects.get(dni=dni)
        except Ciudadano.DoesNotExist:
            raise forms.ValidationError(f'No se encontró ningún ciudadano con DNI "{dni}".')
        return ciudadano


class DerivacionRechazoForm(forms.Form):
    motivo = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "w-full p-3 border border-gray-300 rounded-lg",
                "rows": 3,
                "placeholder": "Motivo del rechazo",
            }
        ),
    )

    def clean_motivo(self):
        return self.cleaned_data.get("motivo") or "Rechazada"
