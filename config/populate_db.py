import sys
import os

# Adicionar o diretório raiz ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_generator import generate_synthetic_data
from config.database import create_table, insert_data

def main():
    print("Gerando dados sintéticos...")
    df = generate_synthetic_data(num_samples=1000)
    
    print("Inicializando banco de dados...")
    create_table()
    
    print("Populando banco de dados...")
    insert_data(df)
    
    print("Concluído!")

if __name__ == "__main__":
    main()
