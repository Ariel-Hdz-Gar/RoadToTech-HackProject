from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor_reglas import LotePerecedero, Bodega, LoteEstancado, EventoLocal, MotorAlertas
from db_connector import obtener_datos_dashboard

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
    # Obtener el diccionario maestro estructurado por tienda
    datos_todas_tiendas = obtener_datos_dashboard()
    
    if not datos_todas_tiendas or id_sucursal not in datos_todas_tiendas:
        return {"sucursal_id": id_sucursal, "total_alertas": 0, "tarjetas_accion": []}
    
    tienda = datos_todas_tiendas[id_sucursal]
    
    for item in tienda["perecederos"]:
        if al := MotorAlertas.procesar_alerta_roja(LotePerecedero(**item)): alertas.append(al)
            
    for item in tienda["bodegas"]:
        if al := MotorAlertas.procesar_alerta_amarilla(Bodega(**item)): alertas.append(al)
            
    for item in tienda["estancados"]:
        if al := MotorAlertas.procesar_alerta_azul(LoteEstancado(**item)): alertas.append(al)
            
    for item in tienda["eventos"]:
        if al := MotorAlertas.procesar_alerta_morada(EventoLocal(**item)): alertas.append(al)

    return {"sucursal_id": id_sucursal, "total_alertas": len(alertas), "tarjetas_accion": alertas}

@app.post("/api/v1/ejecutar-accion/{tipo_alerta}/{id_registro}")
def ejecutar_accion(tipo_alerta: str, id_registro: str):
    """ Este endpoint resuelve el problema mutando el estado de la BD en TigerGraph """
    from db_connector import resolver_accion_tigergraph
    
    exito = resolver_accion_tigergraph(id_registro, tipo_alerta)
    
    if exito:
        return {"status": "success", "mensaje": f"Acción de tarjeta {tipo_alerta} aprobada en TigerGraph."}
    else:
        return {"status": "error", "mensaje": "No se pudo conectar a TigerGraph o falló la mutación."}