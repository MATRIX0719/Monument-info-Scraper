import google.generativeai as genai

def get_gemini_summary(text, api_key):
    """
    Summarizes and organizes text using the Gemini API.

    Args:
        text (str): The text to summarize.
        api_key (str): Your Gemini API key.

    Returns:
        dict: A dictionary containing the summarized data.
        None: If an error occurs.
    """

    genai.configure(api_key=api_key)

    try:
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"Summarize the following text and create useful titles for each topic: {text}"
        response = model.generate_content(prompt)
        ai_output = response.text
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
    # This is a placeholder. You'll need to adapt this to your AI's response format.
    # Example:
    # return {"title1": "summary1", "title2": "summary2"}
    return {"summary":"AI summary placeholder"} #Placeholder.