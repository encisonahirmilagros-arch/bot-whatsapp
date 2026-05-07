from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
import requests

app = Flask(__name__)

usuarios = {}

# Carpeta donde se guardarán los CV
CARPETA_CV = "cv_recibidos"

if not os.path.exists(CARPETA_CV):
    os.makedirs(CARPETA_CV)

@app.route("/whatsapp", methods=["POST"])
def whatsapp():

    numero = request.form.get("From")
    mensaje = request.form.get("Body", "").lower()

    response = MessagingResponse()

    if numero not in usuarios:
        usuarios[numero] = {"estado": "inicio"}

    estado = usuarios[numero]["estado"]

    # ---------------- MENU PRINCIPAL ----------------

    if estado == "inicio":

        response.message(
            "👋 Hola! Bienvenido al sistema de postulaciones.\n\n"
            "Elegí una opción:\n\n"
            "1️⃣ Postularme\n"
            "2️⃣ Consultas\n"
            "3️⃣ Hablar con RRHH"
        )

        usuarios[numero]["estado"] = "menu"

    # ---------------- MENU ----------------

    elif estado == "menu":

        if mensaje == "1":

            response.message(
                "📎 Enviá tu CV en PDF o imagen."
            )

            usuarios[numero]["estado"] = "esperando_cv"

        elif mensaje == "2":

            response.message(
                "📌 Horarios:\nLunes a Viernes de 9 a 18 hs."
            )

        elif mensaje == "3":

            response.message(
                "👩‍💼 Un representante de RRHH te responderá pronto."
            )

        else:

            response.message(
                "⚠️ Opción inválida."
            )

    # ---------------- RECIBIR CV ----------------

    elif estado == "esperando_cv":

        num_media = int(request.form.get("NumMedia", 0))

        if num_media > 0:

            media_url = request.form.get("MediaUrl0")
            media_type = request.form.get("MediaContentType0")

            extension = media_type.split("/")[-1]

            nombre_archivo = f"{numero.replace(':', '_')}.{extension}"

            ruta_archivo = os.path.join(CARPETA_CV, nombre_archivo)

            # Descargar archivo
            archivo = requests.get(media_url)

            with open(ruta_archivo, "wb") as f:
                f.write(archivo.content)

            response.message(
                "✅ CV recibido correctamente."
            )

            response.message(
                "📌 ¿Para qué puesto o empresa querés postularte?"
            )

            usuarios[numero]["estado"] = "puesto"

        else:

            response.message(
                "⚠️ Debés enviar un CV."
            )

    # ---------------- GUARDAR PUESTO ----------------

    elif estado == "puesto":

        usuarios[numero]["puesto"] = mensaje

        response.message(
            f"✅ Postulación registrada para:\n{mensaje}"
        )

        response.message(
            "📨 RRHH revisará tu perfil."
        )

        usuarios[numero]["estado"] = "final"

    # ---------------- FINAL ----------------

    else:

        response.message(
            "Gracias por comunicarte 😊"
        )

    return str(response)
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
