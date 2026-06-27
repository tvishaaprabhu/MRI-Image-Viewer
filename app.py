import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import cv2
import io
import pydicom
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("My Streamlit Image Viewer")

# --- SECTION 1: DATA UPLOADING ---
st.header("1. Upload Image")
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png", "webp", "dcm"])

if uploaded_file is not None:
    if uploaded_file.name.endswith(".dcm"):
        dicom = pydicom.dcmread(uploaded_file)
        img_array = dicom.pixel_array.squeeze()
        img_array = cv2.normalize(img_array, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        format_label = "DICOM"
        width, height = img_array.shape[1], img_array.shape[0]
    else:
        img = Image.open(uploaded_file)
        img_array = np.array(img.convert("L")).squeeze()
        format_label = img.format
        width, height = img.size

    st.subheader("Image Summary")
    data = {
        "Attribute": ["File Name", "Width (pixels)", "Height (pixels)", "Format"],
        "Value": [uploaded_file.name, width, height, format_label]
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
        st.image(img_array, use_container_width=True)
    with col2:
        st.subheader("Processed")
        st.image(processed, use_container_width=True)

    st.divider()

    # --- SECTION 5: K-MEANS CLUSTERING ---
    st.header("5. K-Means Clustering")
    k = st.slider("Number of clusters (K)", min_value=2, max_value=20, value=10)
    run_kmeans = st.button("Run K-Means")

    if run_kmeans:
        with st.spinner("Running K-Means..."):
            pixel_list = processed.reshape((-1, 1)).astype(np.float32)
            km = KMeans(n_clusters=k, init='k-means++', n_init=10, random_state=42)
            labels = km.fit_predict(pixel_list)
            segmented_img = labels.reshape(processed.shape)

            fig, ax = plt.subplots(figsize=(10, 8))
            im = ax.imshow(segmented_img, cmap='nipy_spectral')
            plt.colorbar(im, ax=ax, label='Cluster ID')
            ax.set_title(f"KMeans Anatomical Mapping (K={k})", fontsize=16)
            ax.axis('off')
            st.pyplot(fig)

    st.divider()

    # --- SECTION 6: DOWNLOAD ---
    st.header("6. Download Processed Image")
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
