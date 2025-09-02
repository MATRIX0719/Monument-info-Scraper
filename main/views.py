from django.shortcuts import render
from bs4 import BeautifulSoup
import requests
import nltk
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .gemini_api import get_gemini_summary
import json
import certifi
from urllib.parse import urljoin

nltk.download('punkt')


def organize_raw_data(scraped_data, monument_name):
    paragraphs = scraped_data["paragraphs"]
    organized = {
        "Overview": [],
        "History": [],
        "Architecture": [],
        "Location": []
    }

    for p in paragraphs:
        lower_p = p.lower()
        if any(word in lower_p for word in ["history", "century", "ancient", "founded", "year"]):
            organized["History"].append(p)
        elif any(word in lower_p for word in ["architecture", "style", "design", "carving", "sculpture", "structure", "built", "constructed"]):
            organized["Architecture"].append(p)
        elif any(word in lower_p for word in ["located", "situated", "city", "district", "state", "country", "place", "near"]):
            organized["Location"].append(p)
        else:
            organized["Overview"].append(p)

    for key in organized:
        organized[key] = " ".join(organized[key]) if organized[key] else "Not available"

    return organized


def monument_search(request):
    return render(request, "search_monument.html")


def scrape_data(request):
    if request.method == "POST":
        monument_name = request.POST.get('monument')
        if not monument_name:
            return render(request, "scraped_results.html", {"error": "No monument name provided"})

        wiki_url = f"https://en.wikipedia.org/wiki/{monument_name.replace(' ', '_')}"
        asi_url = f"https://asi.nic.in/{monument_name.lower().replace(' ', '-')}/"
        incredible_url = f"https://www.incredibleindia.org/content/incredible-india-v2/en/destinations/{monument_name.lower().replace(' ', '-')}.html"
        urls = [wiki_url, asi_url, incredible_url]
        all_scraped_data = []
        main_image_url = None
        
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/115.0.0.0 Safari/537.36"
            )
        }

        print(f"Starting scraping for: {monument_name}")

        for url in urls:
            try:
                response = requests.get(url, headers=headers, verify=certifi.where(), timeout=8)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, "html.parser")
                print(f"Successfully connected to: {url}")

                
                if not main_image_url:
                    if "wikipedia" in url:
                        infobox = soup.find("table", class_="infobox")
                        if infobox:
                            image = infobox.find("img")
                            if image and image.get("src"):
                                img_url = image["src"]
                                if img_url.startswith("//"):
                                    img_url = "https:" + img_url
                                elif img_url.startswith("/"):
                                    from urllib.parse import urljoin
                                    img_url = urljoin(url, img_url)
                                if img_url.startswith("http"):
                                    main_image_url = img_url
                    
                    if not main_image_url:
                        largest_img = None
                        largest_width = 0
                        images = soup.find_all("img")
                        for image in images:
                            img_url = image.get("src")
                            width = int(image.get("width", "0")) if image.get("width", "0").isdigit() else 0
                            if (
                                img_url
                                and ".svg" not in img_url.lower()
                                and "logo" not in img_url.lower()
                                and "icon" not in img_url.lower()
                                and width > largest_width
                            ):
                                if img_url.startswith("//"):
                                    img_url = "https:" + img_url
                                elif img_url.startswith("/"):
                                    from urllib.parse import urljoin
                                    img_url = urljoin(url, img_url)
                                largest_img = img_url
                                largest_width = width
                        if largest_img:
                            main_image_url = largest_img
                print(f"Image URL found: {main_image_url}")

                
                paragraphs = []
                titles = []

                
                content_containers = []
                if "wikipedia" in url:
                    content_containers.append(soup.find("div", {"class": "mw-parser-output"}))
                    
                    content_containers.append(soup)
                elif "asi.nic.in" in url:
                    content_containers.append(soup.find("div", {"class": "entry-content"}))
                    
                    content_containers.append(soup.find("main"))
                    content_containers.append(soup.find("body"))
                elif "incredibleindia" in url:
                    content_containers.append(soup.find("div", {"class": "content"}))
                    content_containers.append(soup.find("section"))
                    
                    content_containers.append(soup.find("main"))
                    content_containers.append(soup.find("body"))
                
                
                for container in content_containers:
                    if container:
                        paragraphs = [p.get_text().strip() for p in container.find_all("p") if len(p.get_text().strip()) > 60]
                        titles = [title.text.strip() for title in container.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])]
                        if paragraphs:
                            break 
                
                print(f"Scraped {len(paragraphs)} paragraphs from {url}")

                if paragraphs:
                    scraped_data = {"paragraphs": paragraphs, "titles": titles, "source": url}
                    all_scraped_data.append(scraped_data)

            except requests.exceptions.RequestException as e:
                print(f"Failed to scrape {url}: {e}")
                continue
        
        if not all_scraped_data:
            error_message = f"Could not find any information for {monument_name}. Please try a different name."
            return render(request, "scraped_results.html", {"error": error_message, "url": wiki_url})

        
        combined_text = ""
        for data in all_scraped_data:
            combined_text += " ".join(data["paragraphs"]) + " " + " ".join(data["titles"]) + " "

        sentences = sent_tokenize(combined_text)
        
        if len(sentences) > 1:
            vectorizer = TfidfVectorizer().fit(sentences)
            all_vectors = vectorizer.transform(sentences)
            
            unique_sentences = []
            unique_vectors = []
            
            for i, sentence in enumerate(sentences):
                current_vector = all_vectors[i:i+1]
                
                if not unique_vectors or all(cosine_similarity(current_vector, uv)[0][0] < 0.9 for uv in unique_vectors):
                    unique_sentences.append(sentence)
                    unique_vectors.append(current_vector)
            
            cleaned_text = " ".join(unique_sentences)
        else:
            cleaned_text = combined_text

        organized_data = organize_raw_data({"paragraphs": sent_tokenize(cleaned_text)}, monument_name)
        
        ai_data = get_gemini_summary(json.dumps(organized_data), monument_name)

        if not isinstance(ai_data, dict):
            ai_data = {
                "Overview": "No summary available. Please try again.",
                "History": "Not available.",
                "Architecture": "Not available.",
                "Location": "Not available."
            }

        return render(request, "scraped_results.html", {
            "ai_data": ai_data,
            "url": wiki_url,
            "image_url": main_image_url
        })
    return render(request, "search_monument.html")