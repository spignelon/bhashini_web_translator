from flask import Flask, render_template
from bs4 import BeautifulSoup
import requests
import sqlite3

app = Flask(__name__)

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

# API endpoint for translation
translation_api_url = "http://127.0.0.1:8000/scaler/translate"

# SQLite database configuration
database_path = "translations.db"

def create_database():
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Create a table for storing translations
    cursor.execute('''CREATE TABLE IF NOT EXISTS translations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source_language INTEGER,
                        target_language INTEGER,
                        url TEXT,
                        translated_html TEXT
                    )''')

    conn.commit()
    conn.close()

def save_translation_to_database(source_language, target_language, url, translated_html):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Check if the translation already exists in the database
    cursor.execute('''SELECT id FROM translations
                      WHERE source_language = ? AND target_language = ? AND url = ?''',
                   (source_language, target_language, url))
    existing_translation = cursor.fetchone()

    if existing_translation:
        # If exists, update the translated HTML
        cursor.execute('''UPDATE translations
                          SET translated_html = ?
                          WHERE id = ?''', (translated_html, existing_translation[0]))
    else:
        # If not exists, insert a new translation record
        cursor.execute('''INSERT INTO translations (source_language, target_language, url, translated_html)
                          VALUES (?, ?, ?, ?)''', (source_language, target_language, url, translated_html))

    conn.commit()
    conn.close()

def get_translation_from_database(source_language, target_language, url):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Retrieve translated HTML from the database
    cursor.execute('''SELECT translated_html FROM translations
                      WHERE source_language = ? AND target_language = ? AND url = ?''',
                   (source_language, target_language, url))
    translation = cursor.fetchone()

    conn.close()

    return translation[0] if translation else None

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
        # Check if the translation is already cached in the database
        cached_translation = get_translation_from_database(source_language, target_language, url)

        if cached_translation:
            # If cached, render the translated HTML directly from the database
            return render_template('translated_webpage.html', translated_html=cached_translation)

        # If not cached, fetch the HTML content of the webpage
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html_content = response.text

        # Get the base URL
        base_url = response.url

        # Translate the HTML content
        translated_html = translate_html(html_content, base_url, source_language, target_language)

        # Save the translation to the database for future use
        save_translation_to_database(source_language, target_language, url, translated_html)

        return render_template('translated_webpage.html', translated_html=translated_html)

    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    # Initialize the database
    create_database()
    
    # Run the application
    app.run(debug=True)
