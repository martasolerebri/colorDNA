import streamlit as st
from PIL import Image
import random
from collections import Counter
from google import genai 

st.set_page_config(page_title="ColorDNA", page_icon="🎨", layout="centered")

st.markdown("""
<style>
/* ---------- Global ---------- */
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

/* ---------- Decoración Título ---------- */
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

/* ---------- Componentes ---------- */
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

/* ---------- ARREGLO: Caja de Respuesta IA ---------- */
.ai-box {
    background: rgba(255, 255, 255, 0.05);
    padding: 25px;
    border-radius: 10px;
    border-left: 3px solid #7f7fd5;
    margin-top: 20px;
    text-align: left !important; /* Forzamos a la izquierda */
}
/* Forzamos que los elementos DENTRO de la caja también vayan a la izquierda */
.ai-box p, .ai-box h3, .ai-box li, .ai-box ul {
    text-align: left !important;
    color: #e0e0e0 !important; /* Texto un poco más claro para leer mejor */
}
.ai-box ul {
    margin-left: 20px; /* Sangría para las listas */
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    api_key = st.text_input("Clave de API de Google GenAI", type="password")

def get_image_data(img, size=(100, 100)):
    """Redimensiona y obtiene píxeles sin usar Numpy explícitamente"""
    img_small = img.resize(size)
    img_small = img_small.convert('RGB')
    return list(img_small.getdata())

def simple_kmeans(pixels, k=6, max_iterations=5):
    """Implementación manual de K-Means ligera"""
    if not pixels:
        return [], []
    
    centroids = random.sample(pixels, k)
    
    for _ in range(max_iterations):
        clusters = [[] for _ in range(k)]
        
        for p in pixels:
            distances = [
                (p[0]-c[0])**2 + (p[1]-c[1])**2 + (p[2]-c[2])**2 
                for c in centroids
            ]
            min_dist_index = distances.index(min(distances))
            clusters[min_dist_index].append(p)
            
        new_centroids = []
        for cluster in clusters:
            if cluster:
                r_mean = sum(p[0] for p in cluster) // len(cluster)
                g_mean = sum(p[1] for p in cluster) // len(cluster)
                b_mean = sum(p[2] for p in cluster) // len(cluster)
                new_centroids.append((r_mean, g_mean, b_mean))
            else:
                new_centroids.append(random.choice(pixels))
        
        if new_centroids == centroids:
            break
        centroids = new_centroids
        
    labels = []
    for p in pixels:
        dists = [(p[0]-c[0])**2 + (p[1]-c[1])**2 + (p[2]-c[2])**2 for c in centroids]
        labels.append(dists.index(min(dists)))
        
    return centroids, labels

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])

st.markdown('<h1 class="title-gradient">ColorDNA</h1>', unsafe_allow_html=True)
st.write("Análisis cromático & Consultoría IA.")

uploaded_file = st.file_uploader("", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    
    with st.spinner("Extrayendo ADN..."):
        pixels = get_image_data(img, size=(75, 75)) 
        
        n_colors = 6
        centroids, labels = simple_kmeans(pixels, k=n_colors)
        
        counts = Counter(labels)
        total_pixels = len(pixels)
        
        sorted_indices = sorted(counts, key=counts.get, reverse=True)
        sorted_centroids = [centroids[i] for i in sorted_indices]
        sorted_counts = [counts[i] for i in sorted_indices]
        
        hex_colors = [rgb_to_hex(c) for c in sorted_centroids]
        percentages = [(c / total_pixels) * 100 for c in sorted_counts]

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
                
                # ARREGLO: Pedimos HTML en lugar de Markdown para evitar problemas dentro del div
                prompt = f"""
                Actúa como un experto en teoría del color.
                Paleta: {', '.join(hex_colors)}.
                
                Genera una respuesta SOLO en formato HTML (sin ```html, sin markdown).
                Usa estas etiquetas para estructurar: <h3>, <p>, <b> (negrita), <ul>, <li>.
                
                Contenido:
                1. <h3>Nombre creativo</h3>
                2. <p><b>Vibe:</b> Descripción emocional.</p>
                3. <p><b>Análisis:</b></p> <ul><li>Punto 1</li><li>Punto 2</li></ul>
                4. <p><b>Usos:</b></p> <ul><li>Uso 1</li><li>Uso 2</li></ul>
                
                Sé conciso y elegante.
                """

                with st.spinner("Consultando al oráculo de colores..."):
                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=[img, prompt]
                    )
                    
                    # Limpieza por si la IA pone bloques de código
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