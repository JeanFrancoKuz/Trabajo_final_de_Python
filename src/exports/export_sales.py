import csv, json
import os

def export_sales(ventas, formato="json"):
    os.makedirs("exports", exist_ok=True)
    try:
        if not ventas:
            return {"success": False, "message": "No hay ventas para exportar."}

        if formato.lower() == "csv":
            path = "exports/ventas.csv"
            with open(path, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=ventas[0].keys())
                writer.writeheader()
                for v in ventas:
                    writer.writerow(v)
        else:  # JSON
            path = "exports/ventas.json"
            with open(path, "w", encoding="utf-8") as file:
                json.dump(ventas, file, indent=4, ensure_ascii=False)

        return {"success": True, "message": f"Ventas exportadas a {path}"}

    except Exception as e:
        return {"success": False, "message": f"Error al exportar ventas: {e}"}
