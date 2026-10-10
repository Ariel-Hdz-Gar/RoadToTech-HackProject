import math
from pydantic import BaseModel, Field

# ==========================================
# 1. MODELOS DE DATOS (Contrato de entrada)
# ==========================================

class LotePerecedero(BaseModel):
    producto: str
    dias_para_caducar: int = Field(..., ge=0, description="Días restantes de vida útil")
    trafico_sucursal: str # Puede ser 'alto', 'medio' o 'bajo'

class Bodega(BaseModel):
    volumen_total_m3: float = Field(..., gt=0)
    volumen_ocupado_m3: float = Field(..., ge=0)
    producto_estancado: str

class EventoLocal(BaseModel):
    nombre_evento: str
    afluencia_estimada: int = Field(..., ge=0)

# ==========================================
# 2. LÓGICA DE NEGOCIO (Matemáticas y Reglas)
# ==========================================

class MotorAlertas:
    
    @staticmethod
    def procesar_alerta_roja(lote: LotePerecedero) -> dict | None:
        """ Evalúa FEFO y calcula el descuento óptimo basado en tráfico. """
        if lote.dias_para_caducar <= 3:
            # Fórmula determinista: A menor tráfico y menos días, el descuento debe ser más agresivo.
            descuento_base = 40 if lote.trafico_sucursal == 'bajo' else 20
            penalizacion_tiempo = (3 - lote.dias_para_caducar) * 5 # Sube 5% por cada día más cerca al vencimiento
            descuento_final = descuento_base + penalizacion_tiempo
            
            return {
                "tipo_alerta": "roja",
                "titulo": "Rescate de Perecederos",
                "descripcion": f"Lote de '{lote.producto}' caduca en {lote.dias_para_caducar} días.",
                "recomendacion_inventario": f"Lanzar descuento hiperlocal del {descuento_final}%",
                "recomendacion_personal": "N/A",
                "texto_boton": "Aprobar Descuento",
                "endpoint_aprobacion": "/api/v1/ejecutar-accion/perecedero"
            }
        return None

    @staticmethod
    def procesar_alerta_amarilla(bodega: Bodega) -> dict | None:
        """ Evalúa la ocupación FIFO y la saturación de espacio. """
        porcentaje_ocupacion = (bodega.volumen_ocupado_m3 / bodega.volumen_total_m3) * 100
        
        if porcentaje_ocupacion >= 90.0:
            return {
                "tipo_alerta": "amarilla",
                "titulo": "Saturación de Bodega",
                "descripcion": f"Volumen al {porcentaje_ocupacion:.1f}%. Bloqueo inminente de descarga.",
                "recomendacion_inventario": f"Activar promo 3x2 en {bodega.producto_estancado} para liberar racks.",
                "recomendacion_personal": "Reasignar 1 empleado de piso a bodega para surtido FIFO.",
                "texto_boton": "Aprobar Promoción y Reasignación",
                "endpoint_aprobacion": "/api/v1/ejecutar-accion/liberar-bodega"
            }
        return None

    @staticmethod
    def procesar_alerta_morada(evento: EventoLocal) -> dict | None:
        """ Cruza demanda predictiva con asignación de personal. """
        if evento.afluencia_estimada >= 100:
            # Cálculos estrictos sin IA generativa:
            # 1 cajero extra atiende a 50 personas.
            cajeros_extra = math.ceil(evento.afluencia_estimada / 50)
            
            # Cálculo de punto de reorden: 2 cervezas por persona extra esperada.
            cervezas_extra = evento.afluencia_estimada * 2
            hielo_extra = math.ceil(evento.afluencia_estimada / 10)
            
            return {
                "tipo_alerta": "morada",
                "titulo": "Pico de Demanda Detectado",
                "descripcion": f"Evento: {evento.nombre_evento}. Afluencia estimada: +{evento.afluencia_estimada} personas.",
                "recomendacion_inventario": f"Sobresurtido: {cervezas_extra} cervezas, {hielo_extra} bolsas de hielo.",
                "recomendacion_personal": f"Asignar {cajeros_extra} cajeros extra durante el evento.",
                "texto_boton": "Aprobar Sobresurtido y Turnos Extra",
                "endpoint_aprobacion": "/api/v1/ejecutar-accion/evento-masivo"
            }
        return None