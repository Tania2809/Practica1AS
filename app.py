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

def get_connection():
    return mysql.connector.connect(
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



# ================================
# CRUD - CATEGORIAS
# ================================
@app.route("/categorias", methods=["GET"])
def get_categorias():
    con = get_connection()
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM categorias ORDER BY idCategoria DESC")
    registros = cursor.fetchall()
    con.close()
    return make_response(jsonify(registros))

@app.route("/categoria", methods=["POST"])
def guardar_categoria():
    con = get_connection()
    cursor = con.cursor()

    idCategoria = request.form.get("id")
    nombre = request.form["nombre"]
    descripcion = request.form.get("descripcion")

    if idCategoria:  # Update
        sql = "UPDATE categorias SET nombreCategoria=%s, descripcion=%s WHERE idCategoria=%s"
        val = (nombre, descripcion, idCategoria)
    else:  # Insert
        sql = "INSERT INTO categorias (nombreCategoria, descripcion) VALUES (%s, %s)"
        val = (nombre, descripcion)

    cursor.execute(sql, val)
    con.commit()
    con.close()
    return make_response(jsonify({"success": True}))

@app.route("/categoria/eliminar", methods=["POST"])
def eliminar_categoria():
    con = get_connection()
    cursor = con.cursor()
    idCategoria = request.form["id"]
    cursor.execute("DELETE FROM categorias WHERE idCategoria=%s", (idCategoria,))
    con.commit()
    con.close()
    return make_response(jsonify({"success": True}))

# ================================
# CRUD - LUGARES
# ================================
@app.route("/lugares", methods=["GET"])
def get_lugares():
    con = get_connection()
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM lugares ORDER BY idLugar DESC")
    registros = cursor.fetchall()
    con.close()
    return make_response(jsonify(registros))

@app.route("/lugar", methods=["POST"])
def guardar_lugar():
    con = get_connection()
    cursor = con.cursor()
    idLugar = request.form.get("id")
    nombre = request.form["nombre"]
    direccion = request.form["direccion"]
    ubicacion = request.form["ubicacion"]

    if idLugar:
        sql = """UPDATE lugares SET nombreLugar=%s, direccion=%s, ubicacion=%s WHERE idLugar=%s"""
        val = (nombre, direccion, ubicacion, idLugar)
    else:
        sql = """INSERT INTO lugares (nombreLugar, direccion, ubicacion) VALUES (%s, %s, %s)"""
        val = (nombre, direccion, ubicacion)

    cursor.execute(sql, val)
    con.commit()
    con.close()
    return make_response(jsonify({"success": True}))

@app.route("/lugar/eliminar", methods=["POST"])
def eliminar_lugar():
    con = get_connection()
    cursor = con.cursor()
    idLugar = request.form["id"]
    cursor.execute("DELETE FROM lugares WHERE idLugar=%s", (idLugar,))
    con.commit()
    con.close()
    return make_response(jsonify({"success": True}))

# ================================
# CRUD - CLIENTES
# ================================
@app.route("/clientes", methods=["GET"])
def get_clientes():
    con = get_connection()
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM clientes ORDER BY idCliente DESC")
    registros = cursor.fetchall()
    con.close()
    return make_response(jsonify(registros))

@app.route("/cliente", methods=["POST"])
def guardar_cliente():
    con = get_connection()
    cursor = con.cursor()
    idCliente = request.form.get("id")
    nombre = request.form["nombre"]
    telefono = request.form["telefono"]
    correo = request.form["correo"]

    if idCliente:
        sql = """UPDATE clientes SET nombreCliente=%s, telefono=%s, correoElectronico=%s WHERE idCliente=%s"""
        val = (nombre, telefono, correo, idCliente)
    else:
        sql = """INSERT INTO clientes (nombreCliente, telefono, correoElectronico) VALUES (%s, %s, %s)"""
        val = (nombre, telefono, correo)

    cursor.execute(sql, val)
    con.commit()
    con.close()
    return make_response(jsonify({"success": True}))

@app.route("/cliente/eliminar", methods=["POST"])
def eliminar_cliente():
    con = get_connection()
    cursor = con.cursor()
    idCliente = request.form["id"]
    cursor.execute("DELETE FROM clientes WHERE idCliente=%s", (idCliente,))
    con.commit()
    con.close()
    return make_response(jsonify({"success": True}))

# ================================
# CRUD - EVENTOS
# ================================
@app.route("/eventos", methods=["GET"])
def get_eventos():
    con = get_connection()
    cursor = con.cursor(dictionary=True)
    sql = """
    SELECT e.*, l.nombreLugar, c.nombreCliente, cat.nombreCategoria
    FROM eventos e
    LEFT JOIN lugares l ON e.idLugar = l.idLugar
    LEFT JOIN clientes c ON e.idCliente = c.idCliente
    LEFT JOIN categorias cat ON e.idCategoria = cat.idCategoria
    ORDER BY e.idEvento DESC
    """
    cursor.execute(sql)
    registros = cursor.fetchall()
    con.close()
    return make_response(jsonify(registros))

@app.route("/evento", methods=["POST"])
def guardar_evento():
    con = get_connection()
    cursor = con.cursor()

    idEvento = request.form.get("id")
    idLugar = request.form["idLugar"]
    idCliente = request.form["idCliente"]
    idCategoria = request.form["idCategoria"]
    descripcionUbicacion = request.form["descripcionUbicacion"]
    descripcionEvento = request.form["descripcionEvento"]
    fechaInicio = request.form["fechaInicio"]
    fechaFin = request.form["fechaFin"]
    estado = request.form["estado"]

    if idEvento:
        sql = """
        UPDATE eventos 
        SET idLugar=%s, idCliente=%s, idCategoria=%s, descripcionUbicacion=%s,
            descripcionEvento=%s, fechaInicio=%s, fechaFin=%s, estado=%s
        WHERE idEvento=%s
        """
        val = (idLugar, idCliente, idCategoria, descripcionUbicacion, descripcionEvento, fechaInicio, fechaFin, estado, idEvento)
    else:
        sql = """
        INSERT INTO eventos (idLugar, idCliente, idCategoria, descripcionUbicacion, descripcionEvento, fechaInicio, fechaFin, estado)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """
        val = (idLugar, idCliente, idCategoria, descripcionUbicacion, descripcionEvento, fechaInicio, fechaFin, estado)

    cursor.execute(sql, val)
    con.commit()
    con.close()
    return make_response(jsonify({"success": True}))

@app.route("/evento/eliminar", methods=["POST"])
def eliminar_evento():
    con = get_connection()
    cursor = con.cursor()
    idEvento = request.form["id"]
    cursor.execute("DELETE FROM eventos WHERE idEvento=%s", (idEvento,))
    con.commit()
    con.close()
    return make_response(jsonify({"success": True}))


if __name__ == "__main__":
    app.run(debug=True)






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



