import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import cv2
import io

st.set_page_config(layout="wide")
st.title("My Streamlit Image Viewer")

# --- SECTION 1: DATA UPLOADING ---
st.header("1. Upload Image")
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png", "webp"])

if uploaded_file is not None:
    img = Image.open(uploaded_file)
    img_array = np.array(img.convert("L"))

    st.subheader("Image Summary")
    data = {
        "Attribute": ["File Name", "Width (pixels)", "Height (pixels)", "Format"],
        "Value": [uploaded_file.name, img.size[0], img.size[1], img.format]
    }
    df = pd.DataFrame(data)
    st.dataframe(df, hide_index=True, use_container_width=False)

    st.divider()

    # --- SECTION 2: IMAGE PREPROCESSING ---
    st.header("2. Image Preprocessing")
    normalize = st.checkbox("Normalize (0-255)")
    rescale = st.checkbox("Rescale (0-1)")
    equalize = st.checkbox("Histogram Equalization (brain-masked)")
    flip = st.checkbox("Horizontal Flip")
    rotate = st.checkbox("Rotate 90°")

    processed = img_array.copy()

    if normalize:
        processed = cv2.normalize(processed, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    if rescale:
        processed = (processed / 255.0 * 255).astype(np.uint8)

    if equalize:
        processed_eq = processed.copy()
        mask = processed_eq > 15
        brain_pixels = processed_eq[mask]
        brain_eq = cv2.equalizeHist(brain_pixels.reshape(-1, 1))
        processed_eq[mask] = brain_eq.ravel()
        processed = processed_eq

    if flip:
        processed = cv2.flip(processed, 1)

    if rotate:
        processed = cv2.rotate(processed, cv2.ROTATE_90_CLOCKWISE)

    st.divider()

    # --- SECTION 3: DENOISING ---
    st.header("3. Denoising")
    gaussian = st.checkbox("Gaussian Blur")
    median = st.checkbox("Median Filter")
    nlm = st.checkbox("Non-Local Means Denoising")

    if gaussian:
        processed = cv2.GaussianBlur(processed, (5, 5), 0)

    if median:
        processed = cv2.medianBlur(processed, 5)

    if nlm:
        processed = cv2.fastNlMeansDenoising(processed, h=10)

    st.divider()

    # --- SECTION 4: IMAGE COMPARISON ---
    st.header("4. Image Comparison")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Original")
        st.image(img_array, use_column_width=True)
    with col2:
        st.subheader("Processed")
        st.image(processed, use_column_width=True)

    st.divider()

    # --- SECTION 5: DOWNLOAD ---
    st.header("5. Download Processed Image")
    buf = io.BytesIO()
    Image.fromarray(processed).save(buf, format="PNG")
    st.download_button(
        label="Download Processed Image",
        data=buf.getvalue(),
        file_name="processed_" + uploaded_file.name.rsplit(".", 1)[0] + ".png",
        mime="image/png"
    )

else:
    st.info("Please upload an image to see it displayed here.")
