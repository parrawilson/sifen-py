from dataclasses import dataclass
from typing import Optional

@dataclass
class Emisor:
    ruc: str
    dv: str   
    nombre: str
    nombre_fantasia: str
    telefono: str
    email: Optional[str] = None
    c_tipo_regimen: str ="1"
    c_departamento: str = "1"  # Ejemplo: 1 para Central
    d_des_departamento: str = "CENTRAL"  # Descripción
    c_distrito: str=""
    c_ciudad: str=""  # <- Campo agregado (código de ciudad SIFEN)
    direccion: str=""
    num_casa: str=""
    sucursal: str=""
    direccion_comp1: Optional[str]= None
    direccion_comp2: Optional[str]= None
    c_tipo_contibuyente: str = "1"
    c_actividad_economica: str=""
    info_emisor: str ="Sistema de Facturación Electrónica"
    info_fiscal: str = "Documento electrónico generado automáticamente"
    tipo_doc_responsable_DE: str= ""
    num_doc_responsable_DE: str= ""
    nombre_responsable_DE: str= ""
    cargo_responsable_DE: str= ""
    is_sector_energia: bool= False
    is_sector_seguros: bool= False
    is_sector_supermercado: bool= False
    is_sector_transporte: bool = False

    def validar(self):
        if not self.ruc.isdigit() or len(self.ruc) != 8:
            raise ValueError("RUC debe tener 8 dígitos.")
        if not self.ciudad.isdigit():
            raise ValueError("Código de ciudad debe ser numérico.")