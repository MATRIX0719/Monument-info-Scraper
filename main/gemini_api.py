import google.generativeai as genai
import json

GEMINI_API_KEY = "AIzaSyDJGYwWtXCA3uFoB72nKJ5zih8_Ebmrb60"

def get_gemini_summary(text, monument_name=""):
    genai.configure(api_key=GEMINI_API_KEY)
    
    if not text or text.strip() == "{}":
        return {
            "Overview": "No summary available",
            "History": "Not available",
            "Architecture": "Not available",
            "Location": "Not available"
        }

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""
        You are an expert on Indian monuments.
        You are given scraped data in JSON format about the monument: "{monument_name}".

        Your task:
        - Summarize ONLY details about "{monument_name}".
        - Do not mention other monuments.
        - Create a JSON object with the following keys:
          - "Overview": A short summary.
          - "History": Past events, dates, and people.
          - "Architecture": Structural details, style, and materials.
          - "Location": The monument's location (city, state, country).
        - Be concise, factual, and avoid repetition.
        - If information for a category is missing, use "Not available".
        
        Return ONLY the valid JSON object. Do not include any extra text, code fences (```json), or explanations.

        Text to analyze:
        {text}
        """
        
        response = model.generate_content(prompt)
        ai_output = response.text
        
        
        try:
            if ai_output.startswith("```json"):
                json_str = ai_output.strip().removeprefix("```json").removesuffix("```").strip()
                return json.loads(json_str)
            else:
                return json.loads(ai_output.strip())
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            print(f"AI Output: {ai_output}")
            return None 

    except Exception as e:
        print(f"Error with AI: {e}")
        return None

if __name__ == "__main__":
    test_text = """
    {
        "Overview": "The Taj Mahal is a white marble mausoleum located in Agra, India.",
        "History": "It was commissioned in 1632 by Mughal emperor Shah Jahan to house the tomb of his wife Mumtaz Mahal.",
        "Architecture": "The Taj Mahal combines elements from Islamic, Persian, and Indian architectural styles.",
        "Location": "Agra, India"
    }
    """
    
    result = get_gemini_summary(test_text, "Taj Mahal")
    print("API Response:", result)