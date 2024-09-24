# app.py
import streamlit as st
from utils.util import (
  upload_file_to_gemini,
  poll_file_processing,
  generate_metadata,
  generate_transcription,
  remove_markdown,
  parse_bounding_boxes,
  convert_normalized_to_pixel,
  draw_bounding_boxes
)
from utils.model import load_model
from PIL import Image
from typing import TypedDict, Optional, List, Dict, Any
from utils.util import upload_file_to_gemini
import google.generativeai as genai

def main():
  st.set_page_config(page_title="Gemini Multimodal", layout="wide")
  st.title("Gemini Multimodal Application")

  # Tab selection using radio
  tab = st.radio("", ["Video", "Image", "Audio", "File API"], horizontal=True)

  if tab == "Video":
      video_tab()
  elif tab == "Image":
      image_tab()
  elif tab == "Audio":
      audio_tab()
  elif tab == "File API":
      file_api_tab()

def video_tab():

  # Define the structure for Video Analysis metadata
  class VideoAnalysis(TypedDict):
      name: str
      title: str
      total_duration: float  # Duration in seconds
      summary: str
      small_summary: str
      tags: Optional[List[str]]

  def display_metadata(metadata: VideoAnalysis):
      """Displays the generated metadata in a user-friendly format."""
      st.header("Generated Metadata")
      st.subheader(f"Title: {metadata.get('title', 'N/A')}")
      st.write(f"**Name:** {metadata.get('name', 'N/A')}")
      st.write(f"**Total Duration:** {metadata.get('total_duration', 'N/A')} seconds")
      st.write(f"**Summary:** {metadata.get('summary', 'N/A')}")
      st.write(f"**Small Summary:** {metadata.get('small_summary', 'N/A')}")
      st.write(f"**Tags:** {', '.join(metadata.get('tags', [])) if metadata.get('tags') else 'N/A'}")

  st.header("📹 Video Metadata and Summary Generation")
  st.write("Upload a video to analyze its content and automatically generate metadata and summary.")

  model = load_model(type="video", schemaType=VideoAnalysis)

  uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi", "mkv"])

  if uploaded_file is not None:
      col1, col2, col3 = st.columns([2, 6, 2])  # 20%, 60%, 20% width
      with col2:
          st.video(uploaded_file)
      uploaded_file.seek(0)
      if st.button("Analyze Video"):
          with st.spinner('Uploading video...'):
              uploaded_genai_file = upload_file_to_gemini(uploaded_file)
              if uploaded_genai_file:
                  st.success("File Upload successful!")
              if uploaded_genai_file is None:
                  st.error("Failed to upload the video.")
                  return

          processed_file = poll_file_processing(uploaded_genai_file)
          if processed_file is None:
              st.error("Video processing failed.")
              return

          with st.spinner('Generating metadata...'):
              metadata = generate_metadata(model, processed_file)
              if metadata:
                  st.success("Metadata generation successful!")
                  display_metadata(metadata)
  else:
      st.info("Please upload a video file to begin analysis.")


def image_tab():

  @st.cache_resource
  def get_model():
      model = load_model(type=None, schemaType=None)
      return model


  def process_image(image: Image.Image, object_name: str, model):
      # Define the dynamic prompt with the user-specified object
      prompt = f"""
You are given an image. Identify all {object_name} in the image and provide their bounding boxes.
Return ONLY a valid JSON array in the exact format shown below. Do NOT include any additional text, explanations, comments, trailing commas, or markdown formatting such as code blocks.
Use this JSON schema:
[
{{
"name": "string",
"ymin": float,
"xmin": float,
"ymax": float,
"xmax": float
}}
]
"""

      # Generate content using the multimodal model
      try:
          response = model.generate_content([image, prompt])
      except Exception as e:
          st.error(f"Error generating content from the model: {e}")
          return None

      # Clean the response
      final_response = remove_markdown(response.text)

      # Parse bounding boxes
      try:
          bounding_boxes = parse_bounding_boxes(final_response)
      except ValueError as ve:
          st.error(f"Error parsing bounding boxes: {ve}")
          return None

      # Get image dimensions
      image_width, image_height = image.size

      # Convert normalized coordinates to pixel values
      converted_boxes = convert_normalized_to_pixel(bounding_boxes, image_width, image_height)
      return converted_boxes

  st.header("📸 Object Detection")
  st.write(
      """
Upload an image or use your camera to capture one, then specify the object you want to detect.
The application will draw bounding boxes around the detected objects and display their coordinates.
"""
  )

  # Sidebar for user inputs
  st.sidebar.header("🔍 Detection Settings")

  # Radio buttons to select input method
  input_method = st.sidebar.radio(
      "Select Image Input Method",
      ("Upload Image", "Use Camera")
  )

  # Initialize uploaded_image as None
  uploaded_image = None

  if input_method == "Upload Image":
      uploaded_file = st.sidebar.file_uploader("📂 Choose an image...", type=["jpg", "jpeg", "png"])
      if uploaded_file is not None:
          try:
              # Open the uploaded image
              uploaded_image = Image.open(uploaded_file).convert("RGB")
              st.image(uploaded_image, caption='🖼️ Uploaded Image', use_column_width=True)
          except Exception as e:
              st.error(f"❌ Error opening image: {e}")
  elif input_method == "Use Camera":
      captured_image = st.sidebar.camera_input("📸 Capture an image")
      if captured_image is not None:
          try:
              # Open the captured image
              uploaded_image = Image.open(captured_image).convert("RGB")
              st.image(uploaded_image, caption='🖼️ Captured Image', use_column_width=True)
          except Exception as e:
              st.error(f"❌ Error capturing image: {e}")

  object_name = st.sidebar.text_input("📝 Enter the object to detect", placeholder="e.g., cat, bottle")
  detect_button = st.sidebar.button("🚀 Detect Objects")

  if detect_button:
      if uploaded_image is not None:
          if not object_name.strip():
              st.error("⚠️ Please enter a valid object name to detect.")
              st.stop()

          # Load the model
          with st.spinner("🔄 Loading the model..."):
              model = get_model()

          # Process the image
          with st.spinner("🔍 Detecting objects..."):
              converted_boxes = process_image(uploaded_image, object_name, model)

          if converted_boxes is None:
              st.error("❌ An error occurred during object detection.")
              st.stop()

          if converted_boxes:
              # Draw bounding boxes using the existing function
              annotated_image = draw_bounding_boxes(uploaded_image.copy(), converted_boxes, output_path=None)

              # Display the annotated image
              st.image(annotated_image, caption='🖼️ Annotated Image', use_column_width=True)

              # Display bounding box coordinates
              st.subheader("📍 Bounding Box Coordinates")
              for idx, box in enumerate(converted_boxes, start=1):
                  st.markdown(f"**{idx}. {box['name'].capitalize()}:**")
                  st.markdown(f"- ymin: {box['ymin']}")
                  st.markdown(f"- xmin: {box['xmin']}")
                  st.markdown(f"- ymax: {box['ymax']}")
                  st.markdown(f"- xmax: {box['xmax']}")
                  st.markdown("---")
          else:
              st.warning(f"⚠️ No instances of '{object_name}' were found in the image.")
      else:
          st.error("⚠️ Please provide an image either by uploading or using the camera.")
          st.stop()


def audio_tab():

  st.header("🔊 Audio Transcription")
  st.write("Upload an audio file to transcribe its content.")

  model = load_model(type=None, schemaType=None)

  uploaded_audio = st.file_uploader("Upload an audio file", type=["mp3", "wav", "aiff", "acc", "ogg", "flac"])

  if uploaded_audio is not None:
      st.audio(uploaded_audio, format='audio/mp3')
      if st.button("Transcribe Audio"):
          with st.spinner('Uploading audio...'):
              try:
                  uploaded_genai_file = upload_file_to_gemini(uploaded_audio)
                  if uploaded_genai_file:
                      st.success("File Upload successful!")
              except Exception as e:
                  st.error(f"Error uploading audio: {e}")
                  return

          processed_file = poll_file_processing(uploaded_genai_file)
          if processed_file is None:
              st.error("Audio processing failed.")
              return

          with st.spinner('Transcribing audio...'):
              transcription = generate_transcription(model, processed_file)
              if transcription:
                  st.success("Transcription successful!")
                  st.text_area("Transcription", transcription, height=300)
  else:
      st.info("Please upload an audio file to begin transcription.")


def file_api_tab():

  st.header("📂 File API Operations")
  st.write("List and manage files uploaded to the API.")

  # List files
  if st.button("List Files"):
      st.subheader("Uploaded Files:")
      try:
          files = genai.list_files()
          file_list = list(files)  # Convert generator to list

          # Check if the list has files
          if len(file_list) > 0:
              cols = st.columns(2)  # Create two columns
              with cols[0]:
                  st.markdown("**__Display Name__**")
              with cols[1]:
                  st.write("**__File Name__**")

              for f in file_list:
                  with cols[0]:
                      st.write(f"📄 {f.display_name}")  # Display Name
                  with cols[1]:
                      st.write(f"📄 {f.name}")  # File Name
          else:
              st.markdown("<span style='color:red;'>No files found.</span>", unsafe_allow_html=True)  # Display error if no files
      except Exception as e:
          st.error(f"Error listing files: {e}")

  # Delete file
  st.subheader("Delete a Single File")
  file_name_to_delete = st.text_input("Enter the name of the file to delete")
  if st.button("Delete File"):
      if file_name_to_delete.strip():
          try:
              myfile = genai.get_file(file_name_to_delete)
              myfile.delete()
              st.success(f"File '{file_name_to_delete}' has been deleted.")
          except Exception as e:
              st.error(f"Error deleting file: {e}")
      else:
          st.error("Please enter a valid file name.")

  # Option to delete all files
  st.subheader("Delete All Files")
  delete_all = st.checkbox("Delete all files")
  if delete_all:
      if st.button("Confirm Delete All"):
          with st.spinner("Deleting all files..."):
              try:
                  files = genai.list_files()
                  for f in files:
                      myfile = genai.get_file(f.name)
                      myfile.delete()
                  st.success("All files have been deleted.")
              except Exception as e:
                  st.error(f"Error deleting all files: {e}")


if __name__ == "__main__":
  main()