import os
import pandas as pd

class NutritionalOptimizer:
    def __init__(self):
        file_path = 'ai/utils/data/ingredientes.csv'
        if not os.path.exists(file_path):
            print("Archivo de datos no encontrado en la ruta especificada:", file_path)
            exit(1)
        
        try:
            self.data = pd.read_csv(file_path)
            print("Datos cargados exitosamente.")
        except Exception as e:
            print("Ocurrió un error al cargar el archivo:", e)
            exit(1)

    def sugerir_combinaciones(self, ingredientes_base, perfil_nutricional=None, textura_deseada=None):
        sugerencias = []
        for ingrediente in ingredientes_base:
            combinaciones = self.data[self.data['Ingrediente'] == ingrediente]
            print(f"Combinaciones para {ingrediente}:", combinaciones, "\n")

            if textura_deseada:
                combinaciones_textura = combinaciones[combinaciones['Textura'] == textura_deseada]
                if combinaciones_textura.empty:
                    print(f"No se encontraron combinaciones con textura '{textura_deseada}' para {ingrediente}. Usando todas las texturas disponibles.\n")
                else:
                    combinaciones = combinaciones_textura
                print(f"Combinaciones tras filtrar por textura '{textura_deseada}':", combinaciones, "\n")
            
            if perfil_nutricional:
                for nutriente in perfil_nutricional:
                    combinaciones_perfil = combinaciones[combinaciones['Perfil Nutricional'].str.contains(nutriente, case=False, na=False)]
                    if combinaciones_perfil.empty:
                        print(f"No se encontraron combinaciones con perfil nutricional '{nutriente}' para {ingrediente}. Usando todas las combinaciones disponibles.\n")
                    else:
                        combinaciones = combinaciones_perfil
                    print(f"Combinaciones tras filtrar por perfil nutricional '{nutriente}':", combinaciones, "\n")
            
            for _, row in combinaciones.iterrows():
                sugerencias.append({
                    "ingrediente": row['Ingrediente'],
                    "textura": row['Textura'],
                    "proteina": row.get('Proteina', 'N/A'),
                    "fibra": row.get('Fibra', 'N/A'),
                    "grasa": row.get('Grasa', 'N/A'),
                    "carbohidratos": row.get('Carbohidratos', 'N/A'),
                    "calorías": row.get('Calorías', 'N/A'),
                    "vitaminas": row.get('Vitaminas', 'N/A'),
                    "minerales": row.get('Minerales', 'N/A'),
                    "textura en procesamiento": row.get('Textura en Procesamiento', 'N/A'),
                    "estabilidad térmica": row.get('Estabilidad Térmica', 'N/A'),
                    "estabilidad en congelación": row.get('Estabilidad en Congelación', 'N/A'),
                    "viscosidad": row.get('Viscosidad', 'N/A'),
                    "elasticidad": row.get('Elasticidad', 'N/A'),
                    "sabor": row.get('Sabor', 'N/A'),
                    "olor": row.get('Olor', 'N/A'),
                    "color": row.get('Color', 'N/A'),
                    "sugerencia": row['Sugerencia']
                })
        
        print("Sugerencias finales:", sugerencias)
        return sugerencias

if __name__ == "__main__":
    optimizer = NutritionalOptimizer()
    ingredientes_base = ["Coliflor", "Garbanzo"]
    perfil_nutricional = ["Alto en Fibra", "Alto en Proteína"]
    textura_deseada = "Suave"
    
    sugerencias = optimizer.sugerir_combinaciones(ingredientes_base, perfil_nutricional, textura_deseada)
