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
@app.route("/eventos")
def eventos():
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor(dictionary=True)
    sql    = """
   SELECT e.idEvento, e.descripcionEvento AS nombre,
           DATE(e.fechaInicio) AS fecha,
           TIME(e.fechaInicio) AS hora,
           l.nombre AS lugar,
           c.nombre AS cliente,
           cat.nombre AS categoria
    FROM eventos e
    LEFT JOIN lugares l ON e.idLugar = l.idLugar
    LEFT JOIN clientes c ON e.idCliente = c.idCliente
    LEFT JOIN categorias cat ON e.idCategoria = cat.idCategoria
    """
    cursor.execute(sql)
    registros = cursor.fetchall()
    con.close()
    return render_template("eventos.html", eventos=registros)

#lugares
@app.route("/lugares")
def lugares():
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT idLugar, nombre FROM lugares
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
@app.route("/categorias")
def categorias():
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT * FROM categorias
    """

    cursor.execute(sql)
    registros = cursor.fetchall()

    return render_template("categorias.html", categorias=registros)


@app.route("/evento", methods=["POST"])
def guardarEvento():
    if not con.is_connected():
        con.reconnect()

    idEvento = request.form.get("idEvento")
    nombre   = request.form["nombre"]
    fecha    = request.form["fecha"]
    hora     = request.form["hora"]
    idLugar    = request.form["idLugar"]
    idCliente  = request.form["idCliente"]
    idCategoria= request.form["idCategoria"]

    fechaHoraInicio = f"{fecha} {hora}"

    cursor = con.cursor()

    if idEvento:
        sql = """
        UPDATE eventos
        SET descripcionEvento = %s,
            fechaInicio      = %s,
            idLugar          = %s,
            idCliente        = %s,
            idCategoria      = %s
        WHERE idEvento = %s
        """
        val = (nombre, fechaHoraInicio, idLugar, idCliente, idCategoria, idEvento)
    else:
        sql = """
        INSERT INTO eventos (descripcionEvento, fechaInicio, idLugar, idCliente, idCategoria)
        VALUES (%s, %s, %s, %s, %s)
        """
        val = (nombre, fechaHoraInicio, idLugar, idCliente, idCategoria)

    cursor.execute(sql, val)
    con.commit()
    con.close()

    return make_response(jsonify({}))


@app.route("/lugar", methods=["POST"])
def guardarLugar():
    if not con.is_connected():
        con.reconnect()

    idLugar = request.form.get("idLugar")
    nombre  = request.form["nombre"]

    cursor = con.cursor()

    if idLugar:
        sql = """
        UPDATE lugares
        SET nombre = %s
        WHERE idLugar = %s
        """
        val = (nombre, idLugar)
    else:
        sql = """
        INSERT INTO lugares (nombre)
        VALUES (%s)
        """
        val = (nombre,)

    cursor.execute(sql, val)
    con.commit()
    con.close()

    return make_response(jsonify({}))


@app.route("/cliente", methods=["POST"])
def guardarCliente():
    if not con.is_connected():
        con.reconnect()

    idCliente = request.form.get("idCliente")
    nombre    = request.form["nombre"]
    correo    = request.form.get("correo")  # si tienes este campo
    telefono  = request.form.get("telefono") # si existe

    cursor = con.cursor()

    if idCliente:
        sql = """
        UPDATE clientes
        SET nombre = %s,
            correo = %s,
            telefono = %s
        WHERE idCliente = %s
        """
        val = (nombre, correo, telefono, idCliente)
    else:
        sql = """
        INSERT INTO clientes (nombre, correo, telefono)
        VALUES (%s, %s, %s)
        """
        val = (nombre, correo, telefono)

    cursor.execute(sql, val)
    con.commit()
    con.close()

    return make_response(jsonify({}))


@app.route("/categoria", methods=["POST"])
def guardarCategoria():
    if not con.is_connected():
        con.reconnect()

    idCategoria = request.form.get("idCategoria")
    nombre      = request.form["nombre"]

    cursor = con.cursor()

    if idCategoria:
        sql = """
        UPDATE categorias
        SET nombre = %s
        WHERE idCategoria = %s
        """
        val = (nombre, idCategoria)
    else:
        sql = """
        INSERT INTO categorias (nombre)
        VALUES (%s)
        """
        val = (nombre,)

    cursor.execute(sql, val)
    con.commit()
    con.close()

    return make_response(jsonify({}))


@app.route("/eventos/buscar", methods=["GET"])
def buscarEventos():
    if not con.is_connected():
        con.reconnect()

    args     = request.args
    busqueda = args["busqueda"]
    busqueda = f"%{busqueda}%"

    cursor = con.cursor(dictionary=True)
    sql = """
    SELECT e.idEvento, e.descripcionEvento AS nombre,
           DATE(e.fechaInicio) AS fecha,
           TIME(e.fechaInicio) AS hora,
           l.nombre AS lugar,
           c.nombre AS cliente,
           cat.nombre AS categoria
    FROM eventos e
    LEFT JOIN lugares l ON e.idLugar = l.idLugar
    LEFT JOIN clientes c ON e.idCliente = c.idCliente
    LEFT JOIN categorias cat ON e.idCategoria = cat.idCategoria
    WHERE e.descripcionEvento LIKE %s
       OR l.nombre LIKE %s
       OR c.nombre LIKE %s
       OR cat.nombre LIKE %s
    ORDER BY e.idEvento DESC
    LIMIT 10 OFFSET 0
    """
    val = (busqueda, busqueda, busqueda, busqueda)

    try:
        cursor.execute(sql, val)
        registros = cursor.fetchall()
    except mysql.connector.errors.ProgrammingError as error:
        print(f"Ocurrió un error en MySQL: {error}")
        registros = []
    finally:
        con.close()

    return make_response(jsonify(registros))


@app.route("/lugares/buscar", methods=["GET"])
def buscarLugares():
    if not con.is_connected():
        con.reconnect()

    args     = request.args
    busqueda = args["busqueda"]
    busqueda = f"%{busqueda}%"

    cursor = con.cursor(dictionary=True)
    sql = """
    SELECT idLugar, nombre
    FROM lugares
    WHERE nombre LIKE %s
    ORDER BY idLugar DESC
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
    SELECT idCategoria, nombre
    FROM categorias
    WHERE nombre LIKE %s
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


@app.route("/categoria/eliminar", methods=["POST"])
def eliminarCategoria():
    if not con.is_connected():
        con.reconnect()

    idCategoria = request.form["idCategoria"]

    cursor = con.cursor()
    sql = "DELETE FROM categorias WHERE idCategoria = %s"
    val = (idCategoria,)

    cursor.execute(sql, val)
    con.commit()
    con.close()

    return make_response(jsonify({}))





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






