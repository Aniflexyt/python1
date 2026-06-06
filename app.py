import os
from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
from psycopg2 import OperationalError

app = Flask(__name__)
app.secret_key = "clave-super-secreta"

# Render provee la URL de la base de datos como variable de entorno
DB_URL = os.environ.get("DATABASE_URL", "postgresql://usuario:password@host/basededatos")

def get_db_connection():
    return psycopg2.connect(DB_URL)

@app.route("/", methods=["GET"])
def index():
    try:
        # 3. Consultar todos los estudiantes registrados
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT documento, nombre, correo, programa, ficha FROM estudiantes;")
        estudiantes = cur.fetchall()
        cur.close()
        conn.close()
        return render_template("index.html", estudiantes=estudiantes)
    
    except OperationalError as e:
        # 4. Controlar excepciones: Error de conexión a la base de datos (Ej. SQLSTATE[08006])
        return render_template("error.html", mensaje_error="No se pudo conectar a la base de datos.", detalle=str(e))
    except Exception as e:
        # Error inesperado general del servidor
        return render_template("error.html", mensaje_error="Ocurrió un error inesperado en el servidor.", detalle=str(e))

@app.route("/registrar", methods=["POST"])
def registrar():
    documento = request.form.get("documento")
    nombre = request.form.get("nombre")
    correo = request.form.get("correo")
    programa = request.form.get("programa")
    ficha = request.form.get("ficha")

    # 2. Validar los datos registrados por el usuario
    if not documento or not nombre or not correo or not programa or not ficha:
        flash("Todos los campos son obligatorios. Por favor, completa el formulario.")
        return redirect(url_for("index"))

    try:
        # 1. Registrar estudiantes
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO estudiantes (documento, nombre, correo, programa, ficha) VALUES (%s, %s, %s, %s, %s)",
            (documento, nombre, correo, programa, ficha)
        )
        conn.commit()
        cur.close()
        conn.close()
        flash("¡Estudiante registrado exitosamente!")
        return redirect(url_for("index"))
        
    except psycopg2.IntegrityError:
        flash("Error: El documento ya se encuentra registrado.")
        return redirect(url_for("index"))
    except OperationalError as e:
        return render_template("error.html", mensaje_error="Se perdió la conexión al intentar guardar.", detalle=str(e))
    except Exception as e:
        return render_template("error.html", mensaje_error="Error al registrar.", detalle=str(e))

if __name__ == "__main__":
    app.run(debug=True)
