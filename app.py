import streamlit as st
from PIL import Image
 
img = st.file_uploader("Upload MRI image", type=["jpg", "jpeg", "png"])
 
if img is not None:
    mri = Image.open(img)
    st.image(mri)
    st.write(f"Size: {image.size[0]} x {image.size[1]} px")
    st.write(f"Mode: {image.mode}")
    st.write(f"Format: {image.format}")
 
