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

# Configuração da página do Streamlit
st.set_page_config(
    page_title="FarmTech Solutions - Dashboard Consolidado",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
            <p>Insira dados de área, espaçamento e parâmetros recomendados na Fase 1 para planejar os insumos e a safra.</p>
        </div>
        """, unsafe_allow_html=True)
        st.info("ℹ️ Os formulários interativos de plantio de cana e laranja serão integrados na próxima tarefa.")
        
    with tab_r:
        st.markdown("""
        <div class='glass-card'>
            <h4>📊 Análise Estatística Avançada (R Language)</h4>
            <p>Execute scripts analíticos em R diretamente da dashboard para calcular distribuições, médias e desvios das colheitas.</p>
        </div>
        """, unsafe_allow_html=True)
        st.info("ℹ️ A integração com subprocessos e a exibição de logs estatísticos em R serão disponibilizados na TASK_04.")

# 3. PÁGINA FASE 2 - CRUD
elif page == "Banco de Dados & CRUD (Fase 2)":
    st.markdown("<h1 class='main-title'>Fase 2: Banco de Dados & CRUD</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Gerenciamento de Propriedades, Colheitas e Relatório de Perdas</p>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='glass-card'>
        <h4>🗄️ Sistema de Monitoramento e Planejamento de Colheitas (SMPC)</h4>
        <p>Painel de gerenciamento de dados de plantações, permitindo o registro de propriedades agrícolas, safras, 
        e perdas ocorridas em campo. Conectado de forma direta ao banco de dados relacional Oracle.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("ℹ️ Os formulários para cadastro de novas propriedades e a listagem de colheitas integrada serão disponibilizados nas próximas tarefas.")

# 4. PÁGINA FASE 3 - IOT
elif page == "Monitoramento IoT (Fase 3)":
    st.markdown("<h1 class='main-title'>Fase 3: Monitoramento IoT</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Telemetria em Tempo Real de Sensores e Controle de Irrigação</p>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='glass-card'>
        <h4>🔌 Sensores de Solo e Clima local (ESP32)</h4>
        <p>Monitore dados transmitidos via MQTT sobre umidade, temperatura e luminosidade de campo. 
        O sistema atua automaticamente no controle da bomba d'água baseando-se em níveis críticos.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("ℹ️ A conexão MQTT dinâmica e os cards de telemetria dos sensores IoT serão integrados em breve.")

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
