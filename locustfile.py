import random
from locust import HttpUser, task, between

class PeleadorUser(HttpUser):
    # Simula un tiempo de espera aleatorio entre tareas de 1 a 3 segundos
    # Esto imita el comportamiento de un usuario real que lee la página
    wait_time = between(1, 3)

    @task(3)
    def ver_home_page(self):
        """
        a) Respuesta de Home Page - Index
        Visita la página principal donde está el formulario negro con dorado y el video.
        """
        self.client.get("/")

    @task(1)
    def registrar_usuario(self):
        """
        b) Registro de usuario
        Envía datos aleatorios por POST simulando que un peleador llena el formulario.
        """
        # Generamos datos aleatorios para que la base de datos de Render no colapse por duplicados
        documento_fake = str(random.randint(10000000, 99999999))
        num_aleatorio = random.randint(1, 9999)
        nombre_fake = f"Peleador_Locust_{num_aleatorio}"
        correo_fake = f"locust_{num_aleatorio}@sena.edu.co"
        
        datos_formulario = {
            "documento": documento_fake,
            "nombre": nombre_fake,
            "correo": correo_fake,
            "programa": "ADSO",
            "ficha": "3065826"
        }
        
        # Enviamos la petición POST para registrar al estudiante/peleador
        self.client.post("/", data=datos_formulario)

    @task(2)
    def consultar_informacion(self):
        """
        c) Consulta de información
        Entra a la tabla de registrados para ver a todos los peleadores.
        """
        self.client.get("/registrados")
