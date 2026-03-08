import streamlit as st
import pandas as pd
from datetime import datetime
import os

ARQUIVO = "dados/financeiro.xlsx"

COLUNAS = [
"NR","QTD","TIPO","DESCRIÇÃO","VALOR","DATA VENC",
"CODIGO BOLETO","COD. PIX","DATA PAGTO","VALOR PAGO",
"PAGO COM","RENDIMENTO","DATA"
]

# Criar planilha caso não exista
def iniciar_planilha():
    if not os.path.exists(ARQUIVO):
        df = pd.DataFrame(columns=COLUNAS)
        df.to_excel(ARQUIVO, index=False)

def carregar_dados():
    return pd.read_excel(ARQUIVO)

def salvar_dados(df):
    df.to_excel(ARQUIVO, index=False)

def proximo_nr(df):
    if len(df)==0:
        return 1
    return int(df["NR"].max()+1)

def transportar_pendentes(df, mes_atual):
    
    df["DATA VENC"] = pd.to_datetime(df["DATA VENC"])
    
    pendentes = df[
        (df["DATA PAGTO"].isna()) &
        (df["DATA VENC"].dt.month < mes_atual)
    ]

    for i,row in pendentes.iterrows():
        nova_linha = row.copy()
        nova_linha["DATA VENC"] = datetime(datetime.now().year, mes_atual, row["DATA VENC"].day)
        df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)

    return df

iniciar_planilha()

st.title("💰 Sistema de Controle Financeiro")

df = carregar_dados()

menu = st.sidebar.selectbox(
"Menu",
[
"Dashboard",
"Lançar Despesa",
"Registrar Pagamento",
"Registrar Rendimento",
"Lista de Contas"
]
)

# DASHBOARD

if menu == "Dashboard":

    st.header("Resumo Financeiro")

    total_despesas = df["VALOR"].sum()
    total_pago = df["VALOR PAGO"].sum()
    total_rendimento = df["RENDIMENTO"].sum()

    saldo = total_rendimento - total_pago

    col1,col2,col3,col4 = st.columns([4,3,3,3])

    col1.metric("Total Despesas", f"R$ {total_despesas:,.2f}")
    col2.metric("Total Pago", f"R$ {total_pago:,.2f}")
    col3.metric("Rendimentos", f"R$ {total_rendimento:,.2f}")
    col4.metric("Saldo", f"R$ {saldo:,.2f}")

# NOVA DESPESA

if menu == "Lançar Despesa":

    st.header("Nova Despesa")

    tipo = st.selectbox("Tipo",["CONTA","PRESTAÇÃO","CONDOMINIO","IPTU","DESPESAS"])

    descricao = st.text_input("Descrição")

    valor = st.number_input("Valor",0.0)

    data_venc = st.date_input("Data de vencimento")

    boleto = st.text_input("Código boleto")

    pix = st.text_input("Chave PIX")

    if st.button("Salvar Despesa"):

        nova = {
        "NR":proximo_nr(df),
        "QTD":1,
        "TIPO":tipo,
        "DESCRIÇÃO":descricao,
        "VALOR":valor,
        "DATA VENC":data_venc,
        "CODIGO BOLETO":boleto,
        "COD. PIX":pix,
        "DATA PAGTO":None,
        "VALOR PAGO":0,
        "PAGO COM":"",
        "RENDIMENTO":0,
        "DATA":None
        }

        df = pd.concat([df,pd.DataFrame([nova])],ignore_index=True)

        salvar_dados(df)

        st.success("Despesa cadastrada")

# PAGAMENTO

if menu == "Registrar Pagamento":

    st.header("Registrar Pagamento")

    pendentes = df[df["DATA PAGTO"].isna()]

    id_conta = st.selectbox(
        "Conta",
        pendentes["DESCRIÇÃO"]
    )

    pagamento = st.date_input("Data pagamento")

    forma = st.selectbox(
        "Forma pagamento",
        ["PIX","BOLETO","CARTÃO","TRANSFERÊNCIA"]
    )

    if st.button("Registrar"):

        idx = df[df["DESCRIÇÃO"]==id_conta].index[0]

        df.loc[idx,"DATA PAGTO"] = pagamento
        df.loc[idx,"VALOR PAGO"] = df.loc[idx,"VALOR"]
        df.loc[idx,"PAGO COM"] = forma

        salvar_dados(df)

        st.success("Pagamento registrado")

# RENDIMENTO

if menu == "Registrar Rendimento":

    st.header("Registrar rendimento")

    valor = st.number_input("Valor rendimento",0.0)

    data = st.date_input("Data")

    if st.button("Salvar"):

        nova = {
        "NR":proximo_nr(df),
        "QTD":1,
        "TIPO":"RENDIMENTO",
        "DESCRIÇÃO":"Rendimento",
        "VALOR":0,
        "DATA VENC":None,
        "CODIGO BOLETO":"",
        "COD. PIX":"",
        "DATA PAGTO":None,
        "VALOR PAGO":0,
        "PAGO COM":"",
        "RENDIMENTO":valor,
        "DATA":data
        }

        df = pd.concat([df,pd.DataFrame([nova])],ignore_index=True)

        salvar_dados(df)

        st.success("Rendimento salvo")

# LISTA

if menu == "Lista de Contas":

    st.header("Contas registradas")

    st.dataframe(df)