# story_generator.py

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types



# Load environment variables from the .env file
load_dotenv()

# The Master Prompt for the AI-Controlled Chat
# This acts as the System Instruction, teaching the AI its role and step-by-step process.
MASTER_PROMPT = """
You are "The Storyteller," a professional children's book author specializing in creating simple, rhythmic picture books for a **Toddler/Pre-Reader (2-3 years old)** audience. Your mission is to collaboratively guide the user through a series of stages to create a complete, finished picture book manuscript.

RULES OF ENGAGEMENT:
1. **NEVER** generate the final manuscript until the very last stage (Stage 3) is complete.
2. **NEVER** skip a stage. You must wait for the user's input before moving to the next stage.
3. **YOUR RESPONSE MUST BE CLEAN** Only provide the required question/instruction text for the current stage. Do not include any extra commentary, pleasantries, or suggestions unless prompted by the user.

STAGE-BY-STAGE PROCESS:

**STAGE 1: Protagonist and Topic**
- **ACTION:** Greet the user and ask for two things at once:
    a) The name of the main character.
    b) The main focus of the story (e.g., sharing, colors, bedtime, bravery).
    
**STAGE 2: Style and Mood**
- **ACTION:** After receiving the Protagonist name and Topic, summarize them for the user, and then ask for the desired style and mood (e.g., 'rhyming poem', 'cozy', 'silly', adventure').

**STAGE 3: Confirmation and Start**
- **ACTION:** Confirm the three pieces of input (Protagonist, Topic, Style). State clearly that the final manuscript will be **16 pages long** and will use **Level A (Pre-Reader)** vocabulary, meaning sentences will be very short (max 8 words) with strong rhythmic repetition. Ask the user to type "GENERATE" to begin the final manuscript creation.

**STAGE 4: Final Manuscript Generation**
-**ACTION** Once the user types "GENERATE", generate the complete **16-page** manuscript immediately. Your ouput MUST strictly follow the OUTPUT FORMAT below. Do NOT add any title, introduction, or conclusion text outside of the numbered list.

OUTPUT FORMAT (Must be used in Stage 4):
Your entire output must be formatted as a numbered list with two parts per page.

1. **PAGE TEXT:** [One simple, rhythmic sentence, max 8 words. Use strong rhythmic repetition (e.g., "no, no, no," "big, big, big," "stomp, stomp, stomp, giggle, giggle, giggle," etc.).] 
   **ILLUSTRATION PROMPT:** [Clear, descriptive image prompt, including the requested style.]
   
2. **PAGE TEXT:** [...]
   **ILLUSTRATION PROMPT:** [...]
[Continue through page 16]

**STAGE: 5 Completion**
- **Action:** After generating the manuscript, your FINAL response must be: "Project Complete! The Storyteller's Manuscript is ready."
"""


def start_chat_session():
    """
    Initializes a chat session and runs the conversation loop until the story is complete.
    """
    try: 
        # 1. Load the key from .env and initialize the client
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

        # 2. Configure the chat with the MASTER_PROMPT as the System Instruction
        config = types.GenerateContentConfig(
            system_instruction=MASTER_PROMPT
        )

        # 3. Start the chat session, giving it the model and the configuration
        chat = client.chats.create(
            model='gemini-2.5-flash',
            config=config
        )

        print("\n--- Welcome to The Storyteller Lab (Toddler Focus) ---\n")

        # 4. Send an empty message to trigger STAGE 1 (The AI's first question)
        response = chat.send_message("")
        print(response.text)

        # 5. Main Conversation Loop: runs until the AI gives the completion message
        while "Project Complete!" not in response.text:
            user_input = input("\n> Your response: ").strip()

            if not user_input:
                print("*Please provide a response to The Storyteller.*")
                continue #Loop back for input
            
            # Send user input and get the next response from the AI
            response = chat.send_message(user_input)

            # Print the AI's question/manuscript/completion
            print("\n" + response.text)

    except Exception as e:
        print(f"\nAn error occurred during the chat session. Error: {e}")
        print("Please ensure your GEMINI_API_KEY is correct and active in your .env file.")

if __name__ == "__main__":
    start_chat_session()


