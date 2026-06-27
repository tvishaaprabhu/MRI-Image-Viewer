import streamlit as st
from PIL import Image
 
img = st.file_uploader("Upload MRI image", type=["jpg", "jpeg", "png"])
 
if uploaded_file is not None:
    mri = Image.open(img)
    st.image(image)
 
