from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor_reglas import LotePerecedero, Bodega, EventoLocal, MotorAlertas
from mock_db import db_perecederos, db_bodegas, db_eventos

app = FastAPI(title="API RetailPulse - Centro de Mando")

# Configuración de CORS para que el frontend (HTML/JS) pueda consumir la API sin bloqueos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/v1/simular/alerta-roja")
def simular_perecedero(lote: LotePerecedero):
    """Recibe datos de un lote y devuelve la alerta si está próximo a caducar."""
    alerta = MotorAlertas.procesar_alerta_roja(lote)
    if not alerta:
        return {"status": "ok", "mensaje": "Inventario sano, no requiere acción."}
    return alerta

@app.post("/api/v1/simular/alerta-amarilla")
def simular_bodega(bodega: Bodega):
    """Recibe datos de capacidad y devuelve la alerta si hay saturación."""
    alerta = MotorAlertas.procesar_alerta_amarilla(bodega)
    if not alerta:
        return {"status": "ok", "mensaje": "Capacidad de bodega dentro de los límites."}
    return alerta

@app.post("/api/v1/simular/alerta-morada")
def simular_evento(evento: EventoLocal):
    """Recibe datos de un evento y calcula el personal y sobresurtido necesario."""
    alerta = MotorAlertas.procesar_alerta_morada(evento)
    if not alerta:
        return {"status": "ok", "mensaje": "Afluencia baja, no requiere acción especial."}
    return alerta

@app.get("/api/v1/alertas/{id_sucursal}")
def obtener_alertas_dashboard(id_sucursal: int):
    """
    Endpoint principal para el Frontend. 
    Escanea la DB simulada y devuelve las Tarjetas de Acción procesadas.
    """
    alertas_generadas = []

    # 1. Buscar problemas en perecederos (Alerta Roja)
    for item in db_perecederos:
        if item["id_sucursal"] == id_sucursal:
            lote = LotePerecedero(**item)
            alerta = MotorAlertas.procesar_alerta_roja(lote)
            if alerta:
                alertas_generadas.append(alerta)

    # 2. Buscar problemas de saturación en bodega (Alerta Amarilla)
    for item in db_bodegas:
        if item["id_sucursal"] == id_sucursal:
            bodega = Bodega(**item)
            alerta = MotorAlertas.procesar_alerta_amarilla(bodega)
            if alerta:
                alertas_generadas.append(alerta)

    # 3. Buscar eventos locales (Alerta Morada)
    for item in db_eventos:
        if item["id_sucursal"] == id_sucursal:
            if item["afluencia_estimada"] > 0:
                evento = EventoLocal(**item)
                alerta = MotorAlertas.procesar_alerta_morada(evento)
                if alerta:
                    alertas_generadas.append(alerta)

    return {
        "sucursal_id": id_sucursal,
        "total_alertas": len(alertas_generadas),
        "tarjetas_accion": alertas_generadas
    }

@app.post("/api/v1/ejecutar-accion/{tipo_accion}")
def ejecutar_accion(tipo_accion: str):
    """
    Endpoint que el frontend llamará al presionar el botón verde.
    """
    return {"status": "success", "mensaje": f"Acción '{tipo_accion}' ejecutada y notificada al sistema."}