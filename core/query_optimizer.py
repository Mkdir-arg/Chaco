# core/query_optimizer.py
"""
Optimizador automático de consultas ORM
"""
from django.db import connection
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

class QueryOptimizer:
    """Optimiza consultas ORM automáticamente"""
    
    @staticmethod
    def optimize_queryset(queryset, cache_key=None, timeout=300):
        """Optimiza queryset con select_related y prefetch_related automático"""
        model = queryset.model
        
        # Auto-detectar ForeignKey para select_related
        foreign_keys = []
        for field in model._meta.fields:
            if field.many_to_one and not field.null:
                foreign_keys.append(field.name)
        
        if foreign_keys:
            queryset = queryset.select_related(*foreign_keys)
        
        # Auto-detectar ManyToMany para prefetch_related
        many_to_many = []
        for field in model._meta.many_to_many:
            many_to_many.append(field.name)
        
        if many_to_many:
            queryset = queryset.prefetch_related(*many_to_many)
        
        # Cache si se especifica
        if cache_key:
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            result = list(queryset)
            cache.set(cache_key, result, timeout)
            return result
        
        return queryset
    
    @staticmethod
    def get_slow_queries():
        """Obtiene queries lentas para análisis"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT query_time, sql_text 
                FROM mysql.slow_log 
                WHERE query_time > 1 
                ORDER BY query_time DESC 
                LIMIT 10
            """)
            return cursor.fetchall()
    
    @staticmethod
    def analyze_query_performance():
        """Analiza performance de queries"""
        queries = connection.queries
        slow_queries = [q for q in queries if float(q['time']) > 0.1]
        
        if slow_queries:
            logger.warning(f"Found {len(slow_queries)} slow queries")
            for query in slow_queries[:5]:  # Top 5
                logger.warning(f"Slow query ({query['time']}s): {query['sql'][:100]}...")
        
        return {
            'total_queries': len(queries),
            'slow_queries': len(slow_queries),
            'avg_time': sum(float(q['time']) for q in queries) / len(queries) if queries else 0
        }