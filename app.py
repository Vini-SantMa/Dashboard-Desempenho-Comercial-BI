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
    
   
    h1, h2, h3 {
        color: #2C4156 !important;
        font-family: 'Arial', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

def limpar_dados(arquivo, nome_vendedor):
    try:
        
        tabela_bruta = pd.read_csv(arquivo, header=None, encoding='latin1', sep=',')
        # No arquivo original, feito no sheets, os dados importantes comecam após o DATA, entao precisamos localizar ele, para poder comecar a leitura
        linhas_encontradas = tabela_bruta[
            tabela_bruta.apply(lambda row: row.astype(str).str.contains("DATA", case=False).any(), axis=1)]
        
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
        
        # 5. TRATAMENTO DE DADOS
        tabela = tabela.dropna(subset=["Cliente"])
        
        # Os valores precisam ser transformados em float pro python entender, entao retiramos o R$, a virgula e transformamos em numero
        tabela["Valor"] = tabela["Valor"].astype(str).str.replace("R$", "", regex=False) # Por seguranca, deixa o regex como falso, pra ele nao querer interpretar os simbolos
        tabela["Valor"] = tabela["Valor"].str.replace(".", "", regex=False)
        tabela["Valor"] = tabela["Valor"].str.replace(",", ".", regex=False)
        tabela["Valor"] = pd.to_numeric(tabela["Valor"], errors="coerce").fillna(0)
    
        # Limpar o campo da data, transformando em data mesmo
        tabela["Data"] = pd.to_datetime(tabela["Data"], dayfirst=True, errors="coerce")
        tabela = tabela.dropna(subset=["Data"])
    
        return tabela

    except Exception as e:
        stl.error(f"Erro ao ler planilha {nome_vendedor}: {e}")
        return pd.DataFrame()


try:
    
    df_marianne = limpar_dados("DASHBOARD COMERCIAL DE VENDAS Nov - MARIANNE.csv", "Marianne")
    df_wesley = limpar_dados("DASHBOARD COMERCIAL DE VENDAS Nov - WESLEY.csv", "Wesley")
    
    tabela_final = pd.concat([df_marianne, df_wesley], ignore_index=True) #concatenar ambas
    
except Exception as e:
    stl.warning(f"Erro ao carregar arquivos: {e}")
    tabela_final = pd.DataFrame()

if tabela_final.empty: # Para se houver erro ao carregar os arquivos
    stl.stop()
    

# Interface com o StreamLite

stl.sidebar.header("Filtros") 

filtro_vendedor = stl.sidebar.multiselect(
    "Filtrar Vendedor:", 
    options=tabela_final["Vendedor"].unique(), 
    default=tabela_final["Vendedor"].unique()
)

filtro_status = stl.sidebar.multiselect(
    "Filtrar Situação:", 
    options=tabela_final["Status"].unique(), 
    default=tabela_final["Status"].unique()
)

tabela_view = tabela_final.query("Vendedor == @filtro_vendedor & Status == @filtro_status")

# Layout do dashboard
stl.title("Acompanhamento Time Comercial")
stl.markdown("------")

receita_total = tabela_view[tabela_view["Status"] == "Aprovado"]["Valor"].sum()
propostas_abertas = tabela_view[tabela_view["Status"] == "Negociando"]["Valor"].sum()
oportunidades = len(tabela_view)
total_vendas = len(tabela_view[tabela_view["Status"] == "Aprovado"])

taxa_conv = 0
if oportunidades > 0:
    taxa_conv = (total_vendas / oportunidades) * 100
else:
    taxa_conv = 0


col1, col2, col3, col4 = stl.columns(4)
col1.metric("Vendas Fechadas", f"R$ {receita_total:,.2f}") 
col2.metric("Orçamentos em Aberto", f"R$ {propostas_abertas:,.2f}")
col3.metric("Oportunidades", oportunidades)
col4.metric("Taxa de conversão", f"{taxa_conv:.1f}%")

stl.markdown("---")

coln1, coln2 = stl.columns(2)

with coln1:
    # Tabelinha improvisada pra usar na plotagem do grfico
     tabela_meta = pd.DataFrame({
        "Tipo": ["Meta Mensal", "Realizado"],
        "Valor": [META_MENSAL, receita_total],
        "Cor": ["Meta", "Realizado"]})
     
     graf_meta = px.bar( #grafico de barras
        tabela_meta, 
        x="Tipo", y="Valor", 
        orientation='v', # Vertical
        title="Meta vs Vendas fechadas", text_auto=".5s", color="Tipo",
        color_discrete_map={"Meta": "#C43D3D", "Realizado": "#2C4156"})
     
     graf_meta.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font={'color': "#2C4156", 'size': 15}, 
        xaxis_title="Valor (R$)", yaxis_title="")
     
     stl.plotly_chart(graf_meta, use_container_width=True)
    
with coln2:
    if not tabela_view.empty:
        
        cores_pizza = {
            "Aprovado": "#2ECC71", "Negociando": "#F1C40F", 
            "Recusado": "#E74C3C", 
        }
        graf_pizza = px.pie(
            tabela_view, names="Status", values="Valor", 
            title="Distribuição das Abordagens (R$)", hole=0.5, 
            color = "Status", color_discrete_map=cores_pizza
        )
        
        graf_pizza.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", 
            paper_bgcolor="rgba(0,0,0,0)",
            font={'color': "#2C4156", 'size': 14},
            legend=dict(font=dict(size=14))
        )
        stl.plotly_chart(graf_pizza, use_container_width=True)
    
stl.markdown("### Detalhamento")

stl.dataframe(
    tabela_view.sort_values("Data", ascending=False), # Do mais recente pro mais antigo
    use_container_width=True, 
    column_config={
        "Valor": stl.column_config.NumberColumn(format="R$ %.2f"), #Formato brasileiro do valor em R$
        "Data": stl.column_config.DateColumn(format="DD/MM/YYYY") #Formato brasileiro da data
    }
)