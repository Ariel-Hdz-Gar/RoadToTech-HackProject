import math
from pydantic import BaseModel, Field

# ==========================================
# 1. MODELOS DE DATOS (Contrato de entrada)
# ==========================================

class LotePerecedero(BaseModel):
    id_registro: str
    producto: str
    dias_para_caducar: int

class Bodega(BaseModel):
    id_registro: str
    volumen_total_m3: float
    volumen_ocupado_m3: float
    producto_estancado: str

class LoteEstancado(BaseModel):
    id_registro: str
    producto: str
    dias_sin_vender: int
    producto_cruzado: str

class EventoLocal(BaseModel):
    id_registro: str
    nombre_evento: str
    afluencia_estimada: int
    dias_para_evento: int

# ==========================================
# 2. LÓGICA DE NEGOCIO (Matemáticas y Reglas)
# ==========================================

class MotorAlertas:
    @staticmethod
    def procesar_alerta_roja(lote: LotePerecedero) -> dict | None:
        if lote.dias_para_caducar <= 3:
            return {
                "id_registro": lote.id_registro,
                "tipo_alerta": "roja",
                "titulo": "Rescate de Perecederos (FEFO)",
                "descripcion": f"Lote de '{lote.producto}' caduca en {lote.dias_para_caducar} días.",
                "recomendacion_inventario": "Lanzar descuento hiperlocal del 40%.",
                "recomendacion_personal": "N/A",
                "texto_boton": "Aprobar Descuento",
                "endpoint_aprobacion": f"/api/v1/ejecutar-accion/roja/{lote.id_registro}"
            }
        return None

    @staticmethod
    def procesar_alerta_amarilla(bodega: Bodega) -> dict | None:
        porcentaje = (bodega.volumen_ocupado_m3 / bodega.volumen_total_m3) * 100
        if porcentaje > 90.0:
            return {
                "id_registro": bodega.id_registro,
                "tipo_alerta": "amarilla",
                "titulo": "Saturación de Bodega (FIFO)",
                "descripcion": f"Bodega al {porcentaje:.1f}% de capacidad. Riesgo logístico.",
                "recomendacion_inventario": f"Promoción 3x2 en {bodega.producto_estancado}.",
                "recomendacion_personal": "Reasignar 1 empleado de piso a bodega.",
                "texto_boton": "Aprobar Promoción 3x2",
                "endpoint_aprobacion": f"/api/v1/ejecutar-accion/amarilla/{bodega.id_registro}"
            }
        return None

    @staticmethod
    def procesar_alerta_azul(lote: LoteEstancado) -> dict | None:
        if lote.dias_sin_vender > 40:
            return {
                "id_registro": lote.id_registro,
                "tipo_alerta": "azul",
                "titulo": "Capital Estancado",
                "descripcion": f"Lote de '{lote.producto}' lleva {lote.dias_sin_vender} días sin rotación.",
                "recomendacion_inventario": f"Venta cruzada automática: 15% de descuento al llevar {lote.producto_cruzado}.",
                "recomendacion_personal": "N/A",
                "texto_boton": "Aprobar Venta Cruzada",
                "endpoint_aprobacion": f"/api/v1/ejecutar-accion/azul/{lote.id_registro}"
            }
        return None

    @staticmethod
    def procesar_alerta_morada(evento: EventoLocal) -> dict | None:
        if evento.afluencia_estimada > 0 and evento.dias_para_evento <= 5:
            cajeros = math.ceil(evento.afluencia_estimada / 50)
            return {
                "id_registro": evento.id_registro,
                "tipo_alerta": "morada",
                "titulo": "Demanda Predictiva",
                "descripcion": f"Evento: {evento.nombre_evento} en {evento.dias_para_evento} días.",
                "recomendacion_inventario": "Sobresurtir cerveza y hielos inmediatamente.",
                "recomendacion_personal": f"Asignar {cajeros} cajeros extra para el evento.",
                "texto_boton": "Aprobar Sobresurtido y Turnos",
                "endpoint_aprobacion": f"/api/v1/ejecutar-accion/morada/{evento.id_registro}"
            }
        return None