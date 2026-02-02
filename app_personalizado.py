# Bibliotecas necessárias para a criação do página/dashboard
import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração da página ---
# Define o título da página, seu ícone e layout para ocupar toda a tela.
st.set_page_config(
    page_title="Dashboard de Salários na Área de Dados",
    page_icon="📊",
    layout='wide',
    menu_items={
        'About': "Tem nada aqui ainda, to pensando noq colocar🫠..."}
)

# --- Carregamento dos dados ---
# Carrega o CSV direto da URL (sem precisar baixar manualmente)
# Se preferir usar local: df = pd.read_csv('caminho/para/arquivo.csv')
df = pd.read_csv('https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv')

# --- Barra lateral (Filtros) ---
st.sidebar.header(body="🔍Filtros", anchor='filtro', help="Selecione os filtros desejados para refinar a análise dos dados.", divider='red')

# Padrão dos filtros: pega valores únicos da coluna, ordena e cria dropdown
# multiselect() = permite selecionar múltiplos valores | default = seleciona todos por padrão
# Filtro por ano
anos_disponiveis = sorted(df['ano'].unique())
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)

# Filtro por senioridade
senioridades_disponiveis = sorted(df['senioridade'].unique())
senioridades_selecionadas = st.sidebar.multiselect("Senioridade", senioridades_disponiveis, default=senioridades_disponiveis)

# Filtro por Tipo de Contrato
contratos_disponiveis = sorted(df['contrato'].unique())
contratos_selecionados = st.sidebar.multiselect("Tipo de Contrato", contratos_disponiveis, default=contratos_disponiveis)

# Filtro por Tamanho da Empresa
tamanhos_disponiveis = sorted(df['tamanho_empresa'].unique())
tamanhos_selecionados = st.sidebar.multiselect("Tamanho da Empresa", tamanhos_disponiveis, default=tamanhos_disponiveis)

# --- Aplicação dos filtros no DataFrame ---
# Boolean indexing: (df['coluna'].isin(lista)) retorna True/False para cada linha
# & = AND (todas as condições devem ser verdadeiras)
# Resultado: um novo dataframe apenas com as linhas que passam em TODOS os filtros
df_filtrado = df[
    (df['ano'].isin(anos_selecionados)) &
    (df['senioridade'].isin(senioridades_selecionadas)) &
    (df['contrato'].isin(contratos_selecionados)) &
    (df['tamanho_empresa'].isin(tamanhos_selecionados))
]

# --- Conteúdo Principal ---
st.title(body='📊 :red[Dashboard] de :green[Salários] na :blue[Área de Dados]', anchor='dashboard', text_alignment='center', help='Desenvolvido por 💸🥋Luan🥋💸')
st.markdown("Explore os dados salariais na área de dados nos últimos anos. Utilize os filtros à esquerda para refinar sua análise.")
st.markdown("---")

# --- Métricas Principais (KPIs) ---
st.subheader("Métricas gerais (Salário anual em USD)", anchor='metricas', help="Principais métricas salariais com base nos filtros aplicados.")
st.info("💡 **Delta**: indica variação percentual em relação à média total do dataset.")

# Calcula as métricas principais usando funções do pandas
# .mean() = média | .min() = mínimo | .max() = máximo | .mode()[0] = valor mais frequente
if not df_filtrado.empty:
    salario_medio = df_filtrado['usd'].mean()
    salario_minimo = df_filtrado["usd"].min()
    salario_maximo = df_filtrado['usd'].max()
    total_registros = df_filtrado.shape[0]  # .shape[0] = número de linhas
    cargo_mais_frequente = df_filtrado["cargo"].mode()[0]
else:
    # Se não houver dados após filtros, define valores zerados
    salario_medio, salario_minimo, salario_maximo, total_registros, cargo_mais_frequente = 0, 0, 0, 0, ""
    st.warning("Nenhum dado disponível para os filtros selecionados.")

col1, col2, col3, col4, col5 = st.columns(5)
# .metric() exibe um KPI (indicador) com label, valor e delta (variação percentual)
# delta -> Comparamos com a média geral do dataset completo (df) para ter contexto
col1.metric("Salário :yellow[médio]", f"${salario_medio:,.0f}", delta=f"{(salario_medio/df['usd'].mean()*100-100):+.2f}%" if salario_medio else "N/A")
col2.metric("Salário :green[mínimo]", f"${salario_minimo:,.0f}")
col3.metric("Salário :red[máximo]", f"${salario_maximo:,.0f}")
col4.metric("Total de :blue[registros]", f"{total_registros:,}", delta=f"{(total_registros/df.shape[0]*100-100):+.2f}%" if total_registros else "N/A")
col5.metric("Cargo mais :blue[frequente]", cargo_mais_frequente)

st.markdown("---")

# --- Análises/Gráficos Visuais com Plotly ---
st.subheader("Gráficos", anchor='graficos', help="Visualizações gráficas para melhor compreensão dos dados salariais.")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        # groupby('cargo') agrupa por cargo | ['usd'].mean() calcula média | nlargest(10) pega top 10
        # sort_values(ascending=True) ordena crescente (mais baixo embaixo, mais alto no topo)
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_cargos = px.bar(
            top_cargos,
            x='usd',
            y='cargo',
            orientation='h',
            title="Top 10 cargos por salário médio",
            labels={'usd': 'Média salarial anual (USD)', 'cargo': ''},
            color='usd',  # Usa a coluna 'usd' para definir a intensidade da cor
            color_continuous_scale='Reds'  # Escala de cores: branco → vermelho (quanto maior o valor, mais vermelho)
        )
        grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'}, coloraxis_showscale=False)
        st.plotly_chart(grafico_cargos, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de cargos.")

with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x='usd',
            nbins=30,
            title="Distribuição de salários anuais",
            labels={'usd': 'Faixa salarial (USD)', 'count': ''}
        )
        grafico_hist.update_layout(title_x=0.1)
        # Cor única fixa: #C41E3A é um código hexadecimal (vermelho escuro)
        # Para mudar: use 'red', 'blue' ou qualquer cor em hex (procure em color-hex.com)
        grafico_hist.update_traces(marker_color='#C41E3A')
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição.")

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtrado.empty:
        # value_counts() conta quantas vezes cada valor aparece na coluna 'remoto'
        # reset_index() transforma o resultado em um dataframe comum
        remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
        grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_trabalho',
            values='quantidade',
            title='Proporção dos tipos de trabalho',
            hole=0.5,
            # color_discrete_sequence: lista de cores (uma para cada categoria)
            # A ordem segue os dados: primeira cor = primeira categoria, etc
            color_discrete_sequence=['#C41E3A', '#E74C3C', '#F39C12']
        )
        grafico_remoto.update_traces(textinfo='percent+label')
        grafico_remoto.update_layout(title_x=0.1)
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico dos tipos de trabalho.")

with col_graf4:
    if not df_filtrado.empty:
        # Filtra apenas registros onde cargo == 'Data Scientist'
        # groupby('residencia_iso3') agrupa por país | ['usd'].mean() calcula salário médio por país
        df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
        media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
        grafico_paises = px.choropleth(media_ds_pais,
            locations='residencia_iso3',
            color='usd',
            color_continuous_scale='rdylgn',
            title='Salário médio de Cientista de Dados por país',
            labels={'usd': 'Salário médio (USD)', 'residencia_iso3': 'País'})
        grafico_paises.update_layout(title_x=0.1)
        st.plotly_chart(grafico_paises, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de países.")

# --- Gráfico Personalizado ---
st.subheader("Crie seu próprio gráfico", anchor='grafico-personalizado', help="Selecione as variáveis e o tipo de visualização desejada.")

# Obtém colunas disponíveis para visualização
# Exclui colunas que não fazem sentido como variáveis numéricas (ano, id, etc)
colunas_numericas = df_filtrado.select_dtypes(include=['number']).columns.tolist()
colunas_numericas = [col for col in colunas_numericas if col not in ['ano']]  # Remove 'ano' pois é melhor como categoria
todas_colunas = df_filtrado.columns.tolist()

if not df_filtrado.empty:
    col_pers1, col_pers2, col_pers3 = st.columns(3)
    
    with col_pers1:
        tipo_grafico_pers = st.selectbox(
            "Tipo de gráfico",
            ["Barras", "Dispersão", "Linha", "Histograma", "Box Plot"],
            help="Escolha o tipo de visualização"
        )
    
    with col_pers2:
        eixo_x = st.selectbox(
            "Eixo X",
            todas_colunas,
            help="Selecione a coluna para o eixo X"
        )
    
    with col_pers3:
        eixo_y = st.selectbox(
            "Eixo Y",
            colunas_numericas if colunas_numericas else todas_colunas,
            help="Selecione a coluna numérica para o eixo Y"
        )
    
    # Criar gráfico baseado nas seleções
    try:
        if tipo_grafico_pers == "Barras":
            grafico_pers = px.bar(
                df_filtrado.groupby(eixo_x)[eixo_y].mean().reset_index(),
                x=eixo_x,
                y=eixo_y,
                title=f"Gráfico de Barras: {eixo_y} por {eixo_x}",
                labels={eixo_x: eixo_x, eixo_y: eixo_y},
                color=eixo_y,
                color_continuous_scale='Reds'
            )
            grafico_pers.update_layout(coloraxis_showscale=False)
        elif tipo_grafico_pers == "Dispersão":
            grafico_pers = px.scatter(
                df_filtrado,
                x=eixo_x,
                y=eixo_y,
                title=f"Gráfico de Dispersão: {eixo_y} vs {eixo_x}",
                labels={eixo_x: eixo_x, eixo_y: eixo_y},
                color=eixo_y,
                color_continuous_scale='Reds'
            )
            grafico_pers.update_layout(coloraxis_showscale=False)
        elif tipo_grafico_pers == "Linha":
            grafico_pers = px.line(
                df_filtrado.groupby(eixo_x)[eixo_y].mean().reset_index(),
                x=eixo_x,
                y=eixo_y,
                title=f"Gráfico de Linha: {eixo_y} por {eixo_x}",
                labels={eixo_x: eixo_x, eixo_y: eixo_y}
            )
            grafico_pers.update_traces(line=dict(color='#C41E3A', width=3))
        elif tipo_grafico_pers == "Histograma":
            if eixo_y in colunas_numericas:
                grafico_pers = px.histogram(
                    df_filtrado,
                    x=eixo_y,
                    nbins=20,
                    title=f"Histograma de {eixo_y}",
                    labels={eixo_y: eixo_y}
                )
                grafico_pers.update_traces(marker_color='#C41E3A')
            else:
                st.error("Para Histograma, escolha uma coluna numérica no eixo Y")
                grafico_pers = None
        else:  # Box Plot
            if eixo_y in colunas_numericas:
                grafico_pers = px.box(
                    df_filtrado,
                    x=eixo_x,
                    y=eixo_y,
                    title=f"Box Plot: {eixo_y} por {eixo_x}",
                    labels={eixo_x: eixo_x, eixo_y: eixo_y}
                )
                grafico_pers.update_traces(marker=dict(color='#C41E3A'))
            else:
                st.error("Para Box Plot, escolha uma coluna numérica no eixo Y")
                grafico_pers = None
        
        if grafico_pers:
            grafico_pers.update_layout(title_x=0.1)
            st.plotly_chart(grafico_pers, use_container_width=True)
    
    except Exception as e:
        st.error(f"Erro ao criar gráfico: {str(e)}")
        st.info("Dica: Certifique-se de que as colunas selecionadas são compatíveis com o tipo de gráfico escolhido.")

st.markdown("---")

# --- Tabela de Dados Detalhados ---
st.subheader("Dados Detalhados")
st.dataframe(df_filtrado)
