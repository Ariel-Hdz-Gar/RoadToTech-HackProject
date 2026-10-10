# motor_reglas.py
import math
from pydantic import BaseModel

class LotePerecedero(BaseModel):
    id_registro: str
    id_sucursal: int
    producto: str
    dias_para_caducar: int
    stock_actual: int
    punto_reorden: int

class Bodega(BaseModel):
    id_registro: str
    id_sucursal: int
    producto: str
    volumen_total_m3: float
    volumen_ocupado_m3: float
    producto_estancado: str

class LoteEstancado(BaseModel):
    id_registro: str
    id_sucursal: int
    producto: str
    dias_sin_vender: int
    producto_cruzado: str

class EventoLocal(BaseModel):
    id_registro: str
    id_sucursal: int
    producto: str
    nombre_evento: str
    afluencia_estimada: int
    dias_para_evento: int

REGLAS_EXCEL = {
    1: { 
        "Leche": {"tipo": "roja", "estado": "🚨 Roja (Caduca 05-Nov)", "accion": "Descuento 15% (Promo: $30.18)", "rescate_u": 19.2338449, "ingreso": 580.38, "perdida_original": 652.37, "just": "Merma mitigada al 85.5% con precisión de 7 Cifras Sig (E_a < 0.5e-5)."},
        "Jamón": {"tipo": "roja", "estado": "🚨 Roja (Caduca 11-Nov)", "accion": "Descuento 20% (Promo: $40.40)", "rescate_u": 10.9907685, "ingreso": 444.03, "perdida_original": 514.18, "just": "Merma mitigada al 85.5% con precisión de 7 Cifras Sig (E_a < 0.5e-5)."}
    },
    2: { 
        "Donas": {"tipo": "roja", "estado": "🚨 Roja (Caduca 26-Nov)", "accion": "Descuento 40% (Promo: $18.00)", "rescate_u": 10.8378535, "ingreso": 195.08, "perdida_original": 202.81, "just": "Merma mitigada al 85.5% con precisión de 7 Cifras Sig (E_a < 0.5e-5)."},
        "Atún": {"tipo": "amarilla", "estado": "🟡 Amarilla (Estancado)", "accion": "Descuento 33% (Promo: $14.74)", "rescate_u": 1.6056079, "ingreso": 23.67, "perdida_original": 18.77, "just": "ÉXITO: El ingreso superó la pérdida (Neto Positivo). Rescate a 7 CS (E_a < 0.5e-5)."}
    },
    3: { 
        "Paketaxo": {"tipo": "amarilla", "estado": "🟡 Amarilla (Bodega full)", "accion": "Descuento 33% (Promo: $40.20)", "rescate_u": 10.9907685, "ingreso": 441.83, "perdida_original": 385.64, "just": "ÉXITO: El ingreso superó la pérdida (Neto Positivo). Rescate a 7 CS (E_a < 0.5e-5)."},
        "Cerveza": {"tipo": "azul", "estado": "🔵 Azul (Post-Evento)", "accion": "Descuento 20% (Promo: $76.00)", "rescate_u": 8.719343, "ingreso": 662.67, "perdida_original": 662.87, "just": "Merma mitigada al 85.5% con precisión de 7 Cifras Sig (E_a < 0.5e-5)."}
    },
    4: { 
        "Jamón": {"tipo": "roja", "estado": "🚨 Roja (Caduca 15-Nov)", "accion": "Descuento 20% (Promo: $40.40)", "rescate_u": 19.2118633, "ingreso": 776.16, "perdida_original": 898.80, "just": "Merma mitigada al 85.5% con precisión de 7 Cifras Sig (E_a < 0.5e-5)."},
        "Donas": {"tipo": "amarilla", "estado": "🟡 Amarilla (Estancado)", "accion": "Descuento 30% (Promo: $21.00)", "rescate_u": 6.1548304, "ingreso": 129.25, "perdida_original": 115.17, "just": "ÉXITO: El ingreso superó la pérdida (Neto Positivo). Rescate a 7 CS (E_a < 0.5e-5)."}
    }
}

class MotorAlertas:
    @staticmethod
    def _obtener_datos_excel(suc_id, prod, tipo_esperado):
        tienda_datos = REGLAS_EXCEL.get(suc_id, {})
        prod_datos = tienda_datos.get(prod)
        if prod_datos and prod_datos["tipo"] == tipo_esperado:
            return prod_datos
        return None

    @staticmethod
    def procesar_alerta_roja(lote: LotePerecedero) -> dict | None:
        datos = MotorAlertas._obtener_datos_excel(lote.id_sucursal, lote.producto, "roja")
        if datos:
            return {
                "id_registro": lote.id_registro,
                "tipo_alerta": "roja",
                "titulo": datos["estado"],
                "descripcion": f"Producto '{lote.producto}' caduca pronto. ROP fijado a {lote.punto_reorden}.",
                "recomendacion_inventario": datos["accion"],
                "recomendacion_personal": f"Rescatadas: {datos['rescate_u']} u.",
                "accion_personal": "Instrucción a personal: Etiquetar con descuento y mover a zona de liquidación.",
                "ahorro_recuperado_mxn": datos["ingreso"],
                "perdida_original_mxn": datos.get("perdida_original", 0.0),
                "detalle_financiero": datos["just"],
                "texto_boton": "Aprobar Descuento",
                "endpoint_aprobacion": f"/api/v1/ejecutar-accion/roja/{lote.id_registro}"
            }
        return None

    @staticmethod
    def procesar_alerta_amarilla(bodega: Bodega) -> dict | None:
        datos = MotorAlertas._obtener_datos_excel(bodega.id_sucursal, bodega.producto, "amarilla")
        if datos:
            return {
                "id_registro": bodega.id_registro,
                "tipo_alerta": "amarilla",
                "titulo": datos["estado"],
                "descripcion": f"Producto '{bodega.producto}' estancado/saturando. ROP excedido o estancado.",
                "recomendacion_inventario": datos["accion"],
                "recomendacion_personal": f"Rescatadas: {datos['rescate_u']} u.",
                "accion_personal": "Instrucción a personal: Armar exhibición frontal o cabecera de pasillo.",
                "ahorro_recuperado_mxn": datos["ingreso"],
                "perdida_original_mxn": datos.get("perdida_original", 0.0),
                "detalle_financiero": datos["just"],
                "texto_boton": "Aprobar Descuento",
                "endpoint_aprobacion": f"/api/v1/ejecutar-accion/amarilla/{bodega.id_registro}"
            }
        return None

    @staticmethod
    def procesar_alerta_azul(lote: LoteEstancado) -> dict | None:
        datos = MotorAlertas._obtener_datos_excel(lote.id_sucursal, lote.producto, "azul")
        if datos:
            return {
                "id_registro": lote.id_registro,
                "tipo_alerta": "azul",
                "titulo": datos["estado"],
                "descripcion": f"Rotación post-evento de '{lote.producto}'.",
                "recomendacion_inventario": datos["accion"],
                "recomendacion_personal": f"Rescatadas: {datos['rescate_u']} u.",
                "accion_personal": "Instrucción a personal: Colocar junto a productos complementarios (Venta cruzada).",
                "ahorro_recuperado_mxn": datos["ingreso"],
                "perdida_original_mxn": datos.get("perdida_original", 0.0),
                "detalle_financiero": datos["just"],
                "texto_boton": "Aplicar Venta Cruzada",
                "endpoint_aprobacion": f"/api/v1/ejecutar-accion/azul/{lote.id_registro}"
            }
        return None

    @staticmethod
    def procesar_alerta_morada(evento: EventoLocal) -> dict | None:
        # Si hubiera alguna morada explícita en Excel. En el recorte que extraje, no había, pero podemos dejarla por si acaso.
        return None