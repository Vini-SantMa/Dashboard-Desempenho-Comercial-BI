
import pandas as pd
import plotly.express as px
import streamlit as stl 

# Configuração da página
stl.set_page_config(page_title="Acompanhamento Comercial", layout="wide")

META_MENSAL = 50000

stl.markdown("""
<style>
    .stApp {
        background-color: #D2D7DB; 
    }
    section[data-testid="stSidebar"] {
        background-color: #98A1AA;
    }
    div[data-testid="stMetric"] {
        background-color: #2C4156;
        border: 1px solid #1f2e3d;
        padding: 15px 20px;
        border-radius: 12px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    }
    div[data-testid="stMetric"] label {
        color: #D2D7DB !important; 
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #FFFFFF !important; 
    }
    h1, h2, h3, h4 {
        color: #2C4156 !important;
        font-family: 'Arial', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

@stl.cache_data

def limpar_dados(arquivo, nome_vendedor):
    try:
        tabela_bruta = pd.read_csv(arquivo, header=None, encoding='latin1', sep=',')
         # No arquivo original, feito no sheets, os dados importantes comecam após o DATA, entao precisamos localizar ele, para poder comecar a leitura
        linhas_encontradas = tabela_bruta[tabela_bruta.apply(lambda row: row.astype(str).str.contains("DATA", case=False).any(), axis=1)]
        
        if linhas_encontradas.empty: #Se nao encontrar "data", avisa ao usuario
             stl.error(f"A palavra 'DATA/data' não foi encontrada no arquivo")
             return pd.DataFrame() 
            
        linha_do_cabecalho = linhas_encontradas.index[0]
         # ja temos o importante, pulando o inicio que nao serve
        tabela = pd.read_csv(arquivo, skiprows=linha_do_cabecalho, encoding='latin1', sep=',')
        
        # As colunas que contem os dados sao a partir da 1  (A 0 está vazia no sheets)
        colunas_importantes = [1, 2, 3, 4]
        tabela = tabela.iloc[:, colunas_importantes]
        
        tabela.columns = ["Data", "Cliente", "Valor", "Status"]
        tabela["Vendedor"] = nome_vendedor
        
        
        
        tabela = tabela.dropna(subset=["Cliente"])
        
        # Os valores precisam ser transformados em float pro python entender, entao retiramos o R$, a virgula e transformamos em numero
        tabela["Valor"] = tabela["Valor"].astype(str).str.replace("R$", "", regex=False) # Por seguranca, deixa o regex como falso, pra ele nao querer interpretar os simbolos
        tabela["Valor"] = tabela["Valor"].str.replace(".", "", regex=False)
        tabela["Valor"] = tabela["Valor"].str.replace(",", ".", regex=False)
        tabela["Valor"] = pd.to_numeric(tabela["Valor"], errors="coerce").fillna(0)
    
        # Tratamento das datas
        tabela["Data"] = pd.to_datetime(tabela["Data"], dayfirst=True, errors="coerce")
        tabela = tabela.dropna(subset=["Data"])
    
        return tabela
    except Exception as e:
        stl.error(f"Erro ao processar {nome_vendedor}: {e}")
        return pd.DataFrame()

# carregando os dados
try:
    df_mariana = limpar_dados("DASHBOARD COMERCIAL DE VENDAS Nov - MARIANNE.csv", "Marianne")
    df_wesley = limpar_dados("DASHBOARD COMERCIAL DE VENDAS Nov - WESLEY.csv", "Wesley")
    tabela_final = pd.concat([df_mariana, df_wesley], ignore_index=True) #concatenar ambas
except Exception as e:
    tabela_final = pd.DataFrame()

if tabela_final.empty:  # Para se houver erro ao carregar os arquivos
    stl.warning("Não foi possível carregar os dados. Verifique os arquivos CSV.")
    stl.stop()
    
    # Streamlit interface
stl.sidebar.title("Filtros")
filtro_vendedor = stl.sidebar.multiselect(
    "Filtrar Vendedor:", 
    tabela_final["Vendedor"].unique(),
    default=tabela_final["Vendedor"].unique()
    )

filtro_status = stl.sidebar.multiselect(
    "Filtrar situação:",
    tabela_final["Status"].unique(),
    default=tabela_final["Status"].unique()
    )

tabela_view = tabela_final.query("Vendedor == @filtro_vendedor & Status == @filtro_status")


# Calculos dos dados expostos
receita_total = tabela_view[tabela_view["Status"] == "Aprovado"]["Valor"].sum()
qtd_vendas = len(tabela_view[tabela_view["Status"] == "Aprovado"])
pipeline_aberto = tabela_view[tabela_view["Status"] == "Negociando"]["Valor"].sum()
total_oportunidades = len(tabela_view)

taxa_conversao = 0
if total_oportunidades > 0:
    taxa_conversao = (qtd_vendas / total_oportunidades) * 100
else:
    taxa_conversao = 0
ticket_medio = 0
if qtd_vendas > 0:
    ticket_medio = receita_total / qtd_vendas
else:
    ticket_medio = 0




# --- Layout dashboard---
stl.title("📊 Sales Pulse")
stl.markdown("---")

# NOVO: Barra dde progressso da meta
percentual_meta = receita_total / META_MENSAL
percentual_exibicao = min(percentual_meta, 1.0) # Evitar da barra quebrar

stl.markdown(f"### 🎯 Atingimento da Meta: R$ {receita_total:,.2f} / R$ {META_MENSAL:,.2f} ({percentual_meta*100:.1f}%)")
stl.progress(percentual_exibicao)
stl.markdown("<br>", unsafe_allow_html=True)

# Colunas dos kpi
col1, col2, col3, col4, col5 = stl.columns(5)
col1.metric("💰 Vendas Fechadas", f"R$ {receita_total:,.2f}") 
col2.metric("🛒 Qtd Vendas", f"{qtd_vendas}") 
col3.metric("🎫 Ticket Médio", f"R$ {ticket_medio:,.2f}")
col4.metric("📂 Em Negociação", f"R$ {pipeline_aberto:,.2f}")
col5.metric("📈 Taxa Conversão", f"{taxa_conversao:.1f}%")
stl.markdown("----")

stl.markdown("<br>", unsafe_allow_html=True)

# Divisão para os Gráficos
c_graf1, c_graf2 = stl.columns((1, 1))

with c_graf1:
    # Gráfico de evolução de vendas no passar do tempo
    df_tempo = tabela_view[tabela_view["Status"] == "Aprovado"].groupby("Data")["Valor"].sum().reset_index()
    if not df_tempo.empty:
        fig_linha = px.line(df_tempo, x="Data", y="Valor", title="Evolução do faturamento", markers=True)
        fig_linha.update_traces(line_color='#2C4156', marker=dict(size=8, color='#2ECC71'))
        fig_linha.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",
            xaxis_title="", yaxis_title="R$",
            font={'color': "#2C4156"}
            )
        stl.plotly_chart(fig_linha, use_container_width=True)
    else:
        stl.info("Nenhuma venda 'Aprovada' no período selecionado.")

with c_graf2:
    if not tabela_view.empty:
        cores_pizza = {"Aprovado": "#2ECC71", "Negociando": "#F1C40F", "Recusado": "#E74C3C"}
        graf_pizza = px.pie(
            tabela_view, names="Status", values="Valor", 
            title="Distribuição do Pipeline (R$)", hole=0.5, 
            color="Status", color_discrete_map=cores_pizza
        )
        graf_pizza.update_traces(textposition='inside', textinfo='percent+label', textfont_size=14)
        graf_pizza.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font={'color': "#2C4156"}, showlegend=False
            )
        stl.plotly_chart(graf_pizza, use_container_width=True)

stl.markdown("---")


c_tab1, c_tab2 = stl.columns((1, 2))

with c_tab1:
    # NOVO: Ranking Curva ABC
    stl.markdown("<h4>🏆 Top 5 Clientes</h4>", unsafe_allow_html=True)
    df_top_clientes = tabela_view[tabela_view["Status"] == "Aprovado"].groupby("Cliente")["Valor"].sum().reset_index()
    df_top_clientes = df_top_clientes.sort_values(by="Valor", ascending=False).head(5)
    
    if not df_top_clientes.empty:
        stl.dataframe(
            df_top_clientes, 
            hide_index=True, 
            use_container_width=True,
            column_config={"Valor": stl.column_config.NumberColumn("Total (R$)", format="R$ %.2f")}
        )
    else:
        stl.write("Sem dados suficientes.")

with c_tab2:
    stl.markdown("<h4>📂 Base de Dados Analítica</h4>", unsafe_allow_html=True)
    stl.dataframe(
        tabela_view.sort_values("Data", ascending=False), 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Valor": stl.column_config.NumberColumn(format="R$ %.2f"),
            "Data": stl.column_config.DateColumn(format="DD/MM/YYYY")
        }
    )