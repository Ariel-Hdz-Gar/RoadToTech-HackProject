# motor_reglas.py
import math
from pydantic import BaseModel

class LotePerecedero(BaseModel):
    id_registro: str
    producto: str
    dias_para_caducar: int
    stock_actual: int
    punto_reorden: int

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

class MotorAlertas:
    @staticmethod
    def procesar_alerta_roja(lote: LotePerecedero) -> dict | None:
        # Alerta por caducidad próxima o por punto de reorden alcanzado
        if lote.dias_para_caducar <= 3 or lote.stock_actual <= lote.punto_reorden:
            return {
                "id_registro": lote.id_registro,
                "tipo_alerta": "roja",
                "titulo": "Reabastecimiento / Rescate (FEFO)",
                "descripcion": f"'{lote.producto}' caduca en {lote.dias_para_caducar} días o stock actual ({lote.stock_actual}) tocó punto de reorden ({lote.punto_reorden}).",
                "recomendacion_inventario": "Emitir orden de compra al almacén central por lote de 26 días.",
                "recomendacion_personal": "Revisar espacio en anaquel.",
                "texto_boton": "Aprobar Pedido a Almacén",
                "endpoint_aprobacion": f"/api/v1/ejecutar-accion/roja/{lote.id_registro}"
            }
        return None

    @staticmethod
    def procesar_alerta_amarilla(bodega: Bodega) -> dict | None:
        porcentaje = (bodega.volumen_ocupado_m3 / bodega.volumen_total_m3) * 100
        if porcentaje > 80.0:
            return {
                "id_registro": bodega.id_registro,
                "tipo_alerta": "amarilla",
                "titulo": "Saturación de Espacio en Bodega",
                "descripcion": f"Bodega al {porcentaje:.1f}% de capacidad por espacio físico.",
                "recomendacion_inventario": f"Acelerar rotación de {bodega.producto_estancado}.",
                "recomendacion_personal": "Reordenar pasillos.",
                "texto_boton": "Optimizar Espacio",
                "endpoint_aprobacion": f"/api/v1/ejecutar-accion/amarilla/{bodega.id_registro}"
            }
        return None

    @staticmethod
    def procesar_alerta_azul(lote: LoteEstancado) -> dict | None:
        if lote.dias_sin_vender > 10:
            return {
                "id_registro": lote.id_registro,
                "tipo_alerta": "azul",
                "titulo": "Rotación Lenta de Semiperecederos",
                "descripcion": f"'{lote.producto}' lleva {lote.dias_sin_vender} días con baja rotación.",
                "recomendacion_inventario": f"Venta cruzada: Descuento al combinar con {lote.producto_cruzado}.",
                "recomendacion_personal": "N/A",
                "texto_boton": "Aplicar Venta Cruzada",
                "endpoint_aprobacion": f"/api/v1/ejecutar-accion/azul/{lote.id_registro}"
            }
        return None

    @staticmethod
    def procesar_alerta_morada(evento: EventoLocal) -> dict | None:
        if evento.afluencia_estimada > 0 and evento.dias_para_evento <= 3:
            # Modelo Numérico de Colas (Erlang Retail):
            # - Tasa de captura de mercado: 12% de la afluencia acude a esta sucursal específica.
            # - Ventana de pico comercial: 3 horas (pre y post evento).
            # - Capacidad de despacho: 20 clientes/hora por cajero (promedio 3 min/ticket).
            # - Límite físico estructural: Máximo 3 cajas simultáneas en tienda de conveniencia.
            clientes_tienda = evento.afluencia_estimada * 0.12
            tasa_llegada_hora = clientes_tienda / 3.0
            cajeros_calculados = math.ceil(tasa_llegada_hora / 20.0)
            cajeros = min(max(1, cajeros_calculados), 3)

            return {
                "id_registro": evento.id_registro,
                "tipo_alerta": "morada",
                "titulo": "Demanda Predictiva por Evento",
                "descripcion": f"Evento: {evento.nombre_evento} en {evento.dias_para_evento} días.",
                "recomendacion_inventario": "Sobresurtir Cerveza de 6 y Atún.",
                "recomendacion_personal": f"Habilitar {cajeros} cajero(s) de refuerzo (Turno parcial de 4h en horario pico del evento).",
                "texto_boton": "Aprobar Recursos Extra",
                "endpoint_aprobacion": f"/api/v1/ejecutar-accion/morada/{evento.id_registro}"
            }
        return None