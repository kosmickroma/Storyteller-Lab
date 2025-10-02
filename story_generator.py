# story_generator.py

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables from the .env file
load_dotenv()



# Prompts user for the three necessary components to generate a story.
def get_user_inputs():
    print("\n---Storyteller Lab Input---")

    # 1. Protagonist Name
    # The .strip() method removes any accidental leading/trailing spaces.
    protagonist = input("Enter the name of the main character: ").strip()

    # 2. Target Topic
    topic = input("What is the main topic or lesson of the story: ").strip()

    # 3. Style/Tone
    style = input("What is the desired style or tone ('rhyming poem', 'exciting adventure', 'cozy'): ").strip()

    # Simple validation check: ensure the user provided *something* for each input
    if not all([protagonist, topic, style]):
        print("\n*Error: All three inputs (Protagonist, Topic, Style) are required. Please try again.*\n")
        return get_user_inputs() #Recursively asks again if the inputs are missing
    
    # Return a dictionary of the captured parameters
    return {
        "protagonist": protagonist,
        "topic": topic,
        "style": style
    }


##############################################################
########## Generate Story#####################################
##############################################################

# Constructs a detailed prompt, calls the Gemini API, and prints the generated story.

def generate_story(protagonist, topic, style):
    try:
        # 1. Initialize the client using the key from .env
        # os.environ["GEMINI_API_KEY"] loads the key saved to .env file
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

        # 2. Construct the detailed prompt (The Prompt Engineering)
        prompt = f"""
        You are a professional children's book author specializing in writing short, engaging picture books for a 2-year old audience. Your task is to write a complete, very simple picture book manuscript based on the user's inputs.
        USER INPUTS:
        - PROTAGONIST: {protagonist}
        - MAIN TOPIC/LESSON: {topic}
        - STYLE/TONE:        {style}

        CONSTRAINTS:
        1. The entire book must be **8 pages** long, no more, no less.
        2. Each page must contain **one single, simple sentence** (maximum 8 words) using basic, rhythmic, and high repetiive language appropriate for a 2-year old.
        3. The story must clearly feature the PROTAGONIST and address the MAIN TOPIC/LESSON.

        OUTPUT FORMAT: Your entire output must be formatted as a numbered list with two parts per page, following the exact structure below. Do not include any other text, titles, or introduction outiside of this list.

        1. **PAGE TEXT:** [The simple page sentence]
           **ILLUSTRATION PROMPT:** [Clear, descriptive, simple prompt for an image generator, using the style/tone: {style}]

        2. **PAGE TEXT:** [...]
           **ILLUSTRATION PROMPT:** [...]
        [Continue through page 8]
        """

        # Configure the model call for creativity
        config = types.GenerateContentConfig(
            temperature=0.8,
            max_output_tokens=1024
        )

        # 4. Make the API call
        print("\n*Connecting to Storyteller AI...Generating your story.*")
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=config
        )

        # 5. Print the result
        print("\n\n--- THE STORYTELLER LAB PRESENTS ---\n")
        print(response.text)
        print ("\n----------------------------------------------")
    except Exception as e:
        print(f"\nAn error occurred during API call. Error: {e}")
        print("Please ensure your GEMINI_API_KEY is correct and active in your .env file.")



##############################################################
########## Testing Block - Run to test this function #########
##############################################################

if __name__ == "__main__":
    story_parameters = get_user_inputs()
    if story_parameters:
        generate_story(
            story_parameters["protagonist"],
            story_parameters["topic"],
            story_parameters["style"]
        )

    
