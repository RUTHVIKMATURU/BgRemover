import streamlit as st
from rembg import remove
from PIL import Image
from io import BytesIO
import os
import traceback
import time

st.set_page_config(layout="wide", page_title="Image Background Remover")

st.title("📷 Image Background Remover")
st.write(
    "Upload an image and we'll remove the background for you using the [rembg](https://github.com/danielgatis/rembg) library. "
    "Thanks to open-source contributions! :sparkles:"
)

st.sidebar.title("📤 Upload and Download")

# --- Constants ---
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_IMAGE_SIZE = 2000  # Max dimension to prevent overload

# --- Helper Functions ---
def convert_image(img):
    """Convert PIL Image to bytes"""
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def resize_image(image, max_size):
    """Resize while maintaining aspect ratio"""
    width, height = image.size
    if width <= max_size and height <= max_size:
        return image
    if width > height:
        new_width = max_size
        new_height = int(height * (max_size / width))
    else:
        new_height = max_size
        new_width = int(width * (max_size / height))
    return image.resize((new_width, new_height), Image.LANCZOS)

@st.cache_data
def process_image(image_bytes):
    try:
        image = Image.open(BytesIO(image_bytes)).convert("RGBA")
        resized = resize_image(image, MAX_IMAGE_SIZE)
        result = remove(resized)
        return image, result
    except Exception as e:
        st.error(f"Image processing error: {str(e)}")
        return None, None

def fix_image(uploaded_file):
    try:
        start = time.time()
        progress = st.sidebar.progress(0)
        status = st.sidebar.empty()

        status.text("🔄 Reading image...")
        progress.progress(10)

        image_bytes = uploaded_file.getvalue()
        status.text("⚙️ Processing image...")
        progress.progress(30)

        original, removed = process_image(image_bytes)
        if original is None or removed is None:
            return

        progress.progress(90)
        status.text("📸 Displaying result...")

        col1, col2 = st.columns(2)
        col1.image(original, caption="Original Image", use_container_width=True)
        col2.image(removed, caption="Background Removed", use_container_width=True)

        st.sidebar.download_button(
            label="⬇️ Download Output (PNG)",
            data=convert_image(removed),
            file_name="removed_background.png",
            mime="image/png"
        )

        progress.progress(100)
        status.text(f"✅ Completed in {time.time() - start:.2f} seconds")

    except Exception as e:
        st.error("An unexpected error occurred.")
        st.sidebar.error("⚠️ Processing failed.")
        print(traceback.format_exc())

# --- UI: File Upload ---
uploaded = st.sidebar.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

# --- Info ---
with st.sidebar.expander("ℹ️ Info & Tips"):
    st.write("""
    - Supported: PNG, JPG, JPEG
    - Max file size: 10MB
    - Large images are automatically resized
    - Output will be a transparent PNG
    """)

if uploaded:
    if uploaded.size > MAX_FILE_SIZE:
        st.error("File too large. Please upload an image smaller than 10MB.")
    else:
        fix_image(uploaded)
else:
    st.info("👈 Upload an image from the sidebar to begin.")
