import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import os
import json
from dotenv import load_dotenv
import datetime
import pyperclip

# Cargar variables del .env
load_dotenv()


# Obtener credenciales desde el archivo .env
credenciales_json = os.getenv("GOOGLE_CREDENTIALS")

if credenciales_json:
    credenciales_dict = json.loads(credenciales_json)
    CREDENTIALS = Credentials.from_service_account_info(credenciales_dict, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
    CLIENT = gspread.authorize(CREDENTIALS)
else:
    st.error("Error: No se encontraron las credenciales de Google.")


dispersion_bonos = CLIENT.open("Disperción de bonos").sheet1
bonos_10k = CLIENT.open("bonos_10k").sheet1

# Mostrar logo en la esquina superior derecha
col1, col2 = st.columns([8, 1])
with col2:
    st.image("logo_r5.png", width=100)

st.title("Validación de Placa y Token para Bonos ⛽")
placa = st.text_input("Ingresa tu placa:")
token = st.text_input("Ingresa el token que llegó a tu correo:")
validar = st.button("Validar")

if validar:
    st.session_state['validated'] = True
    registros = dispersion_bonos.get_all_records()
    bono_encontrado = False
    
    for registro in registros:
        if (registro["Placa"].strip().upper() == placa.strip().upper() and
            registro["Token"].strip() == token.strip()):
            if registro["Fecha de Expiración"]:
                fecha_str = registro["Fecha de Expiración"].strip()
                
                formatos_fecha = ["%d/%m/%Y", "%Y-%m-%d"]
                fecha_expiracion = None
                for formato in formatos_fecha:
                    try:
                        fecha_expiracion = datetime.datetime.strptime(fecha_str, formato).date()
                        break
                    except ValueError:
                        continue
                
                if fecha_expiracion is None:
                    st.error("Error: Formato de fecha no reconocido en la base de datos.")
                    st.stop()
                
                hoy = datetime.date.today()

                
                if hoy > fecha_expiracion:
                    st.error(f"Lo sentimos, la fecha de expiración de tu código fue el {fecha_expiracion.strftime('%d/%m/%Y')}.")
                    st.stop()
            
            correo_usuario = registro["Correo"]
            bono_encontrado = True
            
            # Buscar un bono disponible
            bonos = bonos_10k.get_all_records()
            for i, bono in enumerate(bonos):
                if not bono["Correo"]:
                    bonos_10k.update_cell(i+2, bonos_10k.find("Correo").col, correo_usuario)
                    codigo_bono = bono["codigo"]
                    
                    st.text("✨ Tu código para seguir el viaje ✨ • Cópialo ahora ")
                    st.code(codigo_bono)
                    st.success("🎉 ¡FELICIDADES! ¡GANASTE TU BONO! 🎁\n\nSigue estos pasos para reclamar tu premio:\n\n1️⃣ COPIA este código exclusivo \n\n 2️⃣ Haz clic en \"Redimir mi Código\" \n\n 3️⃣  Pega tu código y ¡disfruta de tu recompensa!\n\n⏰ ¡No esperes! Tu bono especial te está esperando ⏰")
                    
                    
                    st.markdown('<div style="display: flex; justify-content: center; margin-top: 20px;"><a href="https://bonosenmascarados.plandereconocimientos.com/pages/login" style="padding: 20px 40px; background-color: #007BFF; color: white; text-decoration: none; font-size: 20px; border-radius: 10px; display: block; text-align: center;">Redimir mi Código</a></div>', unsafe_allow_html=True)
                    st.stop()
            
            st.error("Lo sentimos, no hay bonos disponibles en este momento.")
            st.stop()
    
    if not bono_encontrado:
        st.error("Lo sentimos, la placa y el token no coinciden o no están registrados en nuestro sistema. Por favor, intenta de nuevo más tarde o comunícate con nuestros copilotos por medio del chat de la App.")

if 'validated' in st.session_state and st.session_state['validated']:
    st.empty()
