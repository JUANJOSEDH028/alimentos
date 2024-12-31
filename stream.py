import streamlit as st
import pandas as pd
import json
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from datetime import datetime
import os

# Ruta del archivo de alimentos (asegúrate de que está en el mismo directorio que este script)
file_path = "alimentos_limpios.xlsx"
data = pd.read_excel(file_path)

# Autenticación con Google Drive
def autenticar_google_drive():
    client_secrets_content = {
        "web": {
            "client_id": st.secrets["client_secrets.web.client_id"],
            "project_id": st.secrets["client_secrets.web.project_id"],
            "auth_uri": st.secrets["client_secrets.web.auth_uri"],
            "token_uri": st.secrets["client_secrets.web.token_uri"],
            "auth_provider_x509_cert_url": st.secrets["client_secrets.web.auth_provider_x509_cert_url"],
            "client_secret": st.secrets["client_secrets.web.client_secret"],
            "redirect_uris": st.secrets["client_secrets.web.redirect_uris"]
        }
    }

    with open("client_secrets.json", "w") as f:
        json.dump(client_secrets_content, f)

    gauth = GoogleAuth()
    gauth.LoadClientConfigFile("client_secrets.json")
    gauth.LocalWebserverAuth()
    gauth.SaveCredentialsFile("mycreds.txt")
    return GoogleDrive(gauth)

def subir_a_google_drive():
    drive = autenticar_google_drive()
    archivo = "historial_consumo.csv"

    if os.path.exists(archivo):
        file_drive = drive.CreateFile({'title': archivo})
        file_drive.SetContentFile(archivo)
        file_drive.Upload()
        st.success(f"Archivo '{archivo}' subido a Google Drive con éxito.")
    else:
        st.error("No se encontró el archivo para subir.")

# Función para cerrar el día
def cerrar_dia():
    st.header("Cierre del Día")
    if os.path.exists("historial_consumo.csv"):
        historial = pd.read_csv("historial_consumo.csv")
        resumen = historial[["Calorías", "Grasas (g)", "Proteínas (g)", "Carbohidratos (g)"]].sum()
        st.subheader("Resumen del Día")
        st.table(resumen)

        # Agregar la fecha del cierre al historial y guardar en un archivo general
        fecha_cierre = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        historial["Fecha de Cierre"] = fecha_cierre

        if os.path.exists("historial_general.csv"):
            historial_general = pd.read_csv("historial_general.csv")
            historial_general = pd.concat([historial_general, historial], ignore_index=True)
        else:
            historial_general = historial

        historial_general.to_csv("historial_general.csv", index=False)

        # Limpiar el historial diario
        os.remove("historial_consumo.csv")
        st.success("Día cerrado con éxito. Los datos se guardaron en el historial general.")
    else:
        st.info("No hay registros en el historial diario para cerrar el día.")

# Configuración inicial
st.sidebar.title("Menú")
opcion = st.sidebar.radio("Selecciona una opción:", ["Configurar Objetivos", "Registrar Alimentos", "Resumen Diario", "Subir a Google Drive", "Cerrar Día"])

def configurar_objetivos():
    st.header("Configuración de Objetivos")
    peso = st.number_input("Peso actual (kg):", min_value=1.0, step=0.1)
    altura = st.number_input("Altura (cm):", min_value=1.0, step=0.1)
    edad = st.number_input("Edad (años):", min_value=1, step=1)
    peso_deseado = st.number_input("Peso deseado (kg):", min_value=1.0, step=0.1)

    if st.button("Calcular Objetivos"):
        objetivo_proteinas = peso * 1.8
        if peso_deseado > peso:
            limite_calorias = peso_deseado * 22 * 1.5 + 500
            st.success(f"Meta diaria de calorías: {limite_calorias:.2f} calorías.")
        elif peso_deseado < peso:
            limite_calorias = 10 * peso + 6.25 * altura - 5 * edad + 5 - 500
            st.success(f"Límite diario de calorías: {limite_calorias:.2f} calorías.")
        else:
            limite_calorias = 10 * peso + 6.25 * altura - 5 * edad + 5
            st.success(f"Requerimiento calórico diario: {limite_calorias:.2f} calorías.")

        st.success(f"Objetivo diario de proteínas: {objetivo_proteinas:.2f} g.")

def registrar_alimentos():
    st.header("Registro de Alimentos Consumidos")
    alimento_nombre = st.selectbox("Selecciona un alimento:", data["name"])
    alimento = data[data["name"] == alimento_nombre].iloc[0]
    cantidad = st.number_input("Cantidad consumida (g):", min_value=1.0, step=1.0)

    if st.button("Registrar Alimento"):
        valores = alimento[["Calories", "Fat (g)", "Protein (g)", "Carbohydrate (g)"]] * (cantidad / 100)
        fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        registro = pd.DataFrame({
            'Fecha y Hora': [fecha_hora],
            'Alimento': [alimento["name"]],
            'Cantidad (g)': [cantidad],
            'Calorías': [valores["Calories"]],
            'Grasas (g)': [valores["Fat (g)"]],
            'Proteínas (g)': [valores["Protein (g)"]],
            'Carbohidratos (g)': [valores["Carbohydrate (g)"]],
        })

        if os.path.exists("historial_consumo.csv"):
            historial = pd.read_csv("historial_consumo.csv")
            historial = pd.concat([historial, registro], ignore_index=True)
        else:
            historial = registro

        historial.to_csv("historial_consumo.csv", index=False)
        st.success("Registro guardado con éxito.")

def mostrar_resumen():
    st.header("Resumen Diario")
    if os.path.exists("historial_consumo.csv"):
        historial = pd.read_csv("historial_consumo.csv")
        resumen = historial[["Calorías", "Grasas (g)", "Proteínas (g)", "Carbohidratos (g)"]].sum()
        st.table(resumen)
    else:
        st.info("No hay registros en el historial.")

if opcion == "Configurar Objetivos":
    configurar_objetivos()
elif opcion == "Registrar Alimentos":
    registrar_alimentos()
elif opcion == "Resumen Diario":
    mostrar_resumen()
elif opcion == "Subir a Google Drive":
    subir_a_google_drive()
elif opcion == "Cerrar Día":
    cerrar_dia()
