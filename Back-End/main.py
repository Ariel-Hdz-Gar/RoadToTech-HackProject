from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor_reglas import LotePerecedero, Bodega, LoteEstancado, EventoLocal, MotorAlertas
from mock_db import db_perecederos, db_bodegas, db_estancados, db_eventos

app = FastAPI(title="API RetailPulse - MVP 4 Tarjetas")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

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
    alertas = []
    
    for item in db_perecederos:
        if item["id_sucursal"] == id_sucursal:
            if al := MotorAlertas.procesar_alerta_roja(LotePerecedero(**item)): alertas.append(al)
            
    for item in db_bodegas:
        if item["id_sucursal"] == id_sucursal:
            if al := MotorAlertas.procesar_alerta_amarilla(Bodega(**item)): alertas.append(al)
            
    for item in db_estancados:
        if item["id_sucursal"] == id_sucursal:
            if al := MotorAlertas.procesar_alerta_azul(LoteEstancado(**item)): alertas.append(al)
            
    for item in db_eventos:
        if item["id_sucursal"] == id_sucursal:
            if al := MotorAlertas.procesar_alerta_morada(EventoLocal(**item)): alertas.append(al)

    return {"sucursal_id": id_sucursal, "total_alertas": len(alertas), "tarjetas_accion": alertas}

@app.post("/api/v1/ejecutar-accion/{tipo_alerta}/{id_registro}")
def ejecutar_accion(tipo_alerta: str, id_registro: str):
    """ Este endpoint simula la resolución del problema mutando el estado de la BD """
    global db_perecederos, db_bodegas, db_estancados, db_eventos
    
    if tipo_alerta == "roja":
        db_perecederos = [x for x in db_perecederos if x["id_registro"] != id_registro]
    elif tipo_alerta == "amarilla":
        db_bodegas = [x for x in db_bodegas if x["id_registro"] != id_registro]
    elif tipo_alerta == "azul":
        db_estancados = [x for x in db_estancados if x["id_registro"] != id_registro]
    elif tipo_alerta == "morada":
        db_eventos = [x for x in db_eventos if x["id_registro"] != id_registro]
        
    return {"status": "success", "mensaje": f"Acción de tarjeta {tipo_alerta} aprobada y problema resuelto."}