"""
Motor de ejecución de flujos (FlowRuntime).
Maneja el ciclo de vida de instancias: inicio y avance de nodos.
"""
import logging

from django.db import transaction
from django.utils import timezone

from .models import InstanciaFlujo, InstanciaLog

logger = logging.getLogger(__name__)

# Tipos de nodo reconocidos
TIPO_INICIO = 'inicio'
TIPO_FIN = 'fin'
TIPO_ACCION_HUMANA = 'accion_humana'
TIPO_ESPERA = 'espera'
TIPO_DECISION = 'decision'


class FlowRuntime:
    """
    Runtime del motor de flujos.
    Controla el avance de instancias a través de los nodos definidos en VersionFlujo.definicion.

    Contrato JSON de definición de flujo:
    {
        "nodos": [{"id": "n1", "tipo": "inicio", "nombre": "Admisión", "config": {}}],
        "transiciones": [{"desde": "n1", "hasta": "n2", "condicion": null}]
    }

    La condición tiene la forma: {"campo": "x", "operador": "==", "valor": "y"}
    Operadores soportados: ==, !=, >, >=, <, <=, in
    condicion=null implica transición libre (siempre se toma).
    """

    @staticmethod
    @transaction.atomic
    def iniciar(inscripcion) -> InstanciaFlujo:
        """
        Inicia el flujo para una inscripción a programa.
        Crea la InstanciaFlujo en el nodo de inicio y registra el log inicial.
        Si el nodo inicio tiene transición libre, avanza automáticamente.

        Raises:
            ValueError: si el programa no tiene flujo activo o ya hay una instancia.
        """
        version_activa = inscripcion.programa.flujo_activo
        if not version_activa:
            raise ValueError(
                f'El programa "{inscripcion.programa.nombre}" no tiene un flujo publicado.'
            )

        if InstanciaFlujo.objects.filter(inscripcion=inscripcion).exists():
            raise ValueError(
                f'La inscripción {inscripcion.pk} ya tiene una instancia de flujo activa.'
            )

        definicion = version_activa.definicion
        nodo_inicio = FlowRuntime._buscar_nodo_por_tipo(definicion, TIPO_INICIO)
        if not nodo_inicio:
            raise ValueError('El flujo no tiene un nodo de tipo "inicio".')

        instancia = InstanciaFlujo.objects.create(
            inscripcion=inscripcion,
            version_flujo=version_activa,
            nodo_actual=nodo_inicio['id'],
        )
        InstanciaLog.objects.create(
            instancia=instancia,
            nodo_desde='',
            nodo_hasta=nodo_inicio['id'],
            motivo='Inicio de flujo',
        )

        # Si hay transición libre desde el nodo inicio, avanzar
        transicion_libre = FlowRuntime._buscar_transicion_libre(definicion, nodo_inicio['id'])
        if transicion_libre:
            instancia = FlowRuntime.avanzar(instancia, datos={}, usuario=None)

        return instancia

    @staticmethod
    @transaction.atomic
    def avanzar(instancia: InstanciaFlujo, datos: dict, usuario=None) -> InstanciaFlujo:
        """
        Avanza la instancia al siguiente nodo evaluando las condiciones de transición.

        Args:
            instancia: la InstanciaFlujo a avanzar.
            datos: datos del contexto para evaluar condiciones.
            usuario: usuario que dispara el avance (puede ser None para avances automáticos).

        Returns:
            InstanciaFlujo actualizada.

        Raises:
            ValueError: si no hay transición válida disponible o la instancia no está activa.
        """
        if instancia.estado != InstanciaFlujo.Estado.ACTIVA:
            raise ValueError(
                f'La instancia {instancia.pk} no está activa (estado: {instancia.estado}).'
            )

        definicion = instancia.version_flujo.definicion
        nodo_destino = FlowRuntime._evaluar_transiciones(
            definicion, instancia.nodo_actual, datos
        )
        if nodo_destino is None:
            raise ValueError(
                f'No hay transición válida desde el nodo "{instancia.nodo_actual}".'
            )

        nodo_desde = instancia.nodo_actual
        instancia.nodo_actual = nodo_destino['id']

        if nodo_destino['tipo'] == TIPO_FIN:
            instancia.estado = InstanciaFlujo.Estado.COMPLETADA
            instancia.fecha_cierre = timezone.now()

        instancia.save(update_fields=['nodo_actual', 'estado', 'fecha_cierre'])

        InstanciaLog.objects.create(
            instancia=instancia,
            nodo_desde=nodo_desde,
            nodo_hasta=nodo_destino['id'],
            usuario=usuario,
            datos_transicion=datos,
        )

        if nodo_destino['tipo'] == TIPO_ACCION_HUMANA:
            FlowRuntime._notificar_accion_humana(instancia, nodo_destino)

        return instancia

    # ------------------------------------------------------------------
    # Métodos internos
    # ------------------------------------------------------------------

    @staticmethod
    def _buscar_nodo_por_tipo(definicion: dict, tipo: str) -> dict | None:
        for nodo in definicion.get('nodos', []):
            if nodo.get('tipo') == tipo:
                return nodo
        return None

    @staticmethod
    def _buscar_nodo_por_id(definicion: dict, nodo_id: str) -> dict | None:
        for nodo in definicion.get('nodos', []):
            if nodo.get('id') == nodo_id:
                return nodo
        return None

    @staticmethod
    def _buscar_transicion_libre(definicion: dict, nodo_id: str) -> dict | None:
        for t in definicion.get('transiciones', []):
            if t.get('desde') == nodo_id and t.get('condicion') is None:
                return t
        return None

    @staticmethod
    def _evaluar_transiciones(definicion: dict, nodo_actual_id: str, datos: dict) -> dict | None:
        """
        Evalúa las transiciones disponibles desde el nodo actual y devuelve el nodo destino.
        Estrategia: evalúa primero las transiciones condicionales; si ninguna matchea,
        usa la transición libre (condicion=null) como fallback.
        Esto permite que los nodos `decision` tengan un camino por defecto sin que
        bloquee la evaluación de condiciones.
        """
        transiciones = [
            t for t in definicion.get('transiciones', [])
            if t.get('desde') == nodo_actual_id
        ]

        # 1. Evaluar condicionales primero
        for transicion in transiciones:
            if transicion.get('condicion') is not None:
                if FlowRuntime._evaluar_condicion(transicion['condicion'], datos):
                    nodo_destino = FlowRuntime._buscar_nodo_por_id(definicion, transicion['hasta'])
                    if nodo_destino:
                        return nodo_destino

        # 2. Fallback: transición libre
        for transicion in transiciones:
            if transicion.get('condicion') is None:
                nodo_destino = FlowRuntime._buscar_nodo_por_id(definicion, transicion['hasta'])
                if nodo_destino:
                    return nodo_destino

        return None

    @staticmethod
    def _evaluar_condicion(condicion: dict | None, datos: dict) -> bool:
        """
        Evalúa una condición simple contra los datos del contexto.
        condicion=None → transición libre, siempre True.
        """
        if condicion is None:
            return True

        campo = condicion.get('campo')
        operador = condicion.get('operador')
        valor = condicion.get('valor')

        if campo not in datos:
            return False

        valor_dato = datos[campo]

        try:
            if operador == '==':
                return valor_dato == valor
            elif operador == '!=':
                return valor_dato != valor
            elif operador == '>':
                return valor_dato > valor
            elif operador == '>=':
                return valor_dato >= valor
            elif operador == '<':
                return valor_dato < valor
            elif operador == '<=':
                return valor_dato <= valor
            elif operador == 'in':
                return valor_dato in valor
        except (TypeError, ValueError):
            return False

        return False

    @staticmethod
    def _notificar_accion_humana(instancia: InstanciaFlujo, nodo: dict) -> None:
        """Notificación best-effort al llegar a un nodo de acción humana."""
        try:
            logger.info(
                'Flujo %s — instancia %s requiere acción humana en nodo "%s" (%s)',
                instancia.version_flujo.flujo.nombre,
                instancia.pk,
                nodo.get('nombre', nodo['id']),
                nodo['id'],
            )
        except Exception:
            pass
