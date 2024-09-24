import re

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