from openai import OpenAI
from django.conf import settings
from django.contrib.auth.models import User
from legajos.models import Ciudadano, InscriptoActividad
import logging
import unicodedata
import re


logger = logging.getLogger(__name__)


class EnhancedChatbotService:
    """Chatbot con fallback local cuando OpenAI no esta disponible."""

    def __init__(self):
        self.client = None
        self.model = "gpt-3.5-turbo"
        self.max_tokens = 500
        self.openai_available = False

        api_key = getattr(settings, "OPENAI_API_KEY", None)
        if api_key:
            try:
                self.client = OpenAI(api_key=api_key)
                self.openai_available = True
            except Exception as exc:
                logger.warning("OpenAI client unavailable, using local fallback: %s", exc)

    def _normalize(self, text):
        cleaned = unicodedata.normalize("NFD", text.lower())
        return "".join(ch for ch in cleaned if unicodedata.category(ch) != "Mn").strip()

    def consultar_ciudadanos(self):
        try:
            total = Ciudadano.objects.count()
            activos = Ciudadano.objects.filter(activo=True).count()
            return f"Total: {total} ciudadanos ({activos} activos)"
        except Exception as exc:
            return f"Error al consultar ciudadanos: {exc}"

    def consultar_usuarios(self):
        try:
            total = User.objects.count()
            activos = User.objects.filter(is_active=True).count()
            return f"Total: {total} usuarios ({activos} activos)"
        except Exception as exc:
            return f"Error al consultar usuarios: {exc}"

    def listar_nombres_ciudadanos(self, limite=5):
        try:
            ciudadanos = Ciudadano.objects.values("nombre", "apellido", "dni")[:limite]
            if not ciudadanos:
                return "No hay ciudadanos cargados todavia."

            nombres = []
            for c in ciudadanos:
                nombre = (c.get("nombre") or "").strip()
                apellido = (c.get("apellido") or "").strip()
                dni = (c.get("dni") or "").strip()
                full_name = f"{nombre} {apellido}".strip() or "Sin nombre"
                if dni:
                    nombres.append(f"- {full_name} (DNI: {dni})")
                else:
                    nombres.append(f"- {full_name}")

            return "Estos son algunos ciudadanos registrados:\n" + "\n".join(nombres)
        except Exception as exc:
            return f"Error al listar ciudadanos: {exc}"

    def consultar_actividad_ciudadano(self, ciudadano):
        try:
            inscripciones = (
                InscriptoActividad.objects
                .filter(ciudadano=ciudadano)
                .select_related("actividad")
                .order_by("-fecha_inscripcion")[:5]
            )
            if not inscripciones:
                return f"{ciudadano.nombre_completo} no tiene actividades registradas."

            lineas = []
            for ins in inscripciones:
                estado = (ins.estado or "").lower()
                actividad = getattr(ins, "actividad", None)
                nombre_act = actividad.nombre if actividad else "Actividad sin nombre"
                lineas.append(f"- {nombre_act} (estado: {estado})")

            return (
                f"{ciudadano.nombre_completo} tiene {len(inscripciones)} actividad(es) registrada(s):\n"
                + "\n".join(lineas)
            )
        except Exception as exc:
            return f"Error al consultar actividades: {exc}"

    def _history_topic(self, conversation_history):
        if not conversation_history:
            return None

        for msg in reversed(conversation_history):
            content = self._normalize(getattr(msg, "content", ""))
            if not content:
                continue
            if any(k in content for k in ["ciudadano", "ciudadanos", "legajo", "legajos"]):
                return "ciudadanos"
            if any(k in content for k in ["usuario", "usuarios"]):
                return "usuarios"
        return None

    def _extract_last_dni_from_history(self, conversation_history):
        if not conversation_history:
            return None
        for msg in reversed(conversation_history):
            content = getattr(msg, "content", "") or ""
            found = re.findall(r"\b\d{7,10}\b", content)
            if found:
                return found[-1]
        return None

    def fallback_local_response(self, message, conversation_history=None):
        msg = self._normalize(message)
        topic = self._history_topic(conversation_history)
        dni_en_historial = self._extract_last_dni_from_history(conversation_history)

        if any(word in msg for word in ["hola", "buenos dias", "buenas tardes", "buenas noches", "hey"]):
            return "Hola, soy el Asistente NODO. Puedo ayudarte con ciudadanos, usuarios y estadisticas."

        ciudadanos_keywords = ["ciudadano", "ciudadanos", "legajo", "legajos"]
        count_keywords = ["cuantos", "cuantas", "cantidad", "total", "tenemos", "hay"]
        name_intent = any(k in msg for k in ["nombre", "nombres", "como se llama", "quien", "quienes"])
        count_ciudadanos = any(k in msg for k in ciudadanos_keywords) and any(k in msg for k in count_keywords)

        if count_ciudadanos and name_intent:
            return f"{self.consultar_ciudadanos()}\n{self.listar_nombres_ciudadanos()}"

        if count_ciudadanos:
            return self.consultar_ciudadanos()

        if any(k in msg for k in ["usuario", "usuarios"]) and any(k in msg for k in count_keywords):
            return self.consultar_usuarios()

        if name_intent:
            if any(k in msg for k in ciudadanos_keywords):
                return self.listar_nombres_ciudadanos()
            if (
                "cual es el nombre" in msg
                or "cuales son los nombres" in msg
                or "cual es su nombre" in msg
                or "cuales son sus nombres" in msg
                or (topic == "ciudadanos" and any(k in msg for k in ["su", "sus"]))
            ):
                return self.listar_nombres_ciudadanos()

        if any(k in msg for k in ["listar ciudadanos", "mostrar ciudadanos", "mostrame ciudadanos"]):
            return self.listar_nombres_ciudadanos()

        actividad_intent = any(
            k in msg for k in ["actividad", "actividades", "taller", "programa", "inscripto", "inscripta", "inscrito"]
        )
        referencia_ciudadano = any(k in msg for k in ["ese ciudadano", "esa ciudadana", "ese", "esa", "su", "sus"])
        if actividad_intent and (topic == "ciudadanos" or referencia_ciudadano):
            ciudadano = None
            if dni_en_historial:
                ciudadano = Ciudadano.objects.filter(dni=str(dni_en_historial)).first()
            if not ciudadano:
                ciudadano = Ciudadano.objects.order_by("id").first()
            if ciudadano:
                return self.consultar_actividad_ciudadano(ciudadano)
            return "No encuentro ciudadanos para validar actividades."

        return None

    def get_system_context(self):
        stats = f"""
Estadisticas del sistema:
- {self.consultar_ciudadanos()}
- {self.consultar_usuarios()}
"""
        return f"""
Eres un asistente del Sistema SEDRONAR.

{stats}

Responde de forma amigable y profesional.
"""

    def generate_response(self, message, conversation_history=None):
        try:
            local_response = self.fallback_local_response(message, conversation_history)
            if local_response:
                return {"content": local_response, "tokens_used": 0}

            if not self.openai_available:
                return {
                    "content": (
                        "Puedo ayudarte con consultas como: "
                        "'cuantos ciudadanos hay', 'cuantos usuarios hay', "
                        "'mostrame nombres de ciudadanos'."
                    ),
                    "tokens_used": 0,
                }

            messages = [{"role": "system", "content": self.get_system_context()}]
            if conversation_history:
                history_slice = conversation_history[-10:]
                for msg in history_slice:
                    role = getattr(msg, "role", None)
                    content = getattr(msg, "content", None)
                    if role in ("user", "assistant") and content:
                        messages.append({"role": role, "content": content})
            messages.append({"role": "user", "content": message})

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=0.7,
            )

            return {
                "content": response.choices[0].message.content,
                "tokens_used": response.usage.total_tokens,
            }
        except Exception as exc:
            logger.warning("OpenAI response failed, using local fallback: %s", exc)
            local_response = self.fallback_local_response(message, conversation_history)
            if local_response:
                return {"content": local_response, "tokens_used": 0, "error": str(exc)}
            return {
                "content": (
                    "No pude procesar esa consulta con IA en este momento. "
                    "Puedo ayudarte con ciudadanos, usuarios y actividades."
                ),
                "tokens_used": 0,
                "error": str(exc),
            }
