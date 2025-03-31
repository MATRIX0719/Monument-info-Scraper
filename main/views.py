from django.shortcuts import render
from bs4 import BeautifulSoup
import requests

def monument_search(request):
    return render(request, 'search_monument.html')

def scrape_data(request):
    url = "https://en.wikipedia.org/wiki/Taj_Mahal"

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        
        paragraphs = [ p.text.strip() for p in soup.find_all("p")]
        
        scraped_data = {
            "paragraphs" : paragraphs,
        }
        
        # print(scraped_data)
        return render(request, "data.html",{"data": scraped_data})
    except Exception as e:
        erorrMessage = "Unexpected error"
        return render(request, erorrMessage)