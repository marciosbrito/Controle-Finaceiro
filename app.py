import streamlit as st
import pandas as pd
import os

ARQUIVO = "financeiro_simples.xlsx"

st.set_page_config(layout="wide")
st.title("📊 Controle Financeiro")

# ==============================
# BASE
# ==============================
if os.path.exists(ARQUIVO):
    df = pd.read_excel(ARQUIVO)
else:
    df = pd.DataFrame(columns=[
        "DATA", "DESCRICAO", "TIPO", "VALOR", "PAGO"
    ])

# tratamento
df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")
df["VALOR"] = pd.to_numeric(df["VALOR"], errors="coerce").fillna(0)

if "PAGO" not in df.columns:
    df["PAGO"] = False

# ==============================
# LANÇAMENTO
# ==============================
st.subheader("➕ Novo lançamento")

c1, c2, c3, c4 = st.columns(4)

data = c1.date_input("Data")
descricao = c2.text_input("Descrição")
tipo = c3.selectbox("Tipo", ["rendimento", "despesa"])
valor = c4.number_input("Valor", min_value=0.0)

pago = st.checkbox("Já foi pago?")

if st.button("Salvar"):
    novo = pd.DataFrame([{
        "DATA": data,
        "DESCRICAO": descricao,
        "TIPO": tipo,
        "VALOR": valor,
        "PAGO": pago
    }])

    df = pd.concat([df, novo], ignore_index=True)
    df.to_excel(ARQUIVO, index=False)

    st.success("Lançamento salvo!")
    st.rerun()

# ==============================
# FILTRO POR MÊS
# ==============================
st.subheader("📅 Selecionar mês")

df["MES"] = df["DATA"].dt.to_period("M")
meses = df["MES"].dropna().unique()

if len(meses) > 0:
    mes_sel = st.selectbox("Mês", meses)
else:
    mes_sel = None

# definir df_mes
if mes_sel:
    df_mes = df[df["MES"] == mes_sel]
else:
    df_mes = df



# ==============================
# LISTA COM BAIXA
# ==============================
st.subheader("📋 Lançamentos")

edited_df = st.data_editor(df_mes, use_container_width=True)

if st.button("💾 Salvar alterações / dar baixa"):
    df.loc[edited_df.index] = edited_df
    df.to_excel(ARQUIVO, index=False)
    st.success("Atualizado!")
    st.rerun()

# ==============================
# EXCLUIR
# ==============================
st.subheader("🗑️ Excluir")

if not df_mes.empty:
    idx = st.selectbox("Selecione", df_mes.index)

    if st.button("Excluir"):
        df = df.drop(idx).reset_index(drop=True)
        df.to_excel(ARQUIVO, index=False)
        st.warning("Excluído!")
        st.rerun()

# ==============================
# RESUMO (SEPARADO)
# ==============================
st.subheader("📊 Resumo")

# pagos
rendimento_pago = df_mes[(df_mes["TIPO"] == "rendimento") & (df_mes["PAGO"] == True)]["VALOR"].sum()
despesa_paga = df_mes[(df_mes["TIPO"] == "despesa") & (df_mes["PAGO"] == True)]["VALOR"].sum()

# pendentes
rendimento_pendente = df_mes[(df_mes["TIPO"] == "rendimento") & (df_mes["PAGO"] == False)]["VALOR"].sum()
despesa_pendente = df_mes[(df_mes["TIPO"] == "despesa") & (df_mes["PAGO"] == False)]["VALOR"].sum()

# saldo real (só pagos)
saldo_real = rendimento_pago - despesa_paga

# saldo futuro (inclui pendentes)
saldo_previsto = (rendimento_pago + rendimento_pendente) - (despesa_paga + despesa_pendente)

c1, c2, c3, c4 = st.columns(4)

c1.metric("💰 Recebido", f"R$ {rendimento_pago:,.2f}")
c2.metric("💸 Pago", f"R$ {despesa_paga:,.2f}")
c3.metric("📊 Saldo Atual", f"R$ {saldo_real:,.2f}")
c4.metric("📅 Saldo Previsto", f"R$ {saldo_previsto:,.2f}")

st.subheader("📌 Todas as Pendências")

# garantir MES como string válida
df["MES"] = df["MES"].astype(str)

# remover linhas inválidas (NaT, vazio, None)
df_valid = df[
    (df["MES"] != "NaT") &
    (df["MES"] != "None") &
    (df["MES"] != "")
].copy()

# converter para número
df_valid["MES_NUM"] = df_valid["MES"].str.replace("-", "").astype(int)


# mostra pendentes de TODOS os meses
pendentes = df_valid[
    (df_valid["PAGO"] == False)
]

if not pendentes.empty:

    total_pendente = pendentes["VALOR"].sum()

    st.metric("💸 Total em aberto", f"R$ {total_pendente:,.2f}")

    st.dataframe(
        pendentes.sort_values("MES_NUM"),
        use_container_width=True
    )

else:
    st.warning("Nenhuma pendência encontrada")

st.subheader("📊 Resumo Geral")

# já pagos
recebido = df[(df["TIPO"] == "rendimento") & (df["PAGO"] == True)]["VALOR"].sum()
pago = df[(df["TIPO"] == "despesa") & (df["PAGO"] == True)]["VALOR"].sum()

# pendentes
a_receber = df[(df["TIPO"] == "rendimento") & (df["PAGO"] == False)]["VALOR"].sum()
a_pagar = df[(df["TIPO"] == "despesa") & (df["PAGO"] == False)]["VALOR"].sum()

c1, c2, c3, c4 = st.columns(4)

c1.metric("💰 Já Recebido", f"R$ {recebido:,.2f}")
c2.metric("💸 Já Pago", f"R$ {pago:,.2f}")
c3.metric("📤 A Pagar", f"R$ {a_pagar:,.2f}")
c4.metric("📥 A Receber", f"R$ {a_receber:,.2f}")

st.subheader("💰 Situação Financeira")

saldo_real = recebido - pago
saldo_futuro = (recebido + a_receber) - (pago + a_pagar)

c1, c2 = st.columns(2)

c1.metric("💵 Saldo Atual (em conta)", f"R$ {saldo_real:,.2f}")
c2.metric("🔮 Saldo A PAGAR", f"R$ {saldo_futuro:,.2f}")
