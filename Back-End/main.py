from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="API RetailPulse - Centro de Mando")

# Configuración de CORS para que el frontend (HTML/JS) pueda consumir la API sin bloqueos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/alertas/{id_sucursal}")
def obtener_alertas_sucursal(id_sucursal: int):
    """
    Retorna las Tarjetas de Acción activas para una sucursal específica.
    Por ahora retorna datos estáticos, luego los calcularemos desde Tigerdata.
    """
    return {
        "sucursal_id": id_sucursal,
        "alertas_activas": [
            {
                "id_alerta": 101,
                "tipo_alerta": "morada",
                "titulo": "Pico de Demanda Detectado",
                "descripcion": "Concierto en Arena Local a 2km. Afluencia estimada: +300%.",
                "recomendacion_inventario": "Sobresurtido: 500 cervezas, 100 bolsas de hielo.",
                "recomendacion_personal": "Asignar 2 cajeros extra de 8:00 PM a 12:00 AM.",
                "texto_boton": "Aprobar Sobresurtido y Turnos Extra",
                "endpoint_aprobacion": "/api/v1/ejecutar-accion/evento-masivo"
            },
            {
                "id_alerta": 102,
                "tipo_alerta": "amarilla",
                "titulo": "Saturación de Bodega",
                "descripcion": "Volumen al 90%. Riesgo de bloqueo para descarga matutina.",
                "recomendacion_inventario": "Activar promoción 3x2 en lote estancado de botanas.",
                "recomendacion_personal": "Reasignar 1 empleado de piso a bodega para surtido FIFO.",
                "texto_boton": "Aprobar Promoción y Reasignación",
                "endpoint_aprobacion": "/api/v1/ejecutar-accion/liberar-bodega"
            }
        ]
    }

@app.post("/api/v1/ejecutar-accion/{tipo_accion}")
def ejecutar_accion(tipo_accion: str):
    """
    Endpoint que el frontend llamará al presionar el botón verde.
    """
    return {"status": "success", "mensaje": f"Acción '{tipo_accion}' ejecutada y notificada al sistema."}