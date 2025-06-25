class DatosSupermercado:
    def __init__(self, nombre_cajero=None, efectivo=None, vuelto=None, donacion=None, descripcion_donacion=None):
        self.nombre_cajero = nombre_cajero
        self.efectivo = efectivo
        self.vuelto = vuelto
        self.donacion = donacion
        self.descripcion_donacion = descripcion_donacion

    def validar(self):
        if self.nombre_cajero and len(self.nombre_cajero) > 20:
            raise ValueError("Nombre de cajero no puede exceder 20 caracteres")
        
        if self.descripcion_donacion and len(self.descripcion_donacion) > 20:
            raise ValueError("Descripción de donación no puede exceder 20 caracteres")
        
        # Validar montos numéricos
        for field in ['efectivo', 'vuelto', 'donacion']:
            value = getattr(self, field)
            if value is not None and not isinstance(value, (Decimal, int, float)):
                raise ValueError(f"{field} debe ser un valor numérico")