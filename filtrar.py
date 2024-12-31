import pandas as pd

# Ruta al archivo crudo
file_path = r"C:\Users\practicantev\juan\alimentos\registro.xlsx"  # Reemplaza con la ruta al archivo original

# Cargar la hoja que contiene los datos crudos
data_raw = pd.read_excel(file_path, sheet_name='SR Legacy and FNDDS', skiprows=3)

# Seleccionar columnas clave
relevant_columns = [
    'ID', 'name', 'Food Group', 'Calories', 'Fat (g)', 'Protein (g)', 
    'Carbohydrate (g)', 'Sugars (g)', 'Fiber (g)'
]

# Filtrar las columnas relevantes
filtered_data = data_raw[relevant_columns]

# Eliminar filas con datos críticos faltantes
filtered_data = filtered_data.dropna(subset=['ID', 'name', 'Calories'])

# Guardar el archivo limpio
filtered_data.to_excel("alimentos_limpios.xlsx", index=False)

# Confirmación
print("Datos limpios guardados en 'alimentos_limpios.xlsx'")
