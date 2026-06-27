import streamlit as st
from PIL import Image
 
uploaded_file = st.file_uploader("Upload MRI image", type=["jpg", "jpeg", "png"])
 
if uploaded_file:
    image = Image.open(uploaded_file)
    col1, col2 = st.columns(2)
    with col1:
        st.image(image)
    with col2:
        st.table({
            "Property": ["Width", "Height", "Mode", "Format", "File Size"],
            "Value": [
                f"{image.size[0]} px",
                f"{image.size[1]} px",
                image.mode,
                image.format or "N/A",
                f"{uploaded_file.size / 1024:.1f} KB"
            ]
        })
 
