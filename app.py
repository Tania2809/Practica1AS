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
    password="*Q~ic:$9XVr2")


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


# EVENTOS



#lugares
@app.route("/lugares")
def lugares():
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT * FROM lugares
    """

    cursor.execute(sql)
    registros = cursor.fetchall()

    return render_template("lugares.html", lugares=registros)


#clientes
@app.route("/clientes")
def clientes():
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT * FROM clientes
    """

    cursor.execute(sql)
    registros = cursor.fetchall()

    return render_template("clientes.html", clientes=registros)



#categorias
@app.route("/categorias/agregar", methods=["POST"])
def guardarCategoria():
    if not con.is_connected():
        con.reconnect()

    if request.is_json:
        data = request.get_json()
        nombre = data.get("nombreCategoria")
        descripcion = data.get("descripcion")
    else:
        nombre = request.form.get("nombreCategoria")
        descripcion = request.form.get("descripcion")

    cursor = con.cursor(dictionary=True)
    sql = """
    INSERT INTO categorias (nombreCategoria, descripcion)
    VALUES (%s, %s)
    """
    val = (nombre, descripcion)
    cursor.execute(sql, val)
    con.commit()
    cursor.close()
    return make_response(jsonify({}))
    

@app.route("/categorias")
@app.route("/categories")
def categorias():
    # Renderiza la plantilla que contiene formulario y tabla
    return render_template("categorias.html")

@app.route("/categorias/lista")
def categorias_lista():
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM categorias")
    registros = cursor.fetchall()
    cursor.close()
    return jsonify(registros)

@app.route("/categoria/eliminar", methods=["POST"])
def eliminarCategoria():
    if not con.is_connected():
        con.reconnect()

    if request.is_json:
        idCategoria = request.get_json().get("idCategoria")
    else:
        idCategoria = request.form.get("idCategoria")

    cursor = con.cursor()
    sql = "DELETE FROM categorias WHERE idCategoria = %s"
    val = (idCategoria,)
    cursor.execute(sql, val)
    con.commit()
    cursor.close()
    return make_response(jsonify({}))






@app.route("/lugar", methods=["POST"])
def guardarLugar():
    if not con.is_connected():
        con.reconnect()
        
        nombre    = request.form["nombre"]
        direccion = request.form["direccion"]
        ubicacion = request.form["ubicacion"]
        
        cursor = con.cursor(dictionary=True)
        
        sql = """
        INSERT INTO lugares (nombre, direccion, ubicacion)
        VALUES (%s, %s, %s)
        """
        
        val = (nombre, direccion, ubicacion)

    cursor.execute(sql, val)
    con.commit()
    con.close()

    return make_response(jsonify({}))


@app.route("/cliente", methods=["POST"])
def guardarCliente():
    if not con.is_connected():
        con.reconnect()

    nombre    = request.form["nombre"]
    correo    = request.form.get("correo")  # si tienes este campo
    telefono  = request.form.get("telefono") # si existe
    
    cursor = con.cursor(dictionary=True)
    
    sql = """
    INSERT INTO clientes (nombre, correo, telefono)
    VALUES (%s, %s, %s)
    """
    val = (nombre, correo, telefono)

    cursor.execute(sql, val)
    con.commit()
    con.close()

    return make_response(jsonify({}))



    

@app.route("/clientes/buscar", methods=["GET"])
def buscarClientes():
    if not con.is_connected():
        con.reconnect()

    args     = request.args
    busqueda = args["busqueda"]
    busqueda = f"%{busqueda}%"

    cursor = con.cursor(dictionary=True)
    sql = """
    SELECT idCliente, nombre, correo, telefono
    FROM clientes
    WHERE nombre LIKE %s
       OR correo LIKE %s
       OR telefono LIKE %s
    ORDER BY idCliente DESC
    LIMIT 10 OFFSET 0
    """
    val = (busqueda, busqueda, busqueda)

    try:
        cursor.execute(sql, val)
        registros = cursor.fetchall()
    except mysql.connector.errors.ProgrammingError as error:
        print(f"Ocurrió un error en MySQL: {error}")
        registros = []
    finally:
        con.close()

    return make_response(jsonify(registros))



@app.route("/categorias/buscar", methods=["GET"])
def buscarCategorias():
    if not con.is_connected():
        con.reconnect()
        
    args     = request.args
    busqueda = args["busqueda"]
    busqueda = f"%{busqueda}%"

    cursor = con.cursor(dictionary=True)
    sql = """
    SELECT idCategoria, nombreCategoria, descripcion
    FROM categorias
    WHERE nombreCategoria LIKE %s
    ORDER BY idCategoria DESC
    LIMIT 10 OFFSET 0
    """
    val = (busqueda,)

    try:
        cursor.execute(sql, val)
        registros = cursor.fetchall()
    except mysql.connector.errors.ProgrammingError as error:
        print(f"Ocurrió un error en MySQL: {error}")
        registros = []
    finally:
        con.close()

    return make_response(jsonify(registros))







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



