from flask import Flask, render_template
from bs4 import BeautifulSoup
import requests
# import sqlite3

# if not os.path.isfile("cache.db"):
#     exists = False
# else:
#     exists = True

# conn = sqlite3.connect("cache.db")
# c = conn.cursor()

# if exists == False:
#     c.execute('''CREATE TABLE cache(website TEXT, cache TEXT)''')
    
headers = {
    "Sec-Fetch-User": "?1",
    "Te": "trailers",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Mode": "navigate",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Site": "same-origin"
}


app = Flask(__name__)

# API endpoint for translation
translation_api_url = "http://127.0.0.1:8000/scaler/translate"

def translate_text(text, source_language, target_language):
    payload = {
        "source_language": source_language,
        "content": text,
        "target_language": target_language
    }
    response = requests.post(translation_api_url, json=payload)
    translated_content = response.json()["translated_content"]
    return translated_content

def translate_html(html_content, base_url, source_language, target_language):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract all text fields from the webpage
    text_fields = [tag for tag in soup.find_all(text=True) if tag.string and tag.string.strip()]

    # Translate each text field
    for tag in text_fields:
        translated_text = translate_text(tag.string, source_language, target_language)
        tag.replace_with(translated_text)

    # Update the links to stylesheets and other resources
    for tag in soup.find_all(['link', 'script', 'img'], href=True):
        if tag['href'].startswith(('http://', 'https://')):
            continue  # Skip absolute URLs
        tag['href'] = f"{base_url.rstrip('/')}/{tag['href']}"

    return str(soup)

@app.route('/translate_webpage/<int:source_language>/<int:target_language>/<path:url>')
def translate_webpage(source_language, target_language, url):
    try:
        # Fetch the HTML content of the webpage
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html_content = response.text

        # Get the base URL
        base_url = response.url

        # Translate the HTML content
        translated_html = translate_html(html_content, base_url, source_language, target_language)

        return render_template('translated_webpage.html', translated_html=translated_html)

    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
