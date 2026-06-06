from flask import Flask, render_template, request, session
import random
import psycopg2
from psycopg2 import OperationalError

app = Flask(__name__)
app.secret_key = "clave-super-secreta"  # Necesaria para manejar sesiones

# Tu URL exacta de Render
DB_URL = "postgresql://torneo_dwdy_user:f3OpS5khsewskTq6FpdOA7cvG6tdWZp3@dpg-d8hmdbgjs32c73cr93eg-a.oregon-postgres.render.com/torneo_dwdy"

def get_db_connection():
    return psycopg2.connect(DB_URL)

@app.route("/", methods=["GET", "POST"])
def index():
    # --- 1. LÓGICA ORIGINAL DE TU JUEGO ---
    if "numero" not in session:
        session["numero"] = random.randint(1, 100)
    if "veces" not in session:
        session["veces"] = 0

    mensaje = ""
    
    if request.method == "POST":
        try:
            # Opción A: El usuario envió un intento de juego
            if "intento" in request.form:
                intento = int(request.form["intento"])
                numero = session["numero"]
                session["veces"] += 1

                if intento < numero:
                    mensaje = "El número es MAYOR."
                elif intento > numero:
                    mensaje = "El número es MENOR."
                else:
                    mensaje = f"¡Adivinaste! Lo lograste en {session['veces']} oportunidades. Llena el formulario para guardar tu récord."
                    # Calculamos un puntaje: entre menos veces, más puntos (ej. max 100)
                    session["puntaje_ganado"] = max(100 - (session["veces"] * 5), 10)
                    
                    # Reiniciamos el juego
                    session["numero"] = random.randint(1, 100)
                    session["veces"] = 0

            # Opción B: El usuario envió el formulario con sus datos de estudiante
            elif "documento" in request.form:
                documento = request.form.get("documento")
                nombre = request.form.get("nombre")
                correo = request.form.get("correo")
                programa = request.form.get("programa")
                ficha = request.form.get("ficha")
                puntaje = session.get("puntaje_ganado", 0) # Tomamos el puntaje guardado en sesión

                # Requerimiento 1 y 2: Guardar y validar
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO jugadores (documento, nombre, correo, programa, ficha, puntaje) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (documento) 
                    DO UPDATE SET puntaje = GREATEST(jugadores.puntaje, EXCLUDED.puntaje);
                """, (documento, nombre, correo, programa, ficha, puntaje))
                conn.commit()
                cur.close()
                conn.close()
                
                mensaje = f"¡Datos de {nombre} guardados exitosamente en la base de datos!"
                session["puntaje_ganado"] = 0 # Reiniciamos el puntaje tras guardar

        except ValueError:
            mensaje = "Ingresa un número válido."
        except OperationalError as e:
            # Requerimiento 4: Control de excepciones de la Base de Datos
            return render_template("error.html", mensaje_error="No se pudo conectar a la base de datos para guardar.", detalle=str(e))
        except Exception as e:
            return render_template("error.html", mensaje_error="Ocurrió un error inesperado.", detalle=str(e))

    # --- 2. CONSULTAR TODOS LOS ESTUDIANTES/JUGADORES (Requerimiento 3) ---
    jugadores = []
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT nombre, puntaje, programa, ficha FROM jugadores ORDER BY puntaje DESC;")
        jugadores = cur.fetchall()
        cur.close()
        conn.close()
    except OperationalError as e:
        return render_template("error.html", mensaje_error="Fallo al consultar la tabla de posiciones.", detalle=str(e))

    return render_template("index.html", mensaje=mensaje, jugadores=jugadores)

if __name__ == "__main__":
    app.run(debug=True)
