from django.db import models


DIAS_SEMANA = [
    (0, 'Lunes'),
    (1, 'Martes'),
    (2, 'Miércoles'),
    (3, 'Jueves'),
    (4, 'Viernes'),
    (5, 'Sábado'),
    (6, 'Domingo'),
]


class ConfiguracionTurnos(models.Model):
    """
    Configuración de turnos reutilizable que puede asociarse a cualquier entidad
    del sistema: Programa, Institución, Actividad Institucional o Recurso genérico.
    """

    class ModoTurno(models.TextChoices):
        AUTO = 'AUTO', 'Automático (ciudadano elige slot)'
        MANUAL = 'MANUAL', 'Manual (operador asigna)'
        AMBOS = 'AMBOS', 'Ambos'

    nombre = models.CharField(max_length=200, verbose_name='Nombre')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    requiere_aprobacion = models.BooleanField(
        default=False,
        verbose_name='Requiere aprobación',
        help_text='Si está activo, el turno queda pendiente hasta ser confirmado por el backoffice.',
    )
    modo_turno = models.CharField(
        max_length=10,
        choices=ModoTurno.choices,
        default=ModoTurno.AUTO,
        verbose_name='Modo de asignación',
    )
    anticipacion_minima_hs = models.PositiveIntegerField(
        default=24,
        verbose_name='Anticipación mínima (horas)',
        help_text='Horas mínimas de anticipación para reservar un turno.',
    )
    anticipacion_maxima_dias = models.PositiveIntegerField(
        default=30,
        verbose_name='Anticipación máxima (días)',
        help_text='Hasta cuántos días en el futuro puede reservarse un turno.',
    )
    permite_cancelacion_ciudadano = models.BooleanField(
        default=True,
        verbose_name='Permite cancelación por ciudadano',
    )
    cancelacion_hasta_hs = models.PositiveIntegerField(
        default=24,
        verbose_name='Cancelación hasta (horas antes)',
        help_text='El ciudadano puede cancelar hasta X horas antes del turno.',
    )
    creado = models.DateTimeField(auto_now_add=True)
    modificado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuración de turnos'
        verbose_name_plural = 'Configuraciones de turnos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    @property
    def entidad_origen(self):
        """Retorna la entidad a la que pertenece esta configuración, si existe."""
        if hasattr(self, 'programa'):
            return ('programa', self.programa)
        if hasattr(self, 'institucion'):
            return ('institucion', self.institucion)
        if hasattr(self, 'planfortalecimiento'):
            return ('actividad', self.planfortalecimiento)
        if hasattr(self, 'recursoturnos'):
            return ('recurso', self.recursoturnos)
        return (None, None)


class DisponibilidadConfiguracion(models.Model):
    """Franja horaria semanal para una ConfiguracionTurnos."""

    configuracion = models.ForeignKey(
        ConfiguracionTurnos,
        on_delete=models.CASCADE,
        related_name='disponibilidades',
        verbose_name='Configuración',
    )
    dia_semana = models.IntegerField(choices=DIAS_SEMANA, verbose_name='Día de la semana')
    hora_inicio = models.TimeField(verbose_name='Hora de inicio')
    hora_fin = models.TimeField(verbose_name='Hora de fin')
    duracion_turno_min = models.PositiveIntegerField(
        default=30,
        verbose_name='Duración del turno (minutos)',
    )
    cupo_maximo = models.PositiveIntegerField(
        default=1,
        verbose_name='Cupo máximo por slot',
    )
    activo = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        verbose_name = 'Disponibilidad'
        verbose_name_plural = 'Disponibilidades'
        ordering = ['dia_semana', 'hora_inicio']
        unique_together = [['configuracion', 'dia_semana', 'hora_inicio']]

    def __str__(self):
        return (
            f'{self.configuracion.nombre} — {self.get_dia_semana_display()} '
            f'{self.hora_inicio:%H:%M}–{self.hora_fin:%H:%M}'
        )

    @property
    def slots_preview(self):
        """Cantidad de slots que genera esta franja."""
        from datetime import datetime, timedelta
        inicio = datetime.combine(datetime.today(), self.hora_inicio)
        fin = datetime.combine(datetime.today(), self.hora_fin)
        duracion = timedelta(minutes=self.duracion_turno_min)
        if duracion.seconds == 0:
            return 0
        count = 0
        while inicio + duracion <= fin:
            count += 1
            inicio += duracion
        return count
