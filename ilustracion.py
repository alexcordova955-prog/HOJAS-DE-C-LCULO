import streamlit as st

st.write("Calculo")
col1, col2 = st.columns([10, 15])
def areaperno(dp,Fu):
    Ap =   3.1416 / 4 * (dp * 2.54) ** 2  # Área del perno en cm²
    return Ap

with col1:
    st.subheader("Datos de entrada")
    dp = st.number_input("Diametro del perno (mm)", value=8.0, min_value=0.1)
    Fu = st.number_input("Resistencia ultima a corte de pernos Fu (kgf/cm²)", value=3370.0, min_value=0.1)
