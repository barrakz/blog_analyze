import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
from collections import Counter

nltk.download('stopwords')
nltk.download('punkt')

# Funkcja do pobierania artykułów z różnymi klasami, obsługująca różne formaty daty
def get_articles(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        article_data = []

        # Przeszukiwanie elementów div z klasą "blog-post-card"
        div_articles = soup.find_all('div', class_='blog-post-card')
        for article in div_articles:
            title = article.find('h3', class_='blog-post-card-title').text.strip()
            link = article.find('a')['href']
            date_elem = article.find('time', class_='blog-post-card-date')
            
            # Obsługa różnych formatów daty
            if date_elem:
                date = date_elem['datetime']
                try:
                    datetime.strptime(date, "%m/%d/%y")
                except ValueError:
                    # Jeśli format daty jest nieprawidłowy, spróbuj odnaleźć datę w tekście
                    date_text = date_elem.get_text().strip()
                    date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{2,4})', date_text)
                    date = date_match.group(1) if date_match else "Brak daty"
            else:
                date = "Brak daty"

            article_data.append((title, link, date))

        # Przeszukiwanie elementów div z klasą "blog-categories-card"
        li_articles = soup.find_all('div', class_='blog-categories-card')
        for article in li_articles:
            title = article.find('h3', class_='blog-categories-card-title').text.strip()
            link = article.find('a')['href']
            date_elem = article.find('div', class_='blog-categories-card-footer')
            
            # Obsługa różnych formatów daty
            if date_elem:
                date = date_elem.find('p').text.strip()
                try:
                    datetime.strptime(date, "%m/%d/%y")
                except ValueError:
                    # Jeśli format daty jest nieprawidłowy, spróbuj odnaleźć datę w tekście
                    date_text = date_elem.get_text().strip()
                    date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{2,4})', date_text)
                    date = date_match.group(1) if date_match else "Brak daty"
            else:
                date = "Brak daty"

            article_data.append((title, link, date))

        # Sortowanie wszystkich artykułów według daty w formacie MM/DD/YY (najnowsze na początku)
        article_data.sort(key=lambda x: datetime.strptime(x[2], "%m/%d/%y") if x[2] != "Brak daty" else datetime.min, reverse=True)

        return article_data
    else:
        print("Błąd podczas pobierania strony.")
        return []

# Funkcja do analizy artykułu
def analyze_article(title, article_url, date):
    response = requests.get(article_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        article_content = soup.find('span', id='hs_cos_wrapper_post_body').get_text()

        # Przekształcenie tekstu na małe litery przed tokenizacją
        article_content = article_content.lower()

        # Tokenizacja słów
        tokens = word_tokenize(article_content)
        word_count = len(tokens)
        letter_count = sum(len(word) for word in tokens if word.isalpha())

        # Usunięcie znaków interpunkcyjnych i stop words
        tokens = [word for word in tokens if word.isalnum() and word not in stopwords.words('english')]

        # Znajdowanie 5 najczęściej występujących fraz kluczowych
        phrase_counter = Counter()
        for i in range(len(tokens)):
            for j in range(i + 1, len(tokens) + 1):
                phrase = ' '.join(tokens[i:j])
                phrase_counter[phrase] += 1

        top_phrases = phrase_counter.most_common(5)
        print(f"Tytuł artykułu: {title}")
        print(f"Data artykułu: {date}")
        print("Liczba słów w artykule:", word_count)
        print("Liczba liter w artykule:", letter_count)
        print("Najczęściej występujące frazy kluczowe:")
        for phrase, count in top_phrases:
            print(f"{phrase}: {count} razy")

        print("-" * 30)
    else:
        print(f"Błąd podczas pobierania artykułu {article_url}")

# Główna funkcja
def main():
    hubspot_url = 'https://blog.hubspot.com/'
    
    # Pobieranie wszystkich artykułów ze strony
    all_articles = get_articles(hubspot_url)

    if all_articles:
        # Pobieranie 3 najnowszych artykułów z całej strony
        newest_articles = all_articles[:3]

        for i, (title, article_link, date) in enumerate(newest_articles):
            print(f"Analiza artykułu {i+1}:")
            analyze_article(title, article_link, date)
        
        print(f"Liczba wszystkich artykułów na stronie: {len(all_articles)}")

if __name__ == "__main__":
    main()
