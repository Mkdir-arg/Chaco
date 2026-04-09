from datetime import datetime

from django import forms
from django.core.exceptions import ValidationError

from ..models import ConfiguracionTurnos, DisponibilidadConfiguracion


class ConfiguracionTurnosForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionTurnos
        fields = [
            "nombre",
            "activo",
            "requiere_aprobacion",
            "modo_turno",
            "anticipacion_minima_hs",
            "anticipacion_maxima_dias",
            "permite_cancelacion_ciudadano",
            "cancelacion_hasta_hs",
        ]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-input w-full rounded-lg border-gray-300"}),
            "modo_turno": forms.Select(attrs={"class": "form-select w-full rounded-lg border-gray-300"}),
            "anticipacion_minima_hs": forms.NumberInput(
                attrs={"class": "form-input w-full rounded-lg border-gray-300", "min": 0}
            ),
            "anticipacion_maxima_dias": forms.NumberInput(
                attrs={"class": "form-input w-full rounded-lg border-gray-300", "min": 1}
            ),
            "cancelacion_hasta_hs": forms.NumberInput(
                attrs={"class": "form-input w-full rounded-lg border-gray-300", "min": 0}
            ),
        }


class DisponibilidadConfiguracionForm(forms.ModelForm):
    class Meta:
        model = DisponibilidadConfiguracion
        fields = ["dia_semana", "hora_inicio", "hora_fin", "duracion_turno_min", "cupo_maximo", "activo"]
        widgets = {
            "dia_semana": forms.Select(attrs={"class": "form-select w-full rounded-lg border-gray-300"}),
            "hora_inicio": forms.TimeInput(
                attrs={"type": "time", "class": "form-input w-full rounded-lg border-gray-300"}
            ),
            "hora_fin": forms.TimeInput(
                attrs={"type": "time", "class": "form-input w-full rounded-lg border-gray-300"}
            ),
            "duracion_turno_min": forms.NumberInput(
                attrs={"class": "form-input w-full rounded-lg border-gray-300", "min": 5, "step": 5}
            ),
            "cupo_maximo": forms.NumberInput(
                attrs={"class": "form-input w-full rounded-lg border-gray-300", "min": 1}
            ),
        }

    def clean(self):
        cleaned = super().clean()
        hora_inicio = cleaned.get("hora_inicio")
        hora_fin = cleaned.get("hora_fin")
        duracion = cleaned.get("duracion_turno_min")

        if hora_inicio and hora_fin:
            if hora_fin <= hora_inicio:
                raise ValidationError("La hora de fin debe ser posterior a la hora de inicio.")

            if duracion:
                inicio_dt = datetime.combine(datetime.today(), hora_inicio)
                fin_dt = datetime.combine(datetime.today(), hora_fin)
                minutos_totales = int((fin_dt - inicio_dt).total_seconds() / 60)
                cleaned["_slots_preview"] = minutos_totales // duracion
                cleaned["_resto_min"] = minutos_totales % duracion

        return cleaned


class AprobarTurnoForm(forms.Form):
    notas = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "class": "form-textarea w-full rounded-lg border-gray-300",
                "placeholder": "Notas internas opcionales...",
            }
        ),
        label="Notas internas",
    )


class RechazarTurnoForm(forms.Form):
    motivo = forms.CharField(
        required=True,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "class": "form-textarea w-full rounded-lg border-gray-300",
                "placeholder": "Motivo de rechazo (visible para el ciudadano)...",
            }
        ),
        label="Motivo de rechazo",
    )


class CancelarTurnoBackofficeForm(forms.Form):
    motivo = forms.CharField(
        required=True,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "class": "form-textarea w-full rounded-lg border-gray-300",
                "placeholder": "Motivo de cancelación (visible para el ciudadano)...",
            }
        ),
        label="Motivo de cancelación",
    )
