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

def extract_colors(image, num_colors=6):
    small_image = image.resize((150, 150))
    pixels = np.array(small_image).reshape(-1, 3)
    
    kmeans = KMeans(n_clusters=num_colors, random_state=42)
    kmeans.fit(pixels)
    
    colors = kmeans.cluster_centers_.astype(int)
    labels = kmeans.labels_
    counts = Counter(labels)
    
    sorted_indices = sorted(counts, key=counts.get, reverse=True)
    final_colors = [tuple(colors[i]) for i in sorted_indices]
    quantities = [counts[i] for i in sorted_indices]
    
    return final_colors, quantities

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])

st.markdown('<h1 class="title-gradient">ColorDNA</h1>', unsafe_allow_html=True)
st.write("Upload an image and analyze its colors")

uploaded_file = st.file_uploader("Select an image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, use_container_width=True)
    
    colors, quantities = extract_colors(img)
    total = sum(quantities)
    hex_colors = [rgb_to_hex(c) for c in colors]
    
    st.subheader("Extracted Palette")
    cols = st.columns(6)
    for i, hex_color in enumerate(hex_colors):
        with cols[i]:
            st.markdown(f'<div style="background:{hex_color}; height:60px; border-radius:8px;"></div>', 
                       unsafe_allow_html=True)
            st.caption(hex_color.upper())
    
    st.divider()
    st.subheader("Chromatic Distribution")

    fig = go.Figure(data=[go.Pie(
        labels=hexs,      
        labels=hex_colors,      
        values=quantities,
        marker=dict(colors=hex_colors),
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
        prompt = f"Analyze this color palette {hex_colors} as if you were Miranda in the movie The Devil Wears Prada. Give me a creative name and the vibe it conveys. Respond in simple HTML with <h3>, <p> and <ul>."
        
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[img, prompt]
            )
            response_text = response.text.replace("```html", "").replace("```", "")
            st.markdown(response_text, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error: {e}")
    elif not api_key:
        st.info("Add your API key for AI analysis")

else:
    st.info("Upload an image to get started")