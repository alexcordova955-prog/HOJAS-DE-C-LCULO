
import streamlit as st
import os
import math
from PIL import Image
st.set_page_config(layout="wide")
#Para ejecutar usar en consola: streamlit run conexdiag.py
#Estilo CSS para fondo oscuro
st.markdown(
    """
    <style>
    body {
        background-color: #d3d3d3;
        color: white;
    }
    .stApp {
        background-color: #d3d3d3;
    }
    </style>
    """, unsafe_allow_html=True
)
st.markdown("<h1 style='color: blue; font-size: 40px;'>Cálculos de Conexión Metálica Soldada-Apernada</h1>", unsafe_allow_html=True)
st.title("Cálculos de Conexión Metálica Soldada-Apernada de diagonales")
def custom_title(text, color="blue", font_size="20px"):
    """Función para cambiar el estilo de los títulos de forma fácil."""
    st.markdown(f"<h1 style='color: {color}; font-size: {font_size};'>{text}</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([10, 15, 15])

# Funciones auxiliares
def calcular_pernos(dp, Fu, T):
    """Calcula el número de pernos necesarios"""
    Ap = 3.1416 / 4 * (dp * 2.54) ** 2  # Área del perno en cm²
    Vdesign = 0.75 * Ap * Fu / 1000     # Resistencia del perno en toneladas
    return T / Vdesign, Ap, Vdesign

def calcular_bloque_corte(dp, Fya, Fua, twp, Npf, Npc, Sepint, Sepext, bwp, Sepextv):
    """Calcula áreas y resistencia del bloque de corte"""
    Anv = (twp * (Sepext + (Npc - 1) * Sepint) - (Npc-1) * (dp * 25.4 + 1.5)*twp - 0.5*(dp*25.4+1.5)*twp) * Npf / 100
    Ant = (twp * (bwp - (bwp - 2 * Sepextv)) * 1/2 - 1/2 * (dp * 25.4 + 1.5) * twp) * 2 / 100
    #Ant = ((bwp - 2 * Sepextv) -(1)*(dp*25.4+1.5))*twp/100

    Agv = twp * (Sepext + (Npc - 1) * Sepint) * Npf / 100
    Agt = twp * (bwp - (bwp - 2 * Sepextv)) * 2 / 2 / 100
    Rnc = min(0.6 * Fua * Anv + Fya * Agt, 0.6 * Fya * Agv + Fua * Ant)
    return Anv, Ant, Agv, Agt, 0.75 * Rnc / 1000  # Retorna también Rncf en toneladas

def calcular_aplastamiento_desgarre(dp, twp, Fu, Npf, Npc, Sepext, Sepint):
    """Calcula la resistencia al aplastamiento y desgarre"""
    Raplas1p = 0.75 * (2.4 * dp * 25.4) * twp * Fu / 1000 / 100
    Raplastotal = Npf * Npc * Raplas1p
    Lce = Sepext - 0.5 * (dp * 25.4 + 1.5)
    Lci = Sepint - (dp * 25.4 + 1.5)
    R1desgext = 0.75 * (1.2 * Lce * twp * Fu) / 1000 / 100
    R2desgint = 0.75 * (1.2 * Lci * twp * Fu) / 1000 / 100
    Rdesg = Npf * R1desgext + (Npc - 1) * Npf * R2desgint
    return Raplastotal, Rdesg, R1desgext, R2desgint

def calcular_capacidad_tension(twp, bwp, Fya):
    """Calcula la resistencia a tensión"""
    return 0.9 * twp * bwp * Fya / 1000 / 100  # Retorna en toneladas

# Datos de entrada
with col1:
    st.header("Datos de entrada")

    dp = st.number_input("Diámetro de perno (in)", value=0.875, min_value=0.1, format="%.3f")
    Fu = st.number_input("Resistencia última a corte de pernos (kgf/cm²)", value=3370.0, min_value=0.1)
    T = st.number_input("Fuerza axial (tonnef)", value=50.0, min_value=0.1)
    Npf = st.number_input("Numero de filas de pernos", value=2.0, min_value=1.0)
    Npc = st.number_input("Numero de columnas de perno", value=3.0, min_value=1.0)
    Sepintv = st.number_input("Separación interna vertical (mm)", value=140.0, min_value=0.1)
    Sepint = st.number_input("Separación interna horizontal de pernos (en mm)", value=65.0, min_value=0.1)
    Sepext = st.number_input("Separación externa horizontal de pernos al borde (en mm)", value=40.0, min_value=0.1)
    Sepextv = st.number_input("Separación externa vertical de pernos (en mm)", value=80.0, min_value=0.1)
    Fya = st.number_input("Resistencia de fluencia de acero (kgf/cm²)", value=2480.0, min_value=0.1)
    Fua = st.number_input("Resistencia de última de acero (kgf/cm²)", value=3450.0, min_value=0.1)
    bwp = st.number_input("Ancho de placa (mm)", value=300.0, min_value=0.1)
    twp = st.number_input("Espesor de placa (mm)", value=20.0, min_value=0.1)
    twpg = st.number_input("Espesor de placa gusset(mm)", value=20.0, min_value=0.1)
    L1 = st.number_input("Longitud 1 de placa gusset (mm)", value=130.0, min_value=0.1)
    L2 = st.number_input("Longitud 2 de placa gusset (mm)", value=350.0, min_value=0.1)
    Lc = st.number_input("Anho equivalente de placa gusset (mm)", value=240.0, min_value=0.1)
    E = st.number_input("Modulo de elasticidad (Pa)", value=2000000.0, min_value=2000000.0)

# Resultados
with col2:

    st.header("Resultados de placa de conexion")
    # Cálculo de pernos
    Np, Ap, Vdesign = calcular_pernos(dp, Fu, T)
    st.subheader("Número de pernos J3-1")
    st.write(f"Area de pernos: {Ap:.2f} cm²")
    st.write(f"Número necesario: {Np:.2f}")

    # Cálculo de bloque de corte
    Anv, Ant, Agv, Agt, Rncf = calcular_bloque_corte(dp, Fya, Fu, twp, Npf, Npc, Sepint, Sepext, bwp, Sepextv)
    st.subheader("Bloque de corte J4-5")
    st.write(f"Área neta de corte (Anv): {Anv:.2f} cm²")
    st.write(f"Área neta de tensión (Ant): {Ant:.2f} cm²")
    st.write(f"Área grossa de corte (Agv): {Agv:.2f} cm²")
    st.write(f"Área grossa de tensión (Agt): {Agt:.2f} cm²")
    st.write(f"Resistencia: {Rncf:.2f} toneladas")

    # Aplastamiento y desgarre
    Raplastotal, Rdesg, R1desgext, R2desgint = calcular_aplastamiento_desgarre(dp, twp, Fu, Npf, Npc, Sepext, Sepint)
    st.subheader("Aplastamiento J3-6a y desgarre ")
    st.write(f"Resistencia al aplastamiento: {Raplastotal:.2f} toneladas")
    st.write(f"Resistencia al desgarre: {Rdesg:.2f} toneladas")

    # Capacidad a tensión
    Rtp = calcular_capacidad_tension(twp, bwp, Fya)
    st.subheader("Capacidad a tensión")
    st.write(f"Resistencia a tensión: {Rtp:.2f} toneladas")
    # Título de la aplicación
    #mostrar imagen
    st.header("Ilustraciones")
    #st.image("detallediagonal.jpeg", caption="Ilustración de la Conexión", use_container_width=True)




    #PLACA GUSSET
    #Cortante de bloque
    with col3:
        st.header("Resultados de placa gusset")
        #Cálculo de bloque de cortante
        Anvg = (twpg * (Sepext + (Npc - 1) * Sepint) - (Npc-1) * (dp * 25.4 + 1.5)*twpg - 0.5*(dp*25.4+1.5)*twpg) * Npf / 100
        Agvg = twpg * (Sepext + (Npc - 1) * Sepint) * Npf / 100
        #El area neta de tension Ant al igual que el Agt area gruesa de tension cambian, debido a que la sección de falla se d en el gramil, entre dos pernos
        Antg = twpg*(bwp-2*Sepextv)/100 - twpg*(Npf-1)*(dp*25.4+1.5)/100
        Agtg = twpg*(bwp-2*Sepextv)/100
        Rncg = min(0.6 * Fua * Anvg + Fya * Agtg, 0.6 * Fya * Agvg + Fua * Antg)*0.75/1000
        st.subheader("Bloque de cortante")
        st.write(f"El area neta a corte en placa gusset es Anvg: {Anvg:.2f} cm²")
        st.write(f"El area gruesa a corte en placa gusset es Agvg: {Agvg:.2f} cm²")
        st.write(f"El área neta de tensión en placa gusset es Antg: {Antg:.2f} cm²")
        st.write(f"El área gruesa de tensión en placa gusset es Agtg: {Agtg:.2f} cm²")
        st.write(f"La resistencia a cortante en placa gusset es Rncg: {Rncg:.2f} toneladas")

        #FLUENCIA DE SECCIÓN DE WHITMORE
        t1 = (Npc - 1) * Sepint * math.tan(math.radians(30))
        lw = (Npf-1)*Sepintv + 2*t1
        Aggw = lw*twpg/100
        Rnw = 0.9*Aggw*Fya/1000
        st.subheader("Fluencia de sección de Whitmore")
        st.write(f"El area gruesa de fluencia es Aggw: {Aggw:.2f} cm²")
        st.write(f"La resistencia a fluencia en sección de Whitmore es Rnw: {Rnw:.2f} toneladas")

        #RESISTENCIA A CORTANTE VERTICAL
        Rnv = 0.9*0.6*(L1+L2)*twpg*Fya/1000/100
        st.subheader("Resistencia a cortante vertical")
        st.write(f"La resistencia a cortante vertical es Rnv: {Rnv:.2f} toneladas")

        #RESISTENCIA A COMPRESIÓN DE LA PLACA GUSSET
        Ag = Lc*twpg
        Ix = (Lc*twpg**3)/12
        rx = math.sqrt(Ix/Ag)
        Rel = 1*L2/rx
        fe = 3.1416**2*E/(Rel**2)
        Relac = Fya/fe
        if Relac <= 4.71 * (E / Fya) ** 0.5:
            Fcr = 0.658 ** Relac * Fya
        else:
            Fcr = 0.877 * fe

        if Rel <= 25:
            Pnc = 0.9*Fya*Ag/1000/100
        else:
            Pnc = 0.9*Fcr*Ag/1000/100

        st.subheader("Resistencia a compresión de la placa gusset")
        st.write(f"El area de la placa gusset es Ag: {Ag:.2f} cm²")
        st.write(f"La resistencia critica fcr es: {Fcr:.2f} toneladas")
        st.write(f"La relacion kl/r es: {Rel:.2f} toneladas")
        st.write(f"La resistencia a compresión de la placa gusset es Pnc: {Pnc:.2f} toneladas")

        #ILUSTRACIONES
        st.header("Ilustraciones")

        st.image("diagonalnv.png", caption="Ilustración del cálculo", use_container_width=True)

        #PRESENTACION EN LATEX DE LOS CALCULOS
        st.header("Presentación en LaTeX")
        st.subheader("Numero de pernos J3-1")
        st.latex(rf"Ap = \frac{{3.1416}}{{4}} \times ({dp} \times 2.54)^2= {Ap:.2f} cm^2")
        st.latex(rf"Vdesign = 0.75 \times Ap \times \frac{{Fu}}{{1000}} = {Vdesign:.2f} toneladas")
        st.latex(rf"Np = \frac{{T}}{{Vdesign}} = {Np:.2f}")

        st.subheader("Bloque de corte J4-5")
        st.latex(rf"Anv = (twp \times (Sepext + (Npc -1) \times Sepint) - (Npc-1) \times (dp \times 25.4 + 1.5) \times twp - 0.5\times (dp \times 25.4 + 1.5) \times twp) \times Npf / 100 = {Anv:.2f} cm^2")
        st.latex(rf"""
A_{{nv}} = \left( {twp} \cdot \left( {Sepext} + ({Npc} - 1) \cdot {Sepint} \right) - 
({Npc} - 1) \cdot \left( {dp * 25.4:.2f} + 1.5 \right) \cdot {twp} - 
0.5 \cdot \left( {dp * 25.4:.2f} + 1.5 \right) \cdot {twp} \right) \cdot \frac{{{Npf}}}{{100}} = {Anv:.2f}
""")
        st.latex(rf"Ant = (twp \times (bwp - (bwp - 2 \times Sepextv)) \times 1/2 - 1/2 \times (dp \times 25.4 + 1.5) \times twp) \times 2 / 100 = {Ant:.2f} cm^2")
        st.latex(rf"""
A_{{nt}} = \left( {twp} \cdot \left( {bwp} - ({bwp} - 2 \times {Sepextv}) \right) \cdot \frac{{1}}{{2}} - 
1/2 \cdot \left( {dp * 25.4:.2f} + 1.5 \right) \cdot {twp} \right) \times 2 / 100 = {Ant:.2f}
""")
        st.latex(rf"Agv = twp \times (Sepext + (Npc -1) \times Sepint) \times Npf / 100 = {Agv:.2f} cm^2")
        st.latex(rf"""
A_{{gv}} = \left( {twp} \cdot \left( {Sepext} + ({Npc} - 1) \cdot {Sepint} \right) \right) \cdot \frac{{{Npf}}}{{100}} = {Agv:.2f}
""")
        st.latex(rf"Agt = twp \times (bwp - (bwp - 2 \times Sepextv)) \times 2 / 100 = {Agt:.2f} cm^2")
        st.latex(rf"""
A_{{gt}} = \left( {twp} \cdot \left( {bwp} - ({bwp} - 2 \times {Sepextv}) \right) \right) \times 2 / 100 = {Agt:.2f}    
""")
        st.latex(rf"Rncf = min(0.6 \times Fu \times Anv + Fya \times Agt, 0.6 \times Fya \times Agv + Fu \times Ant) = {Rncf:.2f} toneladas")
        st.latex(rf"""
R_{{ncf}} = \min \left( 0.6 \times {Fu} \times {Anv} + {Fya} \times {Agt}, 0.6 \times {Fya} \times {Agv} + {Fu} \times {Ant} \right) = {Rncf:.2f}
""")

        st.subheader("Aplastamiento J3-6a y desgarre")
        st.latex(rf"Raplastotal = 0.75 \times 2.4 \times dp \times 25.4 \times twp \times Fu / 1000 / 100 = {Raplastotal:.2f} toneladas")
        st.latex(rf"""
R_{{aplast}} = 0.75 \times 2.4 \times {dp} \times 25.4 \times {twp} \times {Fu} / 1000 / 100 = {Raplastotal:.2f}
""")
        st.latex(rf"Rdesg = Npf \times R1desgext + (Npc - 1) \times Npf \times R2desgint = {Rdesg:.2f} toneladas")
        st.latex(rf"""
R_{{desg}} = {Npf} \times {R1desgext} + ({Npc} - 1) \times {Npf} \times {R2desgint} = {Rdesg:.2f}
""")
        st.latex(rf"Rtp = twp \times bwp \times Fya / 1000 = {Rtp:.2f} toneladas")
        st.latex(rf"""
R_{{tp}} = {twp} \times {bwp} \times {Fya} / 1000 = {Rtp:.2f}   
""")

        st.subheader("Capacidad a tensión")
        st.latex(rf"Rtp = twp \times bwp \times Fya / 1000 = {Rtp:.2f} toneladas")
        st.latex(rf"""
R_{{tp}} = {twp} \times {bwp} \times {Fya} / 1000 = {Rtp:.2f}   
""")


        
        
        
        
        
        



       

   








 
        
    




