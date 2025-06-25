from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from .DatosSeguros import DatosSeguros
from .emisor import Emisor
from .receptor import Receptor
from .item import ItemFactura
from decimal import Decimal
from .cuota import Cuota
from .datos_energia import DatosEnergia
from .datos_supermercado import DatosSupermercado
from .datos_transporte import DatosTransporte
from .transportista import Transportista

@dataclass
class Factura:
    datos_energia: DatosEnergia
    datos_seguros: DatosSeguros
    datos_supermercado: DatosSupermercado
    datos_transporte: DatosTransporte
    datos_transportista = Transportista
    emisor: Emisor
    receptor: Receptor
    items: List[ItemFactura]
    fecha_emision: datetime = field(default_factory=datetime.now)
    #Tipo de operacion: 1(B2B), 2(B2C), 3(B2G), 4(B2F)
    #B2B (Business to Business):Transacciones comerciales entre dos empresas o negocios.
    #B2C (Business to Consumer):Transacciones comerciales entre una empresa y un consumidor final (persona individual). 
    #B2G (Business to Government):Transacciones comerciales entre una empresa y una entidad del gobierno (Organismo o Entidad del Estado). 
    #B2F (Business to Foreign):Transacciones comerciales entre una empresa local (con RUC) y una empresa o persona del exterior. 
    tipo_operacion: str = "1"  # 1: B2B
    tipo_factura: str = "1"    # 1: Factura electrónica
    moneda: str = "PYG"        # Código ISO (PYG: Guaraní)
    timbrado: str= "12345678" # ocho caracteres
    serie_timbrado: str = "AB"
    inicio_vig_timbrado: datetime = datetime.now().strftime("%Y-%m-%d")
    numero_factura: str = "001-001-0000005"  # Formato: Est-Pto-Number
    tipo_emision: str= "Normal"
    tipo_impuesto_afectado: str = "1"
    codigo_seguridad:str ="000000001"
    indicador_presencia: str = "1"
    condicion_venta: str = "1"  # 1: Contado, 2: Crédito
    plazo_credito: Optional[int] = None  # Obligatorio si es crédito a plazo
    # 1 Plazo, 2 Cuota
    tipo_credito: Optional[str] = None  # 1: Plazo, 2: Cuota (requerido si condicion_venta=2)
    cuotas: Optional[List[Cuota]] = None  # Lista de cuotas (si tipo_credito="2")
    monto_entrega: Optional[Decimal] = None  # Decimal para precisión monetaria


    # Nuevos campos según gCamFE
    codigo_seguridad: str  # tiCodSe (9 dígitos, no secuencial)
    indicador_presencia: str = "1"  # tiIndPres (1-6,9)
    desc_indicador_presencia: str = "Operación presencial"  # tdDesIndPres
    tipo_transaccion: str = "1"  # tiTipTra (1-13)
    desc_tipo_transaccion: str = "Venta de mercadería"  # tdDesTiTran
    codigo_establecimiento: str = "001"  # tdEst (3 dígitos)
    codigo_punto_expedicion: str = "001"  # tdPunExp (3 dígitos)
    codigo_ciudad: str = "1"  # tcCiuEmi (1-5 dígitos)
    desc_ciudad: str = "ASUNCION"  # tdDesCiuEmi
    codigo_distrito: str = "1"  # tcDisEmi (1-4 dígitos)
    desc_distrito: str = "ASUNCION"  # tdDesDisEmi
    fecha_hora_emision: datetime = field(default_factory=datetime.now)  # fecHhmmss


    #CAMPOS GENERALES DE CARGA
    orden_compra: str =""
    orden_venta: str = ""
    num_asiento: str = ""
    unidad_medida_total_vol: str = ""
    total_vol_merc: str =""
    unidad_medida_total_peso: str = ""
    total_peso_merc: str =""
    id_carga: str =""


    condicion_tipo_cambio:str = "" #Condición del tipo de cambio 1(Global), 2(Por ítem)
    tipo_cambio_base: str = "" # hasta 9 digitos, limite de 4 digitos a decimales
    condicion_anticipo: str ="" #1 anticipo global, 2 anticipo por item

    def validar(self):
        """Valida la factura completa según reglas SIFEN."""
        if not self.items:
            raise ValueError("La factura debe tener al menos un ítem.")
        
        for item in self.items:
            item.validar()  # Valida cada ítem
    
        if self.condicion_venta == "2":  # Crédito
            if not self.tipo_credito:
                raise ValueError("Debe especificar el tipo de crédito (1: Plazo, 2: Cuotas).")
            
            if self.tipo_credito == "1" and not self.plazo_credito:  # Crédito a plazo
                raise ValueError("Debe especificar plazo de crédito para créditos a plazo.")
                
            if self.tipo_credito == "2" and not self.cuotas:  # Crédito en cuotas
                raise ValueError("Debe especificar las cuotas para créditos en cuotas.")





        
        if not all(part.isdigit() for part in self.numero_factura.split("-")):
            raise ValueError("Número de factura debe tener formato XXX-XXX-XXXXXXX (numérico).")

    def generar_id(self) -> str:
        """Genera el ID único para el XML según formato SIFEN (44 caracteres exactos)."""
        partes = self.numero_factura.split("-")
        return (
            f"{self.tipo_operacion}"                     # 1 carácter
            f"{self.emisor.ruc}"                         # 8 caracteres
            f"{self.emisor.dv}"                          # 1 carácter
            f"{self.tipo_factura.zfill(2)}"              # 2 caracteres
            f"{partes[0].zfill(3)}"                      # 3 caracteres (Establecimiento)
            f"{partes[1].zfill(3)}"                      # 3 caracteres (Punto expedición)
            f"{partes[2].zfill(7)}"                      # 7 caracteres (Número)
            f"{self.fecha_emision.strftime('%Y%m%d')}"   # 8 caracteres (AAAAMMDD)
            "00000000001"                                   # 8 caracteres FIJOS (nro aleatorio)
        )  # Total: 1+8+1+2+3+3+7+8+8 = 44 caracteres

    def calcular_totales(self) -> dict:
        """Calcula totales generales de la factura."""
        subtotal = sum(item.calcular_subtotal() for item in self.items)
        iva = sum(item.calcular_iva() for item in self.items)
        return {
            "subtotal": subtotal,
            "iva": iva,
            "total": subtotal + iva
        }