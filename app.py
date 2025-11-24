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

    return render_template("index.html")


@app.route("/home")
def landing():

    return render_template("index.html")


@app.route("/app")
def app2():
    if not con.is_connected():
        con.reconnect()

    con.close()

    return "<h5>Hola, soy la view app</h5>"


@app.route("/loginView")
def loginView():
    if not con.is_connected():
        con.reconnect()

    con.close()
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    if not con.is_connected():
        con.reconnect()
        
    try:
        
        cursor = con.cursor(dictionary=True)
        
        if request.is_json:
            data = request.get_json()
            nombre = data.get("username")
            contrasena = data.get("password")
        else:
            nombre = request.form.get("username")
            contrasena = request.form.get("password")
        sql = """
        SELECT * FROM Usuario WHERE nombre = %s AND contrasena = %s
        """
        val = (nombre, contrasena)
        cursor.execute(sql, val)
        res = cursor.fetchall()
        if(len(res) > 0):
            return "1"
        else:
            return "0"
    except Exception as e:
        return str(e)   

        
# EVENTOS
@app.route("/eventos/all")
def eventos():
    if not con.is_connected():
        con.reconnect()
    cursor = con.cursor(dictionary=True)
    sql = """
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
    return render_template("tablaEventos.html", eventos=eventos)


def triggerUpdateEventos():
    import pusher
    
    pusher_client = pusher.Pusher(
        app_id="2046019",
        key="db840e3e13b1c007269e",
        secret="0f06a16c943fdf4bbc11",
        cluster="us2",
        ssl=True
    )
    
    pusher_client.trigger("canalEventos", "newDataInserted", {"message": "triggered"})
    return make_response(jsonify({}))


@app.route("/eventos/agregar", methods=["POST"])
def guardarEvento():
    if not con.is_connected():
        con.reconnect()

    try:
        
        data = request.get_json()
        id1 = data.get("idEvento")
        descripcionEvento = data.get("descripcionEvento")
        fechainicio = data.get("fechaInicio")
        fechaFin = data.get("fechaFin")
        idCategoria = data.get("idCategoria")
        idLugar = data.get("idLugar")
        idCliente = data.get("idCliente")
    
        if id1:
            sql = """
            UPDATE eventos

            SET descripcionEvento = %s,
                fechaInicio = %s,
                fechaFin = %s,
                idCategoria = %s,
                idLugar = %s,
                idCliente = %s
            WHERE idEvento = %s
            """
        
            val = (descripcionEvento, fechainicio, fechaFin, idCategoria, idLugar, idCliente, id1)
        else:
            sql = """
        INSERT INTO eventos (descripcionEvento, fechaInicio, fechaFin, idCategoria, idLugar, idCliente)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
            val = (descripcionEvento, fechainicio, fechaFin, idCategoria, idLugar, idCliente)
    
        cursor = con.cursor(dictionary=True)
       
        try:
            cursor.execute(sql, val)
            con.commit()
            cursor.close()
            triggerUpdateEventos()
            return make_response(jsonify({}))
        except mysql.connector.Error as sql_error:
            cursor.close()
            return make_response(jsonify({"error": str(sql_error)}))
    except Exception as e:
        return make_response(jsonify({"error": str(e)}))


@app.route("/eventos/buscar", methods=["GET"])
def buscarEvento():
    if not con.is_connected():
        con.reconnect()

    args = request.args
    busqueda = args.get("busqueda", "")
    
    busqueda = f"%{busqueda}%"
    cursor = con.cursor(dictionary=True)
    sql = """
SELECT 
    e.*,
    c.nombreCategoria,
    l.nombreLugar,
    l.direccion,
    cl.nombreCliente
FROM eventos e
INNER JOIN categorias c ON e.idCategoria = c.idCategoria
INNER JOIN lugares l ON e.idLugar = l.idLugar
INNER JOIN clientes cl ON e.idCliente = cl.idCliente
WHERE e.descripcionEvento LIKE %s
    """
    val = (busqueda,)

    try:
        cursor.execute(sql, val)
        registros = cursor.fetchall()

    except mysql.connector.errors.ProgrammingError as error:
        print(f"Ocurrió un error de programación en MySQL: {error}")
        return error
        registros = []

    finally:
        cursor.close()

    return render_template("tablaEventos.html", eventos=registros)


@app.route("/eventos/eliminar", methods=["POST"])
def eliminarEvento():
    try:
        if not con.is_connected():
            con.reconnect()

        id = ""

        if request.is_json:
            data = request.get_json()
            if isinstance(data, dict):
                # Caso JSON con objeto
                id = str(data.get("idEvento", "")).strip()
            else:
                # Caso JSON con número suelto
                id = str(data).strip()
        else:
            # Caso enviado por form
            id = str(request.form.get("idEvento", "")).strip()

        if not id.isdigit():
            return make_response(jsonify({"error": "ID de evento no válido"}), 400)

        cursor = con.cursor(dictionary=True)
        sql = "DELETE FROM eventos WHERE idEvento = %s"
        cursor.execute(sql, (id,))
        con.commit()
        cursor.close()
        triggerUpdateEventos()
        return make_response(jsonify({"success": True}), 200)

    except Exception as e:
        import traceback
        print("ERROR en eliminarEvento:", traceback.format_exc())
        return make_response(jsonify({"ultimo error": str(e)}), 500)


@app.route("/eventos/editar/<int:id1>", methods=["GET"])
def editarEvento(id1):
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor(dictionary=True)
    sql = """
    SELECT * FROM eventos
    WHERE idEvento = %s
    """
    val = (id1,)

    cursor.execute(sql, val)
    registros = cursor.fetchall()
    con.close()
    return make_response(jsonify(registros))

  
@app.route("/eventos")
def eventos_view():
    if not con.is_connected():
        con.reconnect()
        
    cursor = con.cursor(dictionary=True)
    sql = "SELECT idLugar, nombreLugar FROM lugares"        
    cursor.execute(sql)
    lugares = cursor.fetchall()
    sql = "SELECT idCategoria,nombreCategoria FROM categorias"
    cursor.execute(sql)
    categorias = cursor.fetchall()
    sql = "SELECT idCliente,nombreCliente FROM clientes"
    cursor.execute(sql)
    clientes = cursor.fetchall()
    cursor.close()
        
    return render_template("eventos.html", lugares=lugares, categorias=categorias,clientes=clientes)


def triggerUpdateLugares():
    import pusher
    
    pusher_client = pusher.Pusher(
        app_id="2046019",
        key="db840e3e13b1c007269e",
        secret="0f06a16c943fdf4bbc11",
        cluster="us2",
        ssl=True
    )
    
    pusher_client.trigger("canalLugares", "newDataInserted", {"message": "triggered"})
    return make_response(jsonify({}))


# lugares
@app.route("/lugares")
def lugares():
    if not con.is_connected():
        con.reconnect()
        
    return render_template("lugares.html")


@app.route("/lugares/all", methods=["GET"])
def ListarLugares():
    try:
        if not con.is_connected():
            con.reconnect()
        
        cursor = con.cursor(dictionary=True)
        sql = "SELECT * FROM lugares"
        cursor.execute(sql)
        lugares = cursor.fetchall()
        cursor.close()
        
        return render_template("tablaLugares.html", lugares=lugares)
        
    except Exception as e:
        print(f"Error en ListarLugares: {str(e)}")
        return make_response(jsonify({"error": str(e)}), 500)
        return make_response(jsonify({"error": str(e)}))
    return render_template("tablaLugares.html", lugares=l)


@app.route("/lugar/guardar", methods=["POST"])
def guardarLugar():
    try:
        if not con.is_connected():
            con.reconnect()
            
        if request.is_json:
            data = request.get_json()
            print(" front lugar/guardar" + str(data))
            id1 = data.get("idLugar")
            nombreL = data.get("nombreLugar")
            direccion = data.get("direccion")
            ubicacion = data.get("ubicacion")
            
        cursor = con.cursor(dictionary=True)

        if id1:
            sql = """
            UPDATE lugares

            SET nombreLugar = %s,
                direccion = %s,
                ubicacion = %s
            WHERE idLugar = %s
            """
            val = (nombreL, direccion, ubicacion, id1)
        else:
            sql = """
            INSERT INTO lugares (nombreLugar, direccion, ubicacion)
            VALUES (%s, %s, %s)
            """
            val = (nombreL, direccion, ubicacion)

        cursor.execute(sql, val)
        con.commit()
        con.close()
        triggerUpdateLugares()
        return make_response(jsonify({"success": True}), 200)
        
    except Exception as e:
        print(f"Error en guardarLugar: {str(e)}")
        return make_response(jsonify({"error": str(e)}), 500)

@app.route("/lugar/editar/<int:id1>" , methods=["GET"])
def editarlugares(id1):
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor(dictionary=True)
    sql = """
    SELECT * FROM lugares
    WHERE idLugar = %s
    """
    val = (id1,)

    cursor.execute(sql, val)
    registros = cursor.fetchall()
    con.close()
    return make_response(jsonify(registros))

@app.route("/lugar/buscar", methods=["GET"])
def buscarLugar():
    if not con.is_connected():
        con.reconnect()
        
    args = request.args
    busqueda = args.get("busqueda", "")
    
    busqueda = f"%{busqueda}%"
    cursor = con.cursor(dictionary=True)
    sql = """
    SELECT *
    FROM lugares
    WHERE nombreLugar LIKE %s
    """
    val = (busqueda,)
    
    try:
        cursor.execute(sql, val)
        l = cursor.fetchall()

    except mysql.connector.errors.ProgrammingError as error:
        print(f"Ocurrió un error de programación en MySQL: {error}")
        return error
        l = []

    finally:
        cursor.close()

    return render_template("tablaLugares.html", lugares=l)



# categorias

# Ruta para obtener la vista principal de categorías
@app.route("/categorias", methods=["GET"])
def categorias():
    if not con.is_connected():
        con.reconnect()
    return render_template("categorias.html")


# Obtener todas las categorías
@app.route("/categorias/all", methods=["GET"])
def ListarCategorias():
    if not con.is_connected():
        con.reconnect()
    
    registros = []
    try:
        cursor = con.cursor(dictionary=True)
        sql = "SELECT * FROM categorias ORDER BY idCategoria DESC"
        cursor.execute(sql)
        registros = cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener categorías: {e}")
    finally:
        cursor.close()
    
    return render_template("tablaCategorias.html", categorias=registros)


def pusherCategoria():
    import pusher
    
    pusher_client = pusher.Pusher(
        app_id="2046019",
        key="db840e3e13b1c007269e",
        secret="0f06a16c943fdf4bbc11",
        cluster="us2",
        ssl=True
    )
    
    pusher_client.trigger("canalCategorias", "newDataInserted", {"message": "triggered"})
    return make_response(jsonify({}))


# Guardar nueva categoría
@app.route("/categorias/agregar", methods=["POST"])
def guardarCategoria():
        # Verificar conexión
        if not con.is_connected():
            con.reconnect()

        data = request.get_json()
        id1 = data.get("idCategoria")
        nombre = data.get("nombreCategoria")
        descripcion = data.get("descripcion")

        cursor = con.cursor(dictionary=True)

        if id1:
            sql = """
            UPDATE categorias
            SET nombreCategoria = %s,
                descripcion = %s
            WHERE idCategoria = %s
            """
            val = (nombre, descripcion, id1)
        else:
            sql = """
            INSERT INTO categorias (nombreCategoria, descripcion)
            VALUES (%s, %s)
            """
            val = (nombre, descripcion) 
  
        
        cursor.execute(sql, val)
        con.commit()
        cursor.close()
        pusherCategoria()
        return make_response(jsonify({}))
    
# Buscar categorías
@app.route("/categorias/buscar", methods=["GET"])
def buscarCategorias():
        if not con.is_connected():
            con.reconnect()

        args = request.args
        busqueda = args.get("busqueda", "").strip()
        
        print(f"Búsqueda recibida: '{busqueda}'")
        
        if not busqueda:
            # Si no hay búsqueda, devolver todas las categorías
            return ListarCategorias()
        
        busqueda_param = f"%{busqueda}%"
        
        cursor = con.cursor(dictionary=True)
        sql = """
        SELECT idCategoria, nombreCategoria, descripcion
        FROM categorias 
        WHERE nombreCategoria LIKE %s 
           OR descripcion LIKE %s
        ORDER BY idCategoria DESC
        """
        val = (busqueda_param, busqueda_param)

        print(f"Ejecutando consulta: {sql}")
        print(f"Valores: {val}")
        
        cursor.execute(sql, val)
        registros = cursor.fetchall()
        
        print(f"Resultados encontrados: {len(registros)}")
        for registro in registros:
            print(f"   - {registro['idCategoria']}: {registro['nombreCategoria']} - {registro['descripcion']}")

        cursor.close()
        
        return render_template("tablaCategorias.html", categorias=registros)

@app.route("/categorias/editar/<int:id>", methods=["GET"])
def editarCategoria(id):
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor(dictionary=True)
    sql = """
    SELECT * FROM categorias
    WHERE idCategoria = %s
    """
    val = (id,)

    cursor.execute(sql, val)
    registros = cursor.fetchall()
    con.close()
    return make_response(jsonify(registros))
        


    
# clientes
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
        sql = """
        SELECT * FROM clientes
        """

        cursor.execute(sql)
        registros = cursor.fetchall()
    except Exception as e:
        return make_response(jsonify({"error": str(e)}))
    return render_template("tablaClientes.html", clientes=registros)


@app.route("/clientes/buscar", methods=["GET"])
def buscarCliente():
    if not con.is_connected():
        con.reconnect()

    args = request.args
    busqueda = args.get("busqueda", "")
    
    busqueda = f"%{busqueda}%"
    cursor = con.cursor(dictionary=True)
    sql = """
    SELECT *
    FROM clientes
    WHERE nombreCliente LIKE %s
    """
    val = (busqueda,)

    try:
        cursor.execute(sql, val)
        registros = cursor.fetchall()

    except mysql.connector.errors.ProgrammingError as error:
        print(f"Ocurrió un error de programación en MySQL: {error}")
        return error
        registros = []

    finally:
        cursor.close()

    return render_template("tablaClientes.html", clientes=registros)

    
@app.route("/clientes/agregar", methods=["POST"])
def guardarCliente():
    if not con.is_connected():
        con.reconnect()

    data = request.get_json()
    print(" front cliente/agregar" + str(data))
    id1 = data.get("idCliente")        
    nombre = data.get("nombreCliente")
    telefono = data.get("telefono")
    correo = data.get("correoElectronico")

    cursor = con.cursor(dictionary=True)
    
    if id1:
        sql = """
        UPDATE clientes

        SET nombreCliente = %s,
            telefono = %s,
            correoElectronico = %s
        WHERE idCliente = %s
        """
    
        val = (nombre, telefono, correo, id1)
    else:
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


@app.route("/clientes/editar/<int:id1>", methods=["GET"])
def editarCliente(id1):
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor(dictionary=True)
    sql = """
    SELECT * FROM clientes
    WHERE idCliente = %s
    """
    val = (id1,)

    cursor.execute(sql, val)
    registros = cursor.fetchall()
    con.close()
    return make_response(jsonify(registros))


# ! ELIMINAR O COMENTAR AL SUBIR A GITHUB
#if __name__ == '__main__':
#    app.run(debug=True)

