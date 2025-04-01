import google.generativeai as genai
import json

GEMINI_API_KEY = "AIzaSyCtglWBrix-q84vzTPy1xpVY3GY0b6PSM0"

def get_gemini_summary(text):
    """
    Summarizes and organizes text using the Gemini API.

    Args:
        text (str): The text to summarize.

    Returns:
        dict: A dictionary containing the summarized data.
        None: If an error occurs.
    """

    genai.configure(api_key=GEMINI_API_KEY)  # Use the declared API key

    try:
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        prompt = f"Summarize the following text and create useful titles for each topic. Return the result as a JSON object with 'title' and 'summary' keys for each topic: {text}"
        response = model.generate_content(prompt)
        ai_output = response.text

        print("RAW API Output:")
        print(ai_output)

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
        return json.loads(ai_output)
    except json.JSONDecodeError:
        print("Error decoding JSON from API response. Returning raw output.")
        return {"raw_output": ai_output}

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

    #Test model listing.
    try:
        for model in genai.list_models():
            print(f"Model: {model.name}")
            print(f"  Description: {model.description}")
            print(f"  Supported Generation Methods: {model.supported_generation_methods}")
    except Exception as e:
        print(f"Error listing models: {e}")

# def get_gemini_summary(text):
#     """
#     Summarizes and organizes text using the Gemini API.

#     Args:
#         text (str): The text to summarize.
#         api_key (str): Your Gemini API key.

#     Returns:
#         dict: A dictionary containing the summarized data.
#         None: If an error occurs.
#     """
#     genai.configure(api_key=GEMINI_API_KEY)

#     for model in genai.list_models():
#         print(f"Model: {model.name}")
#         print(f"Description: {model.description}")
#         print(f"Supported Generation Methods: {model.supported_generation_methods}")

#     try:
#         model = genai.GenerativeModel('gemini-pro')
#         prompt = f"Summarize the following text and create useful titles for each topic: {text}"
#         response = model.generate_content(prompt)
#         ai_output = response.text
        
#         #changes made yash
#         print("RAW API Output:")
#         print(ai_output)

#         organized_data = parse_ai_response(ai_output) 

#         return organized_data

#     except Exception as e:
#         print(f"Error during Gemini API call: {e}")
#         return None



# def parse_ai_response(ai_output):
#     """
#     Parses the AI's response to create a Python dictionary.

#     Args:
#         ai_output (str): The AI's text response.

#     Returns:
#         dict: A dictionary containing the summarized data.
#     """
#     try:
#         return json.loads(ai_output)
#     except json.JSONDecodeError:
#         print("Error decoding JSON from API response. Returning raw output.")
#         return {"raw_output": ai_output}

#     # This is a placeholder. You'll need to adapt this to your AI's response format.
#     # Example:
#     # return {"title1": "summary1", "title2": "summary2"}
#     # return {"summary":"AI summary placeholder"} #Placeholder.