import csv, json
import os

def export_users(usuarios, formato="json"):
    os.makedirs("exports", exist_ok=True)
    try:
        if not usuarios:
            return {"success": False, "message": "No hay usuarios para exportar."}

        if formato.lower() == "csv":
            path = "exports/usuarios.csv"
            with open(path, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=usuarios[0].keys())
                writer.writeheader()
                for u in usuarios:
                    writer.writerow(u)
        else:  # JSON
            path = "exports/usuarios.json"
            with open(path, "w", encoding="utf-8") as file:
                json.dump(usuarios, file, indent=4, ensure_ascii=False)

        return {"success": True, "message": f"Usuarios exportados a {path}"}

    except Exception as e:
        return {"success": False, "message": f"Error al exportar usuarios: {e}"}
