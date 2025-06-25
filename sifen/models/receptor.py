from dataclasses import dataclass
import re
from typing import Optional

@dataclass
class Receptor:
    ruc: str
    dv: str
    tipo_doc_sin_ruc: str
    nombre: str
    nombre_fantasia: str= ""
    direccion: str= ""
    num_casa: str = "0000"
    telefono: str = ""
    celular: str = ""
    email: str= ""
    codigo_cliente: Optional[str] = None  # Opcional: Código interno del cliente
    #Naturaleza del receptor: 1(Contribuyente), 2(No Contribuyente)
    nat_receptor: str = "1"  # 1: Persona física, 2: Jurídica
    #Tipo de contribuyente. 1(Persona Fisica), 2(Persona Juridica)
    tipo_contribuyente: str ="1"
    pais: str = "PRY"  # Código ISO de Paraguay
    c_departamento: str ="2"
    c_distrito: str = "7"
    c_ciudad: str = "1046"  # Código de ciudad (ej: 1 para Asunción)

    def validar(self):
        if not self.ruc.isdigit() or len(self.ruc) not in (6, 8):  # RUC Paraguay puede ser 6 u 8 dígitos
            raise ValueError("RUC del receptor debe ser numérico (6 u 8 dígitos).")
        if not self.dv.isdigit() or len(self.dv) != 1:
            raise ValueError("DV debe ser un dígito (0-9).")
        if self.tipo_contribuyente not in ("1", "2"):
            raise ValueError("Tipo de contribuyente debe ser '1' (física) o '2' (jurídica).")

    @staticmethod
    def validar_email(email):
        """Valida el formato del email según estándares SIFEN"""
        if not email:
            return None
            
        # Expresión regular para validación básica
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(patron, email):
            raise print("Formato de email inválido")
            
        # Validación de longitud máxima (según XSD)
        if len(email) > 80:  # El XSD no especifica longitud, 80 es un estándar común
            raise print("El email no puede exceder los 80 caracteres")
            
        return email.strip().lower()