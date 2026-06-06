from flask import Flask, render_template, request, redirect, url_for
import psycopg2
from psycopg2 import OperationalError

app = Flask(__name__)
app.secret_key = "clave-super-secreta"

DB_URL = "postgresql://torneo_dwdy_user:f3OpS5khsewskTq6FpdOA7cvG6tdWZp3@dpg-d8hmdbgjs32c73cr93eg-a.oregon-postgres.render.com/torneo_dwdy"


def get_db_connection():
    return psycopg2.connect(DB_URL)


@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":

        documento = request.form["documento"]
        nombre = request.form["nombre"]
        correo = request.form["correo"]
        programa = request.form["programa"]
        ficha = request.form["ficha"]

        # VALIDACIONES

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

                ON CONFLICT (documento)
                DO NOTHING;
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

            return redirect(url_for("menu"))

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


@app.route("/menu")
def menu():
    return render_template("menu.html")


@app.route("/registrados")
def registrados():

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
            "registrados.html",
            estudiantes=estudiantes
        )

    except OperationalError as e:

        return render_template(
            "error.html",
            mensaje_error="Error al consultar registros.",
            detalle=str(e)
        )

    except Exception as e:

        return render_template(
            "error.html",
            mensaje_error="Error inesperado.",
            detalle=str(e)
        )


if __name__ == "__main__":
    app.run(debug=True)
