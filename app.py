import numpy as np
from PIL import Image
import streamlit as st
from google import genai
from collections import Counter
import plotly.graph_objects as go 
from sklearn.cluster import KMeans

st.set_page_config(page_title="ColorDNA", page_icon="🎨", layout="centered")
st.markdown(f"<style>{open('style.css').read()}</style>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Settings")
    api_key = st.text_input("Google API Key", type="password")
    st.info("Get your key at [Google AI Studio](https://aistudio.google.com/)")

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
st.write("Upload an image and analyze its colors")

archivo = st.file_uploader("Select an image", type=["jpg", "png", "jpeg"])

if archivo:
    img = Image.open(archivo)
    st.image(img, use_container_width=True)
    
    colores, cantidades = extraer_colores(img)
    total = sum(cantidades)
    hexs = [rgb_a_hex(c) for c in colores]
    porcentajes = [(cnt/total)*100 for cnt in cantidades]
    
    st.subheader("Extracted Palette")
    cols = st.columns(6)
    for i, hex_color in enumerate(hexs):
        with cols[i]:
            st.markdown(f'<div style="background:{hex_color}; height:60px; border-radius:8px;"></div>', 
                       unsafe_allow_html=True)
            st.caption(hex_color.upper())
    
    st.divider()
    st.subheader("Chromatic Distribution")

    fig = go.Figure(data=[go.Pie(
        labels=hexs,      
        values=cantidades,
        marker=dict(colors=hexs),
        hoverinfo="label+percent", 
        textinfo="none"         
    )])

    fig.update_layout(
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=0, b=0, l=0, r=0),
        height=250,
    )

    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    if api_key and st.button("Analyze with AI"):
        prompt = f"Analyze this color palette {hexs}. Give me a creative name, the vibe it conveys, and what it could be used for. Respond in simple HTML with <h3>, <p> and <ul>."
        
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
        st.info("Add your API key for AI analysis")

else:
    st.info("Upload an image to get started")