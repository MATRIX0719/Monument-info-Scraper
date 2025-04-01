from django.shortcuts import render
from bs4 import BeautifulSoup
import requests
from .gemini_api import get_gemini_summary

def monument_search(request):
    return render(request, 'search_monument.html')

def scrape_data(request):
    if request.method == "POST":
        url = request.POST.get('url')
        if url:
            try:
                response = requests.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, "html.parser")

                paragraphs = [p.text.strip() for p in soup.find_all("p")]
                titles = [title.text.strip() for title in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])]

                scraped_data = {
                    "paragraphs": paragraphs,
                    "titles": titles,
                }

                api_key = "AIzaSyCtglWBrix-q84vzTPy1xpVY3GY0b6PSM0"  
                ai_data = get_gemini_summary(str(scraped_data))

                if ai_data:
                    return render(request, "scraped_results.html", {"ai_data": ai_data, "url": url})
                else:
                    return render(request, "scraped_results.html", {"data": scraped_data, "url": url})
                

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