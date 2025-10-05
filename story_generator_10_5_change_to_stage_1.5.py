# story_generator.py

import os
import streamlit as st
import re
from dotenv import load_dotenv
from google import genai
from google.genai import types


# Load environment variables from the .env file
load_dotenv()

# Get API key from environment for easy access
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

######################################################################################
############################ MASTER PROMPT "TODDLER" #################################
######################################################################################



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

**STAGE 1.5: Character Detail Generation**
- **ACTION:** After receiving the Protagonist name and Topic in Stage 1, immediately generate a **detailed** physical description of the Protagonist (e.g., specific colors, size, defining features, clothing, mood, unique characteristics). Present it to the user in this EXACT format on its own line: "CHARACTER DETAILS: [your detailed description here]". This description MUST be used as a prefix for all future ILLUSTRATION PROMPTS to maintain visual consistency.

**STAGE 2: Style and Mood**
- **ACTION:** After receiving the Protagonist name and Topic, summarize them for the user, and then ask for the desired style and mood (e.g., 'rhyming poem', 'cozy', 'silly', adventure').

**STAGE 3: Confirmation and Start**
- **ACTION:** Confirm the three pieces of input (Protagonist, Topic, Style). Then create a short, catchy children's book title (3-5 words maximum) and present it in this EXACT format on its own line: "BOOK TITLE: [Your Title Here]". State clearly that the final manuscript will be **16 pages long** and will use **Level A (Pre-Reader)** vocabulary, meaning sentences will be very short (max 8 words) with strong rhythmic repetition. Ask the user to confirm these details are correct, and state that when they are ready, they should **type 'START STORY'** to begin the final manuscript creation.
 
**STAGE 4: Final Manuscript Generation**
-**ACTION** Once the user types "START STORY", generate the complete **16-page** manuscript immediately. Your ouput MUST strictly follow the OUTPUT FORMAT below. Do NOT add any title, introduction, or conclusion text outside of the numbered list.

OUTPUT FORMAT (Must be used in Stage 4):
Your entire output must be formatted as a numbered list with two parts per page.

1. **PAGE TEXT:** [One simple sentence, max 10 words. Use a strong, consistent **AABB rhyming structure** (page 1 rhymes with page 2, page 3 with page 4, etc.). Maintain a bold, bouncy, and rhythmic meter reminiscent of **Dr. Seuss**. Example: "Little Lola loves to leap high. She jumps and plays beneath the blue sky."] 
    **ILLUSTRATION PROMPT:** [**Highly detailed and consistent** description of the Protagonist for consistency, followed by the scene description and requested style.]
    
2. **PAGE TEXT:** [...]
    **ILLUSTRATION PROMPT:** [...]
[Continue through page 16]

**STAGE: 5 Completion**
- **Action:** After generating the manuscript, your FINAL response must be: "Project Complete! The Storyteller's Manuscript is ready."
"""

# --- GLOBAL STYLE SETTINGS FOR IMAGE GENERATION ---
GLOBAL_IMAGE_STYLE = "children's book illustration, vintage style cartoon, 80s and 90s aesthetic, soft pastel colors, dreamy lighting, crayon texture, grainy texture, soft fuzzy lines, simple shapes, whimsical, fantastical, professional digital painting"



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

# Function to generate an image from a prompt
def generate_image_for_page(client, prompt: str, page_number: int):
    """
    Generates an image using the Gemini/Imagen model and caches it in session state.
    Returns the generated image object.
    """

    # Create a unique key for caching this specific image prompt
    cache_key = f"image_page_{page_number}"

    # 1. Check if the image is already cached
    if cache_key in st.session_state:
        return st.session_state[cache_key]

    st.toast(f"🎨 Generating image for Page {page_number}...")

    try: 
        # 2. Call the image generation
        # We use a reliable, high-quality model for this task
        result = client.models.generate_images(
            model='imagen-3.0-generate-002',
            prompt=prompt,
            config=dict(
                number_of_images=1,
                output_mime_type="image/jpeg",
                aspect_ratio="1:1" # Standard square for a picture book
            )
        )
        

        # 3. Extract the image object
        if result.generated_images:
            image_data = result.generated_images[0]
            # Save the image data directly to cache_key to avoid re-generation
            st.session_state[cache_key] = image_data
            return image_data
        
    except Exception as e:
        error_message = str(e)
        st.error(f"❌ Image generation failed for Page {page_number}. Error: {error_message[:100]}...")
        # Return None or a placeholder if generation fails
        # Cache the faliure status to prevent retrying on every rerun
        st.session_state[cache_key] = 'FAILED'
        
        return None
    
# Parse Manuscript
def parse_manuscript (full_text: str):
    """
    Parses the full 16-page manuscript string into a list of dictionaries,
    where each dictionary contains 'page_text' and 'image_prompt'.
    """

    pages = []
    # Split the text by the page numbering ("1.", "2.", etc.)
    # We use regex to handle any variation in spacing after the number.
    segments = re.split(r'\s*\d+\.\s*', full_text)

    # The first segment will be empty or a title, so we start from the second element.
    for segment in segments[1:]:
        # Split each segment into PAGE TEXT and ILLUSTRATION PROMPT
        if "ILLUSTRATION PROMPT:" in segment:
            parts = segment.split("ILLUSTRATION PROMPT:", 1)
            page_text = parts[0].replace("PAGE TEXT:", "").replace('*', '').strip()
            # Capture the description content from the Gemini output
            illustration_content = parts[1].strip()

            # COMBINE: Prepend the global style to the contextual description
            final_image_prompt = f"{GLOBAL_IMAGE_STYLE}, {illustration_content}"

            pages.append({
                "page_text": page_text,
                "image_prompt": final_image_prompt,
                "generated": False # Flag to track image generation status
            })
    return pages

# ------------------ GENERATE COVER IMAGE ------------------ #
def generate_cover_image(client, protagonist_description: str, title: str):
    """
    Generates a cover image for the book using the protagonist description and title.
    Returns the generated image object.
    """

    # Check if cover is already cached
    if 'cover_image' in st.session_state:
        return st.session_state['cover_image']

    st.toast("🎨 Creating your book cover...")

    try:
        #Create a cover-appropriate prompt
        cover_prompt = f"{GLOBAL_IMAGE_STYLE}, book cover illustration, NO text, NO letters, NO words in image, {protagonist_description} in a dynamic hero pose, exciting and inviting composition, perfect for a children's book cover"

        # Call the image generation
        result = client.models.generate_images(
            model='imagen-3.0-generate-002',
            prompt=cover_prompt,
            config=dict(
                number_of_images=1,
                output_mime_type="image/jpeg",
                aspect_ratio="1:1"
            )
        )

        # Extract and cache the image
        if result.generated_images:
            image_data = result.generated_images[0]
            st.session_state['cover_image'] = image_data
            return image_data

    except Exception as e:
        error_message = str(e)
        st.error(f"❌ Cover generation failed: {error_message[:100]}...")
        st.session_state['cover_image'] = 'FAILED'
        return None 

#########################################################################################################
############################ MAIN #######################################################################
#########################################################################################################


def main():

    # Initialize a flag to prevent double-submission
    if 'processing_user_input' not in st.session_state:
        st.session_state.processing_user_input = False
    # ### --- REMOVED: input_placeholder is gone! --- ###

#######################################################################################
########################### LOGO ######################################################
#######################################################################################

    # --- DESIGN (Apply a clear header and separation) --- 
    # Reduce top padding of the entire page
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 2rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    with st.container():
        # --- LOGO ---#
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.image("app_logo.png", width=400)

        # 2. Use st.markdown for the remaining centered text (Subtitle and Ages)
        st.markdown(
            """
            <div style="text-align: center;">
                <h2 style="font-size: 1.8em; font-weight: 300; margin-bottom: -0.1em;">🧸 Toddler Edition 🌙</h2>
                <p style="font-size: 1.4em; margin-top: -1.0em; font-weight: 300;">Ages 2-3</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.divider()

    # --- SESSION STATE SETUP ---
    if "gemini_chat" not in st.session_state:
        st.session_state.messages = []
        initialize_gemini_chat() 
        st.session_state.chat_initiated = False 

    # --- CHAT INITIATION LOGIC: Show start button if chat hasn't begun ---
    # This block handles the initial screen and forces an exit (return) once the button is clicked or if the chat hasn't started yet.
    if not st.session_state.chat_initiated:

        # Check for button click FIRST, before creating columns
        button_clicked = False
        
        # Three equal-width columns to center the button
        with st.container():
            col1, col2, col3 = st.columns([1,1,1])
            with col2: # Button in the middle column (col2)
                if st.button("Start New Story Conversation", type="primary", key="start_button"):
                    button_clicked = True
            
        # Handle the button click AFTER the columns context
        if button_clicked:
                st.session_state.chat_initiated = True

                # Call API to get Stage 1 response
                with st.spinner("Initializing The Storyteller..."):
                    first_response = st.session_state.gemini_chat.send_message("") 
            
                st.session_state.messages.append({"role": "assistant", "content": first_response.text})
                st.rerun()
                
                 
        return   
        
    # --- CHAT HISTORY DISPLAY ---
    if st.session_state.chat_initiated:
        # --- HIDE CONVERSATION WHEN STORY IS COMPLETE ---#
        # Only display the chat history if the final story flag is NOT set.
        if not st.session_state.get('story_complete', False):
            display_history()
        # Check if the final manuscript is complete and ready to display 
        if 'parsed_pages' in st.session_state and st.session_state.story_complete:

            # Success message appears right before the story
            st.success("🥳 Story is Ready! 🎉")

            # ------ DEBUG - CHECK TITLE GENERATION ------ #
            # Show what message we're trying to extract from
            #if len(st.session_state.messages) >= 2:
                #st.write("🔍 DEBUG - Stage 3 Message:")
                #st.write(st.session_state.messages[-2]['content'])
            #st.write("🔍 DEBUG - Generated Title:")
            #st.write(st.session_state.story_header)
            #st.divider()
            # ------------------ END DEBUG ----------------#

            # 1. Display the Header
            st.subheader("Storyteller Lab Presents:")
            st.title(st.session_state.story_header)
            st.divider()

            client = get_gemini_client(GEMINI_API_KEY) # Retrieve the client

            # -------- DISPLAY COVER IMAGE -------- #
            # Generate and display the book cover
            if 'protagonist_description' in st.session_state:
                with st.container(border=True):
                    st.markdown("**Book Cover**")

                    # Generate cover if not already done
                    if 'cover_image' not in st.session_state:
                        with st.spinner("Generating book cover..."):
                            generate_cover_image(
                                client,
                                st.session_state.protagonist_description,
                                st.session_state.story_header
                            )
                    # Display the cover
                    if 'cover_image' in st.session_state:
                        cover_data = st.session_state['cover_image']
                        if cover_data == 'FAILED':
                            st.warning("Cover generation failed.")
                        else:
                            st.image(cover_data.image.image_bytes, caption="Your Story Cover")

                st.divider()

            # 2. Loop through each page for text and image generation/display
            for i, page in enumerate(st.session_state.parsed_pages):
                page_number = i + 1

                # Use st.container() to visually seperate each page
                with st.container(border=True):
                    st.markdown(f"**Page {page_number}**")

                    # Create two columns for the text (left) and image (right)
                    col1, col2 = st.columns([1,1])

                    # LEFT COLUMN: Display the text
                    with col1:
                        st.markdown(
                            f"""
                            <div style="display: flex; align-items: center; justify-content: center; height: 100%; text-align: center;">
                                <p style="font-size: 2em; font-weight: bold; line-height: 1.4;">{page['page_text']}</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    # RIGHT COLUMN: Generate and display the image
                    with col2:
                        # Check if image is already generated/cached
                        if f"image_page_{page_number}" not in st.session_state:
                            # Only generate if the image is not already in the session state
                            with st.spinner(f"Generating image for Page {page_number}..."):
                                # The generate_image_for_page function will save it to session_state
                                generate_image_for_page(client, page['image_prompt'], page_number)

                        # Display the image once it exists (either freshly generated or cached)
                        if f"image_page_{page_number}" in st.session_state:
                            image_data = st.session_state[f"image_page_{page_number}"]
                            if image_data == 'FAILED':
                                st.warning("Image generation failed for this page.")
                            # The client gives us image data, which Streamlit can display
                            st.image(image_data.image.image_bytes, caption=f"Illustration for Page {page_number}")

                        else: 
                            st.warning ("Image generation failed for this page.")
                            st.markdown ("---") # Visual separator between pages
            # --- Reset Button --- #
            st.divider()
            col1, col2, col3 = st.columns([1,1,1])
            with col2:
                if st.button("🔃 Start New Story", type="primary", key="reset_button"):
                    # Clear all session state
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.rerun()
            # Stop execution here to avoid displaying the chat input placeholder on the final screen
            return

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
        # Check lock status and acquire lock immediately
        if st.session_state.processing_user_input:
            return
        
        prompt = user_input
        
        # Check for the GENERATE command
        if ready_to_generate and prompt.upper() == "START STORY":
            pass

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
                
                # --- MANUSCRIPT VISIBILITY CONTROL (For testing) ---
                # 5. Add AI response to history
                #st.session_state.messages.append({"role": "assistant", "content": ai_response})

                if "Project Complete!" not in ai_response:
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})

                # -------- EXTRACT CHARACTER DETAILS FROM STAGE 2 -------- #
                # Check if the AI provided character details (happens after Stage 1)
                if "CHARACTER DETAILS:" in ai_response:
                    char_details_match = re.search(r"CHARACTER DETAILS:\s*(.+?)(?:\n|$)", ai_response)
                    if char_details_match:
                        st.session_state.protagonist_description = char_details_match.group(1).strip()


                # 6. Check for completion and trigger auto-scroll
                if "Project Complete!" in ai_response:
                    st.session_state.story_complete = True # Set flag for success message
                
                    # Project Complete
                    # 1. Store the raw manuscipt text
                    raw_manuscript = ai_response.replace("Project Complete! The Storyteller's Manuscript is ready.", "").strip()
                    st.session_state.raw_manuscript = raw_manuscript

                    # 2. Immediately parse and store the page data
                    st.session_state.parsed_pages = parse_manuscript(raw_manuscript)

                    # 3. Extract the book title from Stage 3 message
                    # The AI was instructed to fromat it as "BOOK TITLE: [Title]"
                    summary_text = st.session_state.messages[-2]['content']

                    # Look for 'BOOK TITLE: " followed by the actual title
                    title_match = re.search(r"BOOK TITLE:\s*(.+?)(?:\n|$)", summary_text)

                    if title_match:
                        # Successfully extracted the title
                        book_title = title_match.group(1).strip()
                        st.session_state.story_header = book_title

                        # --------- EXTRACT CHARACTER DESCRIPTION -------- #
                        # EXTRACT CHARACTER DESCRIPTION (FALLBACK ONLY)"

                        # Only extract if we don't already have detailed character info
                        if 'protagonist_description' not in st.session_state:

                            char_match = re.search(r"we have ([^,]+)", summary_text)
                            if char_match:
                                st.session_state.protagonist_description = char_match.group(1).strip()
                            else: 
                                st.session_state.protagonist_description = "the main character"
                    # Fallback if the AI didn't follow the format
                    else: 
                        st.session_state.story_header = "A Storyteller Lab Creation"
                        st.session_state.protagonist_description = "the main character"


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