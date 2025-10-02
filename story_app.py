# story_generator.py

import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types



# Load environment variables from the .env file
load_dotenv()

# Get API key from environment for easy access
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

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


##########################################################################
########################### STREAMLIT LOGIC ##############################
##########################################################################

# Initializing the Gemini Chat
def initialize_gemini_chat():
    """Initializes the Gemini client and a new chat session."""
    if not GEMINI_API_KEY:
        st.error("Error: GEMINI_API_KEY not found. Please check your .env file.")
        return None
    
    client = genai.Client(api_key=GEMINI_API_KEY)
    config = types.GenerateContentConfig(system_instruction=MASTER_PROMPT)

    # Use the model that is proven to handle constraints
    chat = client.chats.create(model='gemini-2.5-flash', config=config)

    # Trigger Stage 1 by sending an empty message
    response = chat.send_message("")

    # Save the new chat object and the history
    # st.session_state is crucial: it saves data between runs
    st.session_state.gemini_chat = chat
    st.session_state.messages = [{"role": "assistant", "content": response.text}]

# Displaying History
def display_history():
    """Displays all messages stored in session state."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

##################################################################################
############################ Streamlit Application Core ##########################
##################################################################################

def main():
    # --- DESIGN (Will be improved later) --- 
    st.title ("📚 The Storyteller Lab (Toddler Focus) ✏️")

    # --- SESSION STATE SETUP ---
    # Check if the chat session has been initialized (i.e., if it's the first time running)
    if "gemini_chat" not in st.session_state:
        # Initialize the chat session if it's the first time running
        st.session_state.messages = []
        initialize_gemini_chat()

    # --- DISPLAY HISTORY --- #
    display_history()

    # --- USER INPUT HANDLER ---
    # st.chat_input replaces the old Python input() call
    if prompt := st.chat_input("Start the conversation or type your answer here..."):
        # 1. Add user message to history and display it
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Send user input to the active chat session
        with st.spinner("The Storyteller is thinking..."):
            # Use the saved chat object from session state
            response = st.session_state.gemini_chat.send_message(prompt)

            # 3 Add AI response to history and display it
            ai_response = response.text
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            with st.chat_message("assistant"):
                st.markdown(ai_response)

            # 4. Check for completion and give a nice message
            if "Project Complete!" in ai_response:
                st.info("🥳 Manuscript Generated! Scroll up to see the complete story and illustration prompts.")
                # Optionally disable the input after completion (requires a new session state variable if you want it disabled permanently)

# Run the main function
if __name__ == "__main__":
    main()


