from flask import Flask, render_template
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

# API endpoint for translation
translation_api_url = "http://127.0.0.1:8000/scaler/translate"

def translate_text(text):
    payload = {
        "source_language": 23,
        "content": text,
        "target_language": 1
    }
    response = requests.post(translation_api_url, json=payload)
    translated_content = response.json()["translated_content"]
    return translated_content

def translate_html(html_content, base_url):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract all text fields from the webpage
    text_fields = [tag for tag in soup.find_all(text=True) if tag.string and tag.string.strip()]

    # Translate each text field
    for tag in text_fields:
        translated_text = translate_text(tag.string)
        tag.replace_with(translated_text)

    # Update the links to stylesheets and other resources
    for tag in soup.find_all(['link', 'script', 'img'], href=True):
        if tag['href'].startswith(('http://', 'https://')):
            continue  # Skip absolute URLs
        tag['href'] = f"{base_url.rstrip('/')}/{tag['href']}"

    return str(soup)

@app.route('/translate_webpage/<path:url>')
def translate_webpage(url):
    try:
        # Fetch the HTML content of the webpage
        response = requests.get(url)
        response.raise_for_status()
        html_content = response.text

        # Get the base URL
        base_url = response.url

        # Translate the HTML content
        translated_html = translate_html(html_content, base_url)

        return render_template('translated_webpage.html', translated_html=translated_html)

    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
