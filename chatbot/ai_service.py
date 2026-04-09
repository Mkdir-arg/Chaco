from openai import OpenAI
from django.conf import settings
from django.contrib.auth.models import User
from legajos.models import Ciudadano
from .models import ChatbotKnowledge


class ChatbotAIService:
    def __init__(self):
        api_key = settings.OPENAI_API_KEY
        if api_key:
            self.client = OpenAI(api_key=api_key)
            self.model = "gpt-3.5-turbo"
            self.max_tokens = 500
            self.openai_available = True
        else:
            self.client = None
            self.openai_available = False
    
    def get_system_context(self):
        """Obtiene contexto del sistema SEDRONAR"""
        context = """
        Eres un asistente virtual del Sistema SEDRONAR (Secretaría Nacional de Políticas Integrales sobre Drogas).
        
        FUNCIONALIDADES DEL SISTEMA:
        - Gestión de Ciudadanos: Registro y seguimiento de personas
        - Legajos: Historiales detallados de atención
        - Usuarios: Administración de personal del sistema
        - Dashboard: Estadísticas y reportes
        
        INSTRUCCIONES:
        - Responde solo sobre funcionalidades del sistema SEDRONAR
        - Sé conciso y profesional
        - Si no sabes algo, sugiere contactar al administrador
        - No proporciones información personal de ciudadanos
        """
        
        # Agregar conocimiento personalizado (optimizado)
        knowledge = ChatbotKnowledge.objects.filter(is_active=True).only('title', 'content')
        if knowledge.exists():
            context += "\n\nCONOCIMIENTO ADICIONAL:\n"
            for item in knowledge:
                context += f"- {item.title}: {item.content}\n"
        
        return context
    
    def get_system_stats(self):
        """Obtiene estadísticas completas del sistema"""
        try:
            from django.db.models import Count, Q
            from core.models import Institucion
            from legajos.models import PlanFortalecimiento, InscriptoActividad
            
            stats = {
                'ciudadanos': Ciudadano.objects.count(),
                'legajos': Ciudadano.objects.filter(legajos__isnull=False).distinct().count(),
                'instituciones': Institucion.objects.filter(activo=True).count(),
                'actividades': PlanFortalecimiento.objects.filter(estado='ACTIVO').count(),
                'usuarios': User.objects.count()
            }
            
            return f"""Estadísticas del sistema SEDRONAR:
- {stats['ciudadanos']} ciudadanos registrados
- {stats['legajos']} ciudadanos con legajos activos
- {stats['instituciones']} instituciones activas
- {stats['actividades']} actividades/programas activos
- {stats['usuarios']} usuarios del sistema"""
        except Exception as e:
            return f"Error obteniendo estadísticas: {str(e)}"
    
    def query_database(self, question):
        """Consulta la base de datos según la pregunta"""
        try:
            from django.db.models import Count, Q
            from core.models import Institucion
            from legajos.models import PlanFortalecimiento, InscriptoActividad, LegajoAtencion
            
            question_lower = question.lower().strip()
            
            # Respuestas a saludos comunes
            saludos = ['hola', 'buenos dias', 'buenas tardes', 'buenas noches', 'buen dia', 'hey', 'hi']
            if any(saludo in question_lower for saludo in saludos) and len(question_lower) < 20:
                return "¡Hola! Soy el Asistente NODO del sistema SEDRONAR. Puedo ayudarte con:\n\n• Consultar cuántos ciudadanos hay registrados\n• Ver cuántas instituciones tenemos\n• Conocer las actividades por institución\n• Verificar si un ciudadano participa en actividades\n\n¿En qué puedo ayudarte?"
            
            # Detectar tipo de consulta
            if 'cuantos ciudadanos' in question_lower or 'cuántos ciudadanos' in question_lower:
                count = Ciudadano.objects.count()
                return f"Actualmente hay {count} ciudadanos registrados en el sistema."
            
            elif 'cuantos legajos' in question_lower or 'cuántos legajos' in question_lower:
                count = LegajoAtencion.objects.count()
                return f"Hay {count} legajos de atención registrados en el sistema."
            
            elif 'cuantas instituciones' in question_lower or 'cuántas instituciones' in question_lower:
                count = Institucion.objects.filter(activo=True).count()
                return f"Hay {count} instituciones activas en la red SEDRONAR."
            
            elif 'cuantas actividades' in question_lower or 'cuántas actividades' in question_lower:
                if 'por institucion' in question_lower or 'por institución' in question_lower:
                    # Actividades por institución
                    instituciones = Institucion.objects.filter(activo=True).annotate(
                        num_actividades=Count('legajo_institucional__planes_fortalecimiento', 
                                            filter=Q(legajo_institucional__planes_fortalecimiento__estado='ACTIVO'))
                    ).filter(num_actividades__gt=0)
                    
                    if instituciones.exists():
                        resultado = "Actividades por institución:\n"
                        for inst in instituciones:
                            resultado += f"- {inst.nombre}: {inst.num_actividades} actividades\n"
                        return resultado
                    else:
                        return "No hay instituciones con actividades activas registradas."
                else:
                    count = PlanFortalecimiento.objects.filter(estado='ACTIVO').count()
                    return f"Hay {count} actividades/programas activos en total."
            
            elif 'participa' in question_lower and ('actividad' in question_lower or 'institucion' in question_lower or 'institución' in question_lower):
                # Buscar DNI o nombre en la pregunta
                import re
                dni_match = re.search(r'\b\d{7,8}\b', question)
                
                if dni_match:
                    dni = dni_match.group()
                    try:
                        ciudadano = Ciudadano.objects.get(dni=dni)
                        inscripciones = InscriptoActividad.objects.filter(
                            ciudadano=ciudadano,
                            estado__in=['INSCRITO', 'ACTIVO']
                        ).select_related('actividad', 'actividad__legajo_institucional__institucion')
                        
                        if inscripciones.exists():
                            resultado = f"{ciudadano.nombre_completo} (DNI: {dni}) participa en:\n"
                            for insc in inscripciones:
                                inst = insc.actividad.legajo_institucional.institucion
                                resultado += f"- {insc.actividad.nombre} en {inst.nombre}\n"
                            return resultado
                        else:
                            return f"{ciudadano.nombre_completo} (DNI: {dni}) no está inscrito en ninguna actividad actualmente."
                    except Ciudadano.DoesNotExist:
                        return f"No se encontró ningún ciudadano con DNI {dni}."
                else:
                    return "Por favor, proporciona el DNI del ciudadano para consultar su participación en actividades."
            
            return None  # No se pudo responder con consulta directa
            
        except Exception as e:
            return None  # Dejar que OpenAI maneje el error
    
    def generate_response(self, message, conversation_history=None):
        """Genera respuesta usando OpenAI o consultas directas"""
        try:
            # Primero intentar responder con consulta directa a la BD
            db_response = self.query_database(message)
            if db_response:
                return {
                    'content': db_response,
                    'tokens_used': 0
                }
            
            # Si OpenAI no está disponible, respuesta por defecto
            if not self.openai_available:
                return {
                    'content': '¡Hola! Soy el Asistente NODO. Puedo ayudarte con consultas sobre el sistema SEDRONAR. Prueba preguntarme: "¿Cuántos ciudadanos tenemos?" o "¿Cuántas instituciones hay?"',
                    'tokens_used': 0
                }
            
            # Si no se puede responder directamente, usar OpenAI
            system_prompt = self.get_system_context()
            stats = self.get_system_stats()
            
            messages = [
                {"role": "system", "content": f"{system_prompt}\n\n{stats}"}
            ]
            
            # Agregar historial de conversación (últimos 5 mensajes)
            if conversation_history:
                # Optimizar acceso a mensajes con only() si es QuerySet
                if hasattr(conversation_history, 'only'):
                    history_msgs = conversation_history.only('role', 'content')[-5:]
                else:
                    history_msgs = conversation_history[-5:]
                    
                for msg in history_msgs:
                    messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })
            
            # Agregar mensaje actual
            messages.append({"role": "user", "content": message})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=0.7
            )
            
            return {
                'content': response.choices[0].message.content,
                'tokens_used': response.usage.total_tokens
            }
            
        except Exception as e:
            # Respuesta de fallback amigable
            return {
                'content': '¡Hola! Soy el Asistente NODO. Puedo ayudarte con información del sistema SEDRONAR. Pregúntame sobre ciudadanos, instituciones o actividades.',
                'tokens_used': 0,
                'error': str(e)
            }