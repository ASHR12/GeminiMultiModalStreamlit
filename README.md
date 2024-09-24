# GoogleGeminiAI

## Installation

Run the following command to install the required packages, you can add more packages if you want:

```bash
pip install -r requirements.txt
```

## How to Create and Activate a Virtual Environment in VSCode Terminal

Navigate to your project directory and run the following commands for windows:

```bash
cd path/to/your/project
python -m venv venv
venv\Scripts\activate
```

## Configuration

### Basic Setup for API Key and Model

1. Create a `.env` file in your project directory with the following content:

   ```plaintext
   API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxx
   MODEL=gemini-1.5-flash-latest
   ```

   Replace `xxxxxxxxxxxxxxxxxxxxxxxxxxx` with your actual API key and `gemini-1.5-flash-latest` with the model you want to use.

2. Configure your application to use these settings.

# Run streamlit application

```
streamlit run <filename>.py
```
