import streamlit as st
from pdf2image import convert_from_bytes
import io
from zipfile import ZipFile, ZIP_DEFLATED
from PIL import Image

# Function to crop an image by removing a percentage from the bottom and right sides
def crop_image(image, width_percentage, height_percentage):
    width, height = image.size
    new_width = int(width * (1 - width_percentage))
    new_height = int(height * (1 - height_percentage))
    return image.crop((0, 0, new_width, new_height))

# Function to resize an image to the desired dimensions
def resize_image(image, desired_width, desired_height):
    return image.resize((desired_width, desired_height))

# Function to create a ZIP file of the resized images and generate a download link
def create_download_zip(images, prefix="pages"):
    zip_buffer = io.BytesIO()
    with ZipFile(zip_buffer, 'a') as zip_file:
        for i, image in enumerate(images, start=1):
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            zip_file.writestr(f"{prefix}_page_{i}.png", img_byte_arr, compress_type=ZIP_DEFLATED)
    zip_buffer.seek(0)
    return zip_buffer

def main():
    st.title("Visioscreen - Carrefour")
    st.subheader("By Visioscreen")

    uploaded_pdfs = st.file_uploader("Upload one or more PDF files", type="pdf", accept_multiple_files=True)

    if uploaded_pdfs:
        desired_width = st.number_input("Enter desired width in pixels", value=600, step=100)
        desired_height = st.number_input("Enter desired height in pixels", value=800, step=100)

        if st.button("Process PDF and Download ZIP"):
            all_images = []
            for uploaded_pdf in uploaded_pdfs:
                uploaded_pdf.seek(0)
                images = convert_from_bytes(uploaded_pdf.read())

                for image in images:
                    # Crop the image by removing 36% of the height and 16% of the width
                    cropped_image = crop_image(image, width_percentage=0.13, height_percentage=0.40)
                    # Resize the cropped image
                    resized_image = resize_image(cropped_image, desired_width, desired_height)
                    all_images.append(resized_image)

            # Create a ZIP file with all the resized images
            zip_buffer = create_download_zip(all_images, "all_pages")
            st.download_button(label="Download all images in ZIP",
                               data=zip_buffer,
                               file_name="all_pages_resized.zip",
                               mime="application/zip")

if __name__ == "__main__":
    st.markdown("""
                    <style>
                    .stActionButton {visibility: hidden;}
                    /* Hide the Streamlit footer */
                    .reportview-container .main footer {visibility: hidden;}
                    /* Additionally, hide Streamlit's hamburger menu - optional */
                    .sidebar .sidebar-content {visibility: hidden;}
                    </style>
                    """, unsafe_allow_html=True)
    main()
