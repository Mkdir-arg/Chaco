from django import forms
from django.utils import timezone

from ..models import Derivacion, EvaluacionInicial, EventoCritico, PlanIntervencion, SeguimientoContacto


class EvaluacionInicialForm(forms.ModelForm):
    """Formulario para evaluación inicial"""

    assist_puntaje = forms.IntegerField(
        required=False,
        label='ASSIST - Puntaje Total',
        widget=forms.NumberInput(
            attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'min': '0',
                'max': '100',
            }
        ),
    )

    phq9_puntaje = forms.IntegerField(
        required=False,
        label='PHQ-9 - Puntaje Total',
        widget=forms.NumberInput(
            attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'min': '0',
                'max': '27',
            }
        ),
    )

    class Meta:
        model = EvaluacionInicial
        fields = [
            'situacion_consumo',
            'antecedentes',
            'red_apoyo',
            'condicion_social',
            'riesgo_suicida',
            'violencia',
        ]
        widgets = {
            'situacion_consumo': forms.Textarea(
                attrs={
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                    'rows': 4,
                    'placeholder': 'Describe la situación actual de consumo...',
                }
            ),
            'antecedentes': forms.Textarea(
                attrs={
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                    'rows': 4,
                    'placeholder': 'Antecedentes médicos, psiquiátricos y de consumo...',
                }
            ),
            'red_apoyo': forms.Textarea(
                attrs={
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                    'rows': 3,
                    'placeholder': 'Describe la red de apoyo familiar y social...',
                }
            ),
            'condicion_social': forms.Textarea(
                attrs={
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                    'rows': 3,
                    'placeholder': 'Situación socioeconómica, vivienda, trabajo, educación...',
                }
            ),
            'riesgo_suicida': forms.CheckboxInput(
                attrs={
                    'class': 'rounded border-gray-300 text-red-600 shadow-sm focus:border-red-500 focus:ring-red-500',
                }
            ),
            'violencia': forms.CheckboxInput(
                attrs={
                    'class': 'rounded border-gray-300 text-red-600 shadow-sm focus:border-red-500 focus:ring-red-500',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.tamizajes:
            tamizajes = self.instance.tamizajes
            if 'ASSIST' in tamizajes:
                self.fields['assist_puntaje'].initial = tamizajes['ASSIST'].get('puntaje')
            if 'PHQ9' in tamizajes:
                self.fields['phq9_puntaje'].initial = tamizajes['PHQ9'].get('puntaje')

    def build_tamizajes_payload(self):
        """Mapea los campos del formulario al JSON persistido en el modelo."""
        tamizajes = {}
        fecha_base = timezone.localdate().isoformat()
        if self.instance and self.instance.pk and getattr(self.instance, 'modificado', None):
            fecha_base = self.instance.modificado.date().isoformat()

        assist_puntaje = self.cleaned_data.get('assist_puntaje')
        if assist_puntaje is not None:
            tamizajes['ASSIST'] = {
                'puntaje': assist_puntaje,
                'fecha': fecha_base,
            }

        phq9_puntaje = self.cleaned_data.get('phq9_puntaje')
        if phq9_puntaje is not None:
            tamizajes['PHQ9'] = {
                'puntaje': phq9_puntaje,
                'fecha': fecha_base,
            }

        return tamizajes if tamizajes else None


class PlanIntervencionForm(forms.ModelForm):
    """Formulario para plan de intervención"""

    actividad_1 = forms.CharField(max_length=100, required=False, label="Actividad 1")
    frecuencia_1 = forms.CharField(max_length=50, required=False, label="Frecuencia 1")
    responsable_1 = forms.CharField(max_length=50, required=False, label="Responsable 1")

    actividad_2 = forms.CharField(max_length=100, required=False, label="Actividad 2")
    frecuencia_2 = forms.CharField(max_length=50, required=False, label="Frecuencia 2")
    responsable_2 = forms.CharField(max_length=50, required=False, label="Responsable 2")

    actividad_3 = forms.CharField(max_length=100, required=False, label="Actividad 3")
    frecuencia_3 = forms.CharField(max_length=50, required=False, label="Frecuencia 3")
    responsable_3 = forms.CharField(max_length=50, required=False, label="Responsable 3")

    class Meta:
        model = PlanIntervencion
        fields = ['vigente']
        widgets = {
            'vigente': forms.CheckboxInput(
                attrs={
                    'class': 'rounded border-gray-300 text-indigo-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for index in range(1, 4):
            self.fields[f'actividad_{index}'].widget.attrs.update(
                {
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                    'placeholder': 'Ej: Entrevista individual',
                }
            )
            self.fields[f'frecuencia_{index}'].widget.attrs.update(
                {
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                    'placeholder': 'Ej: Semanal',
                }
            )
            self.fields[f'responsable_{index}'].widget.attrs.update(
                {
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                    'placeholder': 'Ej: Operador',
                }
            )

        if self.instance and self.instance.actividades:
            for i, actividad in enumerate(self.instance.actividades[:3], 1):
                self.fields[f'actividad_{i}'].initial = actividad.get('accion')
                self.fields[f'frecuencia_{i}'].initial = actividad.get('freq')
                self.fields[f'responsable_{i}'].initial = actividad.get('responsable')

    def get_actividades_payload(self):
        actividades = []
        index = 1
        while True:
            if self.is_bound:
                has_activity_slot = any(
                    field_name in self.data
                    for field_name in (
                        f'actividad_{index}',
                        f'frecuencia_{index}',
                        f'responsable_{index}',
                    )
                )
                if not has_activity_slot:
                    break
                accion = (self.data.get(f'actividad_{index}') or '').strip()
                frecuencia = (self.data.get(f'frecuencia_{index}') or '').strip()
                responsable = (self.data.get(f'responsable_{index}') or '').strip()
            else:
                if index > 3:
                    break
                accion = (self.cleaned_data.get(f'actividad_{index}') or '').strip()
                frecuencia = (self.cleaned_data.get(f'frecuencia_{index}') or '').strip()
                responsable = (self.cleaned_data.get(f'responsable_{index}') or '').strip()
            if accion:
                actividades.append(
                    {
                        'accion': accion,
                        'freq': frecuencia,
                        'responsable': responsable,
                    }
                )
            index += 1
        return actividades or None


class SeguimientoForm(forms.ModelForm):
    """Formulario para seguimientos"""

    class Meta:
        model = SeguimientoContacto
        fields = ['tipo', 'descripcion', 'adherencia', 'adjuntos']
        widgets = {
            'tipo': forms.Select(
                attrs={
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                }
            ),
            'descripcion': forms.Textarea(
                attrs={
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                    'rows': 4,
                    'placeholder': 'Describe el contacto o actividad realizada...',
                }
            ),
            'adherencia': forms.Select(
                attrs={
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                }
            ),
            'adjuntos': forms.FileInput(
                attrs={
                    'class': 'mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100',
                }
            ),
        }


class DerivacionForm(forms.ModelForm):
    """Formulario para derivaciones"""

    class Meta:
        model = Derivacion
        fields = ['destino', 'actividad_destino', 'motivo', 'urgencia']
        widgets = {
            'destino': forms.Select(
                attrs={
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                }
            ),
            'actividad_destino': forms.Select(
                attrs={
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                }
            ),
            'motivo': forms.Textarea(
                attrs={
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                    'rows': 4,
                    'placeholder': 'Describe el motivo de la derivación...',
                }
            ),
            'urgencia': forms.Select(
                attrs={
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        kwargs.pop('legajo', None)
        super().__init__(*args, **kwargs)

        self.fields['destino'].queryset = self.fields['destino'].queryset.filter(activo=True)
        self.fields['actividad_destino'].required = False

        from ..models import PlanFortalecimiento

        if self.instance and self.instance.pk and self.instance.destino:
            self.fields['actividad_destino'].queryset = PlanFortalecimiento.objects.filter(
                legajo_institucional__institucion=self.instance.destino,
                estado='ACTIVO',
            )
        elif self.data.get('destino'):
            try:
                destino_id = int(self.data.get('destino'))
                self.fields['actividad_destino'].queryset = PlanFortalecimiento.objects.filter(
                    legajo_institucional__institucion_id=destino_id,
                    estado='ACTIVO',
                )
            except (ValueError, TypeError):
                self.fields['actividad_destino'].queryset = PlanFortalecimiento.objects.none()
        else:
            self.fields['actividad_destino'].queryset = PlanFortalecimiento.objects.none()


class EventoCriticoForm(forms.ModelForm):
    """Formulario para eventos críticos"""

    notificar_familia = forms.BooleanField(required=False, label="Notificar a familia")
    notificar_autoridades = forms.BooleanField(required=False, label="Notificar a autoridades")
    notificar_otros = forms.CharField(max_length=200, required=False, label="Otros notificados")

    class Meta:
        model = EventoCritico
        fields = ['tipo', 'detalle']
        widgets = {
            'tipo': forms.Select(
                attrs={
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                }
            ),
            'detalle': forms.Textarea(
                attrs={
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                    'rows': 4,
                    'placeholder': 'Describe el evento crítico...',
                }
            ),
        }

    def get_notificados_payload(self):
        """Mapea checkboxes del form al JSON persistido en el evento."""
        notificaciones = []
        if self.cleaned_data.get('notificar_familia'):
            notificaciones.append('Familia')
        if self.cleaned_data.get('notificar_autoridades'):
            notificaciones.append('Autoridades')
        if self.cleaned_data.get('notificar_otros'):
            notificaciones.append(self.cleaned_data['notificar_otros'])
        return notificaciones if notificaciones else None


class LegajoCerrarForm(forms.Form):
    """Formulario para cerrar legajo"""

    motivo_cierre = forms.CharField(
        max_length=500,
        required=False,
        label='Motivo de cierre',
        widget=forms.Textarea(
            attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'rows': 3,
                'placeholder': 'Motivo del cierre (opcional)',
            }
        ),
    )


class LegajoReabrirForm(forms.Form):
    """Formulario para reabrir legajo."""

    motivo_reapertura = forms.CharField(
        max_length=500,
        required=True,
        label='Motivo de reapertura',
        widget=forms.Textarea(
            attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
                'rows': 4,
                'placeholder': 'Describa el motivo para reabrir el legajo...',
            }
        ),
    )
