import csv
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXPORT_DIR = os.path.join(BASE_DIR, "../exports")

# Crear carpeta de exportaciones si no existe
os.makedirs(EXPORT_DIR, exist_ok=True)

def export_products(productos, formato="json"):
    try:
        if not productos:
            return {"success": False, "message": "No hay productos para exportar"}

        if formato.lower() == "csv":
            file_path = os.path.join(EXPORT_DIR, "productos_export.csv")
            keys = productos[0].keys()
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(productos)
            return {"success": True, "message": f"Archivo CSV generado en {file_path}"}

        elif formato.lower() == "json":
            file_path = os.path.join(EXPORT_DIR, "productos_export.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(productos, f, indent=4, ensure_ascii=False)
            return {"success": True, "message": f"Archivo JSON generado en {file_path}"}

        else:
            return {"success": False, "message": f"Formato {formato} no soportado"}

    except Exception as e:
        return {"success": False, "message": f"Error en la exportación: {e}"}
