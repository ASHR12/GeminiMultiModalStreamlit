import urllib.request
import PIL.Image
from PIL import Image, ImageDraw
import io
import json
def load_image_from_file(file_path):
  return PIL.Image.open(file_path)

def load_image_from_url(image_url):
  with urllib.request.urlopen(image_url) as response:
      image_bytes = response.read()
  return PIL.Image.open(io.BytesIO(image_bytes))

def display_image(image, max_width=600, max_height=350):
  if image.mode != "RGB":
      image = image.convert("RGB")
  
  image_width, image_height = image.size
  if max_width < image_width or max_height < image_height:
      image.thumbnail((max_width, max_height))
  
  image.show()  # This will open the image in the default image viewer on Windows

def get_url_from_gcs(gcs_uri):
  return "https://storage.googleapis.com/" + gcs_uri.replace("gs://", "").replace(" ", "%20")


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
  Draws multiple bounding boxes on the image.
  
  Args:
      image (PIL.Image.Image): The original image.
      bounding_boxes (list of dict): List of bounding boxes with pixel coordinates.
      output_path (str, optional): Path to save the annotated image. If None, returns the image object.
      
  Returns:
      PIL.Image.Image: Image with bounding boxes drawn.
  """
  draw = ImageDraw.Draw(image)
  
  for box in bounding_boxes:
      xmin = box['xmin']
      ymin = box['ymin']
      xmax = box['xmax']
      ymax = box['ymax']
      
      # Draw a red bounding box with a line width of 2
      draw.rectangle([xmin, ymin, xmax, ymax], outline="red", width=4)
      
  
  if output_path:
      image.save(output_path)
      print(f"Annotated image saved at '{output_path}'.")
  return image