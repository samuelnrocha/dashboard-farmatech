from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import sys
import os

# Adicionar o diretório raiz ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import joblib
from config.database import fetch_data
from src.data_generator import generate_synthetic_data

def load_data():
    """
    Carrega dados do banco de dados. Recorre à geração sintética se o banco estiver vazio ou falhar.
    """
    print("Tentando carregar dados do banco de dados...")
    df = fetch_data()
    
    if df.empty:
        print("Banco de dados vazio ou falha na conexão. Gerando dados sintéticos para treinamento...")
        df = generate_synthetic_data(num_samples=1000)
    else:
        print(f"Carregadas {len(df)} linhas do banco de dados.")
        
    return df

def train_model():
    df = load_data()
    
    X = df[['soil_humidity', 'ph_level', 'temperature', 'rainfall', 'nitrogen', 'phosphorus', 'potassium']]
    y = df['crop_yield']
    
    # Divisão
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Treinamento
    print("Treinando Random Forest Regressor...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Avaliação
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"Avaliação do Modelo:")
    print(f"MSE: {mse:.2f}")
    print(f"R2 Score: {r2:.2f}")
    
    # Salvar
    joblib.dump(model, 'model.joblib')
    print("Modelo salvo em model.joblib")

if __name__ == "__main__":
    train_model()
