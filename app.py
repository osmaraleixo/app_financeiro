import pandas as pd
import streamlit as st
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
import datetime
import numpy as np
import quandl
import fundamentus as fd
import base64

quandl.ApiConfig.api_key = 'KBwWAqoE51ctpSvnM22d'

def home():
    st.title('Análise de Ações - Spread')
    st.markdown('---')
    st.subheader('App para análise completa de spreads')

    lista_tickers = fd.list_papel_all()
    
    with st.form(key='Spread'):

        col1, col2, col3, col4 = st.columns(4)
        input_submit_button = st.form_submit_button('Analisar')  
        with col1:
            acao1 = st.selectbox('**:blue[Ativo 1]**', lista_tickers, index=88)
            acao2 = st.selectbox('**:blue[Ativo 2]**', lista_tickers, index=89)
           
        with col2:
            composicao_acao1 = st.number_input(label='**:orange[Composição Ativo 1]**' ,min_value=1, format='%d', step=1)
            composicao_acao2 = st.number_input(label='**:orange[Composição Ativo 2]**' ,min_value=1, format='%d', step=1)

        with col3:
            data_inicio = st.date_input("**:red[Início]**", datetime.date(2021, 1, 1))
            data_fim = st.date_input("**:red[Fim]**", datetime.date(2022, 12, 31))
        
        with col4:
            preco_teto = st.number_input(label='**Preço Teto: - R$**' ,min_value=1.00)
            roi_preco_teto = st.number_input(label='**:violet[ROI Preço Teto - 1 .. 1,5%]**', min_value=1.00)
                 
    if input_submit_button:
        
        ativo1 = yf.download(f'{acao1}.SA', start=data_inicio, end=data_fim)['High']
        ativo2 = yf.download(f'{acao2}.SA', start=data_inicio, end=data_fim)['High']
        
        # Inicializar as variáveis de contagem
        ativo1_mais_caro = 0
        ativo2_mais_caro = 0

        # Interar pelos elementos das listas e comparar os preços
        for preco in range(len(ativo2)):
            if ativo1[preco]*composicao_acao1 > ativo2[preco]*composicao_acao2:
                ativo1_mais_caro +=1
            elif ativo2[preco]*composicao_acao2 > ativo1[preco]*composicao_acao1:
                ativo2_mais_caro +=1
        
        # Calcular as porcentagens
        total = ativo1_mais_caro + ativo2_mais_caro
        porcentagem_ativo1 = (ativo1_mais_caro / total) * 100
        porcentagem_ativo2 = (ativo2_mais_caro / total) * 100
        
        # Verificar qual o maior e menor ativo
        if ativo1_mais_caro > ativo2_mais_caro:
            ativo_maior = acao1
            composicao_maior = composicao_acao1
            percentual_maior = porcentagem_ativo1
            ativo_menor = acao2
            composicao_menor = composicao_acao2
            percentual_menor = porcentagem_ativo2
        elif ativo2_mais_caro > ativo1_mais_caro:
            ativo_maior = acao2
            composicao_maior = composicao_acao2
            percentual_maior = porcentagem_ativo2
            ativo_menor = acao1
            composicao_menor = composicao_acao1
            percentual_menor = porcentagem_ativo1

        ativos = [f'{ativo_maior}.SA', f'{ativo_menor}.SA']
        ativo_maior_df = yf.download(f'{ativo_maior}.SA', start=data_inicio, end=data_fim)['High']
        ativo_menor_df = yf.download(f'{ativo_menor}.SA', start=data_inicio, end=data_fim)['High']
        ativos_df = yf.download(ativos, start=data_inicio, end=data_fim)['High']
       
        ativos_df['Máx.'+str(ativo_maior)] = ativo_maior_df * composicao_maior
        ativos_df['Máx.'+str(ativo_menor)] = ativo_menor_df * composicao_menor
        ativos_df['Créd. Camadas'] = (ativo_maior_df * composicao_maior) - (ativo_menor_df * composicao_menor)
        ativos_df.drop([f'{ativo_maior}.SA', f'{ativo_menor}.SA'], axis=1, inplace=True)
        ativos_df = ativos_df.dropna()

        #st.write(("Maior ativo: " + str(ativo_maior) + " - frequência: {:.2f}%").format(percentual_maior))
        #st.write(("Menor ativo: " + str(ativo_menor) + " - frequência: {:.2f}%").format(percentual_menor))
        #st.markdown("Maior ativo: **{}** - frequência: **{:.2f}%**".format(ativo_maior, percentual_maior))
        #st.markdown("Menor ativo: **{}** - frequência: **{:.2f}%**".format(ativo_menor, percentual_menor))
        st.markdown("Maior ativo: <span style='color:green;font-weight:bold'>{}</span> - frequência: <span style='color:green;font-weight:bold'>{:.2f}%</span>".format(ativo_maior, percentual_maior), unsafe_allow_html=True)
        st.markdown("Menor ativo: <span style='color:red;font-weight:bold'>{}</span> - frequência: <span style='color:red;font-weight:bold'>{:.2f}%</span>".format(ativo_menor, percentual_menor), unsafe_allow_html=True)


        # Grafico de linha com escolha do periodo
        fig1 = px.line(ativos_df, x=ativos_df.index, y='Créd. Camadas', title='Spread - Período Completo: ' + str(ativo_maior) + ' x ' + str(ativo_menor))
        fig1.update_layout(autosize= False, height=700, width=800)
        fig1.update_xaxes(
                rangeslider_visible=True,
                rangeselector=dict(
                    buttons=list([
                        dict(count=40, label="40d", step="day", stepmode="todate"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(count=1, label="1y", step="year", stepmode="backward"),
                        dict(step="all")
                    ])
                )
            )   
        st.plotly_chart(fig1)

        # Grafico Quartil - Período Completo
        fig2 = px.box(ativos_df, x='Créd. Camadas', points='all', title='Quartil - Período Completo: ' + str(ativo_maior) + ' x ' + str(ativo_menor))
        st.plotly_chart(fig2)

        min = round(np.quantile(ativos_df['Créd. Camadas'], .00),2)
        q1 = round(np.quantile(ativos_df['Créd. Camadas'], .25,),2)
        q2 = round(np.quantile(ativos_df['Créd. Camadas'], .50),2)
        q3 = round(np.quantile(ativos_df['Créd. Camadas'], .75),2)
        max = round(np.quantile(ativos_df['Créd. Camadas'], 1.0,),2)

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric('Mín.', min)
        col2.metric("Q1", q1,)
        col3.metric("Q2", q2)
        col4.metric("Q3", q3)
        col5.metric('Máx.', max)
        st.markdown('---')

        # Baixando os dados de mercado
        df_40dias = yf.download(ativos, period='40d')['High']
        ativo_maior_40d = yf.download(f'{ativo_maior}.SA', period='40d')['High']
        ativo_menor_40d = yf.download(f'{ativo_menor}.SA', period='40d')['High']
        df_40dias['Créd. Camadas'] = (ativo_maior_40d * composicao_maior) - (ativo_menor_40d * composicao_menor)
        df_40dias.drop([f'{ativo_maior}.SA', f'{ativo_menor}.SA'], axis=1, inplace=True)
        df_40dias = df_40dias.dropna()

        # Grafico Quartil - 40 dias
        fig3 = px.box(df_40dias, x='Créd. Camadas', points='all', title='Quartil - Últimos 40 Dias: ' + str(ativo_maior) + ' x ' + str(ativo_menor))
        st.plotly_chart(fig3)
        min_2 = round(np.quantile(df_40dias['Créd. Camadas'], .00,),2)
        q1_2 = round(np.quantile(df_40dias['Créd. Camadas'], .25,),2)
        q2_2 = round(np.quantile(df_40dias['Créd. Camadas'], .50),2)
        q3_2 = round(np.quantile(df_40dias['Créd. Camadas'], .75),2)
        max_2 = round(np.quantile(df_40dias['Créd. Camadas'], 1.0,),2)
        ultimo = round(df_40dias['Créd. Camadas'].iloc[-1],2)
            

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        col1.metric('Mín.', min_2)
        col2.metric("Q1", q1_2,)
        col3.metric("Q2", q2_2)
        col4.metric("Q3", q3_2)
        col5.metric('Máx.', max_2)
        col6.metric('Último.',ultimo)
        st.markdown('---')

        st.subheader('Tabela de Dados - Últimos 40 dias: ' + str(ativo_maior) + ' x ' + str(ativo_menor))
        st.dataframe(df_40dias.style.highlight_max(axis=0))
        st.markdown('---')

        # Planejamento das camadas não potencializadas
        st.subheader('Planejamento das Camadas: '+ str(ativo_maior))
        spread_alvo = round(preco_teto * roi_preco_teto)/100

        # Definir as variáveis de exemplo
        codigo = 'Cód.'+str(0)
        preco_inicial = min
        spread = spread_alvo
        preco_final = max
        credito = preco_inicial+spread
        debito = preco_inicial
        variacao = (((credito-debito)/2)+debito)-preco_inicial

        # Criar um DataFrame com as colunas 'código', 'debito' e 'credito'
        df = pd.DataFrame(columns=['Código', 'Débito', 'Crédito', 'Spread'])

        # Adicionar a primeira linha ao DataFrame com os valores iniciais
        df.loc[0] = [codigo, preco_inicial, preco_inicial + spread, spread]

        # Calcular o número de linhas necessárias
        num_linhas = int((preco_final - preco_inicial) / variacao) - 1 

        # Adicionar as linhas adicionais ao DataFrame
        for i in range(1, num_linhas):
            codigo = 'Cód.'+str(i)
            debito = ((credito-debito)/2)+debito
            credito = debito + spread
            spread = credito-debito
            df.loc[i] = [codigo, debito, credito, spread]

        # Imprimir o DataFrame resultante
        st.write(df)

        # Definindo a função para download
        def download_csv():
            csv = df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="dados.csv">Download CSV</a>'
            return href

       # Criando o botão de download
        st.markdown(download_csv(), unsafe_allow_html=True) 
   
def volatilidade():
    st.title('Análise de Volatilidade')
    st.markdown(date.today().strftime('%d/%m/%Y'))
    #st.markdown('---')
    
    lista_tickers = fd.list_papel_all()
    acao = st.selectbox('Selecione a ação', lista_tickers,index=89)
    st.markdown('---')
    st.subheader(':blue[Volatilidade Mensal - Projeção Mês Atual] :bar_chart:')

    dados = yf.download(f'{acao}.SA', start='2020-01-01', interval='1mo')
   
    volatilidade_mensal = dados.drop(columns=['Open', 'Close', 'Adj Close', 'Volume'])
    volatilidade_mensal['Variação %'] = ((volatilidade_mensal['High']/volatilidade_mensal['Low'])-1)*100
    volat_media = round(volatilidade_mensal['Variação %'].mean(),2)
    last_high_mo = volatilidade_mensal['High'].iloc[-1]
    last_low_mo = volatilidade_mensal['Low'].iloc[-1]
    last_variacao_mo = volatilidade_mensal['Variação %'].iloc[-1]
    proj_max_mo = round(last_high_mo+(last_high_mo*(volat_media/100-last_variacao_mo/100)),2)
    proj_min_mo = round(last_low_mo-(last_low_mo*(volat_media/100-last_variacao_mo/100)),2)

    col1, col2, col3, = st.columns(3)
    col1.metric('Projeção Mín.', proj_min_mo,)
    col2.metric('Projeção Máx.', proj_max_mo,)
    col3.metric('Volatilidade Média', str(volat_media)+'%',)

    st.markdown('')
    st.markdown('')
    st.write(dados)

def main():
    st.sidebar.title('Análise de Spread')
    st.sidebar.markdown('---')
    lista_menu = ['Home', 'Volatilidade']
    escolha = st.sidebar.radio('Escolha a opção', lista_menu)

    if escolha == 'Home':
        home()
    if escolha == 'Volatilidade':
        volatilidade()

main()