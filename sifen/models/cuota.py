from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

@dataclass
class Cuota:
    numero: int                     # Número de cuota (1, 2, 3...)
    monto: Decimal                  # Monto con 4 decimales
    moneda: str = "PYG"             # Código ISO (ej: "PYG", "USD")
    desc_moneda: str = "Guaraníes"  # Descripción (ej: "Dólares")
    fecha_vencimiento: Optional[datetime] = None  # Opcional (YYYY-MM-DD)