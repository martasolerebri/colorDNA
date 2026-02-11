import streamlit as st
from PIL import Image
import numpy as np
from collections import Counter
from google import genai
from sklearn.cluster import KMeans

st.set_page_config(page_title="ColorDNA", page_icon="🎨", layout="centered")
st.markdown(f"<style>{open('style.css').read()}</style>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Configuración")
    api_key = st.text_input("API Key de Google", type="password")

def extraer_colores(imagen, num_colores=6):
    img_pequeña = imagen.resize((150, 150))
    pixeles = np.array(img_pequeña).reshape(-1, 3)
    
    kmeans = KMeans(n_clusters=num_colores, random_state=42)
    kmeans.fit(pixeles)
    
    colores = kmeans.cluster_centers_.astype(int)
    etiquetas = kmeans.labels_
    conteo = Counter(etiquetas)
    
    indices_ordenados = sorted(conteo, key=conteo.get, reverse=True)
    colores_finales = [tuple(colores[i]) for i in indices_ordenados]
    cantidades = [conteo[i] for i in indices_ordenados]
    
    return colores_finales, cantidades

def rgb_a_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])

st.markdown('<h1 class="title-gradient">ColorDNA</h1>', unsafe_allow_html=True)
st.write("Sube una imagen y analiza sus colores")

archivo = st.file_uploader("Selecciona una imagen", type=["jpg", "png", "jpeg"])

if archivo:
    img = Image.open(archivo)
    st.image(img, use_container_width=True)
    
    colores, cantidades = extraer_colores(img)
    total = sum(cantidades)
    hexs = [rgb_a_hex(c) for c in colores]
    porcentajes = [(cnt/total)*100 for cnt in cantidades]
    
    st.subheader("Paleta extraída")
    cols = st.columns(6)
    for i, hex_color in enumerate(hexs):
        with cols[i]:
            st.markdown(f'<div style="background:{hex_color}; height:60px; border-radius:8px;"></div>', 
                       unsafe_allow_html=True)
            st.caption(hex_color.upper())
    
    st.divider()
    st.subheader("Distribución")
    
    grados_actual = 0
    partes = []
    for color, pct in zip(hexs, porcentajes):
        grados = (pct/100) * 360
        partes.append(f"{color} {grados_actual}deg {grados_actual+grados}deg")
        grados_actual += grados
    
    gradiente = ", ".join(partes)
    st.markdown(f'''
        <div style="width:200px; height:200px; margin:auto; border-radius:50%; 
                    background:conic-gradient({gradiente}); box-shadow:0 5px 20px rgba(0,0,0,0.3);">
        </div>
    ''', unsafe_allow_html=True)
    
    st.divider()
    
    if api_key and st.button("Analizar con IA"):
        prompt = f"Analiza esta paleta de colores {hexs}. Dame un nombre creativo, el vibe que transmite y para qué se podría usar. Responde en HTML simple con <h3>, <p> y <ul>."
        
        try:
            client = genai.Client(api_key=api_key)
            respuesta = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[img, prompt]
            )
            texto = respuesta.text.replace("```html", "").replace("```", "")
            st.markdown(texto, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error: {e}")
    elif not api_key:
        st.info("Añade tu API key para análisis con IA")

else:
    st.info("Sube una imagen para empezar")