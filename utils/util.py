import pathlib
import google.generativeai as genai
from typing import Optional, Dict, Any, List
import json
import time
from PIL import Image
import streamlit as st
import re
import PIL.Image
from PIL import Image, ImageDraw
import os

def upload_file_to_gemini(file) -> Optional[Dict[str, Any]]:
    """Uploads a file to Google Gemini."""
    try:
        temp_dir = pathlib.Path("temp")
        temp_dir.mkdir(exist_ok=True)
        file_path = temp_dir / file.name
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
        uploaded_file = genai.upload_file(file_path)
        os.remove(file_path)  # Remove the file from local after upload
        return uploaded_file
    except Exception as e:
        st.error(f"Error uploading file: {e}")
        return None


def poll_file_processing(uploaded_file) -> Optional[Dict[str, Any]]:
    """Polls the status of the uploaded file until processing is complete."""
    try:
        with st.spinner('Processing file...'):
            while uploaded_file.state.name == "PROCESSING":
                time.sleep(1)
                uploaded_file = genai.get_file(uploaded_file.name)
            if uploaded_file.state.name == "ACTIVE":
                st.success(" File processing completed.")
                return uploaded_file
            elif uploaded_file.state.name == "FAILED":
                st.error("File processing failed.")
                return None
            else:
                st.error(f"Unexpected file state: {uploaded_file.state.name}")
                return None
    except Exception as e:
        st.error(f"Error during file processing: {e}")
        return None


def generate_metadata(model: Any, video_file) -> Optional[Dict[str, Any]]:
    """Generates metadata for the uploaded video using the Generative AI model."""
    try:
        prompt = "Provide the details based on provided response schema"
        result = model.generate_content([video_file, prompt])
        if result.text:
            metadata = json.loads(result.text)
            return metadata
        else:
            st.error("No response received from the model.")
            return None
    except json.JSONDecodeError as je:
        st.error(f"Error decoding JSON response: {je}")
        return None
    except Exception as e:
        st.error(f"Error generating metadata: {e}")
        return None


def generate_transcription(model: Any, audio_file) -> Optional[str]:
    """Generates transcription for the uploaded audio using the Generative AI model."""
    try:
        prompt = """
Please transcribe this interview in the following format:
[Speaker Name or Speaker A/B]: [Dialogue or caption].
If a speaker's name is mentioned or can be identified in the audio, map the actual names accordingly.
If no names are given, use Speaker A, Speaker B, etc.
Ensure the transcription captures all spoken words accurately, including filler words where appropriate.
"""
        responses = model.generate_content([audio_file, prompt])
        if responses.text:
            transcription = responses.text.strip()
            return transcription
        else:
            st.error("No response received from the model.")
            return None
    except Exception as e:
        st.error(f"Error generating transcription: {e}")
        return None


def remove_markdown(text):
    """
    Remove Markdown formatting from the given text.

    Args:
        text (str): The input text containing Markdown.

    Returns:
        str: The text without any Markdown formatting.
    """
    # Remove headers (e.g., ###, ##, #)
    text = re.sub(r'(^|\s)#+\s+', '', text)
    
    # Remove emphasis (bold, italic, strikethrough)
    text = re.sub(r'(\*{1,2}|_{1,2}|~~)(.*?)\1', r'\2', text)
    
    # Remove code blocks with language specifiers (e.g., ```json)
    text = re.sub(r'```[a-zA-Z]*\n([\s\S]*?)\n```', r'\1', text)  
    
    # Remove inline code
    text = re.sub(r'`{1,3}([^`]*)`{1,3}', r'\1', text)
    
    # Remove links [text](url)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    # Remove images ![alt text](url)
    text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', r'\1', text)
    
    # Remove blockquotes
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
    
    # Remove horizontal rules (---, ***, ___)
    text = re.sub(r'(^|\n)(-{3,}|_{3,}|\*{3,})(\n|$)', r'\1', text)
    
    # Remove lists (unordered and ordered)
    text = re.sub(r'(^|\n)(\s*[-+*]|\d+\.)\s+', r'\1', text)

    # Remove any remaining Markdown-specific characters
    text = re.sub(r'[*_~`]', '', text)

    return text.strip()


def parse_bounding_boxes(response_text):
  """
  Parses the JSON response to extract bounding boxes along with their names.
  
  Args:
      response_text (str): The raw text response from the model.
      
  Returns:
      list of dict: A list containing bounding box dictionaries with object names.
      
  Raises:
      ValueError: If JSON parsing fails or the structure is incorrect.
  """
  try:
      bounding_boxes = json.loads(response_text)
      
      # Validate that the response is a list
      if not isinstance(bounding_boxes, list):
          raise ValueError("Response JSON is not a list.")
      
      # Define the required keys and their expected types
      required_keys = {
          "name": str,
          "ymin": (int, float),
          "xmin": (int, float),
          "ymax": (int, float),
          "xmax": (int, float)
      }
      
      # Validate each bounding box
      for box in bounding_boxes:
          # Check if all required keys are present
          missing_keys = [key for key in required_keys if key not in box]
          if missing_keys:
              raise ValueError(f"Bounding box missing keys: {missing_keys} in {box}")
          
          # Validate the type of each key
          for key, expected_type in required_keys.items():
              if not isinstance(box[key], expected_type):
                  raise ValueError(f"Bounding box key '{key}' has incorrect type in {box}. Expected {expected_type}, got {type(box[key])}.")
      
      return bounding_boxes
  except json.JSONDecodeError as e:
      raise ValueError(f"Invalid JSON response: {e}")

def convert_normalized_to_pixel(bounding_boxes, image_width, image_height):
  """
  Converts normalized bounding box coordinates to pixel values.
  
  Args:
      bounding_boxes (list of dict): List of bounding boxes with normalized coordinates.
      image_width (int): Width of the original image in pixels.
      image_height (int): Height of the original image in pixels.
      
  Returns:
      list of dict: List of bounding boxes with pixel coordinates.
  """
  converted_boxes = []
  for box in bounding_boxes:
      name = (box['name'])
      xmin = (box['xmin'] / 1000) * image_width
      ymin = (box['ymin'] / 1000) * image_height
      xmax = (box['xmax'] / 1000) * image_width
      ymax = (box['ymax'] / 1000) * image_height
      
      # Ensure coordinates are integers
      xmin, ymin, xmax, ymax = map(int, [xmin, ymin, xmax, ymax])
      
      # Validate coordinates
      if not (0 <= xmin < xmax <= image_width) or not (0 <= ymin < ymax <= image_height):
          print(f"Invalid bounding box coordinates after conversion: {box}")
          continue  # Skip invalid boxes
      
      converted_boxes.append({
          'name': name,
          'xmin': xmin,
          'ymin': ymin,
          'xmax': xmax,
          'ymax': ymax
      })
  
  return converted_boxes


def draw_bounding_boxes(image, bounding_boxes, output_path=None):
    """
    Draws multiple bounding boxes on the image with labeled text.
    
    Args:
        image (PIL.Image.Image): The original image.
        bounding_boxes (list of dict): List of bounding boxes with pixel coordinates.
        output_path (str, optional): Path to save the annotated image. If None, returns the image object.
        
    Returns:
        PIL.Image.Image: Image with bounding boxes and labels drawn.
    """
    draw = ImageDraw.Draw(image)
    
    # You may need to adjust the font size based on your needs
    try:
        from PIL import ImageFont
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    for idx, box in enumerate(bounding_boxes, 1):
        xmin = box['xmin']
        ymin = box['ymin']
        xmax = box['xmax']
        ymax = box['ymax']
        name = box['name']
        
        # Draw the red bounding box
        draw.rectangle([xmin, ymin, xmax, ymax], outline="red", width=1)
        
        # Prepare the label text
        label_text = f"{name}"
        
        # Get text size
        text_bbox = draw.textbbox((0, 0), label_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # Calculate text position (above the bounding box)
        text_x = xmin
        text_y = max(0, ymin - text_height - 2)  # 2 pixels padding
        
        # Draw yellow background for text
        draw.rectangle(
            [
                text_x - 2,  # 2 pixels padding
                text_y - 2,
                text_x + text_width + 2,
                text_y + text_height + 2
            ],
            fill="yellow"
        )
        
        # Draw black text on yellow background
        draw.text((text_x, text_y), label_text, fill="black", font=font)
    
    if output_path:
        image.save(output_path)
        print(f"Annotated image saved at '{output_path}'.")
    return image