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

@app.route("/pusherCategorias")
def pusherCategorias():
    import pusher
    
    pusher_client = pusher.Pusher(
        app_id="2046019",
        key="db840e3e13b1c007269e",
        secret="0f06a16c943fdf4bbc11",
        cluster="us2",
        ssl=True
    )
    
    pusher_client.trigger("canalCategorias", "eventoCategorias", {"message": "Hola Mundo"})
    return make_response(jsonify({}))

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
SELECT 
    e.*,
    c.nombreCategoria,
    l.nombreLugar,
    l.direccion,
    cl.nombreCliente
FROM eventos e
INNER JOIN categorias c ON e.idCategoria = c.idCategoria
INNER JOIN lugares l ON e.idLugar = l.idLugar
INNER JOIN clientes cl ON e.idCliente = cl.idCliente;
    """
    cursor.execute(sql)
    eventos = cursor.fetchall()
    return render_template("eventos.html", eventos=eventos)

@app.route("/eventos/agregar", methods=["POST"])
def guardarEvento():
    if not con.is_connected():
        con.reconnect()

    if request.is_json:
        data = request.get_json()
        descripcionUbicacion = data.get("descripcionUbicacion")
        descripcionEvento = data.get("descripcionEvento")
        fechainicio = data.get("fechainicio")
        fechaFin = data.get("fechaFin")
        
    else:
        descripcionUbicacion = request.form.get("descripcionUbicacion")
        descripcionEvento = request.form.get("descripcionEvento")
        fechainicio = request.form.get("fechainicio")
        fechaFin = request.form.gett("fechaFin")

    cursor = con.cursor(dictionary=True)
    sql = """
    INSERT INTO eventos (descripcionUbicacion", descripcionEvento, fechainicio, fechaFin)
    VALUES (%s, %s, %s, %s)
    """
    val = (descripcionUbicacion, descripcionEvento, fechainicio, fechaFin)
    cursor.execute(sql, val)
    con.commit()
    cursor.close()
    return make_response(jsonify({}))

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
    
@app.route("/categorias", methods=["GET"])
def categorias():
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor(dictionary=True)
    sql = "SELECT * FROM categorias"
    cursor.execute(sql)
    registros = cursor.fetchall()
    cursor.close()
    return render_template("categorias.html", categorias=registros)

@app.route("/categorias/buscar", methods=["GET"])
def buscarCategorias():
    if not con.is_connected():
        con.reconnect()

    args = request.args
    busqueda = args["busqueda"]
    busqueda = f"%{busqueda}%"
    
    cursor = con.cursor(dictionary=True)
    sql = """
    SELECT idCategoria,
           nombreCategoria,
           description
    FROM categorias
    WHERE nombreCategoria LIKE %s
    OR    description LIKE %s
    ORDER BY idCategoria DESC
    LIMIT 10 OFFSET 0
    """
    val = (busqueda, busqueda)

    try:
        cursor.execute(sql, val)
        registros = cursor.fetchall()


    except mysql.connector.errors.ProgrammingError as error:
        print(f"Ocurrió un error de programación en MySQL: {error}")
        registros = []

    finally:
        cursor.close()

    return make_response(jsonify(registros))
        


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

#clientes
def triggerUpdateCliente():
    import pusher
    
    pusher_client = pusher.Pusher(
        app_id="2046019",
        key="db840e3e13b1c007269e",
        secret="0f06a16c943fdf4bbc11",
        cluster="us2",
        ssl=True
    )
    
    pusher_client.trigger("canalClientes", "newDataInserted", {"message": "triggered"})
    return make_response(jsonify({}))


@app.route("/clientes")
def clientes():
    if not con.is_connected():
        con.reconnect()
        
    return render_template("clientes.html")

@app.route("/clientes/all", methods=["GET"])
def clientesLista():
    if not con.is_connected():
        con.reconnect()
    registros = []
    try:
        
        cursor = con.cursor(dictionary=True)
        sql    = """
        SELECT * FROM clientes
        """

        cursor.execute(sql)
        registros = cursor.fetchall()
    except Exception as e:
        return make_response(jsonify({"error": str(e)}))
    return render_template("tablaClientes.html", clientes=registros)


@app.route("/clientes/agregar", methods=["POST"])
def guardarCliente():
    if not con.is_connected():
        con.reconnect()

    if request.is_json:
        data = request.get_json()
        nombre = data.get("nombre")
        telefono = data.get("telefono")
        correo = data.get("correo")
    else:
        nombre = request.form.get("nombre")
        telefono = request.form.get("telefono")
        correo = request.form.get("correo")

    
    cursor = con.cursor(dictionary=True)
    
    sql = """
    INSERT INTO clientes (nombreCliente, correoElectronico, telefono)
    VALUES (%s, %s, %s)
    """
    val = (nombre, correo, telefono)

    cursor.execute(sql, val)
    con.commit()
    con.close()
    triggerUpdateCliente()
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













