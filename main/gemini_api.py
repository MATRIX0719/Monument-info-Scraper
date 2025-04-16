import google.generativeai as genai
import json

GEMINI_API_KEY = "AIzaSyCtglWBrix-q84vzTPy1xpVY3GY0b6PSM0"

def get_gemini_summary(text):
    genai.configure(api_key=GEMINI_API_KEY)  

    try:
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        prompt = f"""
        Summarize the following text about a monument, which comes from multiple websites (Wikipedia, ASI, and Incredible India). Organize it into these categories:
        - 'Overview': A short summary of the monument.
        - 'History': Important past events or facts.
        - 'Architecture': How it looks or was built.
        - 'Location': Where it is.
        Make it clear, concise, and avoid repeating things. Return it as a valid JSON string in ```json``` markers. If a category isn’t clear, use 'Not available'. Here’s the text: {text}
        Example:
        ```json
        {{
            "Overview": "A famous monument",
            "History": "Built long ago",
            "Architecture": "Pretty design",
            "Location": "In India"
        }}
    """
        response = model.generate_content(prompt)
        ai_output = response.text
        print("RAW API Output:", ai_output)  
        return parse_ai_response(ai_output)
    except Exception as e:
        print(f"Error with AI: {e}")
        return None

def parse_ai_response(ai_output):
    try:
        start_marker = "```json"         
        end_marker = "```"
        if start_marker in ai_output and end_marker in ai_output:
            json_str = ai_output[ai_output.index(start_marker) + len(start_marker):ai_output.rindex(end_marker)].strip()
            return json.loads(json_str)
        
        else:
            return json.loads(ai_output)
        
    except json.JSONDecodeError as e:
        print(f"Error reading AI’s answer: {e}")
        print("Raw output:", ai_output)
        return {
            "Overview": "Summary not available",
            "History": "Not available",
            "Architecture": "Not available",
            "Location": "Not available"
        }

    except Exception as e:
        print(f"Error during Gemini API call: {e}")
        return None

if __name__ == "__main__":
    test_text = """
    This is some test text. It contains information about a monument. The monument is called the Taj Mahal. It is located in Agra, India. It was built by Shah Jahan in memory of his wife Mumtaz Mahal. It is made of white marble.
    """

    result = get_gemini_summary(test_text)

    if result:
        print("API Response:", result)

    else:
        print("API call failed.")

