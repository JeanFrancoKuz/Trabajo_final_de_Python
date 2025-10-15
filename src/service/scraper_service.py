# service/scraper_service.py
import re
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

def _parse_price(text):
    if not text:
        return None
    # Quitar símbolos y separar decimales con punto
    t = re.sub(r"[^\d,\.]", "", text).strip()
    t = t.replace(",", ".") if t.count(",") == 1 and t.count(".") == 0 else t
    try:
        return float(t)
    except:
        return None

def scrape_product_page(url, timeout=8):
    """
    Intenta obtener nombre, precio, descripcion, categoria desde una página de producto.
    Retorna dict: {"success": True, "data": {...}} o {"success": False, "message": "..."}
    """
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        if resp.status_code != 200:
            return {"success": False, "message": f"Status {resp.status_code} al acceder a {url}"}
        soup = BeautifulSoup(resp.text, "html.parser")

        # 1) Nombre: intentar selectores comunes
        nombre = None
        selectors_name = [
            "h1#title", "h1.product-title", "h1", "span#productTitle", "div.product-name h1"
        ]
        for sel in selectors_name:
            el = soup.select_one(sel)
            if el and el.get_text(strip=True):
                nombre = el.get_text(strip=True)
                break

        # 2) Precio: selectores comunes
        precio = None
        selectors_price = [
            "span#priceblock_ourprice", "span#priceblock_dealprice",
            "span.price", "div.price", "span.product-price", "p.price"
        ]
        for sel in selectors_price:
            el = soup.select_one(sel)
            if el and el.get_text(strip=True):
                precio = _parse_price(el.get_text(strip=True))
                if precio is not None:
                    break

        # 3) Descripción: intentos múltiples
        descripcion = None
        selectors_desc = [
            "div#productDescription", "div.product-description", "div.description",
            "div#description", "section.product-description", "meta[name='description']"
        ]
        for sel in selectors_desc:
            el = soup.select_one(sel)
            if el:
                if el.name == "meta":
                    descripcion = el.get("content", "").strip()
                else:
                    descripcion = el.get_text(" ", strip=True)
                if descripcion:
                    break

        # 4) Categoria (breadcrumb)
        categoria = None
        selectors_cat = [
            "ul.breadcrumb li a", "nav.breadcrumb a", "div.breadcrumb a", "span.category"
        ]
        for sel in selectors_cat:
            nodes = soup.select(sel)
            if nodes:
                # tomar el último texto visible como categoria
                categoria = nodes[-1].get_text(strip=True)
                if categoria:
                    break

        # Garantizar valores por defecto
        if not nombre:
            return {"success": False, "message": "No se pudo extraer el nombre del producto (selector no encontrado)."}
        if precio is None:
            # precio opcional: puedes decidir fallar o setear 0.0; aquí devolvemos success pero precio null
            precio = 0.0

        # Limpiar strings largos
        if descripcion and len(descripcion) > 2000:
            descripcion = descripcion[:2000] + "..."

        return {"success": True, "data": {
            "nombre": nombre,
            "precio": precio,
            "descripcion": descripcion or "",
            "categoria": categoria or "Sin categoría",
            # stock lo dejamos para crear producto con un valor por defecto (p. ej. 10)
        }}

    except requests.exceptions.RequestException as re:
        return {"success": False, "message": f"Error de red al acceder a la URL: {re}"}
    except Exception as e:
        return {"success": False, "message": f"Error al parsear página: {e}"}
