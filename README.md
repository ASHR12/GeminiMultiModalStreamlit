# Gemini Multimodal Streamlit Application

A comprehensive multimodal AI application built with Streamlit and Google's Gemini AI that provides video analysis, object detection, audio transcription, and file management capabilities through an intuitive web interface.

## Project Overview

This application leverages Google's Gemini AI models to process and analyze various types of media content. It provides four main functionalities:

- **Video Analysis**: Upload videos to automatically generate metadata including title, summary, duration, and tags
- **Object Detection**: Upload images or use camera input to detect and locate objects with bounding box visualization
- **Audio Transcription**: Convert audio files to text with speaker identification
- **File API Management**: List, view, and delete files uploaded to the Gemini API

The application is designed to be user-friendly with a clean, tabbed interface that allows users to easily switch between different AI-powered features.

## Features

### 🎥 Video Analysis

- Upload video files (MP4, MOV, AVI, MKV)
- Automatic metadata generation with structured JSON schema
- Extract video title, summary, duration, and relevant tags
- Real-time processing status updates

### 📸 Object Detection

- Upload images (JPG, JPEG, PNG) for object detection
- Specify custom objects to detect or detect all objects
- Visual bounding box annotations with object labels
- Pixel-perfect coordinate extraction and display
- Support for normalized coordinate conversion

### 🔊 Audio Transcription

- Support for multiple audio formats (MP3, WAV, AIFF, AAC, OGG, FLAC)
- Speaker identification and dialogue formatting
- Accurate transcription with filler words preservation
- Interview and conversation transcription optimization

### 📂 File API Management

- List all uploaded files with display names and file names
- Individual file deletion by name
- Bulk delete all files functionality
- Real-time file status monitoring

## Tech Stack

### Core Technologies

- **Python 3.x** - Primary programming language
- **Streamlit** - Web application framework for the user interface
- **Google Generative AI (Gemini)** - Core AI model for multimodal processing

### AI & Machine Learning

- **google-generativeai** - Official Google Gemini AI SDK
- **Pillow (PIL)** - Image processing and manipulation
- **OpenCV** - Computer vision operations

### Utilities & Support

- **python-dotenv** - Environment variable management
- **Rich** - Enhanced terminal output formatting
- **IPython** - Interactive Python environment
- **streamlit-chat** - Chat interface components

### Development Tools

- **Live** - Development server utilities
- **JSON** - Data serialization and parsing
- **Regex (re)** - Text processing and markdown removal

## Project Structure

```
GeminiMultiModalStreamlit/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
├── utils/                          # Utility modules
│   ├── model.py                   # AI model loading and configuration
│   ├── util.py                    # Core utility functions
│   └── removemarkdownsyntax.py    # Markdown text processing
└── temp/                          # Temporary file storage (auto-created)
```

### Key Components

- **`app.py`**: Main application entry point with Streamlit UI and tab management
- **`utils/model.py`**: Handles Gemini AI model initialization, configuration, and caching
- **`utils/util.py`**: Core utilities for file upload, processing, metadata generation, and image processing
- **`utils/removemarkdownsyntax.py`**: Text processing utilities for cleaning AI responses

## Setup Instructions

### Prerequisites

- Python 3.7 or higher
- Google AI API key (from Google AI Studio)
- Virtual environment (recommended)

### 1. Clone and Navigate

```bash
git clone <repository-url>
cd GeminiMultiModalStreamlit
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the project root directory:

```plaintext
API_KEY=your_google_ai_api_key_here
MODEL=gemini-1.5-flash-latest
CACHING_MODEL=gemini-1.5-flash-001
```

**Important**:

- Replace `your_google_ai_api_key_here` with your actual Google AI API key
- You can obtain an API key from [Google AI Studio](https://aistudio.google.com/)
- The `MODEL` can be any supported Gemini model version
- `CACHING_MODEL` is used for cached content operations

### 5. Run the Application

```bash
streamlit run app.py
```

The application will start and be accessible at `http://localhost:8501`

## Usage Guide

### Getting Started

1. Launch the application using the command above
2. The interface will display four tabs: Video, Image, Audio, and File API
3. Select the appropriate tab based on your use case

### Video Analysis

1. Navigate to the **Video** tab
2. Upload a video file using the file uploader
3. Click **"Analyze Video"** to start processing
4. Wait for file upload and processing completion
5. View the generated metadata including title, summary, duration, and tags

### Object Detection

1. Go to the **Image** tab
2. Upload an image using the sidebar file uploader
3. Choose detection mode:
   - **Specific Object**: Enter the object name you want to detect
   - **All Objects**: Check "Detect All Objects" to find everything
4. Click **"Detect Objects"** to process the image
5. View the annotated image with bounding boxes and coordinate details

### Audio Transcription

1. Select the **Audio** tab
2. Upload an audio file (supports multiple formats)
3. Click **"Transcribe Audio"** to start processing
4. Wait for upload and transcription completion
5. View the formatted transcription with speaker identification

### File Management

1. Access the **File API** tab
2. **List Files**: Click to view all uploaded files
3. **Delete Single File**: Enter file name and click delete
4. **Delete All Files**: Check the checkbox and confirm to remove all files

## Configuration

### Environment Variables

The application requires the following environment variables in your `.env` file:

| Variable        | Description                  | Required | Example                   |
| --------------- | ---------------------------- | -------- | ------------------------- |
| `API_KEY`       | Google AI API key            | Yes      | `AIza...`                 |
| `MODEL`         | Gemini model version         | Yes      | `gemini-1.5-flash-latest` |
| `CACHING_MODEL` | Model for caching operations | No       | `gemini-1.5-flash-001`    |

### Model Configuration

The application automatically configures different model settings based on use case:

- **Structured Output** (Video Analysis): JSON schema response with specific temperature and token limits
- **General Purpose** (Image/Audio): Standard configuration with higher creativity settings
- **Caching**: Optimized for repeated operations with TTL management

### File Handling

- Temporary files are automatically created and cleaned up
- Supported video formats: MP4, MOV, AVI, MKV
- Supported image formats: JPG, JPEG, PNG
- Supported audio formats: MP3, WAV, AIFF, AAC, OGG, FLAC
- Files are uploaded to Google's servers and processed remotely

### Performance Optimization

- Model instances are cached using Streamlit's `@st.cache_resource`
- File processing includes polling mechanisms for completion status
- Bounding box coordinates are normalized and converted for accuracy
- Error handling and validation throughout the processing pipeline

---

**Note**: This application requires an active internet connection and valid Google AI API credentials to function properly. Make sure your API key has sufficient quota for the operations you plan to perform.
