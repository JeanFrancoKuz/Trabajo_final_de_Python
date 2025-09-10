from dataclasses import dataclass
from datetime import datetime

class Product:
    def __init__(self, id, nombre, descripcion, precio, categoria, stock, registro):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.precio = precio
        self.categoria = categoria
        self.stock = stock
        self.registro = registro

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "precio": self.precio,
            "categoria": self.categoria,
            "stock": self.stock,
            "registro": self.registro,
        }

    @staticmethod
    def from_row(row):
        if row is None:
            return None
        return Product(
            id=row["id"],
            nombre=row["nombre"],
            descripcion=row["descripcion"],
            precio=row["precio"],
            categoria=row["categoria"],
            stock=row["stock"],
            registro=row["registro"],
        )
