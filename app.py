import streamlit as st
from PIL import Image
import numpy as np
from collections import Counter
from google import genai
from sklearn.cluster import KMeans

st.set_page_config(page_title="ColorDNA", page_icon="🎨", layout="centered")

st.markdown("""
<style>
.stApp {
    background: radial-gradient(1200px at 50% 0%, #1a1f2b 0%, #0e1117 40%);
    color: #f5f5f5;
    font-family: 'Inter', sans-serif;
}
.block-container {
    max-width: 520px !important;
    padding-top: 2.5rem;
}
h1 { text-align: center; font-weight: 700; margin-bottom: 0.2em; }
p { text-align: center; color: #b0b0b0; }
.title-gradient {
    text-align: center;
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(120deg, #ff5f6d, #ffc371, #7f7fd5, #86fde8);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: gradientFlow 8s ease infinite;
}
@keyframes gradientFlow {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
div[data-testid="stTextInput"] label {
    color: #e0e0e0 !important;
    font-size: 0.85em;
}
div[data-testid="stTextInput"] div[data-baseweb="input"] {
    background-color: rgba(255, 255, 255, 0.05) !important;
    border: none !important;
    box-shadow: none !important;
    border-radius: 12px !important;
    color: white !important;
}
div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within {
    box-shadow: none !important;
    outline: none !important;
    background-color: rgba(255, 255, 255, 0.08) !important;
}
section[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.03);
    border: 1px dashed rgba(255,255,255,0.15);
    border-radius: 16px;
}
.footer {
    text-align: center;
    padding: 3rem 0 1rem 0;
    color: #666;
    font-size: 0.75em;
}
.ai-box {
    background: rgba(255, 255, 255, 0.05);
    padding: 25px;
    border-radius: 10px;
    border-left: 3px solid #7f7fd5;
    margin-top: 20px;
    text-align: left !important;
}
.ai-box p, .ai-box h3, .ai-box li, .ai-box ul {
    text-align: left !important;
    color: #e0e0e0 !important;
}
.ai-box ul {
    margin-left: 20px;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Configuración")
    api_key = st.text_input("Clave de API de Google GenAI", type="password")

def extract_colors(image, k=6):
    image = image.resize((150, 150))
    img_array = np.array(image)
    pixels = img_array.reshape(-1, 3)
    
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(pixels)
    
    colors = kmeans.cluster_centers_.astype(int)
    labels = kmeans.labels_
    
    counts = Counter(labels)
    total_pixels = len(pixels)
    
    sorted_indices = sorted(counts, key=counts.get, reverse=True)
    sorted_colors = [tuple(colors[i]) for i in sorted_indices]
    sorted_counts = [counts[i] for i in sorted_indices]
    
    return sorted_colors, sorted_counts, total_pixels

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])

st.markdown('<h1 class="title-gradient">ColorDNA</h1>', unsafe_allow_html=True)
st.write("Análisis cromático & IA.")

uploaded_file = st.file_uploader("", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    
    with st.spinner("Analizando espectro con ML..."):
        n_colors = 6
        centroids, counts, total_pixels = extract_colors(img, k=n_colors)
        
        hex_colors = [rgb_to_hex(c) for c in centroids]
        percentages = [(c / total_pixels) * 100 for c in counts]

    st.image(img, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Paleta de Colores")

    cols = st.columns(n_colors) 
    for i, hex_c in enumerate(hex_colors):
        if i < len(cols):
            with cols[i]:
                st.markdown(f"""
                    <div style="background-color:{hex_c}; height: 50px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);"></div>
                    <p style="font-family:monospace; margin-top:5px; font-size: 0.7em; color: #888;">{hex_c.upper()}</p>
                    """, unsafe_allow_html=True)

    st.divider()

    st.subheader("Distribución Cromática")
    
    gradient_parts = []
    current_deg = 0
    for color, pct in zip(hex_colors, percentages):
        deg = (pct / 100) * 360
        gradient_parts.append(f"{color} {current_deg}deg {current_deg + deg}deg")
        current_deg += deg
    
    conic_gradient = ", ".join(gradient_parts)
    
    st.markdown(f"""
        <div style="display: flex; justify-content: center; margin-top: 20px;">
            <div style="
                width: 200px; 
                height: 200px; 
                border-radius: 50%; 
                background: conic-gradient({conic_gradient});
                position: relative;
                box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
                <div style="
                    position: absolute; 
                    top: 50%; left: 50%; 
                    transform: translate(-50%, -50%); 
                    width: 90px; height: 90px; 
                    background: #151922; 
                    border-radius: 50%;">
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.subheader("Interpretación IA")

    if api_key:
        if st.button("Analizar estilo con Gemini"):
            try:
                client = genai.Client(api_key=api_key)
                prompt = f"""
                Actúa como un experto en teoría del color.
                Paleta: {', '.join(hex_colors)}.
                
                Genera una respuesta SOLO en formato HTML simple (sin bloque de código).
                Usa estas etiquetas para estructurar: <h3>, <p>, <b> (negrita), <ul>, <li>.
                
                Contenido:
                1. <h3>Nombre creativo para la paleta</h3>
                2. <p><b>Vibe:</b> Descripción emocional corta.</p>
                3. <p><b>Análisis:</b></p> <ul><li>Punto clave 1</li><li>Punto clave 2</li></ul>
                4. <p><b>Usos recomendados:</b></p> <ul><li>Uso 1</li><li>Uso 2</li></ul>
                
                Sé conciso, poético y elegante.
                """

                with st.spinner("Consultando al oráculo de colores..."):
                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=[img, prompt]
                    )
                    
                    clean_text = response.text.replace("```html", "").replace("```", "")
                    st.markdown(f'<div class="ai-box">{clean_text}</div>', unsafe_allow_html=True)
            
            except Exception as e:
                st.error(f"Error de conexión con la IA: {e}")
    else:
        st.warning("Introduce tu API Key en la barra lateral para desbloquear la IA.")

else:
    st.info("Sube una imagen para extraer su ADN.")

st.markdown("""
    <div class="footer">
        <hr>
        <p>© 2026 COLORDNA STUDIO • AI ENHANCED</p>
    </div>
    """, unsafe_allow_html=True)