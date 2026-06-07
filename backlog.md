# Backlog de Tarefas: Dashboard Consolidado (FarmTech Solutions)

Este documento contém o backlog estruturado de tarefas atômicas necessárias para a consolidação do ecossistema digital da FarmTech Solutions na Fase 7, englobando as entregas de desenvolvimento (código), infraestrutura/mensageria e documentação acadêmica.

---

## Trilha Técnica (Código & Integração)

### TASK_01_DASHBOARD_SETUP - Configuração Estrutural do Dashboard Base
- **Componente/Módulo:** `fase4-cap-pia/app.py` (ou novo `dashboard_consolidado.py` na raiz)
- **Executor:** Agente de Código
- **Descrição Atômica:** Expandir o dashboard Streamlit existente para servir como o ponto de controle central do projeto. Deve conter um menu lateral que organize a navegação entre todas as Fases do projeto (Fase 1 a 6) de forma limpa e intuitiva, configurando a barra lateral e aplicando o tema visual premium da FarmTech (paleta em tons de verde, escuro/glassmorphism).
- **Critérios de Aceitação (DoD):**
  - [x] Menu lateral do Streamlit funcionando com seções dedicadas para: Início, Clima e Plantio (Fase 1), Banco de Dados & CRUD (Fase 2), Monitoramento IoT (Fase 3), Predições de ML (Fase 4), Alertas de Cloud/AWS (Fase 5) e Visão Computacional (Fase 6).
  - [x] A aplicação roda localmente sem erros usando `streamlit run`.

### TASK_02_INTEGRATION_FASE_1_WEATHER - Integração da Consulta Meteorológica (Fase 1)
- **Componente/Módulo:** `FarmTech-FIAP/python/clima_api.py` integrado à UI do Dashboard
- **Executor:** Agente de Código
- **Descrição Atômica:** Importar e expor a funcionalidade de consulta de clima da API Open-Meteo no Streamlit. O usuário deve conseguir digitar o nome de uma cidade, clicar em "Consultar" e visualizar os dados estruturados de temperatura atual, velocidade do vento e a condição climática em tempo real.
- **Critérios de Aceitação (DoD):**
  - [x] Campo de texto para inserção da cidade no Streamlit.
  - [x] Retorno e renderização dos dados climáticos reais (via API pública) na UI de forma organizada e estilizada.
  - [x] Fallback caso a API falhe ou a cidade não seja localizada.

### TASK_03_INTEGRATION_FASE_1_PLANTING - Integração dos Cálculos de Plantio e Manejo (Fase 1)
- **Componente/Módulo:** `FarmTech-FIAP/python/plantio_cana.py` e `plantio_laranja.py` integrados na UI
- **Executor:** Agente de Código
- **Descrição Atômica:** Criar formulários interativos no Streamlit para permitir a inserção de dados e a realização dos cálculos de manejo de insumos e estimativas de área de plantio desenvolvidos na Fase 1 (cana e laranja), exibindo os resultados diretamente no dashboard.
- **Critérios de Aceitação (DoD):**
  - [x] Inputs interativos do Streamlit (sliders/number inputs) para os parâmetros de plantio.
  - [x] Exibição clara das métricas calculadas em tela.
  - [x] Botão de ação "Exportar Dados para CSV" que gera e salva os arquivos `dados_cana.csv` e `dados_laranja.csv` no diretório apropriado do projeto.

### TASK_04_INTEGRATION_FASE_1_R_ANALYSIS - Execução e Exibição da Análise Estatística em R (Fase 1)
- **Componente/Módulo:** Interface com `FarmTech-FIAP/R/analise.R`
- **Executor:** Agente de Código
- **Descrição Atômica:** Criar um botão no Streamlit que executa o script R (`analise.R`) via subprocesso em Python, lê a saída textual produzida pelo interpretador de R (médias e desvios padrão das colunas dos CSVs) e renderiza as estatísticas geradas diretamente na interface web.
- **Critérios de Aceitação (DoD):**
  - [x] Script R modificado para utilizar caminhos relativos ao invés do caminho absoluto fixado.
  - [x] Botão "Executar Análise Estatística R" que dispara o script.
  - [x] A saída textual do R (ou os dados interpretados) é renderizada de forma elegante no Streamlit.
  - [x] Mensagem de erro amigável caso o R não esteja instalado na máquina executora.

### TASK_05_INTEGRATION_FASE_2_CRUD - Interface de Gerenciamento CRUD (Fase 2)
- **Componente/Módulo:** Integração do módulo `smpc` com a UI do Streamlit
- **Executor:** Agente de Código
- **Descrição Atômica:** Integrar as regras de negócio de colheitas e propriedades implementadas em `smpc/src/services` (Cana-de-açúcar) em uma tela de gerenciamento de dados na Dashboard. Permitir visualizar a listagem de propriedades e colheitas, cadastrar novas propriedades através de formulários Streamlit e exibir o Relatório de Perdas em formato de tabela ou gráficos interativos.
- **Critérios de Aceitação (DoD):**
  - [x] Formulários Streamlit mapeando os atributos obrigatórios de Propriedades e Colheitas.
  - [x] Visualização das tabelas de propriedades e perdas lidas a partir do Oracle DB (ou simulado se offline).
  - [x] Opção de Backup e Restauração exposta na interface gráfica.

### TASK_06_INTEGRATION_FASE_3_IOT - Monitoramento e Simulação de Sensores IoT (Fase 3)
- **Componente/Módulo:** Conexão MQTT em `FarmTech-Cloud-Computing/ir-alem/servidor_dashboard.py` integrada ao Streamlit
- **Executor:** Agente de Código
- **Descrição Atômica:** Criar uma seção na dashboard que mostre as leituras em tempo real dos sensores simulados/físicos do ESP32 (temperatura, umidade do solo, luminosidade/pH). A interface deve se inscrever no broker MQTT (`broker.hivemq.com` no tópico `farmtech/sensores`) de forma assíncrona ou ler dados gerados, exibindo alertas visuais e a lógica de acionamento automático da bomba de irrigação.
- **Critérios de Aceitação (DoD):**
  - [x] Conexão assíncrona com broker MQTT ou simulador integrado de recebimento de mensagens.
  - [x] Gráficos ou cards dinâmicos que atualizam ao receber novos payloads JSON.
  - [x] Indicador visual do status da Bomba de Irrigação (Ativa / Inativa) baseado nas regras de umidade definidas na Fase 3.

### TASK_07_INTEGRATION_FASE_5_AWS_ALERTS - Serviço de Mensageria e Alertas Cloud (Fase 5)
- **Componente/Módulo:** Módulo `src/services/aws_sns_service.py` e emulador Moto Mock
- **Executor:** Agente de Código
- **Descrição Atômica:** Implementar a lógica de mensageria integrada à nuvem AWS utilizando a biblioteca de emulação `moto` (Moto Mock) para emular os serviços AWS SNS (SMS) ou AWS SES (E-mail). Quando as leituras de sensor (Fase 3) atingirem valores críticos ou quando pragas forem detectadas pela visão computacional (Fase 6), a dashboard geral deve realizar uma chamada via `boto3` mockada pela biblioteca `moto` para disparar um alerta, simulando o envio de E-mail/SMS para os operadores.
- **Critérios de Aceitação (DoD):**
  - [x] Implementação de um módulo Python que utilize o SDK `boto3` para enviar SMS/E-mail.
  - [x] Configuração do context manager `mock_aws` do Moto para interceptar as chamadas locais sem requerer chaves da AWS reais.
  - [x] Integração com a lógica de regras da dashboard (ex: se umidade < 30%, disparar alerta AWS).
  - [x] Exibição visual no dashboard do log de sucesso do disparo contendo o MessageId retornado pelo Moto.

### TASK_08_INTEGRATION_FASE_6_YOLO - Visão Computacional para Saúde de Lavouras (Fase 6)
- **Componente/Módulo:** Módulo baseado nos notebooks em `O-despertar-da-Rede-Neural/` integrado à UI
- **Executor:** Agente de Código
- **Descrição Atômica:** Exportar o pipeline de inferência YOLO contido nos notebooks `.ipynb` da Fase 6 para um arquivo Python estruturado. Criar uma aba no Streamlit onde o usuário possa carregar uma imagem estática da plantação (folhas, lavoura) ou selecionar uma imagem de teste, executar a rede YOLO sobre ela, e renderizar a imagem processada exibindo as bounding boxes e a classificação de pragas/doenças detectadas.
- **Ressalva / Condição de Início:** 
  > [!NOTE]
  > **CONDIÇÃO LIBERADA:** O Humano forneceu os pesos do YOLO (`best.pt` localizados no subdiretório `O-despertar-da-Rede-Neural/runs/train/`). O Agente de Código está autorizado a executar esta tarefa.
- **Critérios de Aceitação (DoD):**
  - [x] Presença dos arquivos de pesos `.pt` validados no diretório.
  - [x] Código de carregamento do modelo YOLO encapsulado em uma função Python (com cache para não recarregar a cada renderização do Streamlit).
  - [x] Componente `st.file_uploader` para envio de imagens.
  - [x] Exibição do resultado da imagem com as marcações de detecção geradas pelo YOLO.



### TASK_09_SECURITY_COMPLIANCE - Revisão de Segurança da Informação (Fase 5)
- **Componente/Módulo:** Diretórios de código e arquivos de configuração
- **Executor:** Agente de Código & Humano
- **Descrição Atômica:** Revisar o repositório consolidado para garantir que nenhuma chave de API, senhas do banco Oracle, ou chaves secretas AWS estejam expostas nos arquivos de código (compliance com as diretrizes da ISO 27001/ISO 27002 analisadas na Fase 5). Todas as configurações sensíveis devem ser movidas para um arquivo `.env` gerenciado pela biblioteca `python-dotenv`.
- **Critérios de Aceitação (DoD):**
  - [x] Garantia de que arquivos `.env` e chaves privadas estejam devidamente listados no `.gitignore`.
  - [x] Criação de um `.env.example` completo documentando todas as variáveis necessárias (Oracle, AWS, Open-Meteo se aplicável).

---

## Trilha de Entrega & Documentação (Acadêmica)

### TASK_10_UNIFIED_REPO_STRUCTURE - Organização do Repositório Unificado
- **Componente/Módulo:** Estrutura geral de pastas e arquivos no workspace
- **Executor:** Humano
- **Descrição Atômica:** Ajustar e padronizar toda a árvore de diretórios do projeto para que a entrega ocorra sob um único diretório raiz consistente, organizando os arquivos de dependências de cada fase sob um arquivo `requirements.txt` único na raiz do projeto consolidado.
- **Critérios de Aceitação (DoD):**
  - [x] Arquivo `requirements.txt` unificado na raiz do projeto com todas as bibliotecas necessárias instaladas.
  - [x] Organização limpa e inteligível de subpastas sem conflitos ou código órfão.

### TASK_11_DOCUMENTATION_README - Elaboração da Documentação no GitHub (README.md)
- **Componente/Módulo:** `README.md` (na raiz do repositório)
- **Executor:** Humano
- **Descrição Atômica:** Redigir a documentação técnica principal do repositório. O README deve detalhar o escopo de cada uma das Fases 1 a 6, explicar como executar o Dashboard consolidado da Fase 7, incluir screenshots do Dashboard em funcionamento, prints claros do serviço de mensageria da AWS (SNS/SES) configurado, e disponibilizar o link para o vídeo explicativo.
- **Critérios de Aceitação (DoD):**
  - [x] Seções estruturadas para cada Fase (Fase 1 à Fase 7).
  - [x] Prints da dashboard executando todas as integrações.
  - [x] Prints do serviço de mensageria na AWS com descrição detalhada dos fluxos de notificação.
  - [x] Link visível para o vídeo do YouTube (não listado).

### TASK_12_VIDEO_RECORDING - Gravação do Vídeo Explicativo da Solução
- **Componente/Módulo:** Vídeo demonstrativo (YouTube)
- **Executor:** Humano
- **Descrição Atômica:** Gravar um vídeo contínuo de até 10 minutos demonstrando a execução de todas as funcionalidades de ponta a ponta. O vídeo deve ser enviado no YouTube no modo "Não Listado".
- **Critérios de Aceitação (DoD):**
  - [ ] Duração total de no máximo 10 minutos.
  - [ ] Demonstração prática e visual de todas as funcionalidades descritas.
  - [ ] Envio feito e link adicionado ao README.

### TASK_13_TEACHERS_SHARE - Compartilhamento do Repositório Privado com Tutores
- **Componente/Módulo:** Configurações do repositório no GitHub
- **Executor:** Humano
- **Descrição Atômica:** Adicionar os usuários tutores `SabrinaOtoni` e `anacrissantos` como colaboradores do repositório privado no GitHub.
- **Critérios de Aceitação (DoD):**
  - [ ] Convite enviado no GitHub para ambos os usuários.
  - [ ] Status de convite documentado/verificado.

### TASK_14_FIAP_PORTAL_SUBMISSION - Submissão do PDF de Entrega
- **Componente/Módulo:** Portal do Aluno FIAP
- **Executor:** Humano
- **Descrição Atômica:** Gerar um arquivo PDF que contenha a identificação completa do grupo (nomes e RMs), o link do repositório no GitHub e a URL do vídeo do YouTube. Realizar o upload do PDF no portal acadêmico da FIAP dentro do prazo regulamentar.
- **Critérios de Aceitação (DoD):**
  - [ ] PDF gerado contendo o link correto e testado do GitHub e do vídeo.
  - [ ] Comprovante de submissão no portal da FIAP obtido.
