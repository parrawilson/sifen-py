class Transportista:
    def __init__(self, naturaleza=None, nombre=None, ruc=None, dv=None, 
                 tipo_identificacion=None, numero_identificacion=None,
                 chofer_identificacion=None, chofer_nombre=None, 
                 domicilio_fiscal=None, nacionalidad=None):
        self.naturaleza = naturaleza  # "1"=Jurídica, "2"=Física
        self.nombre = nombre
        self.ruc = ruc
        self.dv = dv
        self.tipo_identificacion = tipo_identificacion
        self.numero_identificacion = numero_identificacion
        self.chofer_identificacion = chofer_identificacion
        self.chofer_nombre = chofer_nombre
        self.domicilio_fiscal = domicilio_fiscal
        self.nacionalidad = nacionalidad

    def validar(self):
        if self.naturaleza not in ["1", "2"]:
            raise ValueError("Naturaleza debe ser '1' (Jurídica) o '2' (Física)")
        
        if not self.nombre:
            raise ValueError("Nombre del transportista es requerido")
            
        if self.naturaleza == "1":
            if not self.ruc or len(self.ruc) != 8:
                raise ValueError("RUC inválido (debe tener 8 dígitos)")
            if not self.dv or len(self.dv) != 1:
                raise ValueError("DV inválido (debe tener 1 dígito)")
        
        if self.naturaleza == "2":
            if not self.tipo_identificacion:
                raise ValueError("Tipo de identificación es requerido")
            if not self.numero_identificacion:
                raise ValueError("Número de identificación es requerido")
        
        if not self.chofer_identificacion:
            raise ValueError("Identificación del chofer es requerida")
        if not self.chofer_nombre:
            raise ValueError("Nombre del chofer es requerido")