import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from dotenv import load_dotenv
import os
from google.generativeai import caching
import datetime

def load_model(type, schemaType):
  load_dotenv()
  genai.configure(api_key=os.getenv('API_KEY'))
  if type is not None and schemaType is not None:
      # Configuration when both type and schemaType are provided
      generation_config = GenerationConfig(
          temperature=0.7,
          top_p=0.9,
          top_k=40,
          candidate_count=1,
          max_output_tokens=8192,
          response_mime_type="application/json",
          response_schema=schemaType
      )
  else:
      # Default configuration when type or schemaType is not provided
      generation_config = GenerationConfig(
          temperature=0.9,
          top_p=1.0,
          top_k=32,
          candidate_count=1,
          max_output_tokens=8192
      )
  
  model_name = os.getenv('MODEL')
  model = genai.GenerativeModel(model_name=model_name, generation_config=generation_config)
  return model


def load_cached_content_model(contents, display_name, system_instruction, ttl_minutes=5):
  print('loading cached content model')
  load_dotenv() 
  genai.configure(api_key=os.getenv('API_KEY'))
  # Create a cache with the specified TTL
  cache = caching.CachedContent.create(
      model=os.getenv('CACHING_MODEL'),
      display_name=display_name,
      system_instruction=system_instruction,
      contents=contents,
      ttl=datetime.timedelta(minutes=ttl_minutes),
  )
  print('cache',cache)
  # Construct a GenerativeModel which uses the created cache.
  model = genai.GenerativeModel.from_cached_content(cached_content=cache)
  return model

