import subprocess
import os
import pandas as pd

def executar_analise_r():
    """
    Executa o script R/analise.R via subprocesso.
    Se o interpretador R não estiver instalado, captura o erro e calcula
    as estatísticas via pandas como fallback.
    Retorna (output_text, r_installed, success)
    """
    script_path = os.path.join("R", "analise.R")
    
    # Verificar se os CSVs existem
    if not os.path.exists("dados_cana.csv") and not os.path.exists("dados_laranja.csv"):
        return "⚠️ Nenhum arquivo de dados (dados_cana.csv ou dados_laranja.csv) foi localizado na raiz. Por favor, cadastre parcelas e exporte para CSV na aba anterior primeiro.", True, False

    try:
        # Tenta executar Rscript
        result = subprocess.run(
            ["Rscript", script_path],
            capture_output=True,
            text=True,
            check=True,
            timeout=15
        )
        return result.stdout, True, True
    except FileNotFoundError:
        # Rscript não foi localizado (R não instalado)
        # Modo Fallback: Calcular via Pandas
        output = "⚠️ [Aviso] Interpretador R (Rscript) não foi localizado no sistema local.\n"
        output += "🔄 Executando Fallback Estatístico nativo (Python / Pandas) para validação:\n\n"
        
        for csv_name in ["dados_cana.csv", "dados_laranja.csv"]:
            if os.path.exists(csv_name):
                output += f"--- Analisando {csv_name} ---\n"
                try:
                    df = pd.read_csv(csv_name)
                    # Filtrar colunas numéricas
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    if len(numeric_cols) == 0:
                        output += "Nenhuma coluna numérica encontrada.\n\n"
                        continue
                    
                    for col in numeric_cols:
                        # Ignorar colunas de chave/identificador
                        if col.lower() in ["id", "registro"]:
                            continue
                        media = df[col].mean()
                        desvio = df[col].std()
                        # Lidar com desvio padrão nulo se houver apenas 1 linha
                        desvio_val = f"{desvio:.2f}" if not pd.isna(desvio) else "0.00 (amostra única)"
                        output += f"Coluna: {col}\n"
                        output += f"  Média: {media:.2f}\n"
                        output += f"  Desvio Padrão: {desvio_val}\n\n"
                except Exception as e:
                    output += f"Erro ao analisar arquivo: {e}\n\n"
            else:
                output += f"Arquivo {csv_name} não encontrado!\n"
                
        return output, False, True
    except subprocess.CalledProcessError as e:
        # Script R deu erro
        return f"❌ Erro ao executar o script R:\nStdout: {e.stdout}\nStderr: {e.stderr}", True, False
    except Exception as e:
        return f"❌ Ocorreu um erro inesperado: {e}", False, False
