import pandas as pd
import yfinance as yf
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import investpy
from datetime import date
import datetime
import seaborn as sns
import numpy as np
import quandl
import ta
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
    

def spread():
    st.title('Spread Financeiro')
    st.markdown(date.today().strftime('%d/%m/%Y'))
    st.markdown('---')
    st.subheader('Análise Completa')


    lista_acaos = ['Copel','Bradesco','Petrobras','Eletrobrás']
    acaos = st.selectbox('Selecione a ação', lista_acaos)
    
    data_inicio = '2021-01-01'
    data_final = '2022-12-31'

    #Análise COPEL
    if acaos == 'Copel':
        lista_delta = ['CPLE6 e 3','CPLE11 e 3','CPLE11 e 6']
        delta = st.selectbox('Selecione os deltas', lista_delta)
        tickers = ['CPLE3.SA', 'CPLE6.SA', 'CPLE11.SA']
        ticker1 = yf.download('CPLE3.SA', start=data_inicio, end=data_final)['High']
        ticker2 = yf.download('CPLE6.SA', start=data_inicio, end=data_final)['High']
        ticker3 = yf.download('CPLE11.SA', start=data_inicio, end=data_final)['High']

        copel = yf.download(tickers, start=data_inicio, end=data_final)['High']
        copel['DELTA6_3'] = ticker2 - ticker1
        copel['DELTA11_3'] = (ticker1*6) - ticker3
        copel['DELTA11_6'] = (ticker2*5) - ticker3
        spread = copel
        df = spread
        
        #Análise CPLE6 X CPLE3
        if delta == 'CPLE6 e 3':
            #Grafico de linha com escolha do periodo
            fig1 = px.line(df, x=copel.index, y='DELTA6_3', title='Spread - Período Completo')
            fig1.update_layout(autosize= False, height=700, width=800)
            fig1.update_xaxes(
                rangeslider_visible=True,
                rangeselector=dict(
                    buttons=list([
                        dict(count=5, label="5d", step="day", stepmode="todate"),
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=40, label="40d", step="day", stepmode="todate"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(count=1, label="YTD", step="year", stepmode="todate"),
                        dict(count=1, label="1y", step="year", stepmode="backward"),
                        dict(step="all")
                    ])
                )
            )   
            st.plotly_chart(fig1)

            #Grafico Quartil - Período Completo
            fig2 = px.box(df, x='DELTA6_3', points='all', title='Quartil - Período Completo')
            st.plotly_chart(fig2)
            df_completo = df
            df_completo.drop(['CPLE11.SA', 'CPLE3.SA', 'CPLE6.SA', 'DELTA11_3', 'DELTA11_6'], axis=1, inplace=True)

            min = round(np.quantile(df_completo, .00),2)
            q1 = round(np.quantile(df_completo, .25,),2)
            q2 = round(np.quantile(df_completo, .50),2)
            q3 = round(np.quantile(df_completo, .75),2)
            max = round(np.quantile(df_completo, 1.0,),2)

            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric('Mín.', min)
            col2.metric("Q1", q1,)
            col3.metric("Q2", q2)
            col4.metric("Q3", q3)
            col5.metric('Máx.', max)
            st.markdown('---')

           
            df_40dias = yf.download(tickers, period='40d')['High']
            copel3_40d = yf.download('CPLE3.SA', period='40d')['High']
            copel6_40d = yf.download('CPLE6.SA', period='40d')['High']
            df_40dias['DELTA6_3'] = copel6_40d - copel3_40d
            df_40dias.drop(['CPLE11.SA', 'CPLE3.SA', 'CPLE6.SA'], axis=1, inplace=True)

            #Grafico Quartil - 40 dias
            fig3 = px.box(df_40dias, x='DELTA6_3', points='all', title='Quartil - Últimos 40 Dias')
            st.plotly_chart(fig3)
            min_2 = round(np.quantile(df_40dias, .00,),2)
            q1_2 = round(np.quantile(df_40dias, .25,),2)
            q2_2 = round(np.quantile(df_40dias, .50),2)
            q3_2 = round(np.quantile(df_40dias, .75),2)
            max_2 = round(np.quantile(df_40dias, 1.0,),2)
            ultimo = round(df_40dias['DELTA6_3'].iloc[-1],2)
            

            col1, col2, col3, col4, col5, col6 = st.columns(6)
            col1.metric('Mín.', min_2)
            col2.metric("Q1", q1_2,)
            col3.metric("Q2", q2_2)
            col4.metric("Q3", q3_2)
            col5.metric('Máx.', max_2)
            col6.metric('Último.',ultimo)
            st.markdown('---')

            st.subheader('Tabela de Dados - 40 dias')
            st.write(df_40dias)
           
            
        #Análise CPLE11 X CPLE3
        if delta == 'CPLE11 e 3':
            #Grafico de linha com escolha do periodo
            fig1 = px.line(df, x=copel.index, y='DELTA11_3', title='Spread - Período Completo')
            fig1.update_layout(autosize= False, height=700, width=800)
            fig1.update_xaxes(
                rangeslider_visible=True,
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=40, label="40d", step="day", stepmode="todate"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(count=1, label="YTD", step="year", stepmode="todate"),
                        dict(count=1, label="1y", step="year", stepmode="backward"),
                        dict(step="all")
                    ])
                )
            )
            st.plotly_chart(fig1)

            #Grafico Quartil - Período Completo
            fig2 = px.box(df, x='DELTA11_3', points='all', title='Quartil - Período Completo')
            st.plotly_chart(fig2)
            df_completo = df
            df_completo.drop(['CPLE11.SA', 'CPLE3.SA', 'CPLE6.SA', 'DELTA6_3', 'DELTA11_6'], axis=1, inplace=True)
            df_completo.fillna({'DELTA11_3':3.88})


            min = round(np.quantile(df_completo, .00),2)
            q1 = round(np.quantile(df_completo, .25,),2)
            q2 = round(np.quantile(df_completo, .50),2)
            q3 = round(np.quantile(df_completo, .75),2)
            max = round(np.quantile(df_completo, 1.0,),2)

            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric('Mín.', min)
            col2.metric("Q1", q1,)
            col3.metric("Q2", q2)
            col4.metric("Q3", q3)
            col5.metric('Máx.', max)
            st.markdown('---')

            df_40dias = yf.download(tickers, period='40d')['High']
            copel3_40d = yf.download('CPLE3.SA', period='40d')['High']
            copel11_40d = yf.download('CPLE11.SA', period='40d')['High']
            df_40dias['DELTA11_3'] = (copel3_40d*6) - copel11_40d
            df_40dias.drop(['CPLE11.SA', 'CPLE3.SA', 'CPLE6.SA'], axis=1, inplace=True)
    
            #df_40dias.fillna({'DELTA11_3':3.88})
            ultimo = round(df_40dias['DELTA11_3'].iloc[-1],2)
        

            #Grafico Quartil - 40 dias
            fig3 = px.box(df_40dias, x='DELTA11_3', points='all', title='Quartil - Últimos 40 Dias')
            st.plotly_chart(fig3)
            min_2 = round(np.quantile(df_40dias, .00,),2)
            q1_2 = round(np.quantile(df_40dias, .25,),2)
            q2_2 = round(np.quantile(df_40dias, .50),2)
            q3_2 = round(np.quantile(df_40dias, .75),2)
            max_2 = round(np.quantile(df_40dias, 1.0,),2)
            

            col1, col2, col3, col4, col5, col6 = st.columns(6)
            col1.metric('Mín.', min_2)
            col2.metric("Q1", q1_2,)
            col3.metric("Q2", q2_2)
            col4.metric("Q3", q3_2)
            col5.metric('Máx.', max_2)
            col6.metric('Último.',ultimo)
            st.markdown('---')

            st.subheader('Tabela de Dados - 40 dias')
            st.write(df_40dias)


        #Análise CPLE11 X CPLE6
        if delta == 'CPLE11 e 6':
            #Grafico de linha com escolha do periodo
            fig1 = px.line(df, x=copel.index, y='DELTA11_6', title='Spread - Período Completo')
            fig1.update_layout(autosize= False, height=700, width=800)
            fig1.update_xaxes(
                rangeslider_visible=True,
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=40, label="40d", step="day", stepmode="todate"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(count=1, label="YTD", step="year", stepmode="todate"),
                        dict(count=1, label="1y", step="year", stepmode="backward"),
                        dict(step="all")
                    ])
                )
            )
            st.plotly_chart(fig1)

            #Grafico Quartil - Período Completo
            fig2 = px.box(df, x='DELTA11_6', points='all', title='Quartil - Período Completo')
            st.plotly_chart(fig2)
            df_completo = df
            df_completo.drop(['CPLE11.SA', 'CPLE3.SA', 'CPLE6.SA', 'DELTA6_3', 'DELTA11_3'], axis=1, inplace=True)
            #df_completo=df.dropna(subset=['DELTA11_6'])

            min = round(np.quantile(df_completo, .00),2)
            q1 = round(np.quantile(df_completo, .25,),2)
            q2 = round(np.quantile(df_completo, .50),2)
            q3 = round(np.quantile(df_completo, .75),2)
            max = round(np.quantile(df_completo, 1.0,),2)

            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric('Mín.', min)
            col2.metric("Q1", q1,)
            col3.metric("Q2", q2)
            col4.metric("Q3", q3)
            col5.metric('Máx.', max)
            st.markdown('---')

            df_40dias = yf.download(tickers, period='40d')['High']
            copel6_40d = yf.download('CPLE6.SA', period='40d')['High']
            copel11_40d = yf.download('CPLE11.SA', period='40d')['High']
            df_40dias['DELTA11_6'] = (copel6_40d*5) - copel11_40d
            df_40dias.drop(['CPLE11.SA', 'CPLE3.SA', 'CPLE6.SA'], axis=1, inplace=True)
            #df_40dias=df.dropna(subset=['DELTA11_6'])  
            ultimo = round(df_40dias['DELTA11_6'].iloc[-1],2)
        
            #Grafico Quartil - 40 dias
            fig3 = px.box(df_40dias, x='DELTA11_6', points='all', title='Quartil - Últimos 40 Dias')
            st.plotly_chart(fig3)
            min_2 = round(np.quantile(df_40dias, .00,),2)
            q1_2 = round(np.quantile(df_40dias, .25,),2)
            q2_2 = round(np.quantile(df_40dias, .50),2)
            q3_2 = round(np.quantile(df_40dias, .75),2)
            max_2 = round(np.quantile(df_40dias, 1.0,),2)
            
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            col1.metric('Mín.', min_2)
            col2.metric("Q1", q1_2,)
            col3.metric("Q2", q2_2)
            col4.metric("Q3", q3_2)
            col5.metric('Máx.', max_2)
            col6.metric('Último.',ultimo)
            st.markdown('---')

            st.subheader('Tabela de Dados - 40 dias')
            st.write(df_40dias)

    #Anáise BRADESCO
    if acaos == 'Bradesco':
        lista_delta = ['BBDC4 e 3']
        delta = st.selectbox('Selecione os deltas', lista_delta)
        tickers = ['BBDC3.SA', 'BBDC4.SA']
        ticker1 = yf.download('BBDC3.SA', start=data_inicio, end=data_final)['High']
        ticker2 = yf.download('BBDC4.SA', start=data_inicio, end=data_final)['High']
       
        bradesco = yf.download(tickers, start=data_inicio, end=data_final)['High']
        bradesco['DELTA4_3'] = ticker2 - ticker1
        spread = bradesco
        df = spread
   
        #Análise BBDC4 X BBDC3
        if delta == 'BBDC4 e 3':
            #Grafico de linha com escolha do periodo
            fig1 = px.line(df, x=bradesco.index, y='DELTA4_3', title='Spread - Período Completo')
            fig1.update_layout(autosize= False, height=700, width=800)
            fig1.update_xaxes(
                rangeslider_visible=True,
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=40, label="40d", step="day", stepmode="todate"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(count=1, label="YTD", step="year", stepmode="todate"),
                        dict(count=1, label="1y", step="year", stepmode="backward"),
                        dict(step="all")
                    ])
                )
            )
            st.plotly_chart(fig1)

            #Grafico Quartil - Período Completo
            fig2 = px.box(df, x='DELTA4_3', points='all', title='Quartil - Período Completo')
            st.plotly_chart(fig2)
            df_completo = df
            df_completo.drop(['BBDC3.SA', 'BBDC4.SA'], axis=1, inplace=True)

            min = round(np.quantile(df_completo, .00),2)
            q1 = round(np.quantile(df_completo, .25,),2)
            q2 = round(np.quantile(df_completo, .50),2)
            q3 = round(np.quantile(df_completo, .75),2)
            max = round(np.quantile(df_completo, 1.0,),2)

            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric('Mín.', min)
            col2.metric("Q1", q1,)
            col3.metric("Q2", q2)
            col4.metric("Q3", q3)
            col5.metric('Máx.', max)
            st.markdown('---')

            df_40dias = yf.download(tickers, period='40d')['High']
            bradesco3_40d = yf.download('BBDC3.SA', period='40d')['High']
            bradesco4_40d = yf.download('BBDC4.SA', period='40d')['High']
            df_40dias['DELTA4_3'] = bradesco4_40d - bradesco3_40d
            df_40dias.drop(['BBDC3.SA', 'BBDC4.SA'], axis=1, inplace=True)

            #Grafico Quartil - 40 dias
            fig3 = px.box(df_40dias, x='DELTA4_3', points='all', title='Quartil - Últimos 40 Dias')
            st.plotly_chart(fig3)
            min_2 = round(np.quantile(df_40dias, .00,),2)
            q1_2 = round(np.quantile(df_40dias, .25,),2)
            q2_2 = round(np.quantile(df_40dias, .50),2)
            q3_2 = round(np.quantile(df_40dias, .75),2)
            max_2 = round(np.quantile(df_40dias, 1.0,),2)
            ultimo = round(df_40dias['DELTA4_3'].iloc[-1],2)
            

            col1, col2, col3, col4, col5, col6 = st.columns(6)
            col1.metric('Mín.', min_2)
            col2.metric("Q1", q1_2,)
            col3.metric("Q2", q2_2)
            col4.metric("Q3", q3_2)
            col5.metric('Máx.', max_2)
            col6.metric('Último.',ultimo)
            st.markdown('---')

            st.subheader('Tabela de Dados - 40 dias')
            st.write(df_40dias)

    #Anáise PETROBRÁS
    if acaos == 'Petrobras':
        lista_delta = ['PETR3 e 4']
        delta = st.selectbox('Selecione os deltas', lista_delta)
        tickers = ['PETR3.SA', 'PETR4.SA']
        ticker1 = yf.download('PETR3.SA', start=data_inicio, end=data_final)['High']
        ticker2 = yf.download('PETR4.SA', start=data_inicio, end=data_final)['High']
       
        petro = yf.download(tickers, start=data_inicio, end=data_final)['High']
        petro['DELTA3_4'] = ticker1 - ticker2
        spread = petro
        df = spread
   
        #Análise PETR3 X PETR4
        if delta == 'PETR3 e 4':
            #Grafico de linha com escolha do periodo
            fig1 = px.line(df, x=petro.index, y='DELTA3_4', title='Spread - Período Completo')
            fig1.update_layout(autosize= False, height=700, width=800)
            fig1.update_xaxes(
                rangeslider_visible=True,
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=40, label="40d", step="day", stepmode="todate"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(count=1, label="YTD", step="year", stepmode="todate"),
                        dict(count=1, label="1y", step="year", stepmode="backward"),
                        dict(step="all")
                    ])
                )
            )
            st.plotly_chart(fig1)

            #Grafico Quartil - Período Completo
            fig2 = px.box(df, x='DELTA3_4', points='all', title='Quartil - Período Completo')
            st.plotly_chart(fig2)
            df_completo = df
            df_completo.drop(['PETR3.SA', 'PETR4.SA'], axis=1, inplace=True)

            min = round(np.quantile(df_completo, .00),2)
            q1 = round(np.quantile(df_completo, .25,),2)
            q2 = round(np.quantile(df_completo, .50),2)
            q3 = round(np.quantile(df_completo, .75),2)
            max = round(np.quantile(df_completo, 1.0,),2)

            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric('Mín.', min)
            col2.metric("Q1", q1,)
            col3.metric("Q2", q2)
            col4.metric("Q3", q3)
            col5.metric('Máx.', max)
            st.markdown('---')

            df_40dias = yf.download(tickers, period='40d')['High']
            petro3_40d = yf.download('PETR3.SA', period='40d')['High']
            petro4_40d = yf.download('PETR4.SA', period='40d')['High']
            df_40dias['DELTA3_4'] = petro3_40d - petro4_40d
            df_40dias.drop(['PETR3.SA', 'PETR4.SA'], axis=1, inplace=True)

            #Grafico Quartil - 40 dias
            fig3 = px.box(df_40dias, x='DELTA3_4', points='all', title='Quartil - Últimos 40 Dias')
            st.plotly_chart(fig3)
            min_2 = round(np.quantile(df_40dias, .00,),2)
            q1_2 = round(np.quantile(df_40dias, .25,),2)
            q2_2 = round(np.quantile(df_40dias, .50),2)
            q3_2 = round(np.quantile(df_40dias, .75),2)
            max_2 = round(np.quantile(df_40dias, 1.0,),2)
            ultimo = round(df_40dias['DELTA3_4'].iloc[-1],2)
            

            col1, col2, col3, col4, col5, col6 = st.columns(6)
            col1.metric('Mín.', min_2)
            col2.metric("Q1", q1_2,)
            col3.metric("Q2", q2_2)
            col4.metric("Q3", q3_2)
            col5.metric('Máx.', max_2)
            col6.metric('Último.',ultimo)
            st.markdown('---')

            st.subheader('Tabela de Dados - 40 dias')
            st.write(df_40dias)

    #Anáise ELETROBRÁS
    if acaos == 'Eletrobrás':
        lista_delta = ['ELET6 e 3']
        delta = st.selectbox('Selecione os deltas', lista_delta)
        tickers = ['ELET6.SA', 'ELET3.SA']
        ticker1 = yf.download('ELET6.SA', start=data_inicio, end=data_final)['High']
        ticker2 = yf.download('ELET3.SA', start=data_inicio, end=data_final)['High']
       
        eletro = yf.download(tickers, start=data_inicio, end=data_final)['High']
        eletro['DELTA6_3'] = ticker1 - ticker2
        spread = eletro
        df = spread
   
        #Análise PETR3 X PETR4
        if delta == 'ELET6 e 3':
            #Grafico de linha com escolha do periodo
            fig1 = px.line(df, x=eletro.index, y='DELTA6_3', title='Spread - Período Completo')
            fig1.update_layout(autosize= False, height=700, width=800)
            fig1.update_xaxes(
                rangeslider_visible=True,
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=40, label="40d", step="day", stepmode="todate"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(count=1, label="YTD", step="year", stepmode="todate"),
                        dict(count=1, label="1y", step="year", stepmode="backward"),
                        dict(step="all")
                    ])
                )
            )
            st.plotly_chart(fig1)

            #Grafico Quartil - Período Completo
            fig2 = px.box(df, x='DELTA6_3', points='all', title='Quartil - Período Completo')
            st.plotly_chart(fig2)
            df_completo = df
            df_completo.drop(['ELET3.SA', 'ELET6.SA'], axis=1, inplace=True)

            min = round(np.quantile(df_completo, .00),2)
            q1 = round(np.quantile(df_completo, .25,),2)
            q2 = round(np.quantile(df_completo, .50),2)
            q3 = round(np.quantile(df_completo, .75),2)
            max = round(np.quantile(df_completo, 1.0,),2)

            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric('Mín.', min)
            col2.metric("Q1", q1,)
            col3.metric("Q2", q2)
            col4.metric("Q3", q3)
            col5.metric('Máx.', max)
            st.markdown('---')

            df_40dias = yf.download(tickers, period='40d')['High']
            eletro3_40d = yf.download('ELET3.SA', period='40d')['High']
            eletro6_40d = yf.download('ELET6.SA', period='40d')['High']
            df_40dias['DELTA6_3'] = eletro6_40d - eletro3_40d
            df_40dias.drop(['ELET3.SA', 'ELET6.SA'], axis=1, inplace=True)

            #Grafico Quartil - 40 dias
            fig3 = px.box(df_40dias, x='DELTA6_3', points='all', title='Quartil - Últimos 40 Dias')
            st.plotly_chart(fig3)
            min_2 = round(np.quantile(df_40dias, .00,),2)
            q1_2 = round(np.quantile(df_40dias, .25,),2)
            q2_2 = round(np.quantile(df_40dias, .50),2)
            q3_2 = round(np.quantile(df_40dias, .75),2)
            max_2 = round(np.quantile(df_40dias, 1.0,),2)
            ultimo = round(df_40dias['DELTA6_3'].iloc[-1],2)
            

            col1, col2, col3, col4, col5, col6 = st.columns(6)
            col1.metric('Mín.', min_2)
            col2.metric("Q1", q1_2,)
            col3.metric("Q2", q2_2)
            col4.metric("Q3", q3_2)
            col5.metric('Máx.', max_2)
            col6.metric('Último.',ultimo)
            st.markdown('---')

            st.subheader('Tabela de Dados - 40 dias')
            st.write(df_40dias)

def panorama():
    st.title('Panorama do Mercado')
    st.markdown(date.today().strftime('%d/%m/%Y'))

    st.subheader('Mercado hoje')
    dict_tickers = {
                  'COPEL 6 PNB':'CPLE6.SA',
                  'COPEL 3 ON':'CPLE3.SA',
                  'COPEL 11 UNT':'CPLE11.SA',
                  'BRADESCO 4 PN':'BBDC4.SA',
                  'BRADESCO 3 ON':'BBDC3.SA',
                  'SANEPAR 4 PN':'SAPR4.SA',
                  'SANEPAR 3 ON':'SAPR3.SA',
                  'SANEPAR 11 UNT':'SAPR11.SA',
                  'PETROBRAS 4':'PETR4.SA'
                  }

    df_info = pd.DataFrame({'Ativo': dict_tickers.keys(),'Ticker': dict_tickers.values()})

    df_info['Ult. Valor'] = ''
    df_info['%'] = ''
    count =0
    with st.spinner('Carregando cotações...'): 
        for ticker in dict_tickers.values():
            cotacoes = yf.download(ticker, period='5d')['Adj Close']
            variacao = ((cotacoes.iloc[-1]/cotacoes.iloc[-2])-1)*100
            df_info['Ult. Valor'][count] = round(cotacoes.iloc[-1],2)
            df_info['%'][count] = round(variacao,2)
            count +=1 

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(df_info['Ativo'][0], value=df_info['Ult. Valor'][0], delta=str(df_info['%'][0])+'%')
        st.metric(df_info['Ativo'][1], value=df_info['Ult. Valor'][1], delta=str(df_info['%'][1])+'%')
        st.metric(df_info['Ativo'][2], value=df_info['Ult. Valor'][2], delta=str(df_info['%'][2])+'%')
   
    with col2:
        st.metric(df_info['Ativo'][5], value=df_info['Ult. Valor'][5], delta=str(df_info['%'][5])+'%')
        st.metric(df_info['Ativo'][6], value=df_info['Ult. Valor'][6], delta=str(df_info['%'][6])+'%')
        st.metric(df_info['Ativo'][7], value=df_info['Ult. Valor'][7], delta=str(df_info['%'][7])+'%')
       
    with col3:
        st.metric(df_info['Ativo'][3], value=df_info['Ult. Valor'][3], delta=str(df_info['%'][3])+'%')
        st.metric(df_info['Ativo'][4], value=df_info['Ult. Valor'][4], delta=str(df_info['%'][4])+'%')

    st.markdown('---')

    lista_tickers = fd.list_papel_all()
    acao = st.selectbox('Selecione a ação', lista_tickers, index=89)

    lista_indicador = ['RSI', 'MM8', 'MM20', 'MM200']
    indicador = st.multiselect('Selecione o(s) indicador(es)', lista_indicador, default=['RSI', 'MM8', 'MM20', 'MM200'])
    
    
    #RSI
    from ta.momentum import RSIIndicator
    from plotly._subplots import make_subplots


    precos = yf.download(f'{acao}.SA', period = '1y')
    precos['MM8'] = precos['Adj Close'].rolling(8).mean()
    precos['MM20'] = precos['Adj Close'].rolling(20).mean()
    precos['MM200'] = precos['Adj Close'].rolling(200).mean()
        
    #st.write(precos)
        
    #Indicadores
    rsi = RSIIndicator(close=precos['Close'], window=30)
    precos['RSI'] = rsi.rsi()
    fig = make_subplots(rows=2, cols=1, vertical_spacing = 0.05, row_width = [ 0.1, 0.7], shared_xaxes=True)
    if 'RSI' in indicador:
        fig.add_trace(go.Scatter(name='RSI', x=precos.index, y=precos['RSI'], marker_color='purple'), row=2, col=1)
    if 'MM8' in indicador:
        fig.add_trace(go.Scatter(name='MM8', x=precos.index, y=precos['MM8'], marker_color = 'green'), row=1, col=1)
    if 'MM20' in indicador:
        fig.add_trace(go.Scatter(name='MM20', x=precos.index, y=precos['MM20'], marker_color = 'blue'), row=1, col=1)
        fig.add_trace(go.Candlestick(x=precos.index, close=precos['Close'], open=precos['Open'], high=precos['High'], low=precos['Low']), row=1,col=1)
        fig.update_layout(autosize= False, height=800, width=900, xaxis_rangeslider_visible=False)
        fig.update_xaxes(
                rangeslider_visible=False,
                rangeselector=dict(
                    buttons=list([
                        dict(count=5, label="5d", step="day", stepmode="todate"),
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=40, label="40d", step="day", stepmode="todate"),
                        dict(count=3, label="3m", step="month", stepmode="backward"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(count=1, label="YTD", step="year", stepmode="todate"),
                        dict(count=1, label="1y", step="year", stepmode="backward"),
                        dict(step="all")
                    ])
                )
            )   
    if 'MM200' in indicador:
        fig.add_trace(go.Scatter(name='MM200', x=precos.index, y=precos['MM200'], marker_color = 'orange'), row=1, col=1)
    
    st.plotly_chart(fig)
      

def macro_economia():
    st.title('Macro Economia')
    st.markdown(date.today().strftime('%d/%m/%Y'))
    st.markdown('---')
    start_date_macro = '2012-01-01'

    st.subheader('Dólar')
    dolar = quandl.get('BCB/10813', start_date = start_date_macro)
    dolar.rename(columns = {'Date':'Data' , 'Value':'Cotação (R$)'}, inplace = True)
    dolar_graph = px.line(dolar ,y= 'Cotação (R$)')
    st.plotly_chart(dolar_graph) 
    st.markdown('---')

    st.subheader('Selic')
    selic = quandl.get('BCB/432', start_date = start_date_macro)
    selic.rename(columns = {'Date':'Data' , 'Value':'Taxa (%)'}, inplace = True)
    selic_graph = px.line(selic, y = 'Taxa (%)')
    st.plotly_chart(selic_graph)

    st.subheader('Cesta Básica')
    cesta_basica_sp = quandl.get('BCB/7493', start_date = start_date_macro)
    cesta_basica_sp.rename(columns = {'Date':'Data' , 'Value':'Preço (R$)'}, inplace = True)
    cesta_sp_graph = px.line(cesta_basica_sp ,y= 'Preço (R$)')
    st.plotly_chart(cesta_sp_graph) 
    st.markdown('---')

    #igpm = quandl.get('BCB/189', start_date = '2010-01-01')
    #st.line_chart(igpm)


def fundamentos():
    st.title('Informações sobre Fundamentos')
    st.markdown(date.today().strftime('%d/%m/%Y'))
    st.markdown('---')

    lista_tickers = fd.list_papel_all()

    comparar = st.checkbox('Comparar 2 ativos')

    col1, col2 = st.columns(2)

    with col1:
        papel1 = st.selectbox('Selecione o ativo 1', lista_tickers, index=89)
        info_papel1 = fd.get_detalhes_papel(papel1)
        st.write('**Empresa:**', info_papel1['Empresa'][0])
        st.write('**Setor:**', info_papel1['Setor'][0])
        st.write('**Subsetor:**', info_papel1['Subsetor'][0])
        st.write('**Patrimônio Líquido:**', f"R${float(info_papel1['Patrim_Liq'][0]):,.2f}")
        st.write('**Núm. Total de Ações:**', f"{float(info_papel1['Nro_Acoes'][0]):,.0f}")
        st.write('**Lucro Líquido 12m:**', f"R${float(info_papel1['Lucro_Liquido_12m'][0]):,.2f}")
        VPA_1 = float(int(info_papel1['VPA'][0])/100)
        st.write('**VPA:**', f"{VPA_1}")
        PVP_1 = float(int(info_papel1['PVP'][0])/100)
        st.write('**P/VPA:**', f"{PVP_1}")
        LPA_1 = float(int(info_papel1['LPA'][0])/100)
        st.write('**LPA:**', f"{LPA_1}")
        PLPA_1 = float(int(info_papel1['PL'][0])/100)
        st.write('**P/LPA:**', f"{PLPA_1}")
        st.write('**ROE:**', info_papel1['ROE'][0])
        st.write('**Dividend Yield:**', info_papel1['Div_Yield'][0])
        st.write('**Preço Atual:**', f"R${info_papel1['Cotacao'][0]}")

        
        if papel1 == 'BBDC4':
            dividendos_media = 0.72     #Dividendos médio dos 3 últimos anos 
            preco_teto = dividendos_media/0.08
            st.write('**Preço Teto 8%:**', f"R${preco_teto:,.2f}")

            if VPA_1 >= preco_teto:
                preco_teto_ajustado = ((VPA_1-preco_teto)/2)+preco_teto
                st.write('**Preço Teto 8% Ajust.:**', f"R${preco_teto_ajustado:,.2f}")

            st.write('**Dividendos (Média 3/8):**', f"R${dividendos_media}")

    st.write(info_papel1)


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
    lista_menu = ['Home', 'Volatilidade', 'Panorama do Mercado', 'Macro Economia', 'Fundamentos', 'Spread']
    escolha = st.sidebar.radio('Escolha a opção', lista_menu)

    if escolha == 'Home':
        home()
    if escolha == 'Spread':
        spread()
    if escolha == 'Volatilidade':
        volatilidade()
    if escolha == 'Panorama do Mercado':
        panorama()
    if escolha == 'Macro Economia':
        macro_economia()
    if escolha == 'Fundamentos':
       fundamentos()


main()
