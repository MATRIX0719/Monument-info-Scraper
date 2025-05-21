from django.shortcuts import render
from bs4 import BeautifulSoup
import requests
import nltk
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .gemini_api import get_gemini_summary
import json

nltk.download('punkt')  
nltk.download('punkt_tab')

def monument_search(request):
    return render(request, 'search_monument.html')

def organize_raw_data(scraped_data):
    paragraphs = scraped_data["paragraphs"]
    organized = {
        "Overview": "Not available",
        "History": "Not available", 
        "Architecture": "Not available",
        "Location": "Not available"
    }

    for p in paragraphs:
        if any(word in p.lower() for word in ["built", "constructed", "design", "structure"]):
            organized["Architecture"] = p
        elif any(word in p.lower() for word in ["history", "founded", "year", "century"]):
            organized["History"] = p
        elif any(word in p.lower() for word in ["located", "city", "country", "place"]):
            organized["Location"] = p
        else:
            organized["Overview"] = p
    return organized

def scrape_data(request):
    if request.method == "POST":
        monument_name = request.POST.get('monument')
        if monument_name:
            try:
                wiki_url = f"https://en.wikipedia.org/wiki/{monument_name.replace(' ', '_')}"
                asi_url = f"https://asi.nic.in/{monument_name.lower().replace(' ', '-')}/"
                incredible_url = f"https://www.incredibleindia.org/content/incredible-india-v2/en/destinations/{monument_name.lower().replace(' ', '-')}.html"
                urls = [wiki_url, asi_url, incredible_url]
                all_scraped_data = []
                main_image_url = None

                for url in urls:
                    try:
                        response = requests.get(url, timeout=5)
                        response.raise_for_status()
                        soup = BeautifulSoup(response.content, "html.parser")
                        paragraphs = [p.text.strip() for p in soup.find_all("p")]
                        titles = [title.text.strip() for title in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])]
                        infobox = soup.find("table", class_="infobox")
                        if infobox:
                            image = infobox.find("img")
                            if image and image.get("src"):
                                img_url = image["src"]
                                if img_url.startswith("/"):
                                    from urllib.parse import urljoin
                                    img_url = urljoin(url, img_url)
                                if img_url.startswith("http"):
                                    main_image_url = img_url
                                    print(f"Found infobox image: {main_image_url}")
                        if not main_image_url:
                            images = soup.find_all("img")
                            for image in images:
                                img_url = image.get("src")
                                if (img_url and ".svg" not in img_url.lower() and "wiki" not in img_url.lower() and 
                                    image.get("width", "0").isdigit() and int(image.get("width", "0")) > 100):
                                    if img_url.startswith("/"):
                                        from urllib.parse import urljoin
                                        img_url = urljoin(url, img_url)
                                    if img_url.startswith("http"):
                                        main_image_url = img_url
                                        print(f"Found backup image: {main_image_url}")
                                        break

                        scraped_data = {"paragraphs": paragraphs, "titles": titles, "source": url}
                        all_scraped_data.append(scraped_data)
                        
                        print(f"Scraped from {url}:")
                        print(f" - {len(paragraphs)} paragraphs")
                        print(f" - {len(titles)} titles")
                        if paragraphs:
                            print(f" - First paragraph: {paragraphs[0][:100]}...")
                        if main_image_url:
                            print(f" - Image URL: {main_image_url}")

                    except requests.exceptions.RequestException as e:
                        print(f"Couldn’t get {url}: {e}")
                combined_text = ""
                for data in all_scraped_data:
                    combined_text += " ".join(data["paragraphs"]) + " " + " ".join(data["titles"]) + " "

                sentences = sent_tokenize(combined_text)
                if len(sentences) > 1:
                    vectorizer = TfidfVectorizer().fit_transform(sentences)
                    similarity_matrix = cosine_similarity(vectorizer)
                    unique_sentences = []
                    for i, sentence in enumerate(sentences):
                        if all(similarity_matrix[i][j] < 0.9 for j in range(i)):
                            unique_sentences.append(sentence)
                    cleaned_text = " ".join(unique_sentences)
                else:
                    cleaned_text = combined_text


                ai_data = get_gemini_summary(cleaned_text)
                print("Raw ai_data:", ai_data)

                if isinstance(ai_data, str):
                    try:
                        ai_data = json.loads(ai_data)
                    except json.JSONDecodeError:
                        ai_data = {"Overview": "Failed to parse AI summary"}
                if not ai_data:
                    ai_data = {
                        "Overview": "No summary available",
                        "History": "Not available",
                        "Architecture": "Not available",
                        "Location": "Not available"
                    }

                return render(request, "scraped_results.html", {
                    "ai_data": ai_data,
                    "url": wiki_url,
                    "image_url": main_image_url
                })

            except Exception as e:
                error_message = f"An unexpected error occurred: {e}"
                return render(request, "scraped_results.html", {"error": error_message, "url": wiki_url})

        else:
            return render(request, "scraped_results.html", {"error": "No monument name provided"})
    return render(request, "search_monument.html")