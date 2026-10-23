# Ahorro de tokens: configuración de las tareas automáticas (cron).
# Archivo real: ~/.config/ahorro-tokens/config.sh

# Modelo para tareas rutinarias (Bibliotecario de Brain) y para decisiones (Estratega, Analista del Espía).
MODELO_RUTINA="sonnet"
MODELO_CRITICO="opus"
# Si el modelo elegido está saturado o no disponible, se usa este.
MODELO_RESPALDO="sonnet"

# 1 = las tareas automáticas usan la llave de API (pago por uso, no tocan tu plan)
#     si existe ~/.config/ahorro-tokens/anthropic_api_key. 0 = usan tu suscripción.
USAR_API_EN_CRON=1

# Tope duro en dólares por cada corrida automática (solo aplica con la llave de API).
TOPE_USD_POR_CORRIDA="1.50"
