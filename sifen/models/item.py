from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Optional
import warnings
from ..utils.constants import MONEDAS

@dataclass
class ItemFactura:
    codigo: str
    descripcion: str
    cantidad: int
    precio_unitario: float
    afectacion_iva: str = "1" #Gravado
    proporcion_iva: Optional[Decimal] = None
    tasa_iva: Optional[float]= None
    liq_IVA: Optional[Decimal]= None
    unidad_medida: str = "77"  # Código SIFEN (77: Unidad)
    codigo_tipo_item: str = "1"  # 1: Producto, 2: Servicio
    codigo_unidad_medida: str = "UNI"  # Código adicional para SIFEN
    descuento: Optional[Decimal] = None  # Decimal para precisión monetaria
    porcentaje_descuento: Optional[Decimal] = None  # Decimal para precisión monetaria
    descuento_global_Item: Optional[Decimal] = None  # Decimal para precisión monetaria


    # Agregar nuevos campos para items más complejos
    codigo_producto: Optional[str] = None  # Código GTIN/EAN
    codigo_unidad_medida_comercial: Optional[str] = None  # Código comercial
    codigo_partida_arancelaria: Optional[str] = None  # Para comercio exterior
    codigo_nandina: Optional[str] = None  # Para comercio exterior
    pais_origen: Optional[str] = None  # Código de país ISO
    nombre_pais_origen: Optional[str] = None
    numero_serie: Optional[str] = None  # Para items con serie
    numero_lote: Optional[str] = None  # Para productos con lote
    fecha_vencimiento: Optional[datetime] = None  # Para productos perecederos

    def _validar_campos_nuevos(self):
        """Validaciones para los nuevos campos de items"""
        if self.codigo_producto and len(self.codigo_producto) > 20:
            raise ValueError("Código de producto (GTIN/EAN) no puede exceder 20 caracteres")
        
        if self.fecha_vencimiento and self.fecha_vencimiento < datetime.now().date():
            warnings.warn("Fecha de vencimiento del producto es anterior a la fecha actual")




    def __post_init__(self):
        """Validaciones automáticas al crear el ítem."""
        self.validar()
        self._validar_descuentos()
        self._validar_campos_nuevos()

    def validar(self):
        """Valida que los campos del ítem cumplan con requisitos SIFEN."""
        if not self.codigo or len(self.codigo) > 20:
            raise ValueError("Código de ítem es obligatorio (max 20 caracteres).")
        if self.cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a 0.")
        if self.precio_unitario <= 0:
            raise ValueError("El precio unitario debe ser positivo.")
        if self.tasa_iva not in (0, 5, 10):  # Ajustar según tasas en Paraguay
            raise ValueError("IVA debe ser 0%, 5% o 10%.")
        if self.unidad_medida not in ("77", "kg", "m"):  # Ejemplo de códigos
            raise ValueError("Unidad de medida no válida.")

    def _validar_descuentos(self):
        """Valida que los descuentos sean coherentes."""
        if self.descuento is not None and self.descuento < 0:
            raise ValueError("El descuento no puede ser negativo.")
        if self.porcentaje_descuento is not None and (self.porcentaje_descuento <= 0 or self.porcentaje_descuento > 100):
            raise ValueError("El porcentaje de descuento debe estar entre 0 y 100.")
        if self.descuento_global_Item is not None and self.descuento_global_Item < 0:
            raise ValueError("El descuento global no puede ser negativo.")
        if self.tasa_iva == 0 and (self.descuento or self.porcentaje_descuento):
            warnings.warn("Aplicando descuentos a un ítem con IVA 0%.")

    def calcular_subtotal(self) -> Decimal:
        """Calcula subtotal sin IVA."""
        return (Decimal(str(self.cantidad * self.precio_unitario)).quantize(Decimal('0.01')))

    def calcular_iva(self) -> Decimal:
        """Calcula monto de IVA sobre la base imponible."""
        return (self.base_imponible * (Decimal(str(self.tasa_iva)) / Decimal("100"))).quantize(Decimal('0.01'))
    




    @property
    def base_imponible(self) -> Decimal:
        """Calcula la base imponible después de descuentos."""
        subtotal = self.calcular_subtotal()
        descuento = Decimal(str(self.descuento or 0))
        descuento_porcentual = subtotal * (Decimal(str(self.porcentaje_descuento or 0)) / Decimal("100"))
        descuento_global = Decimal(str(self.descuento_global_Item or 0))
        return (subtotal - descuento - descuento_porcentual - descuento_global).quantize(Decimal('0.01'))

    @property
    def total(self) -> Decimal:
        """Calcula el total final del ítem (base imponible + IVA)."""
        return (self.base_imponible + self.calcular_iva()).quantize(Decimal('0.01'))

    def to_dict(self) -> dict:
        """Devuelve una representación en diccionario del ítem."""
        return {
            "codigo": self.codigo,
            "descripcion": self.descripcion,
            "cantidad": self.cantidad,
            "precio_unitario": float(self.precio_unitario),
            "iva": self.tasa_iva,
            "unidad_medida": self.unidad_medida,
            "descuento": float(self.descuento) if self.descuento else None,
            "porcentaje_descuento": float(self.porcentaje_descuento) if self.porcentaje_descuento else None,
            "descuento_global": float(self.descuento_global_Item) if self.descuento_global_Item else None,
            "subtotal": float(self.calcular_subtotal()),
            "base_imponible": float(self.base_imponible),
            "total": float(self.total)
        }




    