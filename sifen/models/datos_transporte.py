from .punto_transporte import PuntoTransporte

class DatosTransporte:
    def __init__(self, tipo_transporte=None, modalidad_transporte=None, 
                 responsable_flete=None, condiciones_negocio=None, numero_manifiesto=None,
                 numero_despacho_importacion=None, fecha_inicio_transporte=None,
                 fecha_fin_transporte=None, pais_destino=None, punto_salida=None,
                 punto_llegada=None, transportista=None, vehiculos=None):
        self.tipo_transporte = tipo_transporte
        self.modalidad_transporte = modalidad_transporte
        self.responsable_flete = responsable_flete
        self.condiciones_negocio = condiciones_negocio
        self.numero_manifiesto = numero_manifiesto
        self.numero_despacho_importacion = numero_despacho_importacion
        self.fecha_inicio_transporte = fecha_inicio_transporte
        self.fecha_fin_transporte = fecha_fin_transporte
        self.pais_destino = pais_destino
        self.punto_salida = punto_salida or PuntoTransporte()
        self.punto_llegada = punto_llegada or PuntoTransporte()
        self.transportista = transportista
        self.vehiculos = vehiculos or []

    def validar(self):
        if not self.modalidad_transporte:
            raise ValueError("Modalidad de transporte es requerida")
        if not self.responsable_flete:
            raise ValueError("Responsable del flete es requerido")
        if not self.vehiculos:
            raise ValueError("Debe especificar al menos un vehículo")