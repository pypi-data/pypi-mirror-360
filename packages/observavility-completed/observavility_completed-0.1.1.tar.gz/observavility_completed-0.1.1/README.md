Trazabilidad Distribuida
Propósito: Configura OpenTelemetry para rastrear requests a través de múltiples servicios.
Funcionalidades:

- Instrumentación automática de FastAPI, SQLAlchemy, requests HTTP y httpx
  Exportación de trazas a un sistema de observabilidad (Tempo por defecto)
  Configuración centralizada que solo se ejecuta una vez por proceso (usando @lru_cache)
  Identificación de servicios mediante variables de entorno o parámetros

😴 Dormir bien sabiendo que:

Si algo se rompe, lo encontrarás rápido
Tus decisiones están basadas en datos, no en intuición
Tu código es profesional y mantenible
Tu equipo te ve como el/la ninja de debugging

Qué rastrea:

Requests HTTP entrantes y salientes
Consultas a base de datos
Operaciones entre microservicios

logger.py - Logging Estructurado
Propósito: Proporciona logs estructurados en formato JSON con correlación de trazas.
Funcionalidades:

- Logs en JSON para facilitar análisis y búsquedas
  Correlación automática con trazas OpenTelemetry (agrega trace_id y span_id)
  Configuración estándar con timestamps ISO, niveles de log y manejo de excepciones
  Cache de loggers para evitar reconfiguración

- Caso de Uso Típico:
  En tu aplicación FastAPI

from common_utils.tracing import setup_tracing
from common_utils.logger import get_logger

# Configuración inicial (una sola vez) 🚀🚀🚀🚀🚀

setup_tracing(app=app, engine=db_engine)
logger = get_logger()

# En tus endpoints

@app.get("/users/{user_id}")
async def get_user(user_id: int):
logger.info("Fetching user", user_id=user_id) # Las consultas SQL y requests HTTP se rastrean automáticamente
user = await get_user_from_db(user_id)
return user

- Beneficios

Trazabilidad completa: Puedes seguir una request desde el frontend hasta todas las bases de datos y servicios externos
Logs correlacionados: Cada log tiene el trace_id para encontrar todos los logs relacionados con una operación
Configuración centralizada: Un solo lugar para configurar observabilidad en todos tus microservicios
Análisis fácil: Logs en JSON permiten queries complejas en sistemas como ELK Stack

Es especialmente útil para arquitecturas de microservicios donde necesitas entender el flujo completo de las operaciones distribuidas.

Ejemplo en la vida real:
Cliente: "El checkout falló a las 3:47 PM"
Tú: _revisa 47 logs de 12 servicios diferentes_
"¿Era el user-service? ¿payments-service? ¿inventory-service?"
3 horas después...\_

con observavility-completed:

Cliente: "El checkout falló a las 3:47 PM"
Tú: busca por trace_id
"Ah, veo que el inventory-service tardó 30 segundos en responder porque la DB estaba bloqueada"
5 minutos después: problema resuelto\_
