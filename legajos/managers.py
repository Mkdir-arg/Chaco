from django.db import models
from django.db.models import Count, Prefetch, Q


class OptimizedLegajoManager(models.Manager):
    """Manager optimizado para LegajoAtencion con queries preoptimizadas"""
    
    def with_full_relations(self):
        """Query completa con todas las relaciones optimizadas"""
        return self.select_related(
            'ciudadano',
            'dispositivo',
            'responsable'
        ).prefetch_related(
            'seguimientos__profesional__usuario',
            'derivaciones__origen',
            'derivaciones__destino',
            'eventos',
            'planes__profesional__usuario'
        ).annotate(
            seguimientos_count=Count('seguimientos'),
            eventos_count=Count('eventos'),
            derivaciones_count=Count('derivaciones')
        )
    
    def for_dashboard(self):
        """Query optimizada para dashboard"""
        return self.select_related(
            'ciudadano',
            'dispositivo',
            'responsable'
        ).annotate(
            seguimientos_count=Count('seguimientos'),
            eventos_count=Count('eventos')
        )
    
    def for_list_view(self):
        """Query optimizada para vistas de lista"""
        return self.select_related(
            'ciudadano',
            'dispositivo',
            'responsable'
        ).annotate(
            seguimientos_count=Count('seguimientos')
        )
    
    def activos(self):
        """Legajos activos con optimizaciones"""
        return self.for_list_view().filter(
            estado__in=['ABIERTO', 'EN_SEGUIMIENTO']
        )
    
    def con_riesgo_alto(self):
        """Legajos con riesgo alto optimizados"""
        return self.for_dashboard().filter(
            nivel_riesgo='ALTO'
        )


class OptimizedCiudadanoManager(models.Manager):
    """Manager optimizado para Ciudadano"""
    
    def with_legajos_info(self):
        """Ciudadanos con información de legajos optimizada"""
        return self.prefetch_related(
            Prefetch(
                'legajos',
                queryset=models.get_model('legajos', 'LegajoAtencion').objects.select_related(
                    'dispositivo', 'responsable'
                )
            )
        ).annotate(
            legajos_count=Count('legajos'),
            legajos_activos_count=Count(
                'legajos',
                filter=Q(legajos__estado__in=['ABIERTO', 'EN_SEGUIMIENTO'])
            )
        )
    
    def activos(self):
        """Ciudadanos activos con optimizaciones básicas"""
        return self.filter(activo=True).annotate(
            legajos_count=Count('legajos')
        )


class OptimizedInstitucionManager(models.Manager):
    """Manager optimizado para Institucion"""
    
    def with_full_info(self):
        """Instituciones con información completa optimizada"""
        return self.select_related(
            'provincia',
            'municipio', 
            'localidad'
        ).prefetch_related(
            'encargados',
            'documentos'
        ).annotate(
            legajos_count=Count('legajos'),
            encargados_count=Count('encargados')
        )
    
    def aprobadas(self):
        """Instituciones aprobadas con optimizaciones"""
        return self.with_full_info().filter(
            estado_registro='APROBADO'
        )
    
    def activas(self):
        """Instituciones activas con optimizaciones"""
        return self.with_full_info().filter(
            activo=True,
            estado_registro='APROBADO'
        )


class OptimizedAlertaManager(models.Manager):
    """Manager optimizado para AlertaCiudadano"""
    
    def activas_completas(self):
        """Alertas activas con relaciones completas"""
        return self.select_related(
            'ciudadano',
            'legajo__ciudadano',
            'legajo__dispositivo',
            'cerrada_por'
        ).filter(activa=True)
    
    def por_prioridad(self, prioridad):
        """Alertas por prioridad optimizadas"""
        return self.activas_completas().filter(prioridad=prioridad)
    
    def criticas(self):
        """Alertas críticas optimizadas"""
        return self.por_prioridad('CRITICA')


class OptimizedSeguimientoManager(models.Manager):
    """Manager optimizado para SeguimientoContacto"""
    
    def with_relations(self):
        """Seguimientos con relaciones optimizadas"""
        return self.select_related(
            'legajo__ciudadano',
            'legajo__dispositivo',
            'profesional__usuario'
        )
    
    def recientes(self, dias=30):
        """Seguimientos recientes optimizados"""
        from datetime import datetime, timedelta
        fecha_limite = datetime.now().date() - timedelta(days=dias)
        return self.with_relations().filter(
            creado__date__gte=fecha_limite
        )


class OptimizedDerivacionManager(models.Manager):
    """Manager optimizado para Derivacion"""
    
    def with_full_relations(self):
        """Derivaciones con relaciones completas"""
        return self.select_related(
            'legajo__ciudadano',
            'legajo__dispositivo',
            'origen',
            'destino',
            'actividad_destino'
        )
    
    def pendientes(self):
        """Derivaciones pendientes optimizadas"""
        return self.with_full_relations().filter(estado='PENDIENTE')
    
    def por_urgencia(self, urgencia):
        """Derivaciones por urgencia optimizadas"""
        return self.with_full_relations().filter(urgencia=urgencia)