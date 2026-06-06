import streamlit as st
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import os
from config.database import fetch_data
from src.data_generator import generate_synthetic_data
from src.clima_api import obter_clima
from src.plantio import calcular_insumo_cana, calcular_ruas_laranja, calcular_comprimento_ruas_laranja, calcular_herbicida_laranja
from src.r_executor import executar_analise_r
from src.smpc_service import SMPCService, classificar_perda, obter_produtividade_esperada, calcular_perda
from src.iot_service import IOTService

# Configuração da página do Streamlit
st.set_page_config(
    page_title="FarmTech Solutions - Dashboard Consolidado",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicialização de variáveis de sessão para persistência de registros (Fase 1 - Plantio)
if 'parcelas_cana' not in st.session_state:
    st.session_state.parcelas_cana = []
if 'parcelas_laranja' not in st.session_state:
    st.session_state.parcelas_laranja = []

# Inicialização do serviço SMPC (Fase 2 - CRUD)
if 'smpc_service' not in st.session_state:
    st.session_state.smpc_service = SMPCService()

# Inicialização do serviço IoT (Fase 3)
if 'iot_service' not in st.session_state:
    st.session_state.iot_service = IOTService()


# Estilização CSS Customizada para Estética Premium (Tons de Verde, Dark Mode & Glassmorphism)
st.markdown("""
<style>
    /* Importar Fonte Outfit do Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
    
    /* Configuração Global de Fontes e Cores */
    html, body, [class*="css"], .stApp {
        font-family: 'Outfit', sans-serif;
        background-color: #080f0b;
        color: #e2f0e7;
    }
    
    /* Barra Lateral Estilizada */
    section[data-testid="stSidebar"] {
        background-color: #0b1510 !important;
        border-right: 1px solid rgba(46, 117, 89, 0.2);
    }
    
    section[data-testid="stSidebar"] .stMarkdown h1, 
    section[data-testid="stSidebar"] .stMarkdown h2, 
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #50c878 !important;
        font-weight: 700;
    }
    
    /* Cartões com efeito Glassmorphism */
    .glass-card {
        background: rgba(18, 33, 25, 0.65);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 12px;
        border: 1px solid rgba(80, 200, 120, 0.15);
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    
    .glass-card:hover {
        border-color: rgba(80, 200, 120, 0.35);
        box-shadow: 0 10px 40px 0 rgba(80, 200, 120, 0.12);
        transform: translateY(-2px);
    }
    
    /* Títulos e Destaques */
    .main-title {
        background: linear-gradient(135deg, #50c878 0%, #1d6f42 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.8rem;
        margin-bottom: 5px;
    }
    
    .subtitle {
        color: #a3c4b2;
        font-size: 1.1rem;
        margin-bottom: 25px;
    }
    
    /* Status Badge */
    .status-badge {
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }
    .status-badge.completed {
        background-color: rgba(80, 200, 120, 0.15);
        color: #50c878;
        border: 1px solid rgba(80, 200, 120, 0.3);
    }
    .status-badge.pending {
        background-color: rgba(240, 173, 78, 0.15);
        color: #f0ad4e;
        border: 1px solid rgba(240, 173, 78, 0.3);
    }
    .status-badge.functional {
        background-color: rgba(91, 192, 222, 0.15);
        color: #5bc0de;
        border: 1px solid rgba(91, 192, 222, 0.3);
    }
    
    /* Inputs customizados */
    div[data-baseweb="select"] > div {
        background-color: rgba(11, 21, 16, 0.8) !important;
        border-color: rgba(80, 200, 120, 0.25) !important;
        color: #e2f0e7 !important;
    }
    
    /* Botões Customizados */
    div.stButton > button {
        background: linear-gradient(135deg, #1d6f42 0%, #0e3b21 100%);
        color: #ffffff;
        border: 1px solid rgba(80, 200, 120, 0.3);
        padding: 10px 24px;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(29, 111, 66, 0.2);
    }
    
    div.stButton > button:hover {
        background: linear-gradient(135deg, #258c54 0%, #13522e 100%);
        border-color: rgba(80, 200, 120, 0.6);
        box-shadow: 0 6px 20px rgba(80, 200, 120, 0.3);
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

# ----------------- CARREGAMENTO DE DADOS & MODELOS (FASE 4) -----------------
@st.cache_resource
def load_model():
    try:
        model = joblib.load('model.joblib')
        return model
    except Exception as e:
        st.sidebar.error(f"Erro ao carregar o modelo de ML: {e}")
        return None

@st.cache_data
def get_data():
    df = fetch_data()
    if df.empty:
        # Fallback para dados sintéticos se banco offline
        df = generate_synthetic_data(1000)
    return df

model = load_model()
df = get_data()

# ----------------- MENU LATERAL DE NAVEGAÇÃO -----------------
st.sidebar.markdown("""
<div style='text-align: center; margin-bottom: 20px;'>
    <h1 style='margin: 0; font-size: 1.8rem;'>🌱 FarmTech</h1>
    <span style='color: #a3c4b2; font-size: 0.85rem;'>Solutions | Dashboard</span>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio(
    "Navegação por Fases",
    [
        "Início",
        "Clima e Plantio (Fase 1)",
        "Banco de Dados & CRUD (Fase 2)",
        "Monitoramento IoT (Fase 3)",
        "Predições de ML (Fase 4)",
        "Alertas de Cloud/AWS (Fase 5)",
        "Visão Computacional (Fase 6)"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='font-size: 0.8rem; color: #739682;'>
    <b>Status do Sistema:</b> Online<br>
    <b>Model Loaded:</b> {'Sim' if model else 'Não'}<br>
    <b>Ambiente:</b> Desenvolvimento (Fase 7)
</div>
""", unsafe_allow_html=True)

# ----------------- PÁGINAS DO DASHBOARD -----------------

# 1. PÁGINA INICIAL (BENTO GRID E APRESENTAÇÃO)
if page == "Início":
    st.markdown("<h1 class='main-title'>FarmTech Solutions</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Ecossistema Digital Consolidado de Agricultura Inteligente</p>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='glass-card'>
        <h3>👋 Bem-vindo ao Dashboard de Controle Central</h3>
        <p>Esta aplicação consolida de forma unificada os resultados e as tecnologias de todas as fases do projeto 
        FarmTech Solutions, desenvolvido para otimizar, prever e monitorar a produtividade agrícola de forma sustentável e inteligente.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Bento Grid para status das Fases
    st.subheader("Trilha de Integração do Projeto")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class='glass-card'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <h4>Fase 1: Clima e Manejo de Plantio</h4>
                <span class='status-badge pending'>Pendente de Integração</span>
            </div>
            <p style='font-size: 0.9rem; color: #a3c4b2; margin-top: 10px;'>
                Consulta meteorológica em tempo real usando a API Open-Meteo, modelagem de plantio de cana-de-açúcar e laranja, 
                e análise estatística avançada em linguagem R.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class='glass-card'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <h4>Fase 2: Banco de Dados & CRUD</h4>
                <span class='status-badge pending'>Pendente de Integração</span>
            </div>
            <p style='font-size: 0.9rem; color: #a3c4b2; margin-top: 10px;'>
                Persistência e gerenciamento de dados de propriedades, colheitas e perdas. Integrado diretamente com o Oracle DB (ou simulado).
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class='glass-card'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <h4>Fase 3: Monitoramento IoT</h4>
                <span class='status-badge pending'>Pendente de Integração</span>
            </div>
            <p style='font-size: 0.9rem; color: #a3c4b2; margin-top: 10px;'>
                Coleta de dados de sensores de umidade, temperatura e luminosidade via protocolo MQTT, com controle inteligente de irrigação.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class='glass-card'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <h4>Fase 4: Predições de Machine Learning</h4>
                <span class='status-badge completed'>Integrado / Ativo</span>
            </div>
            <p style='font-size: 0.9rem; color: #a3c4b2; margin-top: 10px;'>
                Algoritmo de regressão para previsão de produtividade com base no solo e clima, auxiliando na tomada de decisões e recomendações agrícolas.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class='glass-card'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <h4>Fase 5: Alertas Cloud & AWS</h4>
                <span class='status-badge pending'>Pendente de Integração</span>
            </div>
            <p style='font-size: 0.9rem; color: #a3c4b2; margin-top: 10px;'>
                Serviço de mensageria na nuvem para alertas críticos em tempo real usando emulador Moto Mock para simular AWS SNS/SES.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class='glass-card'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <h4>Fase 6: Visão Computacional (YOLO)</h4>
                <span class='status-badge pending'>Pendente de Integração</span>
            </div>
            <p style='font-size: 0.9rem; color: #a3c4b2; margin-top: 10px;'>
                Detecção de pragas e avaliação da saúde de folhas em tempo real utilizando redes neurais convolucionais (YOLOv8).
            </p>
        </div>
        """, unsafe_allow_html=True)

# 2. PÁGINA FASE 1 - CLIMA E PLANTIO
elif page == "Clima e Plantio (Fase 1)":
    st.markdown("<h1 class='main-title'>Fase 1: Clima e Manejo de Plantio</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Integração Open-Meteo, Cálculos de Manejo de Cana/Laranja e Análise Estatística em R</p>", unsafe_allow_html=True)
    
    tab_weather, tab_planting, tab_r = st.tabs(["🌦️ Consulta Meteorológica", "🌱 Manejo de Insumos & Plantio", "📊 Análise Estatística R"])
    
    with tab_weather:
        st.markdown("""
        <div class='glass-card'>
            <h4>🌦️ Consulta Meteorológica (API Open-Meteo)</h4>
            <p>Monitore o clima em tempo real para planejar as atividades de campo e manejo de insumos. 
            Abaixo, digite o nome de uma cidade para consultar as informações climáticas reais.</p>
        </div>
        """, unsafe_allow_html=True)
        
        cidade = st.text_input("Digite o nome da cidade", placeholder="Ex: Ribeirão Preto, SP", key="weather_city_input")
        if st.button("Consultar Clima", key="btn_weather_query"):
            if cidade:
                with st.spinner("Consultando dados de latitude, longitude e meteorologia..."):
                    dados_clima = obter_clima(cidade)
                
                if dados_clima:
                    st.markdown(f"### 📍 Condições em {dados_clima['cidade'].title()}")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"""
                        <div class='glass-card' style='text-align: center;'>
                            <h2 style='font-size: 3rem; margin: 0;'>{dados_clima['emoji']}</h2>
                            <p style='font-size: 1.1rem; color: #a3c4b2; margin: 5px 0 0 0;'>Condição</p>
                            <h4 style='color: #50c878; margin: 5px 0 0 0;'>{dados_clima['condicao']}</h4>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"""
                        <div class='glass-card' style='text-align: center;'>
                            <h2 style='font-size: 3rem; margin: 0;'>🌡️</h2>
                            <p style='font-size: 1.1rem; color: #a3c4b2; margin: 5px 0 0 0;'>Temperatura</p>
                            <h4 style='color: #50c878; margin: 5px 0 0 0;'>{dados_clima['temperatura']} °C</h4>
                        </div>
                        """, unsafe_allow_html=True)
                    with col3:
                        st.markdown(f"""
                        <div class='glass-card' style='text-align: center;'>
                            <h2 style='font-size: 3rem; margin: 0;'>💨</h2>
                            <p style='font-size: 1.1rem; color: #a3c4b2; margin: 5px 0 0 0;'>Velocidade do Vento</p>
                            <h4 style='color: #50c878; margin: 5px 0 0 0;'>{dados_clima['vento']} km/h</h4>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div style='font-size: 0.85rem; color: #739682; text-align: right; margin-top: -10px;'>
                        Coordenadas via Nominatim: Latitude {dados_clima['lat']:.4f}, Longitude {dados_clima['lon']:.4f}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error("❌ Cidade não encontrada ou erro na conexão com a API de Clima. Por favor, tente outro nome.")
            else:
                st.warning("⚠️ Insira o nome de uma cidade para prosseguir.")
                
    with tab_planting:
        st.markdown("""
        <div class='glass-card'>
            <h4>🌱 Cálculos de Plantio e Manejo (Cana & Laranja)</h4>
            <p>Monitore, simule e registre dados de manejo de solo e insumos da Fase 1. 
            Você pode cadastrar até 5 parcelas/registros por cultura e gerar relatórios em CSV.</p>
        </div>
        """, unsafe_allow_html=True)
        
        cultura_selecionada = st.radio("Selecione a cultura para manejo:", ["Cana-de-açúcar", "Laranja"], horizontal=True, key="planting_culture_selector")
        
        if cultura_selecionada == "Cana-de-açúcar":
            st.markdown("### 🌾 Manejo de Cana-de-açúcar")
            
            # Formulário
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                tem_area = st.selectbox("Possui o valor da área?", ["Sim", "Não (calcular área)"], key="cana_area_known")
                if tem_area == "Sim":
                    unidade_cana = st.selectbox("Unidade de medida:", ["m²", "ha"], key="cana_unit")
                    area_cana = st.number_input("Valor da área:", min_value=0.0, value=1.0, step=0.1, key="cana_area_value")
                else:
                    comprimento_cana = st.number_input("Comprimento (metros):", min_value=0.0, value=100.0, step=1.0, key="cana_length")
                    largura_cana = st.number_input("Largura (metros):", min_value=0.0, value=50.0, step=1.0, key="cana_width")
                    area_cana = comprimento_cana * largura_cana
                    unidade_cana = "m²"
                    st.info(f"📐 Área calculada: {area_cana:,.2f} m²")
            
            with col_c2:
                # Mostrar pré-cálculo
                NPK_dose = 500 # kg/ha
                if unidade_cana == "m²":
                    area_ha = area_cana / 10000
                else:
                    area_ha = area_cana
                insumo_estimado = area_ha * NPK_dose
                
                st.markdown(f"""
                <div class='glass-card' style='margin-top: 25px;'>
                    <h5>Estimativa de Insumo</h5>
                    <p style='margin: 0;'>Cultura: <b>Cana-de-açúcar</b></p>
                    <p style='margin: 0;'>Insumo: <b>Fertilizante NPK 20-05-20</b></p>
                    <h4 style='color: #50c878; margin-top: 10px;'>{insumo_estimado:,.2f} Kg</h4>
                    <p style='font-size: 0.8rem; color: #a3c4b2; margin: 0;'>Baseado na dosagem padrão de 500 kg/ha.</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Botão Adicionar
            if st.button("Adicionar Parcela de Cana", key="btn_add_cana"):
                if len(st.session_state.parcelas_cana) >= 5:
                    st.error("❌ Limite máximo de 5 parcelas de cana atingido! Exclua alguma para adicionar outra.")
                elif area_cana <= 0:
                    st.error("❌ A área deve ser maior que zero.")
                else:
                    id_parcela = f"P{len(st.session_state.parcelas_cana) + 1}"
                    insumo_kg, area_real_ha = calcular_insumo_cana(area_cana, unidade_cana)
                    nova_parcela = {
                        "ID": id_parcela,
                        "Cultura": "Cana-de-açúcar",
                        "Área Original": area_cana,
                        "Unidade": unidade_cana,
                        "Área (ha)": area_real_ha,
                        "Insumo": "Fertilizante NPK 20-05-20",
                        "Quantidade Insumo (Kg)": insumo_kg
                    }
                    st.session_state.parcelas_cana.append(nova_parcela)
                    st.success(f"✅ Parcela {id_parcela} adicionada com sucesso!")
            
            # Tabela
            if st.session_state.parcelas_cana:
                st.markdown("#### Parcela(s) Cadastrada(s)")
                df_cana = pd.DataFrame(st.session_state.parcelas_cana)
                st.dataframe(df_cana, use_container_width=True)
                
                # Excluir
                col_del_c1, col_del_c2 = st.columns(2)
                with col_del_c1:
                    parcela_para_deletar = st.selectbox("Selecione uma parcela para excluir:", [p["ID"] for p in st.session_state.parcelas_cana], key="select_del_cana")
                    if st.button("Excluir Parcela Selecionada", key="btn_del_cana"):
                        # remove
                        st.session_state.parcelas_cana = [p for p in st.session_state.parcelas_cana if p["ID"] != parcela_para_deletar]
                        # re-index IDs
                        for idx, p in enumerate(st.session_state.parcelas_cana, start=1):
                            p["ID"] = f"P{idx}"
                        st.rerun()
                
                with col_del_c2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("Exportar Dados para CSV", key="btn_export_cana"):
                        # Exporta
                        filepath = "dados_cana.csv"
                        df_cana.to_csv(filepath, index=False)
                        st.success(f"💾 Arquivo `{filepath}` gerado e salvo com sucesso na raiz do projeto!")
                        # Disponibilizar download via UI
                        csv_data = df_cana.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="⬇️ Baixar dados_cana.csv",
                            data=csv_data,
                            file_name="dados_cana.csv",
                            mime="text/csv",
                            key="download_btn_cana"
                        )
            else:
                st.info("Nenhuma parcela de cana cadastrada no momento.")
                
        elif cultura_selecionada == "Laranja":
            st.markdown("### 🍊 Manejo de Laranja")
            
            col_l1, col_l2 = st.columns(2)
            with col_l1:
                largura_terreno = st.number_input("Largura do terreno (m):", min_value=0.0, value=100.0, step=1.0, key="laranja_width")
                comprimento_lavoura = st.number_input("Comprimento do terreno (m):", min_value=0.0, value=200.0, step=1.0, key="laranja_length")
                espacamento_linhas = st.number_input("Espaçamento entre linhas (m):", min_value=0.1, value=6.0, step=0.1, key="laranja_spacing")
                dose_herbicida = st.number_input("Dose de herbicida (L/ha):", min_value=0.0, value=4.0, step=0.1, key="laranja_dose")
                
            with col_l2:
                # Mostrar pré-cálculo
                ruas = calcular_ruas_laranja(largura_terreno, espacamento_linhas)
                comprimento_total_ruas = calcular_comprimento_ruas_laranja(ruas, comprimento_lavoura)
                area_m2 = largura_terreno * comprimento_lavoura
                area_ha = area_m2 / 10000
                herbicida_litros = calcular_herbicida_laranja(largura_terreno, comprimento_lavoura, dose_herbicida)
                
                st.markdown(f"""
                <div class='glass-card'>
                    <h5>Simulação de Resultados</h5>
                    <p style='margin: 0;'>Total de Ruas: <b>{ruas}</b></p>
                    <p style='margin: 0;'>Comprimento das Ruas: <b>{comprimento_total_ruas:,.2f} m</b></p>
                    <p style='margin: 0;'>Área total: <b>{area_m2:,.2f} m² ({area_ha:,.2f} ha)</b></p>
                    <h4 style='color: #50c878; margin-top: 10px;'>{herbicida_litros:,.2f} Litros</h4>
                    <p style='font-size: 0.8rem; color: #a3c4b2; margin: 0;'>Dose de herbicida recomendada.</p>
                </div>
                """, unsafe_allow_html=True)
                
            # Botão Adicionar
            if st.button("Adicionar Registro de Laranja", key="btn_add_laranja"):
                if len(st.session_state.parcelas_laranja) >= 5:
                    st.error("❌ Limite máximo de 5 registros de laranja atingido! Exclua algum para adicionar outro.")
                elif largura_terreno <= 0 or comprimento_lavoura <= 0 or espacamento_linhas <= 0 or dose_herbicida <= 0:
                    st.error("❌ Todos os valores devem ser maiores que zero.")
                else:
                    id_registro = len(st.session_state.parcelas_laranja) + 1
                    novo_registro = {
                        "Registro": id_registro,
                        "Largura Terreno (m)": largura_terreno,
                        "Comprimento Lavoura (m)": comprimento_lavoura,
                        "Espaçamento (m)": espacamento_linhas,
                        "Dose Herbicida (L/ha)": dose_herbicida,
                        "Total Ruas": ruas,
                        "Comprimento Total Ruas (m)": comprimento_total_ruas,
                        "Área (m²)": area_m2,
                        "Área (ha)": area_ha,
                        "Herbicida Requerido (L)": herbicida_litros
                    }
                    st.session_state.parcelas_laranja.append(novo_registro)
                    st.success(f"✅ Registro {id_registro} adicionado com sucesso!")
                    
            # Tabela
            if st.session_state.parcelas_laranja:
                st.markdown("#### Registro(s) Cadastrado(s)")
                df_laranja = pd.DataFrame(st.session_state.parcelas_laranja)
                st.dataframe(df_laranja, use_container_width=True)
                
                # Excluir
                col_del_l1, col_del_l2 = st.columns(2)
                with col_del_l1:
                    reg_para_deletar = st.selectbox("Selecione um registro para excluir:", [r["Registro"] for r in st.session_state.parcelas_laranja], key="select_del_laranja")
                    if st.button("Excluir Registro Selecionado", key="btn_del_laranja"):
                        # remove
                        st.session_state.parcelas_laranja = [r for r in st.session_state.parcelas_laranja if r["Registro"] != reg_para_deletar]
                        # re-index
                        for idx, r in enumerate(st.session_state.parcelas_laranja, start=1):
                            r["Registro"] = idx
                        st.rerun()
                        
                with col_del_l2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("Exportar Dados para CSV", key="btn_export_laranja"):
                        # Exporta
                        filepath = "dados_laranja.csv"
                        df_laranja.to_csv(filepath, index=False)
                        st.success(f"💾 Arquivo `{filepath}` gerado e salvo com sucesso na raiz do projeto!")
                        # download via UI
                        csv_data = df_laranja.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="⬇️ Baixar dados_laranja.csv",
                            data=csv_data,
                            file_name="dados_laranja.csv",
                            mime="text/csv",
                            key="download_btn_laranja"
                        )
            else:
                st.info("Nenhum registro de laranja cadastrado no momento.")
        
    with tab_r:
        st.markdown("""
        <div class='glass-card'>
            <h4>📊 Análise Estatística Avançada (Linguagem R)</h4>
            <p>Execute o processamento estatístico nos CSVs de Cana e Laranja gerados. 
            O dashboard invocará o script R via subprocesso e capturará o resultado.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Botão para disparar o script R
        if st.button("Executar Análise Estatística R", key="btn_run_r_script"):
            with st.spinner("Invocando subprocesso do interpretador R..."):
                output_estatistico, r_instalado, sucesso = executar_analise_r()
                
            if sucesso:
                if not r_instalado:
                    st.info("ℹ️ Nota: Executando no modo Fallback em Python devido à ausência do interpretador R no sistema host.")
                else:
                    st.success("✅ Script R executado com sucesso!")
                
                st.markdown("##### 📝 Relatório Estatístico")
                st.code(output_estatistico, language="text")
            else:
                st.error(output_estatistico)

# 3. PÁGINA FASE 2 - CRUD
elif page == "Banco de Dados & CRUD (Fase 2)":
    st.markdown("<h1 class='main-title'>Fase 2: Banco de Dados & CRUD</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Sistema de Monitoramento e Planejamento de Colheitas (SMPC) - Cana-de-açúcar</p>", unsafe_allow_html=True)
    
    # Carregar instância do serviço
    smpc_service = st.session_state.smpc_service
    
    # Mostrar status da conexão
    status_db_text = "Online (Conectado ao Oracle DB)" if smpc_service.db_online else "Offline (Armazenamento Local Fallback)"
    status_db_color = "#50c878" if smpc_service.db_online else "#f0ad4e"
    st.markdown(f"""
    <div style='text-align: right; font-size: 0.85rem; color: #a3c4b2; margin-top: -20px; margin-bottom: 20px;'>
        Status do Banco Oracle: <span style='color: {status_db_color}; font-weight: bold;'>{status_db_text}</span>
    </div>
    """, unsafe_allow_html=True)

    tab_props, tab_harvest, tab_losses, tab_backup = st.tabs([
        "🏡 Propriedades Rurais", 
        "🌾 Registrar Colheita", 
        "📉 Relatório de Perdas", 
        "💾 Backup & Restauração"
    ])
    
    # --- TAB PROPRIEDADES ---
    with tab_props:
        st.markdown("""
        <div class='glass-card'>
            <h4>🏡 Cadastro e Listagem de Propriedades</h4>
            <p>Registre novas propriedades rurais indicando a área total, localização e classe de solo. 
            Estes dados são associados a cada colheita para predição e análise de perdas.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Cadastro
        with st.expander("➕ Cadastrar Nova Propriedade", expanded=False):
            with st.form("form_cadastrar_propriedade"):
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    nome_prop = st.text_input("Nome da Propriedade:", placeholder="Ex: Fazenda Boa Vista")
                    area_prop = st.number_input("Área Total (hectares):", min_value=0.1, value=10.0, step=1.0)
                with col_p2:
                    local_prop = st.text_input("Localização (Cidade, Estado):", placeholder="Ex: Ribeirão Preto, SP")
                    solo_prop = st.selectbox("Tipo de Solo principal:", [
                        "Latossolo vermelho",
                        "Latossolo vermelho-amarelo",
                        "Nitossolo",
                        "Argissolo",
                        "Cambissolo",
                        "Neossolo Quartzarênico",
                        "Neossolo Litólico",
                        "Planossolo",
                        "Gleissolo",
                        "Vertissolo",
                        "Organossolo",
                        "Outros"
                    ])
                
                btn_prop = st.form_submit_button("Confirmar Cadastro")
                if btn_prop:
                    if not nome_prop.strip() or not local_prop.strip():
                        st.error("❌ Preencha todos os campos obrigatórios (Nome e Localização).")
                    else:
                        sucesso, msg = smpc_service.cadastrar_propriedade(nome_prop.strip(), area_prop, local_prop.strip(), solo_prop)
                        if sucesso:
                            st.success(f"✅ {msg}")
                            st.rerun()
                        else:
                            st.error(f"❌ {msg}")
                            
        # Listagem
        propriedades = smpc_service.listar_propriedades()
        if propriedades:
            st.markdown("#### Propriedades Cadastradas")
            prop_data = []
            for p in propriedades:
                prop_data.append({
                    "ID": p.id,
                    "Nome": p.nome,
                    "Área Total (ha)": p.area_total,
                    "Localização": p.localizacao,
                    "Tipo de Solo": p.tipo_solo,
                    "Total Colheitas": p.obter_total_colheitas(),
                    "Qtd Colhida Acumulada (t)": p.obter_quantidade_total_colhida()
                })
            st.dataframe(pd.DataFrame(prop_data), use_container_width=True)
        else:
            st.info("Nenhuma propriedade cadastrada ainda. Use o formulário acima para registrar a primeira.")

    # --- TAB REGISTRAR COLHEITA ---
    with tab_harvest:
        st.markdown("""
        <div class='glass-card'>
            <h4>🌾 Registro de Colheita de Cana-de-açúcar</h4>
            <p>Selecione a propriedade produtora e registre as safras efetuadas, indicando a área de corte 
            e a tonelagem obtida.</p>
        </div>
        """, unsafe_allow_html=True)
        
        propriedades = smpc_service.listar_propriedades()
        if not propriedades:
            st.warning("⚠️ Cadastre pelo menos uma propriedade primeiro na aba 'Propriedades Rurais' para poder registrar colheitas.")
        else:
            prop_options = {p.nome: p for p in propriedades}
            selected_prop_name = st.selectbox("Selecione a propriedade rural:", list(prop_options.keys()))
            prop_selecionada = prop_options[selected_prop_name]
            
            st.markdown(f"""
            <div style='font-size: 0.9rem; color: #a3c4b2; margin-top: -10px; margin-bottom: 20px;'>
                Solo da propriedade selecionada: <b>{prop_selecionada.tipo_solo}</b> (Produtividade esperada: <b>{obter_produtividade_esperada(prop_selecionada.tipo_solo)} t/ha</b>)
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("form_registrar_colheita"):
                col_h1, col_h2 = st.columns(2)
                with col_h1:
                    data_col = st.date_input("Data da colheita:", datetime.now())
                    area_colhida = st.number_input("Área Colhida (hectares):", min_value=0.1, value=5.0, step=0.5)
                with col_h2:
                    qtd_colhida = st.number_input("Quantidade Colhida (toneladas):", min_value=0.1, value=400.0, step=10.0)
                    tipo_colheita = st.selectbox("Método de Colheita:", ["mecanica", "manual"])
                
                btn_col = st.form_submit_button("Confirmar Registro de Colheita")
                if btn_col:
                    if area_colhida > prop_selecionada.area_total:
                        st.warning(f"⚠️ Atenção: A área colhida ({area_colhida} ha) é maior que a área total cadastrada da propriedade ({prop_selecionada.area_total} ha).")
                    
                    data_str = data_col.strftime('%d/%m/%Y')
                    sucesso, msg = smpc_service.cadastrar_colheita(
                        prop_selecionada.id, data_str, area_colhida, qtd_colhida, 
                        tipo_colheita, prop_selecionada.tipo_solo
                    )
                    if sucesso:
                        st.success(f"✅ {msg}")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")

    # --- TAB RELATORIO DE PERDAS ---
    with tab_losses:
        st.markdown("""
        <div class='glass-card'>
            <h4>📉 Relatório Analítico de Perdas Agrícolas</h4>
            <p>Comparativo científico entre a produtividade real obtida e o rendimento potencial esperado do solo. 
            As perdas são classificadas de Baixa a Crítica.</p>
        </div>
        """, unsafe_allow_html=True)
        
        propriedades = smpc_service.listar_propriedades()
        all_colheitas_data = []
        
        if propriedades:
            for p in propriedades:
                for c in p.colheitas:
                    real_prod = c.produtividade
                    expected_prod = obter_produtividade_esperada(p.tipo_solo)
                    loss_pct = c.percentual_perda
                    if loss_pct is None:
                        loss_pct = calcular_perda(real_prod, expected_prod)
                    
                    class_loss = classificar_perda(loss_pct)
                    
                    all_colheitas_data.append({
                        "Propriedade": p.nome,
                        "Data Colheita": c.data,
                        "Solo": p.tipo_solo,
                        "Área Cortada (ha)": c.area_colhida,
                        "Qtd Colhida (t)": c.quantidade_colhida,
                        "Produtividade Real (t/ha)": real_prod,
                        "Produtividade Esperada (t/ha)": expected_prod,
                        "Perda (%)": loss_pct,
                        "Gravidade": class_loss
                    })
        
        if all_colheitas_data:
            df_losses = pd.DataFrame(all_colheitas_data)
            st.dataframe(df_losses, use_container_width=True)
            
            # Gráficos Interativos (DoD)
            st.subheader("Visualização Gráfica")
            
            col_g1, col_g2 = st.columns(2)
            
            with col_g1:
                # Perda média por propriedade
                st.markdown("##### Média de Perdas (%) por Propriedade")
                loss_by_prop = df_losses.groupby("Propriedade")["Perda (%)"].mean().reset_index()
                st.bar_chart(data=loss_by_prop, x="Propriedade", y="Perda (%)", color="#f0ad4e", use_container_width=True)
                
            with col_g2:
                # Produtividade Real vs Esperada por Propriedade
                st.markdown("##### Real vs Esperado (t/ha) por Propriedade")
                prod_by_prop = df_losses.groupby("Propriedade")[["Produtividade Real (t/ha)", "Produtividade Esperada (t/ha)"]].mean().reset_index()
                st.bar_chart(data=prod_by_prop, x="Propriedade", y=["Produtividade Real (t/ha)", "Produtividade Esperada (t/ha)"], color=["#50c878", "#5bc0de"], use_container_width=True)
        else:
            st.info("Nenhuma colheita cadastrada no momento para gerar relatórios e gráficos.")

    # --- TAB BACKUP & RESTAURAÇÃO (DoD) ---
    with tab_backup:
        st.markdown("""
        <div class='glass-card'>
            <h4>💾 Backup e Restauração de Dados</h4>
            <p>Exporte o banco de dados atual para um arquivo de backup em JSON ou restaure dados a partir de um backup existente.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_b1, col_b2 = st.columns(2)
        
        with col_b1:
            st.markdown("##### Gerar Backup JSON")
            if st.button("Gerar e Salvar Backup localmente", key="btn_save_backup_smpc"):
                # Gerar backup em arquivo físico
                filepath = "backup_smpc_harvest.json"
                sucesso, msg = smpc_service.exportar_backup(filepath)
                if sucesso:
                    st.success(f"✅ {msg}")
                    # Oferecer download
                    with open(filepath, "r", encoding="utf-8") as f:
                        json_str = f.read()
                    st.download_button(
                        label="⬇️ Baixar backup JSON",
                        data=json_str,
                        file_name="backup_smpc_harvest.json",
                        mime="application/json",
                        key="btn_download_backup_json"
                    )
                else:
                    st.error(msg)
                    
        with col_b2:
            st.markdown("##### Restaurar Backup JSON")
            backup_file = st.file_uploader("Selecione o arquivo de backup (.json):", type=["json"], key="uploader_backup_smpc")
            if backup_file is not None:
                json_data_str = backup_file.getvalue().decode("utf-8")
                if st.button("Confirmar Restauração de Backup", key="btn_confirm_restore_smpc"):
                    sucesso, msg = smpc_service.restaurar_backup(json_data_str)
                    if sucesso:
                        st.success(f"✅ {msg}")
                        st.rerun()
                    else:
                        st.error(msg)

# 4. PÁGINA FASE 3 - IOT
# 4. PÁGINA FASE 3 - IOT
elif page == "Monitoramento IoT (Fase 3)":
    st.markdown("<h1 class='main-title'>Fase 3: Monitoramento IoT</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Telemetria em Tempo Real de Sensores e Controle de Irrigação</p>", unsafe_allow_html=True)
    
    # Obter o serviço IoT de st.session_state
    iot = st.session_state.iot_service
    
    # Seção superior para controle e simulação
    col_ctrl, col_sim = st.columns([1, 2])
    
    with col_ctrl:
        st.markdown("""
        <div class='glass-card' style='height: 100%;'>
            <h4 style='color:#50c878; margin-top: 0; margin-bottom: 12px;'>⚙️ Painel de Controle</h4>
            <p style='font-size:0.9rem; color:#a3c4b2;'>Ajuste as configurações operacionais da lavoura e monitore a conectividade do broker MQTT.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Limiar de umidade configurável pelo operador
        limiar = st.slider("Limiar de Umidade para Bomba (%)", 10.0, 90.0, float(iot.limiar_umidade), step=1.0)
        iot.set_limiar_umidade(limiar)
        
        # Informações da conexão
        status_broker = "🟢 Conectado ao Broker" if iot.connected else "🔴 Desconectado (Fallback Local)"
        st.markdown(f"""
        <div style='background-color: rgba(11, 21, 16, 0.6); padding: 12px; border-radius: 8px; border: 1px solid rgba(80, 200, 120, 0.15); margin-top: 10px;'>
            <div style='font-size:0.85rem; margin-bottom: 4px;'><b>Broker:</b> <code>{iot.broker}</code></div>
            <div style='font-size:0.85rem; margin-bottom: 4px;'><b>Tópico:</b> <code>{iot.topic}</code></div>
            <div style='font-size:0.85rem;'><b>Status:</b> <span style='color:{"#50c878" if iot.connected else "#ff6b6b"}; font-weight:bold;'>{status_broker}</span></div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_sim:
        st.markdown("""
        <div class='glass-card' style='height: 100%;'>
            <h4 style='color:#50c878; margin-top: 0; margin-bottom: 8px;'>🎮 Simulador de ESP32 (Telemetria)</h4>
            <p style='font-size:0.9rem; color:#a3c4b2; margin-bottom: 12px;'>Simule o envio de telemetria física pelo ESP32 publicando mensagens JSON no broker MQTT.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            sim_temp = st.slider("Simular Temp (°C)", 10.0, 45.0, 26.0, step=0.5)
        with col_s2:
            sim_umid = st.slider("Simular Umidade (%)", 10.0, 95.0, 48.0, step=1.0)
        with col_s3:
            sim_lumi = st.slider("Simular Luz (lux)", 50, 1200, 600, step=10)
            
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("Enviar Leitura Manual", use_container_width=True):
                pub_ok = iot.publish_data(sim_temp, sim_umid, sim_lumi)
                if pub_ok:
                    st.success("Leitura publicada via MQTT!")
                else:
                    st.info("Fallback: Atualizado localmente (broker desconectado)")
        with col_btn2:
            if st.button("Simular Passo Físico", use_container_width=True):
                iot.simulate_step()
                st.success("Passo físico executado com variação aleatória!")
                
    st.markdown("---")
    
    # Fragmento Streamlit para atualização dinâmica dos dados a cada 2 segundos
    @st.fragment(run_every=2)
    def render_live_telemetry():
        latest = iot.get_latest_data()
        historico = iot.get_history()
        
        # Criar os cards de telemetria
        col1, col2, col3, col4 = st.columns(4)
        
        # Card Temperatura
        with col1:
            val_temp = latest["temperatura"]
            color_temp = "#ff6b6b" if val_temp > 32 else ("#50c878" if val_temp >= 18 else "#4dabf7")
            st.markdown(f"""
            <div class='glass-card' style='text-align: center; border-left: 5px solid {color_temp}; margin-bottom: 10px;'>
                <div style='font-size: 2.2rem;'>🌡️</div>
                <div style='font-size: 0.85rem; text-transform: uppercase; color:#a3c4b2; margin-top:5px;'>Temperatura</div>
                <div style='font-size: 2.0rem; font-weight: bold; color: {color_temp}; margin-top:5px;'>{val_temp} <span style='font-size:1.0rem;'>°C</span></div>
            </div>
            """, unsafe_allow_html=True)
            
        # Card Umidade
        with col2:
            val_umid = latest["umidade"]
            color_umid = "#339af0" if val_umid >= iot.limiar_umidade else "#fcc419"
            st.markdown(f"""
            <div class='glass-card' style='text-align: center; border-left: 5px solid {color_umid}; margin-bottom: 10px;'>
                <div style='font-size: 2.2rem;'>💧</div>
                <div style='font-size: 0.85rem; text-transform: uppercase; color:#a3c4b2; margin-top:5px;'>Umidade do Solo</div>
                <div style='font-size: 2.0rem; font-weight: bold; color: {color_umid}; margin-top:5px;'>{val_umid} <span style='font-size:1.0rem;'>%</span></div>
            </div>
            """, unsafe_allow_html=True)
            
        # Card Luminosidade
        with col3:
            val_lumi = latest["luminosidade"]
            color_lumi = "#fab005"
            st.markdown(f"""
            <div class='glass-card' style='text-align: center; border-left: 5px solid {color_lumi}; margin-bottom: 10px;'>
                <div style='font-size: 2.2rem;'>☀️</div>
                <div style='font-size: 0.85rem; text-transform: uppercase; color:#a3c4b2; margin-top:5px;'>Luminosidade</div>
                <div style='font-size: 2.0rem; font-weight: bold; color: {color_lumi}; margin-top:5px;'>{val_lumi} <span style='font-size:1.0rem;'>lux</span></div>
            </div>
            """, unsafe_allow_html=True)
            
        # Card Status da Bomba
        with col4:
            bomba_on = latest["bomba_ativa"]
            status_bomba = "ATIVA (Irrigando)" if bomba_on else "INATIVA (Desligada)"
            color_bomba = "#50c878" if bomba_on else "#868e96"
            bg_bomba = "rgba(80, 200, 120, 0.12)" if bomba_on else "rgba(134, 142, 150, 0.1)"
            st.markdown(f"""
            <div class='glass-card' style='text-align: center; background-color: {bg_bomba}; border-left: 5px solid {color_bomba}; margin-bottom: 10px;'>
                <div style='font-size: 2.2rem;'>⚙️</div>
                <div style='font-size: 0.85rem; text-transform: uppercase; color:#a3c4b2; margin-top:5px;'>Bomba de Irrigação</div>
                <div style='font-size: 1.3rem; font-weight: bold; color: {color_bomba}; margin-top:12px;'>{status_bomba}</div>
            </div>
            """, unsafe_allow_html=True)
            
        # Exibição de alertas dinâmicos
        if latest["umidade"] < 30.0:
            st.warning(f"⚠️ **Alerta de Emergência**: Umidade crítica detectada abaixo do limite de segurança (Solo em {latest['umidade']}%). Bomba acionada automaticamente!")
        if latest["temperatura"] > 38.0:
            st.error(f"🔥 **Alerta Térmico**: Temperatura ambiente severa ({latest['temperatura']}°C). Risco de queima de folhas e perda de rendimento.")
            
        st.markdown(f"<p style='font-size: 0.8rem; color: #a3c4b2; font-style: italic;'>Último pacote MQTT recebido: {latest['timestamp']} (Atualizando a cada 2s)</p>", unsafe_allow_html=True)
        
        # Histórico de leituras com gráficos interativos
        st.subheader("📊 Histórico Recente de Telemetria")
        
        if len(historico) > 0:
            df_hist = pd.DataFrame(historico)
            
            # Criar gráficos elegantes no tema escuro do app
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5), facecolor='#080f0b')
            
            # Customizar ax1 (Temp e Umidade)
            ax1.set_facecolor('#0b1510')
            indices = np.arange(len(df_hist))
            ax1.plot(indices, df_hist['temperatura'], color='#ff6b6b', label='Temp (°C)', linewidth=2.5)
            ax1.plot(indices, df_hist['umidade'], color='#339af0', label='Umidade (%)', linewidth=2.5)
            ax1.axhline(iot.limiar_umidade, color='#fab005', linestyle='--', label='Limiar Umidade', alpha=0.8)
            ax1.set_title('Temperatura & Umidade do Solo', color='#50c878', fontsize=11, fontweight='bold')
            ax1.legend(facecolor='#080f0b', labelcolor='#e2f0e7', edgecolor='rgba(80, 200, 120, 0.2)', loc='upper left')
            ax1.tick_params(colors='#a3c4b2', labelsize=8)
            ax1.xaxis.label.set_color('#a3c4b2')
            ax1.yaxis.label.set_color('#a3c4b2')
            for spine in ax1.spines.values():
                spine.set_color('rgba(80, 200, 120, 0.2)')
                
            # Customizar ax2 (Luminosidade)
            ax2.set_facecolor('#0b1510')
            ax2.plot(indices, df_hist['luminosidade'], color='#fab005', label='Luz (lux)', linewidth=2.5)
            ax2.set_title('Intensidade Luminosa (lux)', color='#50c878', fontsize=11, fontweight='bold')
            ax2.legend(facecolor='#080f0b', labelcolor='#e2f0e7', edgecolor='rgba(80, 200, 120, 0.2)', loc='upper left')
            ax2.tick_params(colors='#a3c4b2', labelsize=8)
            ax2.xaxis.label.set_color('#a3c4b2')
            ax2.yaxis.label.set_color('#a3c4b2')
            for spine in ax2.spines.values():
                spine.set_color('rgba(80, 200, 120, 0.2)')
                
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)
            
            with st.expander("📄 Tabela Completa de Registros Recentes (JSON/MQTT Data)"):
                st.dataframe(df_hist.iloc[::-1], use_container_width=True)
        else:
            st.info("Aguardando o recebimento ou simulação dos primeiros dados do sensor para plotar gráficos.")
            
    # Chamar o renderizador de telemetria em tempo real
    render_live_telemetry()


# 5. PÁGINA FASE 4 - PREDIÇÕES DE ML (MANTENDO FUNCIONALIDADES ORIGINAIS)
elif page == "Predições de ML (Fase 4)":
    st.markdown("<h1 class='main-title'>Fase 4: Predições de ML</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Modelo Preditivo de Produtividade com Base nos Nutrientes do Solo</p>", unsafe_allow_html=True)
    
    # Sub-navegação com guias para manter a estrutura original de app.py
    tab1, tab2, tab3 = st.tabs(["🔮 Previsões", "📊 Visualização de Dados", "📈 Analytics & Insights"])
    
    with tab1:
        st.markdown("""
        <div class='glass-card'>
            <h4>Previsão de Produtividade Agrícola</h4>
            <p>Ajuste as características do solo abaixo para rodar o modelo preditivo e obter a estimativa de toneladas colhidas por hectare.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if model:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                soil_humidity = st.slider("Umidade do Solo (%)", 0.0, 100.0, 50.0)
                ph_level = st.slider("Nível de pH", 0.0, 14.0, 6.5)
                temperature = st.slider("Temperatura (°C)", 0.0, 50.0, 25.0)
                
            with col2:
                rainfall = st.slider("Chuva (mm)", 0.0, 300.0, 100.0)
                nitrogen = st.slider("Nitrogênio (N)", 0.0, 100.0, 50.0)
                
            with col3:
                phosphorus = st.slider("Fósforo (P)", 0.0, 100.0, 50.0)
                potassium = st.slider("Potássio (K)", 0.0, 100.0, 50.0)
                
            input_data = pd.DataFrame({
                'soil_humidity': [soil_humidity],
                'ph_level': [ph_level],
                'temperature': [temperature],
                'rainfall': [rainfall],
                'nitrogen': [nitrogen],
                'phosphorus': [phosphorus],
                'potassium': [potassium]
            })
            
            if st.button("Executar Previsão de Produtividade"):
                prediction = model.predict(input_data)[0]
                
                st.markdown(f"""
                <div style='background-color: rgba(80, 200, 120, 0.1); border: 1px solid rgba(80, 200, 120, 0.3); padding: 15px; border-radius: 8px; margin-top: 15px;'>
                    <h4 style='margin:0; color:#50c878;'>Produtividade Prevista: {prediction:.2f} toneladas/ha</h4>
                </div>
                """, unsafe_allow_html=True)
                
                # Recomendações
                st.subheader("💡 Recomendações de Manejo do Solo")
                
                recommendations = []
                
                if soil_humidity < 40:
                    recommendations.append("💧 **Umidade do Solo Baixa**: Considere irrigação imediata para evitar estresse hídrico.")
                elif soil_humidity > 80:
                    recommendations.append("⚠️ **Umidade do Solo Alta**: Garanta drenagem adequada para evitar apodrecimento das raízes.")
                
                if ph_level < 5.5:
                    recommendations.append("🧪 **Solo Ácido**: Adicione calcário para corrigir o pH e melhorar a disponibilidade de nutrientes.")
                elif ph_level > 7.5:
                    recommendations.append("🧪 **Solo Alcalino**: Considere adicionar enxofre ou matéria orgânica para reduzir o pH.")
                
                if temperature < 15:
                    recommendations.append("🌡️ **Temperatura Baixa**: Temperatura abaixo do ideal. Considere proteção térmica ou aguardar período mais quente.")
                elif temperature > 35:
                    recommendations.append("🌡️ **Temperatura Alta**: Calor excessivo. Aumente a irrigação e considere sombreamento.")
                
                if rainfall < 75:
                    recommendations.append("☔ **Precipitação Insuficiente**: Nível de chuva baixo. Implemente sistema de irrigação suplementar.")
                elif rainfall > 180:
                    recommendations.append("🌧️ **Precipitação Excessiva**: Risco de lixiviação de nutrientes. Monitore drenagem.")
                
                if nitrogen < 30:
                    recommendations.append("🌿 **Nitrogênio Baixo**: Aplique fertilizantes nitrogenados (ureia, sulfato de amônio) para promover crescimento.")
                elif nitrogen > 80:
                    recommendations.append("🌿 **Nitrogênio Alto**: Excesso de nitrogênio pode causar crescimento vegetativo excessivo. Reduza a dose.")
                
                if phosphorus < 25:
                    recommendations.append("🌾 **Fósforo Baixo**: Adicione superfosfato ou MAP para fortalecer as raízes.")
                
                if potassium < 30:
                    recommendations.append("🍃 **Potássio Baixo**: Aplique cloreto de potássio (KCl) para aumentar resistência a doenças.")
                
                if recommendations:
                    for rec in recommendations:
                        st.info(rec)
                else:
                    st.success("✅ **Condições Ideais**: Todos os parâmetros de nutrientes e clima estão ótimos!")
                    
                # Análise geral
                if prediction < 100:
                    st.warning("📉 **Produtividade Estimada Baixa**: Revise as recomendações de fertilização e controle de pH.")
                elif prediction < 150:
                    st.info("📊 **Produtividade Moderada**: Condições adequadas, porém ajustando alguns parâmetros é possível otimizar o ganho.")
                else:
                    st.balloons()
                    st.success("🚀 **Excelente Produtividade**: Parâmetros ideais para colheita recorde!")
        else:
            st.error("Erro: Modelo preditivo não pôde ser inicializado.")

    with tab2:
        st.markdown("### 📊 Dados Agrícolas")
        st.dataframe(df, use_container_width=True)
        
        st.subheader("Estatísticas Descritivas")
        st.write(df.describe())

    with tab3:
        st.markdown("### 📈 Análise & Insights")
        
        col_an1, col_an2 = st.columns([3, 2])
        
        with col_an1:
            st.subheader("Mapa de Correlação de Nutrientes")
            fig, ax = plt.subplots(figsize=(10, 6))
            # Ajustar tema do matplotlib para fundo escuro
            fig.patch.set_facecolor('#080f0b')
            ax.set_facecolor('#080f0b')
            sns.heatmap(df.corr(), annot=True, cmap='viridis', ax=ax, cbar=True)
            plt.title("Correlação entre Variáveis do Solo e Produtividade", color='#e2f0e7')
            # Customização dos ticks para texto claro
            ax.tick_params(colors='#e2f0e7')
            for text in ax.texts:
                text.set_color('#ffffff')
            st.pyplot(fig)
            
        with col_an2:
            st.subheader("Fatores vs Produtividade")
            factor = st.selectbox("Selecione o Parâmetro de Análise", df.columns.drop('crop_yield'))
            
            fig2, ax2 = plt.subplots(figsize=(6, 5))
            fig2.patch.set_facecolor('#080f0b')
            ax2.set_facecolor('#080f0b')
            sns.scatterplot(data=df, x=factor, y='crop_yield', color='#50c878', ax=ax2)
            ax2.tick_params(colors='#e2f0e7')
            ax2.xaxis.label.set_color('#e2f0e7')
            ax2.yaxis.label.set_color('#e2f0e7')
            plt.title(f"{factor.capitalize()} vs Produtividade (Crop Yield)", color='#e2f0e7')
            st.pyplot(fig2)

# 6. PÁGINA FASE 5 - ALERTAS AWS
elif page == "Alertas de Cloud/AWS (Fase 5)":
    st.markdown("<h1 class='main-title'>Fase 5: Alertas de Cloud & AWS</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Simulação de Notificações Críticas de Irrigação e Anomalias via AWS SNS/SES</p>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='glass-card'>
        <h4>☁️ Centro de Controle de Mensageria e Nuvem</h4>
        <p>Canal integrado para visualização de alertas automáticos. Se os sensores de solo detectarem seca ou 
        a inteligência artificial identificar doenças, alertas urgentes são disparados via AWS.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("ℹ️ Os simuladores locais da AWS SNS/SES utilizando biblioteca Moto e logs de MessageId correspondentes estarão ativos em breve.")

# 7. PÁGINA FASE 6 - VISÃO COMPUTACIONAL (YOLO)
elif page == "Visão Computacional (Fase 6)":
    st.markdown("<h1 class='main-title'>Fase 6: Visão Computacional (YOLO)</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Detecção de Pragas e Diagnóstico de Saúde Foliar em Lavouras</p>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='glass-card'>
        <h4>👁️ Diagnóstico com Inteligência Artificial YOLOv8</h4>
        <p>Faça upload de fotos das folhas ou plantas em campo para que nosso modelo YOLO de visão computacional 
        processe e identifique a presença de pragas ou deficiência nutricional.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("ℹ️ O uploader e o pipeline de inferência YOLO com os pesos carregados serão disponibilizados na aba de visão computacional na respectiva tarefa.")
