import pandas as pd
import os
from datetime import datetime

# Ruta al archivo de datos
file_path = r"C:\Users\practicantev\juan\alimentos\alimentos_limpios.xlsx"
data = pd.read_excel(file_path)

# Ruta al archivo de historial
historial_path = "historial_consumo.csv"

# Variables para objetivos diarios
objetivo_proteinas = 0
limite_calorias = 0

# Función para mostrar alimentos y seleccionar uno
def seleccionar_alimento(data):
    print("\nLista de Alimentos:")
    print(data[['ID', 'name', 'Calories']].head(10))  # Muestra los primeros 10 alimentos
    alimento_id = input("Ingresa el ID del alimento que consumiste: ")
    try:
        alimento = data[data['ID'] == int(alimento_id)]
        if alimento.empty:
            raise ValueError
        return alimento.iloc[0]
    except ValueError:
        print("Entrada no válida. Por favor, inténtalo de nuevo.")
        return seleccionar_alimento(data)

# Función para calcular nutrientes basados en la cantidad
def calcular_nutrientes(alimento, cantidad):
    nutrientes = alimento[['Calories', 'Fat (g)', 'Protein (g)', 'Carbohydrate (g)']].astype(float)
    calculado = nutrientes * (cantidad / 100)
    return calculado

# Guardar registro en historial
def guardar_historial(alimento, cantidad, valores):
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    registro = pd.DataFrame({
        'Fecha y Hora': [fecha_hora],
        'Alimento': [alimento['name']],
        'Cantidad (g)': [cantidad],
        'Calorías': [valores['Calories']],
        'Grasas (g)': [valores['Fat (g)']],
        'Proteínas (g)': [valores['Protein (g)']],
        'Carbohidratos (g)': [valores['Carbohydrate (g)']],
    })
    
    if os.path.exists(historial_path):
        historial = pd.read_csv(historial_path)
        historial = pd.concat([historial, registro], ignore_index=True)
    else:
        historial = registro
    
    historial.to_csv(historial_path, index=False)
    print("\nRegistro guardado en el historial.")

# Alerta de progreso
def mostrar_alertas():
    if not os.path.exists(historial_path):
        print("\nNo hay registros en el historial.")
        return
    
    historial = pd.read_csv(historial_path)
    total_calorias = historial['Calorías'].sum()
    total_proteinas = historial['Proteínas (g)'].sum()
    
    proteinas_restantes = max(0, objetivo_proteinas - total_proteinas)
    calorias_restantes = max(0, limite_calorias - total_calorias)
    
    print(f"\n--- Alertas ---")
    print(f"Te faltan {proteinas_restantes:.2f} g de proteínas para alcanzar tu objetivo.")
    if total_calorias >= limite_calorias:
        print("¡Alerta! Has alcanzado o superado tu límite diario de calorías.")
    else:
        print(f"Te quedan {calorias_restantes:.2f} calorías antes de alcanzar tu límite.")

# Registro de alimentos
def registrar_alimentos():
    print("\n=== Registro de Alimentos Consumidos ===")
    alimento = seleccionar_alimento(data)
    print(f"\nSeleccionaste: {alimento['name']}")
    cantidad = float(input("Ingresa la cantidad consumida (en gramos): "))
    valores = calcular_nutrientes(alimento, cantidad)
    print(f"\nValores calculados para {cantidad} g de {alimento['name']}:")
    print(valores)
    guardar_historial(alimento, cantidad, valores)
    mostrar_alertas()

# Configuración de objetivos
def configurar_objetivos():
    global objetivo_proteinas, limite_calorias
    peso = float(input("\nIngresa tu peso corporal actual en kilogramos: "))
    altura = float(input("Ingresa tu altura en centímetros: "))
    edad = int(input("Ingresa tu edad en años: "))
    peso_deseado = float(input("Ingresa tu peso deseado en kilogramos: "))
    
    # Cálculo del requerimiento diario de proteínas
    objetivo_proteinas = peso * 1.8
    
    if peso_deseado > peso:
        # Meta de calorías para aumentar de peso
        limite_calorias = peso_deseado * 22 * 1.5 + 500
        print("\nObjetivo: Ganar peso.")
        print(f"Meta diaria de calorías: {limite_calorias:.2f} calorías.")
    elif peso_deseado < peso:
        # Límite de calorías para bajar de peso
        limite_calorias = 10 * peso + 6.25 * altura - 5 * edad + 5 - 500
        print("\nObjetivo: Perder peso.")
        print(f"Límite diario de calorías: {limite_calorias:.2f} calorías.")
    else:
        print("\nMantener el peso actual.")
        limite_calorias = 10 * peso + 6.25 * altura - 5 * edad + 5
        print(f"Requerimiento calórico diario: {limite_calorias:.2f} calorías.")
    
    print(f"\nObjetivo diario de proteínas: {objetivo_proteinas:.2f} g.")


# Resumen de consumo diario
def mostrar_resumen():
    if not os.path.exists(historial_path):
        print("\nNo hay registros en el historial.")
        return
    
    historial = pd.read_csv(historial_path)
    resumen = historial[['Calorías', 'Grasas (g)', 'Proteínas (g)', 'Carbohidratos (g)']].sum()
    print("\n=== Resumen del Día ===")
    print(resumen)

# Cerrar el día
def cerrar_dia():
    if not os.path.exists(historial_path):
        print("\nNo hay registros en el historial para este día.")
        return
    
    historial = pd.read_csv(historial_path)
    resumen = historial[['Calorías', 'Grasas (g)', 'Proteínas (g)', 'Carbohidratos (g)']].sum()
    print("\n=== Resumen del Día ===")
    print(resumen)
    print("\nHistorial del día cerrado y guardado. ¡Buen trabajo hoy!")
    historial.to_csv(f"historial_{datetime.now().strftime('%Y_%m_%d')}.csv", index=False)
    os.remove(historial_path)

# Menú principal
def menu():
    configurar_objetivos()
    while True:
        print("\n=== Menú ===")
        print("1. Registrar alimento consumido")
        print("2. Ver resumen diario")
        print("3. Cerrar el día")
        print("4. Salir")
        opcion = input("Selecciona una opción: ")
        
        if opcion == "1":
            registrar_alimentos()
        elif opcion == "2":
            mostrar_resumen()
        elif opcion == "3":
            cerrar_dia()
        elif opcion == "4":
            print("\n¡Hasta luego!")
            break
        else:
            print("\nEntrada no reconocida. Por favor, inténtalo de nuevo.")

# Ejecutar el menú
menu()
