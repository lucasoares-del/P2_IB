import pandas as pd
from sqlalchemy import create_engine, text, inspect
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import matplotlib.pyplot as plt
import numpy as np
import plotly.io as pio
import pymc as pm
import arviz as az
import seaborn as sns
import patsy
import streamlit as st
import bambi as bmb
import arviz as az
from bambi import Prior
import base64
import os



user = "data_iesb"
password = "iesb"
host = "bigdata.dataiesb.com"
port = 5432
database = "iesb"
schema = "public"


engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}")

with engine.connect() as conn:
    conn.execute(text(f"SET search_path TO {schema};"))
    conn.commit()
    
    
query = """
SELECT schemaname, tablename
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY schemaname, tablename;
"""
df_tabelas = pd.read_sql(query, engine)
print(df_tabelas)


df = pd.read_sql_table(
    table_name="ed_enem_2024_resultados_amos_per",  #  <-- Nome da tabela aqui
    con=engine,
    schema="public"
)



# Supondo que df seja o seu DataFrame
df = df[df['tp_dependencia_adm_esc'] != 'Não Respondeu  ']

# Criar uma nova coluna 'categoria_dependencia' com base em 'tp_dependencia_adm_esc'
df['categoria_dependencia'] = df['tp_dependencia_adm_esc'].apply(lambda x: 'Pública' if x in ['Federal        ', 'Estadual       ', 'Municipal      '] else 'Privada')

# Selecionar as colunas de interesse
colunas_notas = ['nota_cn_ciencias_da_natureza', 'nota_ch_ciencias_humanas', 'nota_lc_linguagens_e_codigos', 'nota_mt_matematica', 'nota_redacao']
df_notas = df[colunas_notas + ['categoria_dependencia']]

# Estatísticas descritivas para as notas por categoria de dependência administrativa
df_notas.groupby('categoria_dependencia')[colunas_notas].describe()






# Configuração do tema
sns.set_theme(style="darkgrid")

# Configuração da página
st.title("Dashboard de Notas do ENEM por Dependência Administrativa")

# Seletor para categoria de dependência administrativa
categoria_selecionada = st.selectbox("Selecione a Categoria de Dependência Administrativa", ['Pública', 'Privada'])

# Filtrar o DataFrame com base na categoria selecionada
df_filtrado = df_notas[df_notas['categoria_dependencia'] == categoria_selecionada]

# Seletor para a nota
colunas_notas = ['nota_cn_ciencias_da_natureza', 'nota_ch_ciencias_humanas', 'nota_lc_linguagens_e_codigos', 'nota_mt_matematica', 'nota_redacao']
nota_selecionada = st.selectbox("Selecione a Nota", colunas_notas)

# Histograma para a nota selecionada
fig, ax = plt.subplots(figsize=(8, 6))
sns.histplot(df_filtrado[nota_selecionada], bins=20, kde=True, ax=ax)
ax.set_title(f"Histograma de {nota_selecionada} para Escolas {categoria_selecionada}s")
st.pyplot(fig)

# Boxplot comparando as notas das escolas públicas e privadas
fig, ax = plt.subplots(figsize=(8, 6))
sns.boxplot(data=df_notas, x='categoria_dependencia', y=nota_selecionada, ax=ax)
ax.set_title(f"Boxplot de {nota_selecionada} por Categoria de Dependência Administrativa")
st.pyplot(fig)

# Estatísticas descritivas para a nota selecionada
st.write(df_filtrado[nota_selecionada].describe())

# Estatísticas descritivas para a nota selecionada
st.write(df_filtrado[nota_selecionada].describe())

# Seção de PDF
st.markdown("---")
st.header("📄 Relatório de Inferência Bayesiana")

# Caminho do PDF
caminho_pdf = r"C:\Users\lucam\Documents\Python_VS\Bayes\Relatório___Inferência_Bayseana.pdf"

if os.path.exists(caminho_pdf):
    
    # Ler arquivo
    with open(caminho_pdf, "rb") as pdf_file:
        pdf_bytes = pdf_file.read()
    
    # Botão de download
    st.download_button(
        label="📥 Baixar Relatório de Inferência Bayesiana",
        data=pdf_bytes,
        file_name="Relatório_Inferência_Bayesiana.pdf",
        mime="application/pdf"
    )
    
    # Divisor visual
    st.markdown("---")
    
    # Visualizador
    st.subheader("📖 Visualizar Relatório")
    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    
    pdf_viewer = f'''
    <iframe src="data:application/pdf;base64,{base64_pdf}" 
            width="100%" height="700" type="application/pdf">
    </iframe>
    '''
    st.markdown(pdf_viewer, unsafe_allow_html=True)

else:
    st.error("❌ Arquivo PDF não encontrado!")
    st.code(caminho_pdf)