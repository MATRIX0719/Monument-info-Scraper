from django.shortcuts import render
from bs4 import BeautifulSoup
import requests
import nltk
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .gemini_api import get_gemini_summary

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
        url = request.POST.get('url')
        monument_name = request.POST.get('q')
        if monument_name:
            try:
                wiki_url = f"https://en.wikipedia.org/wiki/{monument_name.replace(' ', '_')}"
                asi_url =  f"https://asi.nic.in/{monument_name.lower().replace(' ', '-')}/"
                incredible_url = f"https://www.incredibleindia.org/content/incredible-india-v2/en/destinations/{monument_name.lower().replace(' ', '-')}.html"
                urls = [wiki_url, asi_url, incredible_url]
                all_scraped_data = []

                for url in urls:
                    try:
                        response = requests.get(url, timeout=5)
                        response.raise_for_status()
                        soup = BeautifulSoup(response.content, "html.parser")
                        paragraphs = [p.text.strip() for p in soup.find_all("p")]
                        titles = [title.text.strip() for title in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])]
                        scraped_data = {"paragraphs": paragraphs, "titles": titles, "source": url}
                        all_scraped_data.append(scraped_data)
                        
                        # ***CHANGE 2: Show what we found***
                        # Print a message like “Wikipedia gave us 5 paragraphs!”
                        print(f"Scraped from {url}:")
                        print(f" - {len(paragraphs)} paragraphs")
                        print(f" - {len(titles)} titles")
                        if paragraphs:  # If we got paragraphs, show the first one
                            print(f" - First paragraph: {paragraphs[0][:100]}...")  # Just the first 100 letters
                        else:
                            print(" - No paragraphs found!")
                        if titles:
                            print(f" - First title: {titles[0]}")
                        else:
                            print(" - No titles found!")
                        print("---")  # A line to keep it neat

                    except requests.exceptions.RequestException:
                        print(f"Couldn’t get {url}, skipping it!")
                        print("---")

                combined_text = ""
                for data in all_scraped_data:
                    combined_text += " ".join(data["paragraphs"]) + " " + " ".join(data["titles"]) + " "

                sentences = sent_tokenize(combined_text)
                if len(sentences) > 1:
                    vectorizer = TfidfVectorizer().fit_transform(sentences)  # Turn sentences into numbers
                    similarity_matrix = cosine_similarity(vectorizer)  # Check which sentences are too alike
                    unique_sentences = []
                    for i, sentence in enumerate(sentences):
                        if all(similarity_matrix[i][j] < 0.9 for j in range(i)):  # If it’s not too similar to earlier ones
                            unique_sentences.append(sentence)
                    cleaned_text = " ".join(unique_sentences)  # Put the unique sentences back together
                else:
                    cleaned_text = combined_text

                api_key = "AIzaSyCtglWBrix-q84vzTPy1xpVY3GY0b6PSM0"  
                ai_data = get_gemini_summary(cleaned_text)

                if ai_data:
                    return render(request, "scraped_results.html", {
                        "ai_data": ai_data,  # Only pass the parsed data
                        "url": wiki_url
                    })
                else:
                    return render(request, "scraped_results.html", {
                        "ai_data": {"Overview": "Couldn’t summarize, sorry!"},
                        "url": url
                    })
                
            except requests.exceptions.RequestException as e:
                error_message = f"Error fetching URL: {e}"
                return render(request, "scraped_results.html", {"error": error_message, "url": url})
            except Exception as e:
                error_message = f"An unexpected error occurred: {e}"
                return render(request, "scraped_results.html", {"error": error_message, "url": url})

        else:
            return render(request, "scraped_results.html")
    else:
        return render(request, "search_monument.html")