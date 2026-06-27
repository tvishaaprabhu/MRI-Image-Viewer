import streamlit as st
import pandas as pd
from PIL import Image

# Set the page to be wider so the side-by-side layout looks better
st.set_page_config(layout="wide")

st.title("My Streamlit Image Viewer")

# Create a file uploader widget
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png", "webp"])

if uploaded_file is not None:
    # Open the image using Pillow
    img = Image.open(uploaded_file)
    
    # Create two columns. The [3, 2] ratio makes the image column slightly wider than the table column.
    col1, col2 = st.columns([3, 2])
    
    # --- LEFT COLUMN: THE IMAGE ---
    with col1:
        st.image(img, caption='Uploaded Image', use_column_width=True)
        
    # --- RIGHT COLUMN: THE TABLE ---
    with col2:
        st.subheader("Image Summary")
        
        # Extract the details
        image_name = uploaded_file.name
        width, height = img.size
        
        # Organize the data into a dictionary
        data = {
            "Attribute": ["File Name", "Width (pixels)", "Height (pixels)", "Format"],
            "Value": [image_name, width, height, img.format]
        }
        
        # Convert it to a Pandas DataFrame for a clean Streamlit table
        df = pd.DataFrame(data)
        
        # Display the table (hide the index column for a cleaner look)
        st.dataframe(df, hide_index=True, use_container_width=True)

else:
    st.info("Please upload an image to see it displayed here.")
