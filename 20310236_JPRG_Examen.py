import requests
import pandas as pd
import hashlib
import time
import sqlite3
import json
from prettytable import PrettyTable
import unittest

# Función que manda llamar a la API para obtener el nombre del idioma en SHA1
def obtener_idioma_encriptado(country_code):
    url = f"https://restcountries.com/v3.1/alpha/{country_code}"
    response = requests.get(url)
    if response.status_code == 200:
        country_data = response.json()
        if 'languages' in country_data[0]:
            language_name = list(country_data[0]['languages'].values())[0]
            sha1_hash = hashlib.sha1(language_name.encode()).hexdigest()
            return sha1_hash
    return None

# Función para obtener el tiempo actual
def obtener_tiempo_actual():
    return time.strftime("%H:%M:%S", time.gmtime())

# Creación de tabla
def crear_tabla_paises():
    paises_regiones = [
        {'region': 'Africa', 'city': 'Angola', 'code': 'AO'},
        {'region': 'Asia', 'city': 'Japan', 'code': 'JP'},
        {'region': 'Europe', 'city': 'Germany', 'code': 'DE'},
        {'region': 'North America', 'city': 'Canada', 'code': 'CA'},
        {'region': 'South America', 'city': 'Brazil', 'code': 'BR'}
    ]

    # Listas para almacenar los datos
    data = []

    # Procesar cada país
    tiempos = []
    for entry in paises_regiones:
        start_time = time.time()  # Tiempo de inicio

        # Obtener el nombre del idioma encriptado en SHA1
        language_sha1 = obtener_idioma_encriptado(entry['code'])

        # Tiempo transcurrido
        end_time = time.time()
        elapsed_time = (end_time - start_time) * 1000  # Convertir a milisegundos

        # Agregar datos a la lista
        data.append({
            'Region': entry['region'],
            'City Name': entry['city'],
            'Language': language_sha1,
            'Time': f"{elapsed_time:.2f} ms"
        })

        # Guardar el tiempo transcurrido
        tiempos.append(elapsed_time)

    df = pd.DataFrame(data)

    # Conectar a la base de datos SQLite y guardar el DataFrame
    conn = sqlite3.connect('regiones.db')
    df.to_sql('paises_lenguas', conn, index=False, if_exists='replace')
    conn.close()

    # Calcular estadísticas de tiempo
    tiempos_serie = pd.Series(tiempos)
    tiempo_total = tiempos_serie.sum()
    tiempo_promedio = tiempos_serie.mean()
    tiempo_minimo = tiempos_serie.min()
    tiempo_maximo = tiempos_serie.max()

    # Mostrar estadísticas
    print(f"Tiempo total: {tiempo_total:.2f} ms")
    print(f"Tiempo promedio: {tiempo_promedio:.2f} ms")
    print(f"Tiempo mínimo: {tiempo_minimo:.2f} ms")
    print(f"Tiempo máximo: {tiempo_maximo:.2f} ms")

    # Guardar el DataFrame como JSON
    df.to_json('data.json', orient='records')

    # Crear tabla en formato PrettyTable
    tabla = PrettyTable()
    tabla.field_names = ["Region", "City Name", "Language", "Time"]
    for index, row in df.iterrows():
        tabla.add_row([row['Region'], row['City Name'], row['Language'], row['Time']])
    
    print(tabla)

# Ejecutar la función principal
crear_tabla_paises()

# Pruebas unitarias
class TestCountryFunctions(unittest.TestCase):

    def test_obtener_idioma_encriptado(self):
        # Test para Region Correcta
        resultado = obtener_idioma_encriptado('AO')
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado, hashlib.sha1('Portuguese'.encode()).hexdigest())

        # Test para un código inválido
        resultado = obtener_idioma_encriptado('ZZ')
        self.assertIsNone(resultado)

    def test_obtener_tiempo_actual(self):
        # Test para verificar que la función retorna un string con formato correcto
        tiempo_actual = obtener_tiempo_actual()
        self.assertRegex(tiempo_actual, r'^\d{2}:\d{2}:\d{2}$')

if __name__ == '__main__':
    unittest.main()
