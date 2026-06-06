import pandas as pd
import numpy as np

def generate_synthetic_data(num_samples=1000):
    """
    Gera dados agrícolas sintéticos.
    """
    np.random.seed(42)


    soil_humidity = np.random.uniform(10, 90, num_samples)  # %
    ph_level = np.random.uniform(4, 9, num_samples)         # pH
    temperature = np.random.uniform(10, 40, num_samples)    # Celsius
    rainfall = np.random.uniform(50, 200, num_samples)      # mm
    
    # Valores NPK (Nitrogênio, Fósforo, Potássio)
    nitrogen = np.random.uniform(0, 100, num_samples)
    phosphorus = np.random.uniform(0, 100, num_samples)
    potassium = np.random.uniform(0, 100, num_samples)

    # Cálculo de Produtividade Sintética (Lógica simplificada)
    # Condições ótimas: pH ~6.5, Umidade ~60%, Temp ~25, etc.
    
    yield_score = (
        - 2 * (ph_level - 6.5)**2 
        - 0.1 * (soil_humidity - 60)**2 
        - 0.2 * (temperature - 25)**2
        + 0.5 * rainfall
        + 0.3 * nitrogen
        + 0.2 * phosphorus
        + 0.1 * potassium
    )
    
    # Normalizar e adicionar ruído
    crop_yield = 100 + yield_score + np.random.normal(0, 10, num_samples)
    crop_yield = np.maximum(0, crop_yield) # Garantir que não haja produtividade negativa

    data = pd.DataFrame({
        'soil_humidity': soil_humidity,
        'ph_level': ph_level,
        'temperature': temperature,
        'rainfall': rainfall,
        'nitrogen': nitrogen,
        'phosphorus': phosphorus,
        'potassium': potassium,
        'crop_yield': crop_yield
    })

    return data

if __name__ == "__main__":
    df = generate_synthetic_data()
    print(df.head())
    df.to_csv("synthetic_farm_data.csv", index=False)
    print("Dados salvos em synthetic_farm_data.csv")
