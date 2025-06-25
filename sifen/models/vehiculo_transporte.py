class VehiculoTransporte:
    def __init__(self, tipo_vehiculo=None, marca=None, tipo_identificacion=None, 
                 numero_identificacion=None, datos_adicionales=None, matricula=None, 
                 numero_vuelo=None):
        self.tipo_vehiculo = tipo_vehiculo  # Ej: "Camión", "Avión"
        self.marca = marca
        self.tipo_identificacion = tipo_identificacion  # 1=Chasis, 2=Motor
        self.numero_identificacion = numero_identificacion
        self.datos_adicionales = datos_adicionales
        self.matricula = matricula
        self.numero_vuelo = numero_vuelo

    def validar(self):
        if not self.tipo_vehiculo or len(self.tipo_vehiculo) > 10:
            raise ValueError("Tipo de vehículo requerido (max 10 caracteres)")
        if not self.marca or len(self.marca) > 10:
            raise ValueError("Marca requerida (max 10 caracteres)")
        if self.tipo_identificacion not in [1, 2]:
            raise ValueError("Tipo identificación debe ser 1 (Chasis) o 2 (Motor)")