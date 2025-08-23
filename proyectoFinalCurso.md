### Proyecto: API de Gestión para E-commerce  
Duración: 2 meses  
Lenguaje: Python (Flask)  
Fecha de Entrega: 17 de Octubre
Base de Datos: SQLite  


### Requisitos Centrales 
Desarrollar una API con operaciones CRUD para 3 entidades:  
1. Usuarios  
2. Productos  
3. Ventas 


### Modelos de Datos

#### Usuario  
| Campo        | Tipo          | Restricciones      |
|--------------|---------------|-------------------|
| id         | Integer       | PK, Autoinc       |
| nombres    | TEXT(100)   | Not Null          |
| apellidos  | TEXT(100)   | Not Null          |
| edad       | Integer       | Not Null          |
| telefono   | TEXT(20)    | Unique            |
| correo     | TEXT(100)   | Unique            |
| clave_hash | TEXT(128)   | Not Null (Hash)   |
| ciudad     | TEXT(50)    | Not Null          |
| pais       | TEXT(50)    | Not Null          |
| registro   | DateTime      | Default=now()     |

#### Producto  
| Campo          | Tipo          | Restricciones    |
|----------------|---------------|-----------------|
| id           | Integer       | PK, Autoinc     |
| nombre       | TEXT(100)   | Not Null        |
| descripcion  | Text          | Nullable        |
| precio       | REAL         | Not Null        |
| categoria    | TEXT(50)    | Not Null        |
| stock        | Integer       | Not Null        |
| registro     | DateTime      | Default=now()   |

#### Venta  
| Campo          | Tipo          | Restricciones               |
|----------------|---------------|----------------------------|
| id           | Integer       | PK, Autoinc                |
| id_usuario   | Integer       | FK (Usuario.id)            |
| id_producto  | Integer       | FK (Producto.id)           |
| cantidad     | Integer       | Not Null                   |
| total_venta  | REAL         | Not Null (Auto calculado)  |
| registro     | DateTime      | Default=now()              |



### Funcionalidades Obligatorias  
## A. Usuarios  
1. Registro:  
   - Hash de contraseña con la libreria de tu preferencia.  
   - Validar unicidad de correo/teléfono.  
2. Autenticación JWT:  
   - Login/logout con tokens.  
3. Operaciones:  
   - CRUD completo.  
   - Filtros: Por país, ciudad, rango de edad.  
   - Exportar a CSV/JSON.  

## B. Productos 
1. Operaciones:  
   - CRUD completo.  
   - Búsqueda por nombre/categoría (coincidencias parciales).  
   - Exportar a CSV/JSON.  
2. Web Scraping:  
   - Endpoint "/productos/importar" que usa BeautifulSoup para extraer datos de páginas como Amazon.  
3. Gestión de Stock:  
   - Actualización automática al registrar ventas.  

## C. Ventas  
1. Operaciones:  
   - CRUD (excepto edición).  
   - Búsqueda por usuario o producto.  
2. Validaciones:  
   - Stock suficiente antes de registrar venta.  
   - Cálculo automático: "total_venta = precio * cantidad".  
3. Reportes:  
   - Generar reporte mensual en Excel ("openpyxl").  


## Endpoints

#### Blueprint: "usuarios_bp.py"  
| Método | Ruta                          | Función                             |
|--------|-------------------------------|-------------------------------------|
| POST   | "/login"                      | Genera token JWT                    |
| POST   | "/registro"                   | Crea usuario (con hash)             |
| GET    | "/usuarios"                   | Lista usuarios (filtros opcionales) |
| GET    | "/usuarios/<id>"              | Usuario por ID                      |
| GET    | "/usuarios/correo/<correo>"   | Usuario por correo                  |
| GET    | "/usuarios/pais/<pais>"       | Usuarios por país (o mensaje)       |
| PUT    | "/usuarios/<id>"              | Actualiza usuario                   |
| DELETE | "/usuarios/<id>"              | Elimina usuario                     |
| GET    | "/usuarios/exportar?formato=" | Exporta a CSV/JSON                  |

#### Blueprint: "productos_bp.py"  
| Método | Ruta                          | Función                             |
|--------|-------------------------------|-------------------------------------|
| POST   | "/productos/importar"         | Importa productos vía web scraping  |
| GET    | "/productos"                  | Lista productos (filtros)           |
| GET    | "/productos/<id>"             | Producto por ID                     |
| GET    | "/productos/nombre/<nombre>"  | Productos por nombre (parcial)      |
| GET    | "/productos/categoria/<cat>"  | Productos por categoría (o mensaje) |
| POST   | "/productos"                  | Crea producto                       |
| PUT    | "/productos/<id>"             | Actualiza producto                  |
| DELETE | "/productos/<id>"             | Elimina producto                    |
| GET    | "/productos/exportar?formato="| Exporta a CSV/JSON                  |

#### Blueprint: "ventas_bp.py"  
| Método | Ruta                          | Función                             |
|--------|-------------------------------|-------------------------------------|
| POST   | "/ventas"                     | Registra venta (valida stock)       |
| GET    | "/ventas"                     | Lista todas las ventas              |
| GET    | "/ventas/<id>"                | Venta por ID                        |
| GET    | "/ventas/usuario/<id>"        | Ventas por usuario (o mensaje)      |
| GET    | "/ventas/producto/<id>"       | Ventas por producto (o mensaje)     |
| DELETE | "/ventas/<id>"                | Elimina venta (restaura stock)      |
| GET    | "/ventas/reporte_mensual?mes="| Reporte Excel (con gráficos)        |

### Módulos Adicionales (extra opcional)
#### "tests/" (Pruebas Unitarias)  
- Validan endpoints, modelos y reglas de negocio con `pytest`.  
- Ejemplos:  
  - "test_registro_usuario_duplicado()"  
  - "test_venta_sin_stock()"  
  - "test_web_scraping()"  


### Requisitos Técnicos 
1. Seguridad:  
   - Contraseñas con hash la libreria de tu preferencia.  
   - Endpoints protegidos con JWT (excepto login/registro).  
2. Validaciones:  
   - Errores HTTP claros (400, 404, 409).  
   - Stock insuficiente → Error 400 + mensaje.  
3. Modularización:  
   - Blueprints enrutados en "app.py":  
     app.register_blueprint(usuarios_bp, url_prefix='/api')
     app.register_blueprint(productos_bp, url_prefix='/api')
     app.register_blueprint(ventas_bp, url_prefix='/api')
4. Documentación:  
   - Colección de Insomnia/Postman para pruebas.  


### Estructura del Proyecto  

proyecto/
├── src/
│   ├── app.py                  # Configuración Flask
│   ├── database.py             # Conexión DB y inicialización
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── usuarios_bp.py      # Endpoints de usuarios
│   │   ├── productos_bp.py     # Endpoints de productos
│   │   └── ventas_bp.py        # Endpoints de ventas
│   └── tests/
│       ├── test_usuarios.py    # Pruebas de usuarios
│       ├── test_productos.py   # Pruebas de productos
│       └── test_ventas.py      # Pruebas de ventas
├── exports/                    # Archivos exportados
├── requirements.txt            # Dependencias
└── .env                        # Variables de entorno


### Funcionalidades Extra (opcionales)  
1. Notificación por WhatsApp:  
   - Al registrar venta, enviar mensaje con "pywhatkit".  
   - Ejemplo: "✅ Venta registrada: Producto X, Cantidad Y, Total $Z".  
2. Organización Automática:  
   - Ejecutar "file_organizer.py" diariamente para clasificar "/exports".  


### Entregables
1. Código fuente en estructura modular (en un repositorio de github).  
2. Colección de Insomnia/Postman con todas las pruebas de los endpoint.  
3. Documentación básica (README.md).  
4. Pruebas unitarias ejecutables con "pytest" (opcional).