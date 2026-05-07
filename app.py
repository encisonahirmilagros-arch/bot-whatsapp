from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
import requests

app = Flask(__name__)

usuarios = {}

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

    # ---------------- PRESENTACIÓN ----------------
    if estado == "inicio":

        response.message(
            "👋 Hola! Somos Arcance Capacitaciones.\n\n"
            "Te damos la bienvenida a nuestro sistema de postulación.\n\n"
            "¿Qué te gustaría hacer?\n\n"
            "1️⃣ Enviar CV\n"
            "2️⃣ Información\n"
            "3️⃣ Hablar con RRHH"
        )

        usuarios[numero]["estado"] = "menu"

    # ---------------- MENÚ ----------------
    elif estado == "menu":

        if mensaje == "1":

            response.message(
                "📎 Genial 😊\n\n"
                "Enviá tu CV en PDF o imagen y nuestro equipo lo va a revisar con atención."
            )

            usuarios[numero]["estado"] = "esperando_cv"

        elif mensaje == "2":

            response.message(
                "📌 Información:\n\n"
                "Arcance se encuentra en proceso de incorporación de nuevos talentos.\n"
                "Buscamos personas responsables, con buena actitud y ganas de aprender.\n\n"
                "📎 Si te interesa, enviá tu CV en la opción 1."
            )

        elif mensaje == "3":

            response.message(
                "👩‍💼 Perfecto.\n\n"
                "Te vamos a derivar con el área de Recursos Humanos.\n"
                "Te van a responder a la brevedad."
            )

        else:

            response.message(
                "⚠️ Opción inválida. Por favor elegí 1, 2 o 3."
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

            archivo = requests.get(media_url)

            with open(ruta_archivo, "wb") as f:
                f.write(archivo.content)

            response.message("✅ ¡Gracias! Recibimos tu CV correctamente 😊")

            response.message("📌 ¿Querés agregar algún comentario o postularte a algún área en particular?")

            usuarios[numero]["estado"] = "puesto"

        else:

            response.message("⚠️ Por favor enviá tu CV en PDF o imagen.")

    # ---------------- PUESTO ----------------
    elif estado == "puesto":

        usuarios[numero]["puesto"] = mensaje

        response.message(
            "✅ Postulación registrada correctamente.\n\n"
            "📨 El equipo de RRHH va a revisar tu perfil."
        )

        usuarios[numero]["estado"] = "final"

    # ---------------- FINAL ----------------
    else:

        response.message("🙏 Gracias por comunicarte con Arcance. ¡Éxitos!")

    return str(response)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)