from dataclasses import dataclass
from datetime import datetime

@dataclass
class Usuario:
    id: int
    nombres: str
    apellidos: str
    edad: int
    correo: str
    telefono: str
    ciudad: str
    pais: str
    clave_hash: str
    registro: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
