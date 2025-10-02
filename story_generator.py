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
- **ACTION:** Confirm the three pieces of input (Protagonist, Topic, Style). State clearly that the final manuscript will be **16 pages long** and will use **Level A (Pre-Reader)** vocabulary, meaning sentences will be very short (max 8 words) with strong rhythmic repetition. Ask the user to confirm these details are correct, and state that when they are ready, they should **type 'START STORY'** to begin the final manuscript creation.
 
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

# Catches the Gemini Client to prevent it from closing
@st.cache_resource
def get_gemini_client(api_key):
    """Initializes and caches the Gemini client for the session lifetime."""
    return genai.Client(api_key=api_key)

# Initializing the Gemini Chat
def initialize_gemini_chat():
    """Initializes the Gemini client and a new chat session."""
    if not GEMINI_API_KEY:
        st.error("Error: GEMINI_API_KEY not found. Please check your .env file.")
        return None
    
    client = get_gemini_client(GEMINI_API_KEY)
    config = types.GenerateContentConfig(system_instruction=MASTER_PROMPT)

    # Use the model that is proven to handle constraints
    chat = client.chats.create(model='gemini-2.5-flash', config=config)

    # Save the new chat object, but history is empty until the user starts
    st.session_state.gemini_chat = chat
    st.session_state.messages = []

# Displaying History
def display_history():
    """Displays all messages stored in session state."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Check if the AI is asking for the GENERATE command  
def is_ready_to_generate():
    """Checks the last AI message to see if the user needs to type GENERATE."""
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
        last_ai_message = st.session_state.messages[-1]["content"]
        # ### --- MODIFIED: Check for the new prompt text to trigger GENERATE --- ###
        return "type 'START STORY'" in last_ai_message
    return False


##################################################################################
############################ Streamlit Application Core ##########################
##################################################################################

def main():

    # --- SUCCESS MESSAGE CHECK (FOR AUTO-SCROLL RETURN) ---
    if 'story_complete' in st.session_state and st.session_state.story_complete:
        st.success("✅ Manuscript is Ready! Scroll down to the end of the conversation to see the full story.")
        st.session_state.story_complete = False # Reset the flag

    # ### --- REMOVED: input_placeholder is gone! --- ###


    # --- DESIGN (Apply a clear header and separation) --- 
    with st.container():
        st.title("📚 The Storyteller Lab (Toddler Focus) ✏️")
        st.divider() # Horizontal line
        st.markdown("<br><br>", unsafe_allow_html=True) 

    # --- SESSION STATE SETUP ---
    if "gemini_chat" not in st.session_state:
        st.session_state.messages = []
        initialize_gemini_chat() 
        st.session_state.chat_initiated = False 

    # --- CHAT INITIATION LOGIC: Show start button if chat hasn't begun ---
    if not st.session_state.chat_initiated:
        if st.button("Start New Story Conversation", type="primary"):
            st.session_state.chat_initiated = True
            
            # Call API to get Stage 1 response
            with st.spinner("Initializing The Storyteller..."):
                first_response = st.session_state.gemini_chat.send_message("") 
            
            st.session_state.messages.append({"role": "assistant", "content": first_response.text})
            st.rerun() 

        display_history()
        return # STOP execution here if we are waiting for the button to be pressed


    # --- CHAT HISTORY DISPLAY ---
    display_history()


    # --- USER INPUT HANDLER (Uses the stable st.chat_input) ---
    
    # 1. Determine prompt label and GENERATE check
    last_message = st.session_state.messages[-1]["content"] if st.session_state.messages else ""
    ready_to_generate = is_ready_to_generate() 

    if ready_to_generate:
        # User must type GENERATE
        input_label = "✨ Type 'START STORY' and press enter to create the manuscript! ✨"
    else:
        # Standard chat reply
        input_label = "Start the conversation or type your answer here..."
        
    # 2. Get input from the fixed-position chat bar
    if user_input := st.chat_input(input_label):
        
        prompt = user_input
        
        # Check for the GENERATE command
        if ready_to_generate and prompt.upper() == "START STORY":
            prompt = "GENERATE"
        elif ready_to_generate and prompt.upper() != "START STORY":
            # If user types anything but GENERATE when prompted, ignore and stop here
            return

        # ### --- FIX FOR DOUBLE SUBMIT BUG (One-run processing) --- ###
        # 3. Add user message to history immediately
        st.session_state.messages.append({"role": "user", "content": prompt})

        # 4. Send user input to the active chat session and get response in the same run
        with st.spinner("The Storyteller is thinking..."):
            
            try:
                response = st.session_state.gemini_chat.send_message(prompt)
                ai_response = response.text
                
                # 5. Add AI response to history
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
            
                # 6. Check for completion and trigger auto-scroll
                if "Project Complete!" in ai_response:
                    st.session_state.story_complete = True # Set flag for success message
                
            except Exception as e:
                # Error handling
                error_message = str(e)
                if "503" in error_message or "overloaded" in error_message.lower():
                    st.error("🔃 Gemini is experiencing high traffic. Please wait a moment and try again.")
                elif "429" in error_message:
                    st.error("🔃 Rate limit reached. Please wait a minute before trying again.")
                else:
                    st.error(f"❌ An error occured: {error_message}")

                # If API fails, remove the user message that was just added
                st.session_state.messages.pop()
        
        # 7. Final rerun to update the display (shows both user message and AI response)
        st.rerun() 

# Run the main function
if __name__ == "__main__":
    main()