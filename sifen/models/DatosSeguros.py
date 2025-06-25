class DatosSeguros:
    def __init__(self, codigo_empresa=None, polizas=None):
        self.codigo_empresa = codigo_empresa  # Código en la Superintendencia de Seguros
        self.polizas = polizas or []  # Lista de objetos PolizaSeguro

    def validar(self):
        if not self.codigo_empresa or len(self.codigo_empresa) > 20:
            raise ValueError("Código de empresa de seguros es requerido (max 20 caracteres)")
        if not self.polizas:
            raise ValueError("Debe incluir al menos una póliza")
        for poliza in self.polizas:
            poliza.validar()