from flask import Flask, render_template, request, redirect, url_for
import psycopg2
from psycopg2 import OperationalError

app = Flask(__name__)

DB_URL = "postgresql://torneo_dwdy_user:f3OpS5khsewskTq6FpdOA7cvG6tdWZp3@dpg-d8hmdbgjs32c73cr93eg-a.oregon-postgres.render.com/torneo_dwdy"

def get_db_connection():
    return psycopg2.connect(DB_URL)


# ----------------------------------------------------------------------
# a) Home Page – Index, página 1
# d) Permite el registro desde el módulo principal
# ----------------------------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":

        documento = request.form["documento"]
        nombre = request.form["nombre"]
        correo = request.form["correo"]
        programa = request.form["programa"]
        ficha = request.form["ficha"]

        if not documento.isdigit():
            return render_template(
                "error.html",
                mensaje_error="Documento inválido",
                detalle="El documento solo debe contener números."
            )

        if "@" not in correo:
            return render_template(
                "error.html",
                mensaje_error="Correo inválido",
                detalle="Ingrese un correo válido."
            )

        try:

            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO jugadores
                (documento, nombre, correo, programa, ficha)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (documento) DO NOTHING;
            """, (
                documento,
                nombre,
                correo,
                programa,
                ficha
            ))

            conn.commit()

            cur.close()
            conn.close()

            # Al registrar con éxito, redirige al módulo 2 para ver los datos reflejados
            return redirect(url_for("modulo_registro"))

        except OperationalError as e:

            return render_template(
                "error.html",
                mensaje_error="Error de conexión con la base de datos.",
                detalle=str(e)
            )

        except Exception as e:

            return render_template(
                "error.html",
                mensaje_error="Error inesperado.",
                detalle=str(e)
            )

    return render_template("index.html")


# ----------------------------------------------------------------------
# b) Registro de usuario, página 2
# c) Consulta de información, embebida en página 2
# ----------------------------------------------------------------------
@app.route("/modulo_registro", methods=["GET", "POST"])
def modulo_registro():

    if request.method == "POST":

        documento = request.form["documento"]
        nombre = request.form["nombre"]
        correo = request.form["correo"]
        programa = request.form["programa"]
        ficha = request.form["ficha"]

        if not documento.isdigit():
            return render_template(
                "error.html",
                mensaje_error="Documento inválido",
                detalle="El documento solo debe contener números."
            )

        if "@" not in correo:
            return render_template(
                "error.html",
                mensaje_error="Correo inválido",
                detalle="Ingrese un correo válido."
            )

        try:

            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO jugadores
                (documento, nombre, correo, programa, ficha)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (documento) DO NOTHING;
            """, (
                documento,
                nombre,
                correo,
                programa,
                ficha
            ))

            conn.commit()

            cur.close()
            conn.close()

            return redirect(url_for("modulo_registro"))

        except OperationalError as e:

            return render_template(
                "error.html",
                mensaje_error="Error de conexión con la base de datos.",
                detalle=str(e)
            )

        except Exception as e:

            return render_template(
                "error.html",
                mensaje_error="Error inesperado.",
                detalle=str(e)
            )

    # Lógica de Consulta de Información (c) Embebida en la misma Página 2
    try:

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                documento,
                nombre,
                correo,
                programa,
                ficha
            FROM jugadores
            ORDER BY nombre;
        """)

        estudiantes = cur.fetchall()

        cur.close()
        conn.close()

        return render_template(
            "modulo_registro.html",
            estudiantes=estudiantes
        )

    except Exception as e:

        return render_template(
            "error.html",
            mensaje_error="Error al consultar registros.",
            detalle=str(e)
        )


@app.route("/eliminar/<documento>")
def eliminar(documento):

    try:

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "DELETE FROM jugadores WHERE documento = %s",
            (documento,)
        )

        conn.commit()

        cur.close()
        conn.close()

        # Al eliminar, vuelve a cargar el módulo secundario de registros actualizados
        return redirect(url_for("modulo_registro"))

    except Exception as e:

        return render_template(
            "error.html",
            mensaje_error="Error al eliminar registro.",
            detalle=str(e)
        )


if __name__ == "__main__":
    app.run(debug=True)
