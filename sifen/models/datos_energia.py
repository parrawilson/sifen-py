class DatosEnergia:
    def __init__(self, numero_medidor=None, codigo_actividad=None, codigo_categoria=None,
                 lectura_anterior=None, lectura_actual=None, consumo_kwh=None):
        self.numero_medidor = numero_medidor
        self.codigo_actividad = codigo_actividad
        self.codigo_categoria = codigo_categoria
        self.lectura_anterior = lectura_anterior
        self.lectura_actual = lectura_actual
        self.consumo_kwh = consumo_kwh

    def validar(self):
        """Valida los datos según requerimientos del XSD"""
        if self.numero_medidor and len(self.numero_medidor) > 50:
            raise ValueError("Número de medidor no puede exceder 50 caracteres")
        
        if self.codigo_actividad and not str(self.codigo_actividad).isdigit():
            raise ValueError("Código de actividad debe ser numérico")
            
        if self.codigo_categoria and len(self.codigo_categoria) > 3:
            raise ValueError("Código de categoría no puede exceder 3 caracteres")