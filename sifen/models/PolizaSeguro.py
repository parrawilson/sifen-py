class PolizaSeguro:
    def __init__(self, numero_poliza=None, unidad_vigencia=None, vigencia=None, 
                 numero_poliza_completo=None, fecha_inicio_vigencia=None, 
                 fecha_fin_vigencia=None, codigo_interno=None):
        self.numero_poliza = numero_poliza
        self.unidad_vigencia = unidad_vigencia  # Ej: "Meses", "Años"
        self.vigencia = vigencia  # Duración numérica
        self.numero_poliza_completo = numero_poliza_completo
        self.fecha_inicio_vigencia = fecha_inicio_vigencia
        self.fecha_fin_vigencia = fecha_fin_vigencia
        self.codigo_interno = codigo_interno

    def validar(self):
        if not self.numero_poliza or len(self.numero_poliza) > 25:
            raise ValueError("Número de póliza es requerido (max 25 caracteres)")
        if not self.unidad_vigencia or len(self.unidad_vigencia) > 15:
            raise ValueError("Unidad de vigencia es requerida (max 15 caracteres)")
        if not self.vigencia or len(self.vigencia) > 10:
            raise ValueError("Vigencia es requerida (max 10 caracteres)")