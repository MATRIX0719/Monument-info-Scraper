import google.generativeai as genai
import json

GEMINI_API_KEY = "AIzaSyCtglWBrix-q84vzTPy1xpVY3GY0b6PSM0"

def get_gemini_summary(text):
    genai.configure(api_key=GEMINI_API_KEY)  # Use the declared API key

    try:
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        prompt = f"""
            Summarize the following text about a monument and organize it into these specific categories: 
            - 'Overview': A brief summary of the monument.
            - 'History': Key historical facts or events.
            - 'Architecture': Details about design or construction.
            - 'Location': Information about where it’s located.
            Return the result as a valid JSON string (enclosed in ```json``` markers) with 'title' and 'summary' keys for each category. If a category isn’t applicable, include it with a summary of 'Not available'. Here’s the text: {text} 
        Example output:
        ```json
        {{
            "Overview": "A brief summary",
            "History": "Historical facts",
            "Architecture": "Design details",
            "Location": "Location info"
        }}
        """
        response = model.generate_content(prompt)
        ai_output = response.text
        print("RAW API OUTPUT:",ai_output)
        return parse_ai_response(ai_output) 
        organized_data = parse_ai_response(ai_output)

        return organized_data

    except Exception as e:
        print(f"Error during Gemini API call: {e}")
        return None

def parse_ai_response(ai_output):
    """
    Parses the AI's response to create a Python dictionary.

    Args:
        ai_output (str): The AI's text response.

    Returns:
        dict: A dictionary containing the summarized data.
    """
    try:
        # Extract JSON content between ```json and ``` markers
        start_marker = "```json"
        end_marker = "```"
        if start_marker in ai_output and end_marker in ai_output:
            json_str = ai_output[ai_output.index(start_marker) + len(start_marker):ai_output.rindex(end_marker)].strip()
            return json.loads(json_str)
        else:
            # If no markers, assume the whole response is JSON
            return json.loads(ai_output)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from API response: {e}")
        print("Raw output:", ai_output)
        # Fallback: Return a default structure instead of raw_output
        return {
            "Overview": "Summary not available due to parsing error",
            "History": "Not available",
            "Architecture": "Not available",
            "Location": "Not available"
        }

# Test the function (optional)
if __name__ == "__main__":
    test_text = """
    This is some test text. It contains information about a monument. The monument is called the Taj Mahal. It is located in Agra, India. It was built by Shah Jahan in memory of his wife Mumtaz Mahal. It is made of white marble.
    """

    result = get_gemini_summary(test_text)

    if result:
        print("API Response:")
        print(result)
    else:
        print("API call failed.")

