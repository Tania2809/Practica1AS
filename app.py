# python.exe -m venv .venv
# cd .venv/Scripts
# activate.bat
# py -m ensurepip --upgrade
# pip install -r requirements.txt

from flask import Flask

from flask import render_template
from flask import request
from flask import jsonify, make_response

import mysql.connector

import datetime
import pytz

from flask_cors import CORS, cross_origin

con = mysql.connector.connect(
    host="185.232.14.52",
    database="u760464709_23005102_bd",
    user="u760464709_23005102_usr",
    password="*Q~ic:$9XVr2"
)

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    if not con.is_connected():
        con.reconnect()

    con.close()

    return render_template("index.html")

@app.route("/app")
def app2():
    if not con.is_connected():
        con.reconnect()

    con.close()

    return "<h5>Hola, soy la view app</h5>"


# Rutas para Eventos (Rodrigo)
@app.route("/eventos")
def eventos():
    if not con.is_connected():
        con.reconnect()
    
    cursor = con.cursor(dictionary=True)
    sql = """
    SELECT e.idEvento, e.descriptionEvento, e.descriptionUbicacion, 
           e.fechaInicio, e.fechaFin, e.estado,
           c.nombreCliente, l.nombreLugar, cat.nombreCategoría
    FROM eventos e
    LEFT JOIN clientes c ON e.idCliente = c.idCliente
    LEFT JOIN lugares l ON e.idLugar = l.idLugar
    LEFT JOIN categories cat ON e.idCategoría = cat.idCategoría
    ORDER BY e.fechaInicio DESC
    LIMIT 10
    """
    
    cursor.execute(sql)
    eventos = cursor.fetchall()
    
    # Formatear fechas
    for evento in eventos:
        if evento["fechaInicio"]:
            evento["fechaInicio"] = evento["fechaInicio"].strftime("%Y-%m-%d %H:%M:%S")
        if evento["fechaFin"]:
            evento["fechaFin"] = evento["fechaFin"].strftime("%Y-%m-%d %H:%M:%S")
    
    con.close()
    return render_template("eventos.html", eventos=eventos)

@app.route("/evento", methods=["POST"])
def guardarEvento():
    if not con.is_connected():
        con.reconnect()
    
    idEvento = request.form.get("idEvento")
    idLugar = request.form.get("idLugar")
    idCliente = request.form.get("idCliente")
    idCategoría = request.form.get("idCategoría")
    descriptionUbicacion = request.form.get("descriptionUbicacion")
    descriptionEvento = request.form.get("descriptionEvento")
    fechaInicio = request.form.get("fechaInicio")
    fechaFin = request.form.get("fechaFin")
    estado = request.form.get("estado")
    
    cursor = con.cursor()
    
    if idEvento:
        sql = """
        UPDATE eventos 
        SET idLugar = %s, idCliente = %s, idCategoría = %s, 
            descriptionUbicacion = %s, descriptionEvento = %s,
            fechaInicio = %s, fechaFin = %s, estado = %s
        WHERE idEvento = %s
        """
        val = (idLugar, idCliente, idCategoría, descriptionUbicacion, 
               descriptionEvento, fechaInicio, fechaFin, estado, idEvento)
    else:
        sql = """
        INSERT INTO eventos (idLugar, idCliente, idCategoría, descriptionUbicacion, 
                            descriptionEvento, fechaInicio, fechaFin, estado)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        val = (idLugar, idCliente, idCategoría, descriptionUbicacion, 
               descriptionEvento, fechaInicio, fechaFin, estado)
    
    cursor.execute(sql, val)
    con.commit()
    con.close()
    
    return make_response(jsonify({"message": "Evento guardado correctamente"}))

# Rutas para Categories (Tania)
@app.route("/categories")
def categories():
    if not con.is_connected():
        con.reconnect()
    
    cursor = con.cursor(dictionary=True)
    sql = "SELECT * FROM categories ORDER BY nombreCategoría"
    cursor.execute(sql)
    categories = cursor.fetchall()
    con.close()
    
    return render_template("categories.html", categories=categories)

@app.route("/categoria", methods=["POST"])
def guardarCategoria():
    if not con.is_connected():
        con.reconnect()
    
    idCategoría = request.form.get("idCategoría")
    nombreCategoría = request.form.get("nombreCategoría")
    descripción = request.form.get("descripción")
    
    cursor = con.cursor()
    
    if idCategoría:
        sql = "UPDATE categories SET nombreCategoría = %s, descripción = %s WHERE idCategoría = %s"
        val = (nombreCategoría, descripción, idCategoría)
    else:
        sql = "INSERT INTO categories (nombreCategoría, descripción) VALUES (%s, %s)"
        val = (nombreCategoría, descripción)
    
    cursor.execute(sql, val)
    con.commit()
    con.close()
    
    return make_response(jsonify({"message": "Categoría guardada correctamente"}))

# Rutas para Clientes (Daniel)
@app.route("/clientes")
def clientes():
    if not con.con.is_connected():
        con.reconnect()
    
    cursor = con.cursor(dictionary=True)
    sql = "SELECT * FROM clientes ORDER BY nombreCliente"
    cursor.execute(sql)
    clientes = cursor.fetchall()
    con.close()
    
    return render_template("clientes.html", clientes=clientes)

@app.route("/cliente", methods=["POST"])
def guardarCliente():
    if not con.is_connected():
        con.reconnect()
    
    idCliente = request.form.get("idCliente")
    nombreCliente = request.form.get("nombreCliente")
    telefono = request.form.get("telefono")
    correoElectronico = request.form.get("correoElectronico")
    
    cursor = con.cursor()
    
    if idCliente:
        sql = """
        UPDATE clientes 
        SET nombreCliente = %s, telefono = %s, correoElectronico = %s 
        WHERE idCliente = %s
        """
        val = (nombreCliente, telefono, correoElectronico, idCliente)
    else:
        sql = """
        INSERT INTO clientes (nombreCliente, telefono, correoElectronico) 
        VALUES (%s, %s, %s)
        """
        val = (nombreCliente, telefono, correoElectronico)
    
    cursor.execute(sql, val)
    con.commit()
    con.close()
    
    return make_response(jsonify({"message": "Cliente guardado correctamente"}))

# Rutas para Lugares (Rene)
@app.route("/lugares")
def lugares():
    if not con.is_connected():
        con.reconnect()
    
    cursor = con.cursor(dictionary=True)
    sql = "SELECT * FROM lugares ORDER BY nombreLugar"
    cursor.execute(sql)
    lugares = cursor.fetchall()
    con.close()
    
    return render_template("lugares.html", lugares=lugares)

@app.route("/lugar", methods=["POST"])
def guardarLugar():
    if not con.is_connected():
        con.reconnect()
    
    idLugar = request.form.get("idLugar")
    nombreLugar = request.form.get("nombreLugar")
    direccion = request.form.get("direccion")
    ubicacion = request.form.get("ubicacion")
    
    cursor = con.cursor()
    
    if idLugar:
        sql = """
        UPDATE lugares 
        SET nombreLugar = %s, direccion = %s, ubicacion = %s 
        WHERE idLugar = %s
        """
        val = (nombreLugar, direccion, ubicacion, idLugar)
    else:
        sql = """
        INSERT INTO lugares (nombreLugar, direccion, ubicacion) 
        VALUES (%s, %s, %s)
        """
        val = (nombreLugar, direccion, ubicacion)
    
    cursor.execute(sql, val)
    con.commit()
    con.close()
    
    return make_response(jsonify({"message": "Lugar guardado correctamente"}))





@app.route("/productos")
def productos():
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT Id_Producto,
           Nombre_Producto,
           Precio,
           Existencias

    FROM productos

    ORDER BY Id_Producto DESC

    LIMIT 10 OFFSET 0
    """

    cursor.execute(sql)
    registros = cursor.fetchall()

    # Si manejas fechas y horas
    """
    for registro in registros:
        fecha_hora = registro["Fecha_Hora"]

        registro["Fecha_Hora"] = fecha_hora.strftime("%Y-%m-%d %H:%M:%S")
        registro["Fecha"]      = fecha_hora.strftime("%d/%m/%Y")
        registro["Hora"]       = fecha_hora.strftime("%H:%M:%S")
    """

    return render_template("productos.html", productos=registros)

@app.route("/productos/ingredientes/<int:id>")
def productos2(id):
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT productos.Nombre_Producto, ingredientes.*, productos_ingredientes.Cantidad FROM productos_ingredientes
    INNER JOIN productos ON productos.Id_Producto = productos_ingredientes.Id_Producto
    INNER JOIN ingredientes ON ingredientes.Id_Ingrediente = productos_ingredientes.Id_Ingrediente
    WHERE productos_ingredientes.Id_Producto = %s
    ORDER BY productos.Nombre_Producto
    """

    cursor.execute(sql, (id, ))
    registros = cursor.fetchall()

    return render_template("modal.html", productosIngredientes=registros)

@app.route("/productos/buscar", methods=["GET"])
def buscarProductos():
    if not con.is_connected():
        con.reconnect()

    args     = request.args
    busqueda = args["busqueda"]
    busqueda = f"%{busqueda}%"
    
    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT Id_Producto,
           Nombre_Producto,
           Precio,
           Existencias

    FROM productos

    WHERE Nombre_Producto LIKE %s
    OR    Precio          LIKE %s
    OR    Existencias     LIKE %s

    ORDER BY Id_Producto DESC

    LIMIT 10 OFFSET 0
    """
    val    = (busqueda, busqueda, busqueda)

    try:
        cursor.execute(sql, val)
        registros = cursor.fetchall()

        # Si manejas fechas y horas
        """
        for registro in registros:
            fecha_hora = registro["Fecha_Hora"]

            registro["Fecha_Hora"] = fecha_hora.strftime("%Y-%m-%d %H:%M:%S")
            registro["Fecha"]      = fecha_hora.strftime("%d/%m/%Y")
            registro["Hora"]       = fecha_hora.strftime("%H:%M:%S")
        """

    except mysql.connector.errors.ProgrammingError as error:
        print(f"Ocurrió un error de programación en MySQL: {error}")
        registros = []

    finally:
        con.close()

    return make_response(jsonify(registros))

@app.route("/producto", methods=["POST"])
# Usar cuando solo se quiera usar CORS en rutas específicas
# @cross_origin()
def guardarProducto():
    if not con.is_connected():
        con.reconnect()

    id          = request.form["id"]
    nombre      = request.form["nombre"]
    precio      = request.form["precio"]
    existencias = request.form["existencias"]
    # fechahora   = datetime.datetime.now(pytz.timezone("America/Matamoros"))
    
    cursor = con.cursor()

    if id:
        sql = """
        UPDATE productos

        SET Nombre_Producto = %s,
            Precio          = %s,
            Existencias     = %s

        WHERE Id_Producto = %s
        """
        val = (nombre, precio, existencias, id)
    else:
        sql = """
        INSERT INTO productos (Nombre_Producto, Precio, Existencias)
                    VALUES    (%s,          %s,      %s)
        """
        val =                 (nombre, precio, existencias)
    
    cursor.execute(sql, val)
    con.commit()
    con.close()

    return make_response(jsonify({}))

@app.route("/producto/<int:id>")
def editarProducto(id):
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT Id_Producto, Nombre_Producto, Precio, Existencias

    FROM productos

    WHERE Id_Producto = %s
    """
    val    = (id,)

    cursor.execute(sql, val)
    registros = cursor.fetchall()
    con.close()

    return make_response(jsonify(registros))

@app.route("/producto/eliminar", methods=["POST"])
def eliminarProducto():
    if not con.is_connected():
        con.reconnect()

    id = request.form["id"]

    cursor = con.cursor(dictionary=True)
    sql    = """
    DELETE FROM productos
    WHERE Id_Producto = %s
    """
    val    = (id,)

    cursor.execute(sql, val)
    con.commit()
    con.close()

    return make_response(jsonify({}))

