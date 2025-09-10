from dataclasses import dataclass
from datetime import datetime

@dataclass
class Sale:
    id: int
    user_id: int
    product_id: int
    cantidad: int
    precio_total: float
    fecha: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
