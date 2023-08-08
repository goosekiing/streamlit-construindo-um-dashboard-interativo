import streamlit as st
import requests
import pandas as pd
import plotly.express as px


st.set_page_config(layout="wide",
                   page_title="Atividade Streamlit",
                   page_icon=":chart_with_upwards_trend:")

def formata_numero(valor, prefixo=""):
    for unidade in ["", "mil"]:
        if valor < 1000:
            return f"{prefixo} {valor:.2f} {unidade}"
        valor /= 1000
    return f"{prefixo} {valor:.2f} milhões"


st.title("DASHBOARD DE VENDAS :shopping_trolley:")
url = "https://labdados.com/produtos"
regioes = ["Brasil", "Sul", "Sudeste", "Centro-Oeste", "Norte", "Nordeste"]

st.sidebar.title("Filtros")
regiao = st.sidebar.selectbox("Região", regioes)

if regiao == "Brasil":
    regiao = ""

todos_anos = st.sidebar.checkbox("Dados de todo o período", value=True)
if todos_anos:
    ano = ""
else:
    ano = st.sidebar.slider("Ano", 2020, 2023)

query_string = {"regiao": regiao.lower(), "ano": ano}
response = requests.get(url, params=query_string)
dados = pd.DataFrame.from_dict(response.json())
dados["Data da Compra"] = pd.to_datetime(dados["Data da Compra"], format= "%d/%m/%Y")

filtro_vendedores = st.sidebar.multiselect("Vendedores", dados["Vendedor"].unique())
if filtro_vendedores:
    dados = dados[dados["Vendedor"].isin(filtro_vendedores)]

# Tabelas de Receita
receita_estados = dados.groupby("Local da compra")[["Preço"]].sum()
receita_estados = dados.drop_duplicates(subset="Local da compra")[["Local da compra", "lat", "lon"]].merge(receita_estados, left_on = "Local da compra", right_index =  True).sort_values("Preço", ascending=False)

receita_categorias = dados.groupby("Categoria do Produto")[["Preço"]].sum().sort_values("Preço", ascending=False)

receita_mensal = dados.set_index("Data da Compra").groupby(pd.Grouper(freq="M"))["Preço"].sum().reset_index()
receita_mensal["Ano"] = receita_mensal["Data da Compra"].dt.year
receita_mensal["Mes"] = receita_mensal["Data da Compra"].dt.month_name()


# Tabelas de Quantidade de Vendas:
quantidade_estados = dados.groupby("Local da compra")[["Preço"]].count()
quantidade_estados = dados.drop_duplicates(subset="Local da compra")[["Local da compra", "lat", "lon"]].merge(quantidade_estados, left_on = "Local da compra", right_index =  True).sort_values("Preço", ascending=False)

quantidade_categorias = dados.groupby("Categoria do Produto")[["Preço"]].count().sort_values("Preço", ascending=False)

quantidade_mensal = dados.set_index("Data da Compra").groupby(pd.Grouper(freq="M"))["Preço"].count().reset_index()
quantidade_mensal["Ano"] = quantidade_mensal["Data da Compra"].dt.year
quantidade_mensal["Mes"] = quantidade_mensal["Data da Compra"].dt.month_name()


# Tabelas Vendedores:
vendedores = pd.DataFrame(dados.groupby("Vendedor")["Preço"].agg(["sum", "count"]))

# Gráficos Receitas:
fig_mapa_receita = px.scatter_geo(receita_estados,
                                  lat= "lat",
                                  lon= "lon",
                                  scope= "south america",
                                  size= "Preço",
                                  template= "seaborn",
                                  hover_name= "Local da compra",
                                  hover_data={"lat": False, "lon": False},
                                  title= "Receita por Estado")

fig_receita_mensal = px.line(receita_mensal,
                             x="Mes",
                             y="Preço",
                             markers=True,
                             range_y=(0, receita_mensal.max()),
                             color="Ano",
                             line_dash="Ano",
                             title= "Receita Mensal")

fig_receita_mensal.update_layout(yaxis_title = "Receita")

fig_receita_estado = px.bar(receita_estados.head(),
                            x="Local da compra",
                            y="Preço",
                            text_auto=True,
                            title="Top Estado(receita")

fig_receita_estado.update_layout(yaxis_title = "Receita")

fig_receita_categorias = px.bar(receita_categorias,
                                text_auto=True,
                                title="Receita por Categoria")

fig_receita_categorias.update_layout(yaxis_title = "Receita")


# Gráficos Quantidades de Vendas:
fig_mapa_vendas = px.scatter_geo(quantidade_estados,
                                  lat= "lat",
                                  lon= "lon",
                                  scope= "south america",
                                  size= "Preço",
                                  template= "seaborn",
                                  hover_name= "Local da compra",
                                  hover_data={"lat": False, "lon": False},
                                  title= "Vendas por Estado")

fig_vendas_mensal = px.line(quantidade_mensal,
                             x="Mes",
                             y="Preço",
                             markers=True,
                             range_y=(0, receita_mensal.max()),
                             color="Ano",
                             line_dash="Ano",
                             title= "Vendas Mensal")

fig_vendas_mensal.update_layout(yaxis_title = "Vendas")

fig_vendas_estado = px.bar(quantidade_estados.head(),
                            x="Local da compra",
                            y="Preço",
                            text_auto=True,
                            title="Top Estados (vendas)")

fig_vendas_estado.update_layout(yaxis_title = "Vendas")

fig_vendas_categorias = px.bar(quantidade_categorias,
                                text_auto=True,
                                title="Quantidade por Categoria")

fig_vendas_categorias.update_layout(yaxis_title = "Vendas")

# Visualização no streamlit:
aba1, aba2, aba3 = st.tabs(["Receita", "Quantidade de Vendas", "Vendedores"])

with aba1:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric("Receita", formata_numero(dados["Preço"].sum(), "R$"))
        st.plotly_chart(fig_mapa_receita, use_container_width=True)
        st.plotly_chart(fig_receita_estado, use_container_width=True)
    with coluna2:
        st.metric("Quantidade de Vendas", formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width=True)
        st.plotly_chart(fig_receita_categorias, use_container_width=True)

with aba2:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric("Receita", formata_numero(dados["Preço"].sum(), "R$"))
        st.plotly_chart(fig_mapa_vendas, use_container_width=True)
        st.plotly_chart(fig_vendas_estado, use_container_width=True)
    with coluna2:
        st.metric("Quantidade de Vendas", formata_numero(dados.shape[0]))
        st.plotly_chart(fig_vendas_mensal, use_container_width=True)
        st.plotly_chart(fig_vendas_categorias, use_container_width=True)

with aba3:
    qtde_vendedores = st.number_input("Quantidade de Vendedores", 2, 10, 5)
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric("Receita", formata_numero(dados["Preço"].sum(), "R$"))
        fig_receita_vendedores = px.bar(vendedores[["sum"]].sort_values("sum", ascending=False).head(qtde_vendedores),
                                        x="sum",
                                        y=vendedores[["sum"]].sort_values("sum", ascending=False).head(qtde_vendedores).index,
                                        text_auto=True,
                                        title=f"Top {qtde_vendedores} Vendedores (receita)")
        st.plotly_chart(fig_receita_vendedores)
    with coluna2:
        st.metric("Quantidade de Vendas", formata_numero(dados.shape[0]))
        fig_vendas_vendedores = px.bar(vendedores[["count"]].sort_values("count", ascending=False).head(qtde_vendedores),
                                        x="count",
                                        y=vendedores[["sum"]].sort_values("sum", ascending=False).head(
                                            qtde_vendedores).index,
                                        text_auto=True,
                                        title=f"Top {qtde_vendedores} Vendedores (quantidade de vendas)")
        st.plotly_chart(fig_vendas_vendedores)


