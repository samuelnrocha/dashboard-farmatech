# ================================================ #
# Script de análise de CSVs: média e desvio padrão #
# ================================================ #

# -----Ler CSV-----
analisar_csv <- function(caminho_arquivo) {
  if (!file.exists(caminho_arquivo)) {
    cat(paste("Arquivo", caminho_arquivo, "não encontrado!\n"))
    return(NULL)
  }
  
  dados <- read.csv(caminho_arquivo, stringsAsFactors = FALSE)
  cat(paste("\n--- Analisando", basename(caminho_arquivo), "---\n"))
  
  # -----Seleciona colunas numéricas-----
  colunas_numericas <- sapply(dados, is.numeric)
  
  if (sum(colunas_numericas) == 0) {
    cat("Nenhuma coluna numérica encontrada.\n")
    return(NULL)
  }
  
  for (coluna in names(dados)[colunas_numericas]) {
    media <- mean(dados[[coluna]], na.rm = TRUE)
    desvio <- sd(dados[[coluna]], na.rm = TRUE)
    cat(paste0("Coluna: ", coluna, "\n"))
    cat(paste0("  Média: ", round(media, 2), "\n"))
    cat(paste0("  Desvio Padrão: ", round(desvio, 2), "\n\n"))
  }
}

# -----Análise dos dois conjuntos de dados (caminhos relativos)-----
analisar_csv("dados_cana.csv")
analisar_csv("dados_laranja.csv")
