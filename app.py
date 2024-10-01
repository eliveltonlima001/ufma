import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Definindo a paleta de cores
colors = ['#32a676', '#16634a', '#8a8a8a', '#5a9bd4']

st.set_page_config(layout="wide")
st.title('Análise de Custos e Características de Imóveis por Cidade')

@st.cache_data
def load_data(nrows):
    DATA_URL = "houses_to_rent_v2.csv"
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    return data

data_load_state = st.text('Loading...')
data = load_data(10000)
data_load_state.text("Dados carregados! (using st.cache_data)")

df = pd.read_csv("houses_to_rent_v2.csv", sep=",", decimal=",")

if st.checkbox('Mostrar Dados Brutos'):
    st.subheader('Dados Brutos')
    st.write(df)

if 'total (R$)' in df.columns:
    df = df.sort_values(by="total (R$)")
else:
    st.error("A coluna 'total (R$)' não foi encontrada no DataFrame.")


col1, col2, col3, col4, col5 = st.columns(5)
col6, col7 = st.columns(2)
col8, col9, col10 = st.columns(3)
col11 = st.columns(1)[0]

# Cards


# Criar coluna para o Custo Total
df['custo_total'] = df[['hoa (R$)', 'rent amount (R$)', 'property tax (R$)', 'fire insurance (R$)']].sum(axis=1)

# Função para formatar os números no padrão brasileiro
def formatar_numero(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Calcular a média do Custo Total
custo_total_medio = df['custo_total'].mean().round(2)

# Exibir no Card
col1.metric(label="Custo Total Médio", value=formatar_numero(custo_total_medio))

# Criar coluna para o Aluguel por m²
df['aluguel_m2'] = df['rent amount (R$)'] / df['area']

# Calcular a média de aluguel por área
media_aluguel_m2 = df['aluguel_m2'].mean().round(2)

# Exibir no Card
col2.metric(label="Média de Aluguel por m²", value=f"{formatar_numero(media_aluguel_m2)}/m²")

# Filtrar dados para imóveis que aceitam animais
imoveis_aceitam_animais = df[df['animal'] == 'acept'].shape[0]
total_imoveis = df.shape[0]
percentual_aceitam_animais = (imoveis_aceitam_animais / total_imoveis) * 100

# Exibir no Card 
col3.metric(label="Imóveis que Aceitam Animais (%)", value=f"{formatar_numero(percentual_aceitam_animais)}%")

# Cálculo do Imposto Médio em relação ao Aluguel
imposto_medio_aluguel = (df['property tax (R$)'] / df['rent amount (R$)']).mean() * 100

col4.metric(
    label="% Imposto / Aluguel Total",
    value=f"{formatar_numero(imposto_medio_aluguel).replace('R$ ', '')}%"
)
# Exibir a quantidade total de imóveis
col5.metric(label="Quantidade Total de Imóveis", value=f"{total_imoveis:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."))



# Gráfico 1: Cascata - Composição do Custo Total
import plotly.graph_objects as go

# Definir os nomes dos componentes em português
componentes_portugues = {
    'hoa (R$)': 'Condomínio (R$)',
    'rent amount (R$)': 'Aluguel (R$)',
    'property tax (R$)': 'Imposto (R$)',
    'fire insurance (R$)': 'Seguro Incêndio (R$)'
}

# Criar DataFrame com a média de cada componente do custo
custo_composicao = df[['hoa (R$)', 'rent amount (R$)', 'property tax (R$)', 'fire insurance (R$)']].mean().reset_index()
custo_composicao.columns = ['Tipo', 'Valor']

# Substituir os nomes dos componentes pelos nomes em português
custo_composicao['Tipo'] = custo_composicao['Tipo'].replace(componentes_portugues)

# Calcular a porcentagem de cada componente em relação ao valor total
total_custo = custo_composicao['Valor'].sum()
custo_composicao['Percentual'] = (custo_composicao['Valor'] / total_custo) * 100

# Função para formatar os números no padrão brasileiro
def formatar_numero(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Criar labels que mostram tanto o valor quanto a porcentagem, já formatados
custo_composicao['Label'] = custo_composicao.apply(
    lambda row: f"{formatar_numero(row['Valor'])} ({row['Percentual']:.2f}%)", axis=1
)

# Criar os deltas formatados (variação bruta entre os valores)
deltas_formatados = custo_composicao['Valor'].apply(lambda x: formatar_numero(x))

# Gráfico de cascata
fig_composicao_custo = go.Figure(go.Waterfall(
    name="Custo",
    orientation="v",
    measure=["relative"] * len(custo_composicao),  # Definir todas as barras como "relativas" (aumentos/diminuições)
    x=custo_composicao['Tipo'],  # Eixo x com os tipos de componentes
    text=custo_composicao['Label'],  # Mostrar valores e porcentagens no gráfico
    y=custo_composicao['Valor'],  # Valores dos componentes
    textposition="outside",  # Exibir os valores fora das barras
    customdata=deltas_formatados,  # Dados personalizados para exibir o delta formatado
    hovertemplate='%{x}<br>Valor: %{customdata}<br>%{text}<extra></extra>',  # Mostrar valor formatado no hover
))

# Personalizar o layout
fig_composicao_custo.update_layout(
    title="Composição do Custo Total",
    xaxis_title="Componente do Custo",
    yaxis_title="Valor Médio (R$)",
    showlegend=False
)
# Exibir o gráfico
fig_composicao_custo.update_layout(xaxis_title='', xaxis_showgrid=False, yaxis_showgrid=False)
col6.plotly_chart(fig_composicao_custo, use_container_width=True)





# Gráfico 2

city_stats = df.groupby("city").agg(
    media_aluguel=('total (R$)', 'mean'),
    quantidade_imoveis=('total (R$)', 'size')
).reset_index()

city_stats.rename(columns={"city": "Cidade", "media_aluguel": "Média de Aluguel", "quantidade_imoveis": "Quantidade de Imóveis"}, inplace=True)
city_stats['Média de Aluguel'] = city_stats['Média de Aluguel'].round(0)
sorted_cities = city_stats.sort_values(by="Média de Aluguel", ascending=False)["Cidade"].tolist()

fig_city_aluguel = px.bar(
    city_stats,
    x="Cidade",
    y="Média de Aluguel",
    color="Quantidade de Imóveis",
    title="Média de Aluguel por Cidade",
    labels={"Cidade": "Cidade", "Média de Aluguel": "Média de Aluguel", "Quantidade de Imóveis": "Quantidade de Imóveis"},
    category_orders={"Cidade": sorted_cities},
    color_continuous_scale=colors
)

# Remover linhas de grade
fig_city_aluguel.update_layout(xaxis_title='', xaxis_showgrid=False, yaxis_showgrid=False)
col7.plotly_chart(fig_city_aluguel, use_container_width=True)


# Gráfico 3: Barras - Imóveis que aceitam animais

# Contar a quantidade de imóveis que aceitam e não aceitam animais
animais_contagem = df['animal'].value_counts().reset_index()
animais_contagem.columns = ['Aceita Animais', 'Quantidade']

# Substituir os rótulos para os valores
animais_contagem['Aceita Animais'] = animais_contagem['Aceita Animais'].replace(
    {'acept': 'Pet friendly', 'not acept': 'Não aceita pet'}
)

# Ordenar do maior para o menor
animais_contagem = animais_contagem.sort_values(by='Quantidade', ascending=True)

# Gráfico de barras
fig_aceita_animais = px.bar(
    animais_contagem, 
    y='Aceita Animais', 
    x='Quantidade', 
    title="Imóveis que Aceitam Animais",
    labels={'Aceita Animais': 'Status', 'Quantidade': 'Quantidade'},
    color='Aceita Animais',  # Definir a coluna que determina as cores
    color_discrete_map={
        'Pet friendly': colors[0],  # Cor para 'Pet friendly'
        'Não aceita pet': colors[1],  # Cor para 'Não aceita pet'
    },
    orientation='h'     # Define a orientação como horizontal
)

# Remover o título do eixo X
fig_aceita_animais.update_layout(xaxis_title='')

# Exibir o gráfico
total_imoveis = df.shape[0]  # Exemplo para total de imóveis, ajuste conforme necessário
col8.plotly_chart(fig_aceita_animais, use_container_width=True, value=f"{total_imoveis:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."))


# Gráfico 4: R$/m² por Tipo de Imóvel (Cluster de Tamanho)

# Definir clusters de tamanho
bins = [0, 50, 100, 150, 200, df['area'].max()]
labels = ['0-50m²', '51-100m²', '101-150m²', '151-200m²', '200m²+']
df['tamanho_cluster'] = pd.cut(df['area'], bins=bins, labels=labels)

# Calcular o R$/m² por cluster
aluguel_m2_cluster = df.groupby('tamanho_cluster')['aluguel_m2'].mean().reset_index()

# Gráfico de barras
fig_rent_m2_cluster = px.bar(
    aluguel_m2_cluster, 
    x='tamanho_cluster', 
    y='aluguel_m2', 
    title="R$/m² por Cluster de Tamanho de Imóvel",
    color='tamanho_cluster',
    color_discrete_map={
        '0-50m²': colors[0], 
        '51-100m²': colors[0], 
        '101-150m²': colors[0], 
        '151-200m²': colors[0], 
        '200m²+': colors[0] 
    },
    labels={'aluguel_m2': 'R$/m²', 'tamanho_cluster': 'Tamanho do Imóvel'}
)

# Remover os rótulos do canto superior esquerdo
fig_rent_m2_cluster.for_each_trace(lambda t: t.update(text=[], textposition='none'))

# Formatação do eixo Y para o padrão brasileiro
fig_rent_m2_cluster.update_yaxes(tickformat=",.2f")  # Formato com vírgula para decimal

# Ajustar o layout para uma visualização limpa
fig_rent_m2_cluster.update_layout(
    xaxis_title="Valor (R$)",
    yaxis_title="Componente do Custo",
    showlegend=False  # Ocultar legenda, já que cada barra é bem rotulada
)

# Exibir o gráfico
col9.plotly_chart(fig_rent_m2_cluster, use_container_width=True)


# Gráfico 5: Imposto Médio por Imóvel e Cidade

# Calcular o imposto médio por cidade
imposto_medio_cidade = df.groupby('city')['property tax (R$)'].mean().reset_index()

# Ordenar os dados de forma ascendente com base no imposto médio
imposto_medio_cidade = imposto_medio_cidade.sort_values(by='property tax (R$)')

# Gráfico de barras com uma única cor
fig_imposto_medio_cidade = px.bar(
    imposto_medio_cidade, 
    y='city',          # Trocar para y para barras horizontais
    x='property tax (R$)', 
    title="Imposto Médio por Imóvel e Cidade",
    labels={'property tax (R$)': 'Imposto Médio (R$)', 'city': 'Cidade'},
    orientation='h',   # Define a orientação como horizontal
    color_discrete_sequence=[colors[2]]  # Usar a primeira cor da paleta
)

# Formatação do eixo X para o padrão brasileiro
fig_imposto_medio_cidade.update_xaxes(tickformat=",.2f")  # Formato com vírgula para decimal

# Exibir o gráfico
col10.plotly_chart(fig_imposto_medio_cidade, use_container_width=True)


# Gráfico 6
import pandas as pd
import plotly.express as px

# Verificar os nomes das colunas
print(df.columns)

# Definir clusters de tamanho
bins = [0, 50, 100, 150, 200, df['area'].max()]
labels = ['0-50m²', '51-100m²', '101-150m²', '151-200m²', '200m²+']
df['tamanho_cluster'] = pd.cut(df['area'], bins=bins, labels=labels)

# Ajustar o nome da coluna de aluguel conforme necessário
aluguel_col = 'rent amount (R$)'  # Nome correto da coluna de aluguel
df['aluguel_m2'] = df[aluguel_col] / df['area']  # Calcular o R$/m²

# Calcular a média do R$/m² por cluster
aluguel_m2_cluster = df.groupby('tamanho_cluster')['aluguel_m2'].mean().reset_index()

# Gráfico de dispersão: R$/m² vs. Área, colorido por tamanho do cluster
fig_scatter_area = px.scatter(
    df, 
    x='area', 
    y='aluguel_m2',  # Usando o aluguel por m² no eixo Y
    color='tamanho_cluster',  # Usando o cluster como cor
    title="Relação entre Área e Preço do Aluguel por Tamanho do Imóvel",
    labels={'area': 'Área (m²)', 'aluguel_m2': 'Preço do Aluguel (R$/m²)', 'tamanho_cluster': 'Tamanho do Imóvel'},
    hover_name='tamanho_cluster',  # Adiciona o tamanho do cluster ao hover
    color_discrete_sequence=px.colors.qualitative.Set1  # Escolha uma paleta de cores
)

# Exibir o gráfico
col11.plotly_chart(fig_scatter_area, use_container_width=True)

# Se desejar, você pode exibir a média de R$/m² por cluster
print(aluguel_m2_cluster)



# Mapa

# Adiciona colunas de latitude e longitude
def add_coordinates(df):
    coordinates = {
        "Belo Horizonte": (-19.9191, -43.9386),
        "Rio de Janeiro": (-22.9068, -43.1729),
        "São Paulo": (-23.5505, -46.6333),
        "Porto Alegre": (-30.0346, -51.2177),
        "Campinas": (-22.9056, -47.0608),
    }
    
    df['latitude'] = np.nan
    df['longitude'] = np.nan
    
    for city, (lat, lon) in coordinates.items():
        df.loc[df['city'] == city, ['latitude', 'longitude']] = lat, lon

    return df

df = add_coordinates(df)

# Filtragem da média de aluguel
city_stats = df.groupby("city").agg(media_aluguel=('total (R$)', 'mean')).reset_index()
min_media_aluguel = int(city_stats["media_aluguel"].min())
max_media_aluguel = int(city_stats["media_aluguel"].max())

min_slider, max_slider = st.slider(
    "Selecione o intervalo de média de aluguel (R$):",
    min_value=min_media_aluguel,
    max_value=max_media_aluguel,
    value=(min_media_aluguel, max_media_aluguel)
)

filtered_cities = city_stats[
    (city_stats["media_aluguel"] >= min_slider) & 
    (city_stats["media_aluguel"] <= max_slider)
]
filtered_data = df[df["city"].isin(filtered_cities["city"])]

if 'latitude' in filtered_data.columns and 'longitude' in filtered_data.columns:
    st.subheader('Mapa de propriedades com base na média de aluguel')
    st.map(filtered_data[['latitude', 'longitude']])
else:
    st.error("O DataFrame deve conter colunas de latitude e longitude nomeadas 'latitude' e 'longitude'.")


