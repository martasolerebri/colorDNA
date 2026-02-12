# 🎨 ColorDNA

> Extract and analyze the color palette of any image with AI-powered insights! ColorDNA uses machine learning to identify dominant colors and gives you a Miranda Priestly perspective on your palette. Live demo at: [colorDNA](https://colordna-y9fwfrdkpucua3hbpadxc5.streamlit.app/)

## How to Use

1. **Get your API key** (optional, for AI analysis):
   - Visit [Google AI Studio](https://aistudio.google.com/)
   - Create a new API key
   - Paste it in the sidebar

2. **Upload an image**:
   - Click on "Select an image"
   - Choose a JPG, PNG, or JPEG file

3. **View your palette**:
   - See the 6 dominant colors with hex codes
   - Check the chromatic distribution chart

4. **Get AI insights** (optional):
   - Click "Analyze with AI"
   - Receive a creative name and vibe analysis

## Technologies Used

- **Streamlit** - Web framework for the UI
- **Pillow (PIL)** - Image processing
- **NumPy** - Numerical operations
- **scikit-learn** - K-means clustering algorithm
- **Plotly** - Interactive charts
- **Google Generative AI** - AI-powered palette analysis

## How It Works

1. **Image Processing**: The uploaded image is resized to 150x150 pixels for faster processing
2. **Color Clustering**: K-means algorithm groups similar colors together into 6 clusters 
3. **Palette Extraction**: The most dominant colors from each cluster are selected
4. **Distribution Analysis**: Colors are ranked by frequency in the image and displayed in a pie chart
5. **AI Analysis**: Gemini AI provides insights about the color combination playing the role of Miranda from the Devil Wears Prada
