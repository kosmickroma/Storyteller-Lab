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

# ------ RATE LIMITING HELPER FUNCTIONS ------ #
# These functions manage the 24-hour generation cooldown using browser localstorage
def check_generation_cooldown():
    """
    Checks if 24 hours have passed since the last generation.
    Returns: (can_generate: bool, hours_remaining: float)
    
    HOW IT WORKS:
    - Reads ' last_generation_time' from session_state (which syncs with localStorage via JavaScript)
    - Compares it to current time
    - Returns True if 24+ hours passed, False otherwise
    """
    # EXPLANATION: We'll store the timestamp in session_state, which Streamlit manages
    # The timestamp gets written to localStorage via JavaScript 

    if 'last_generation_time' not in st.session_state:
        # No previous generation found, user can generate
        return True, 0
    
    # IMPORT: We need datetime to work with timestamps
    from datetime import datetime, timedelta

    # GET: The stored timestamp (format: "2025-10-07 14:30:00")
    last_time_str = st.session_state.last_generation_time

    # CONVERT: String timestamp back into a datetime object we can do math with
    last_time = datetime.strptime(last_time_str, "%Y-%m-%d %H:%M:%S")

    # CALCULATE: How much time has passed since last generation
    time_passed = datetime.now() - last_time

    # CHECK: Has 24 hours (1 day) passed?
    if time_passed >= timedelta(hours=24):
        # YES: Cooldown is over, user can generate again
        return True, 0
    else:
        # NO: Still in cooldown, calculate remaining time
        time_remaining = timedelta(hours=24) - time_passed
        hours_remaining = time_remaining.total_seconds() / 3600 # Convert to hours
        return False, hours_remaining
    

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
- **ACTION:** After receiving the Protagonist name and Topic in Stage 1, you MUST immediately respond with TWO parts:
    
    **PART 1 - CHARACTER DETAILS (FIRST LINE):**
    Your response MUST start with this exact format on the very first line:
    "CHARACTER DETAILS: [species] with [exact fur/skin color] fur/skin, [eye color] eyes, wearing [clothing description with exact colors], [size description], [any accessories]"
    
    **BE EXTREMELY SPECIFIC:**
    - Use exact color names (NOT "dark" or "light" - use "navy blue", "crimson red", "forest green")
    - Specify species if animal (rabbit, mouse, bear, fox, etc.)
    - Describe clothing with exact colors and style
    - Include size (small, tiny, etc.)
    - List any accessories (hat, bow, backpack, etc.)
    
    **EXAMPLE:** 
    "CHARACTER DETAILS: small gray mouse with dark gray fur, bright black eyes, wearing a blue and white striped space suit with orange boots and gloves, small round ears, long thin tail"
    
    **PART 2 - PROCEED TO STAGE 2:**
    After the CHARACTER DETAILS line, immediately summarize the protagonist and topic, then ask for Stage 2 (Style and Mood).
    
**CRITICAL:** Do NOT wait for user confirmation between Stage 1.5 and Stage 2. Generate CHARACTER DETAILS, then immediately ask for Style and Mood in the same response.

**STAGE 2: Style and Mood**
- **ACTION:** After receiving the Protagonist name and Topic, summarize them for the user, and then ask for the desired style and mood (e.g., 'rhyming poem', 'cozy', 'silly', adventure').

**STAGE 3: Confirmation and Start**
- **ACTION:** Confirm the three pieces of input (Protagonist, Topic, Style). 

**CRITICAL INSTRUCTION:** The Style and Mood from Stage 2 are ONLY instructions for your writing approach (tone, pacing, feel). Do NOT use style/mood words like "cozy", "silly", or "adventure" in the book title or story text unless the user's original Topic specifically included those words. The title must come from the Protagonist and Topic only.

Then create a short, catchy children's book title (3-5 words maximum) and present it in this EXACT format on its own line: "BOOK TITLE: [Your Title Here]". State clearly that the final manuscript will be **16 pages long** and will use **Level A (Pre-Reader)** vocabulary, meaning sentences will be very short (max 8 words) with strong rhythmic repetition. Ask the user to confirm these details are correct, and state that when they are ready, they should **type 'START STORY'** to begin the final manuscript creation.

**STAGE 4: Final Manuscript Generation**
-**ACTION** Once the user types "START STORY", generate the complete **16-page** manuscript immediately. Your output MUST strictly follow the OUTPUT FORMAT below. Do NOT add any title, introduction, or conclusion text outside of the numbered list.

OUTPUT FORMAT (Must be used in Stage 4):
Your entire output must be formatted as a numbered list with two parts per page.

**CRITICAL ILLUSTRATION RULES:**
- EVERY illustration prompt MUST start with the CHARACTER DETAILS from Stage 1.5
- The character's appearance (fur color, clothing, features) MUST stay identical across all 16 pages
- **SINGLE CHARACTER ONLY:** Include ONLY the protagonist. DO NOT add companion, friends, siblings, pets or other characters unless the PAGE TEXT explicitly names them. If the protagonist is alone in the text, they MUST be alone in the illustration. No teddy bears, no companion animals, no friends- just the protagonist.
- Describe the SPECIFIC PHYSICAL LOCATION for each scene. The character must be IN the location, not viewing it from elsewhere.

CORRECT EXAMPLES by story type:
  * Space adventure: "inside the rocket cockpit with control panels" NOT "by bedroom window looking at rocket"
  * Forest journey: "standing in the middle of tall pine trees with mushrooms at feet" NOT "looking at forest from house"
  * Ocean story: "swimming underwater surrounded by colorful fish and coral" NOT "looking at ocean from beach"
  * City adventure: "walking down busy sidewalk with tall buildings on both sides" NOT "watching city from car window"
  * Kitchen activity: "standing at the kitchen counter mixing bowl in hands" NOT "peeking into kitchen from doorway"
  * Playground: "sitting on the swing mid-air with playground equipment around" NOT "looking at playground from far away"

WRONG PATTERNS TO AVOID:
  * "watching X" / "looking at X" / "viewing X" - these create distance
  * "by the window" / "through the window" - this keeps character stuck inside
  * "from their room" / "in their bedroom" - avoid unless bedroom IS the setting
  
- If the story involves travel or exploration, show the character IN each new location, actively participating
- Secondary characters (companions, friends, etc.) must also maintain consistent appearance across all pages

1. **PAGE TEXT:** [One simple sentence, max 10 words. Use a strong, consistent **AABB rhyming structure** (page 1 rhymes with page 2, page 3 with page 4, etc.). Maintain a bold, bouncy, and rhythmic meter reminiscent of **Dr. Seuss**. Example: "Little Lola loves to leap high. She jumps and plays beneath the blue sky."] 
    **ILLUSTRATION PROMPT:** [Start with CHARACTER DETAILS, then describe the EXACT PHYSICAL LOCATION and scene action. Example: "white fluffy rabbit with bright blue eyes wearing orange space suit, sitting inside spaceship cockpit with colorful control buttons, looking excited through the front window at stars"]
    
2. **PAGE TEXT:** [...]
    **ILLUSTRATION PROMPT:** [CHARACTER DETAILS + specific location + action]
    
[Continue through page 16]

**STAGE: 5 Completion**
- **Action:** After generating the manuscript, your FINAL response must be: "Project Complete! The Storyteller's Manuscript is ready."
"""

# --- GLOBAL STYLE SETTINGS FOR IMAGE GENERATION ---
GLOBAL_IMAGE_STYLE = "children's book illustration, vintage style cartoon, 80s and 90s aesthetic, soft pastel colors, dreamy lighting, crayon texture, grainy texture, soft fuzzy lines, simple shapes, whimsical, fantastical, professional digital painting, CRITICAL: character must maintain exact colors as described in character details, consistent character appearance across all illustrations, no color variations allowed"


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
    
################################################################################################
############################ PROMPT VALIDATOR & AUTO-CORRECTOR #################################
################################################################################################

# ------------------ PROMPT VALIDATOR & AUTO-CORRECTOR ------------------ #
def validate_and_fix_illustration_prompt(prompt: str, character_details: str, page_number: int) -> str:
    """
    Validates and corrects illustration prompts to ensure they follow the rules.
    
    This is a safety net that catches common Gemini mistakes BEFORE image generation:
    1. Ensures CHARACTER DETAILS are at the start
    2. Removes "watching/looking at" passive language
    3. Fixes location issues (removes "by window", "from room")
    4. Ensures character is IN the location, not observing it
    
    Args:
        prompt: The original illustration prompt from Gemini
        character_details: The CHARACTER DETAILS from Stage 1.5
        page_number: Current page number (for logging)
    
    Returns:
        Fixed/validated prompt ready for Imagen
    """
    
    original_prompt = prompt
    fixed = False
    
    # STEP 1: Ensure CHARACTER DETAILS are present
    if character_details not in prompt:
        # Character details missing! Add them at the start
        prompt = f"{character_details}, {prompt}"
        fixed = True
    
    # STEP 2: Remove passive "watching/looking at" language
    # These phrases create distance - character should BE in the scene
    passive_patterns = [
        (r'\blooking at\b', 'surrounded by'),
        (r'\bwatching\b', 'with'),
        (r'\bviewing\b', 'in'),
        (r'\bobserving\b', 'near'),
        (r'\bseeing\b', 'with'),
        (r'\bgazing at\b', 'surrounded by'),
        (r'\bstaring at\b', 'near')
    ]
    
    for pattern, replacement in passive_patterns:
        if re.search(pattern, prompt, re.IGNORECASE):
            prompt = re.sub(pattern, replacement, prompt, flags=re.IGNORECASE)
            fixed = True
    
    # STEP 3: Fix "by the window" and similar distancing phrases
    # These keep character stuck in one place watching the adventure
    distancing_fixes = [
        (r'\bby the window\b', 'inside with'),
        (r'\bthrough the window\b', 'inside looking out at'),
        (r'\bfrom their room\b', 'in the scene with'),
        (r'\bfrom the bedroom\b', 'in the adventure with'),
        (r'\bfrom their\b', 'with their'),
        (r'\bin their bedroom looking\b', 'in the adventure'),
        (r'\bin the backyard looking at\b', 'with'),
        (r'\bstanding near and watching\b', 'standing with'),
        (r'\bnext to .* looking at\b', 'with')
    ]
    
    for pattern, replacement in distancing_fixes:
        if re.search(pattern, prompt, re.IGNORECASE):
            prompt = re.sub(pattern, replacement, prompt, flags=re.IGNORECASE)
            fixed = True
    
    # STEP 4: Remove repetitive "in their [location] watching" patterns
    # Common mistake: "in their bedroom watching a rocket" should be "inside the rocket"
    if re.search(r'\bin their (bedroom|room|house|home)\b', prompt, re.IGNORECASE):
        if page_number > 3:  # After setup pages, character should be in the adventure
            # Don't specify where - just remove the "in their room" part
            prompt = re.sub(r'\bin their (bedroom|room|house|home)\b', 'in the adventure', prompt, flags=re.IGNORECASE)
            fixed = True

    # STEP 5: Remove phrases that might add extra characters
    # The story should only have ONE character unless text says otherwise
    extra_character_patterns = [
        (r'\bwith (a |an |another )?friend\b', 'alone'),
        (r'\bwith (a |an |another )?companion\b', 'alone'),
        (r'\band (a |an |another )?mouse\b', ''),  # Specific to prevent "and another mouse"
        (r'\band (a |an |another )?bear\b', ''),
        (r'\band (a |an |another )?rabbit\b', ''),
        (r'\band (a |an |another )?character\b', ''),
        (r'\bwith others\b', 'alone'),
        (r'\btogether with\b', 'near'),
        (r'\baccompanied by\b', 'near'),
        (r'\bwith (a |an )?(small |tiny )?teddy bear\b', ''),  # Remove teddy bears
        (r'\bholding (a |an )?(small |tiny )?companion\b', ''),
        (r'\bwith (a |an )?pet\b', ''),
        (r'\bwith (a |an )?sibling\b', ''),
        (r'\bwith (their )?friend\b', 'alone'),
    ]
    
    for pattern, replacement in extra_character_patterns:
        if re.search(pattern, prompt, re.IGNORECASE):
            prompt = re.sub(pattern, replacement, prompt, flags=re.IGNORECASE)
            fixed = True
    
    # Clean up any double spaces or awkward phrasing created by removals
    prompt = re.sub(r'\s+', ' ', prompt).strip()
    prompt = re.sub(r',\s*,', ',', prompt)  # Remove double commas
    prompt = re.sub(r',\s*alone', '', prompt)  # Remove awkward ", alone" at end
    
    # LOG if we made fixes (only in debug mode)
    if fixed and st.session_state.get('show_debug', False):
        st.session_state.setdefault('prompt_fixes', []).append({
            'page': page_number,
            'original': original_prompt,
            'fixed': prompt
        })
    
    return prompt

########################################################################################################
############################ NUCLEAR OPTION: GEMINI SELF-VALIDATION ####################################
########################################################################################################

def nuclear_validate_manuscript(client, raw_manuscript: str, character_details: str, story_theme: str) -> str:
    """
    The NUCLEAR OPTION: Uses Gemini to validate and fix its own illustration prompts.
    
    This catches issues that regex can't, like:
    - Character stuck inside when they should be exploring
    - Passive observation instead of active participation
    - Any other creative ways Gemini finds to avoid following instructions
    
    Args:
        client: Gemini API client
        raw_manuscript: The complete 16-page manuscript text
        character_details: CHARACTER DETAILS from Stage 1.5
        story_theme: Detected story theme (space, ocean, forest, etc.)
    
    Returns:
        Corrected manuscript with fixed illustration prompts
    """
    
    st.toast("🔧 Running quality validation on your story...")
    
    # Build the validation prompt
    validation_prompt = f"""
You are a quality control editor for children's book illustrations. Your job is to review illustration prompts and fix any that show the character as a PASSIVE OBSERVER instead of an ACTIVE PARTICIPANT.

**STORY THEME:** {story_theme}

**CHARACTER DETAILS:** {character_details}

**CRITICAL RULES:**
1. If the story involves travel/exploration (space, ocean, forest, city, etc.), the character must be IN each new location, not viewing it from elsewhere
2. The character should NEVER be "inside looking at" or "watching" the adventure - they should BE IN the adventure
3. For travel stories: Character should be INSIDE vehicle during travel, then OUTSIDE exploring at destinations
4. Remove phrases like "inside the rocket/ship/vehicle" when character should be exploring
5. Keep character details IDENTICAL across all pages

**COMMON MISTAKES TO FIX:**
- "inside the rocket on the planet surface" → "standing on the planet surface"
- "in the cockpit with alien landscape visible" → "walking on the alien landscape"
- "inside looking at the ocean" → "swimming in the ocean"
- "in the vehicle watching the forest" → "standing among the trees in the forest"

**MANUSCRIPT TO REVIEW:**
{raw_manuscript}

**YOUR TASK:**
Review each ILLUSTRATION PROMPT (there are 16 total). For any prompt where the character is stuck inside/watching instead of actively participating:
1. Rewrite ONLY that illustration prompt
2. Keep the PAGE TEXT unchanged
3. Maintain character consistency
4. Ensure character is IN the location, not viewing it

**OUTPUT FORMAT:**
Return the COMPLETE manuscript with all 16 pages. Only change illustration prompts that need fixing. Keep everything else identical, including all numbering and formatting.

If no changes are needed, return the manuscript exactly as provided.
"""

    try:
        # Call Gemini to validate and fix the manuscript
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=validation_prompt
        )
        
        corrected_manuscript = response.text
        
        # Store validation info for debug view
        if corrected_manuscript != raw_manuscript:
            st.session_state.nuclear_validation_applied = True
            st.session_state.nuclear_changes_made = "Manuscript was improved by quality validation"
        else:
            st.session_state.nuclear_validation_applied = False
            
        return corrected_manuscript
        
    except Exception as e:
        st.warning(f"⚠️ Validation check failed: {str(e)[:100]}... Using original manuscript.")
        return raw_manuscript

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
            if 'protagonist_description' in st.session_state:
                character_desc = st.session_state.protagonist_description

                # VALIDATE & FIX the prompt before using it
                page_count = len(pages) + 1 # Current page number
                corrected_prompt = validate_and_fix_illustration_prompt(
                    illustration_content,
                    character_desc,
                    page_count
                )

                # ENHANCED: Add explicit color emphasis
                # Extract specific colors from character description to reinforce them
                color_keywords = []
                if 'red' in character_desc.lower():
                    color_keywords.append('red')
                if 'blue' in character_desc.lower():
                    color_keywords.append('blue')
                if 'orange' in character_desc.lower():
                    color_keywords.append('orange')
                if 'green' in character_desc.lower():
                    color_keywords.append('green')
                if 'purple' in character_desc.lower():
                    color_keywords.append('purple')
                if 'yellow' in character_desc.lower():
                    color_keywords.append('yellow')
                if 'white' in character_desc.lower():
                    color_keywords.append('white')
                if 'black' in character_desc.lower():
                    color_keywords.append('black')
                if 'gray' in character_desc.lower() or 'grey' in character_desc.lower():
                    color_keywords.append('gray')
                
                # Build color emphasis string
                if color_keywords:
                    color_emphasis = f"MAINTAIN EXACT COLORS: {', '.join(color_keywords)} as specified in character details"
                else:
                    color_emphasis = "maintain exact character colors as described"

                final_image_prompt = f"{GLOBAL_IMAGE_STYLE}, SINGLE CHARACTER ONLY: {character_desc}, {corrected_prompt}, {color_emphasis}, character appearance must be identical across all pages, no other characters visible, protagonist alone in scene"
            else:
                final_image_prompt = f"{GLOBAL_IMAGE_STYLE}, {illustration_content}"

            pages.append({
                "page_text": page_text,
                "image_prompt": final_image_prompt,
                "generated": False # Flag to track image generation status
            })
    return pages

# ------------------ GENERATE COVER IMAGE WITH TITLE OVERLAY ------------------ #
def generate_cover_image(client, protagonist_description: str, title: str, story_theme: str = ""):
    """
    Generates a professional, dynamic cover image for the book WITH TITLE TEXT OVERLAY.
    
    Args:
        client: Gemini API client
        protagonist_description: Detailed character description from Stage 1.5
        title: Book title (will be overlaid on the image)
        story_theme: Main theme/setting of the story (e.g., "space adventure", "forest journey")
    
    Returns:
        Generated image object with title text overlaid
    """
    
    # Check if cover is already cached
    if 'cover_image' in st.session_state:
        return st.session_state['cover_image']

    st.toast("🎨 Creating your professional book cover...")

    try:
        # PROFESSIONAL COVER COMPOSITION TECHNIQUES
        composition_styles = [
            "dynamic diagonal composition with character in action pose",
            "character leaping forward toward viewer with outstretched arms",
            "low angle hero shot looking up at character",
            "character in mid-jump with exciting background behind them"
        ]
        
        # Select a random dynamic composition
        import random
        composition = random.choice(composition_styles)
        
        # ENHANCED: Extract colors from character description (same as story pages)
        color_keywords = []
        desc_lower = protagonist_description.lower()
        if 'red' in desc_lower:
            color_keywords.append('red')
        if 'blue' in desc_lower:
            color_keywords.append('blue')
        if 'orange' in desc_lower:
            color_keywords.append('orange')
        if 'green' in desc_lower:
            color_keywords.append('green')
        if 'purple' in desc_lower:
            color_keywords.append('purple')
        if 'yellow' in desc_lower:
            color_keywords.append('yellow')
        if 'white' in desc_lower:
            color_keywords.append('white')
        if 'black' in desc_lower:
            color_keywords.append('black')
        if 'gray' in desc_lower or 'grey' in desc_lower:
            color_keywords.append('gray')
        
        # Build color emphasis string
        if color_keywords:
            color_emphasis = f"MAINTAIN EXACT COLORS: {', '.join(color_keywords)} as specified in character details"
        else:
            color_emphasis = "maintain exact character colors as described"
        
        # BUILD: Professional cover prompt with character consistency
        cover_prompt = f"""
{GLOBAL_IMAGE_STYLE}, professional children's book cover illustration, 

COVER REQUIREMENTS:
- ABSOLUTELY NO TEXT of any kind in the generated image
- NO letters, NO words, NO numbers, NO symbols, NO typography
- NO placeholder text, NO sample text, NO random characters
- The image must be PURE ILLUSTRATION with zero text elements
- Any text will make the image unusable
- Book cover composition with clear focal point

CHARACTER (MUST MATCH EXACTLY):
{protagonist_description}

{color_emphasis}

Character appearance must be IDENTICAL to the description above. This is the SAME character that appears in all story illustrations.

COMPOSITION:
{composition}, exciting and inviting, character is the clear focus, 

CRITICAL POSITIONING FOR TEXT OVERLAY:
- Character positioned in CENTER/MIDDLE 60% of image (vertical center)
- Top 15% of image MUST be simple clear background (sky/space/solid color) for title text
- Bottom 10% should be simple background for branding text
- Character's head should NOT be in the top 15% of the image
- Character should fill the middle area prominently
- Leave clear empty space at very top edge for text overlay

SETTING/THEME:
{story_theme if story_theme else 'exciting adventure setting'}, vibrant and colorful background that supports but doesn't overwhelm the character, sense of wonder and adventure

MOOD:
Joyful, adventurous, inviting, perfect for drawing in young readers, energetic and fun
        """.strip()

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

        # Extract the base image
        if result.generated_images:
            base_image = result.generated_images[0]
            
            # ADD PROFESSIONAL OUTLINED TEXT OVERLAY WITH BRANDING
            from PIL import Image, ImageDraw, ImageFont
            from io import BytesIO
            
            # Convert to PIL Image
            img = Image.open(BytesIO(base_image.image.image_bytes))
            draw = ImageDraw.Draw(img)
            
            # Image dimensions
            width, height = img.size
            
            # ==================== HELPER FUNCTION: OUTLINED TEXT ==================== #
            def draw_outlined_text(draw, position, text, font, outline_color='white', outline_width=6):
                """
                Draws text with thick white outline and transparent/hollow center.
                Perfect for children's book covers!
                """
                x, y = position
                
                # Draw the outline by drawing text multiple times in a circle pattern
                for offset_x in range(-outline_width, outline_width + 1):
                    for offset_y in range(-outline_width, outline_width + 1):
                        # Calculate distance from center
                        distance = (offset_x ** 2 + offset_y ** 2) ** 0.5
                        # Only draw if we're on the "ring" (outline only, not center)
                        if distance <= outline_width and distance >= outline_width - 2:
                            draw.text(
                                (x + offset_x, y + offset_y), 
                                text, 
                                font=font, 
                                fill=outline_color
                            )
                # Note: We do NOT fill the center - that's the "hollow" effect!
            
            # ==================== TITLE TEXT (BUBBLEGUM SANS - WHITE - NO BORDER) ==================== #
            try:
                # Start with good size for kids font
                title_font_size = int(width * 0.10)  # 10% of image width
                
                # Try to load Bubblegum Sans font
                font_paths = [
                    "fonts/BubblegumSans-Regular.ttf",  # Local font folder (most likely)
                    "./fonts/BubblegumSans-Regular.ttf",  # Alternative local path
                    "BubblegumSans-Regular.ttf",  # Same directory
                    "/usr/share/fonts/truetype/bubblegum/BubblegumSans-Regular.ttf",  # Linux
                    "C:\\Windows\\Fonts\\BubblegumSans-Regular.ttf",  # Windows
                ]
                
                title_font = None
                for font_path in font_paths:
                    try:
                        title_font = ImageFont.truetype(font_path, title_font_size)
                        break
                    except:
                        continue
                
                # Fallback if font not found
                if title_font is None:
                    title_font = ImageFont.load_default()
                    
            except:
                title_font = ImageFont.load_default()
            
            # Check if title fits with SAFE MARGINS
            max_title_width = int(width * 0.88)  # Only use 88% of width (6% margin each side)
            bbox = draw.textbbox((0, 0), title, font=title_font)
            text_width = bbox[2] - bbox[0]
            
            # If too long, reduce size gradually
            while text_width > max_title_width and title_font_size > int(width * 0.05):
                title_font_size = int(title_font_size * 0.9)  # Reduce by 10%
                
                # Reload font at smaller size
                title_font = None
                for font_path in font_paths:
                    try:
                        title_font = ImageFont.truetype(font_path, title_font_size)
                        break
                    except:
                        continue
                
                if title_font is None:
                    title_font = ImageFont.load_default()
                    break
                
                # Re-measure
                bbox = draw.textbbox((0, 0), title, font=title_font)
                text_width = bbox[2] - bbox[0]
            
            # Position at top with proper margin
            x = (width - text_width) // 2
            y = int(height * 0.03)  # 3% from top
            
            # Draw simple drop shadow for depth (subtle)
            shadow_offset = 3
            draw.text((x + shadow_offset, y + shadow_offset), title, font=title_font, fill='#000000')
            
            # Draw main white text (clean and simple!)
            draw.text((x, y), title, font=title_font, fill='white')
            
            # ==================== BRANDING TEXT (BOTTOM) ==================== #
            try:
                # Smaller font for copyright
                brand_font_size = int(width * 0.04)  # 4% of image width
                try:
                    brand_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", brand_font_size)
                except:
                    try:
                        brand_font = ImageFont.truetype("arial.ttf", brand_font_size)
                    except:
                        brand_font = ImageFont.load_default()
            except:
                brand_font = ImageFont.load_default()
            
            # Branding text
            branding_text = "© Storyteller Lab"
            
            # Calculate position (centered at bottom)
            bbox = draw.textbbox((0, 0), branding_text, font=brand_font)
            brand_width = bbox[2] - bbox[0]
            
            brand_x = (width - brand_width) // 2
            brand_y = int(height * 0.93)  # 7% from bottom
            
            # Draw branding with subtle outline for readability
            outline_range = 2
            for adj_x in range(-outline_range, outline_range + 1):
                for adj_y in range(-outline_range, outline_range + 1):
                    draw.text((brand_x + adj_x, brand_y + adj_y), branding_text, font=brand_font, fill='black')
            
            # Draw main branding text (white)
            draw.text((brand_x, brand_y), branding_text, font=brand_font, fill='white')
            
            # ==================== SAVE AND RETURN ==================== #
            # Convert back to bytes
            output = BytesIO()
            img.save(output, format='JPEG', quality=95)
            output.seek(0)
            
            # Create return object
            class CoverImageWithTitle:
                def __init__(self, image_bytes):
                    self.image = type('obj', (object,), {'image_bytes': image_bytes})()
            
            cover_with_title = CoverImageWithTitle(output.getvalue())
            st.session_state['cover_image'] = cover_with_title
            return cover_with_title

    except Exception as e:
        error_message = str(e)
        st.error(f"❌ Cover generation failed: {error_message[:100]}...")
        st.session_state['cover_image'] = 'FAILED'
        return None
    
############################################################################################
############################ GENERATE PDF ##################################################
############################################################################################

def generate_pdf_book(title: str, cover_image_bytes, pages_data: list):
    """
    Generates a PDF of the story with cover + text/image pages.
    
    Args:
        title: Book title
        cover_image_bytes: Cover image data from Imagen
        pages_data: List of dicts with 'page_text' and image data
        
    Returns:
        PDF file as bytes (ready for download)
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    from io import BytesIO

    # Build the PDF in memory (not save to disk)
    # BytesIO creates a temp. file-like object in RAM
    buffer = BytesIO()

    # CREATE: A PDF canvas (blank document) with letter size pages
    pdf = canvas.Canvas(buffer, pagesize=letter)

    # GET: Page dimensions for positioning elements
    page_width, page_height = letter # 612 x 792 points (standard US letter)

    # -------- PAGE 1: COVER PAGE -------- #
    # TITLE: Draw the book title at the top
    pdf.setFont("Helvetica-Bold", 36) #Large, bold font
    pdf.drawCentredString(page_width / 2, page_height - 100, title)

    # COVER IMAGE: Place it in the center of the page 
    if cover_image_bytes and cover_image_bytes != 'FAILED':
        try: 
            # CONVERT: Image bytes to ImageReader format
            cover_img = ImageReader(BytesIO(cover_image_bytes))

            # CALCULATE: Image position (centered)
            img_width = 400 # Width in points
            img_height = 400 # Height in points
            x_position = (page_width - img_width) / 2 # Center horizontally
            y_position = (page_height - img_height) / 2 - 50 # Center vertically, nudge down

            # DRAW: The cover image
            pdf.drawImage(cover_img, x_position, y_position, width=img_width, height=img_height)
        except Exception as e:
            pass

    # BRANDING: Add "Storyteller Lab" at the bottom
    pdf.setFont("Helvetica", 12)
    pdf.drawCentredString(page_width / 2, 50, "Created with Storyteller Lab")

    # FINISH: This page and move to the next
    pdf.showPage()

    # ======== PAGES 2-17: STORY PAGES (TEXT + IMAGE SIDE BY SIDE) ======== #
    # LOOP: Through each of the 16 story pages
    for i, page in enumerate(pages_data):
        page_number = i + 1

        # LEFT SIDE: Story text
        # POSITION: Text in the left half of the page, vertically centered 
        text_x = page_width / 4 # Center of the left half 
        text_y = page_height / 2 # MIddle of page

        # FONT: Large, easy-to-read text for toddlers
        pdf.setFont("Helvetica-Bold", 24)

        # WRAP: Text if it's too long (split into multiple lines)
        text = page['page_text']
        max_width = 250 # Maximum width for text in points

        # Simple text wrapping: split by words and fit to width
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            # Check if line is too wide
            if pdf.stringWidth(test_line, "Helvetica-Bold", 24) <= max_width:
                current_line.append(word)
            else: 
                # Line is full, start new line
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        # Don't forget the last line
        if current_line:
            lines.append(' '.join(current_line))

        # DRAW: Each line of text, stacked vertically
        line_height = 30 # Space between lines
        start_y = text_y + (len(lines) * line_height / 2) # Start above center

        for idx, line in enumerate(lines):
            pdf.drawCentredString(text_x, start_y - (idx * line_height), line)

        # RIGHT SIDE: Illustration image
        # CHECK: If this page has a generated image in session_state
        image_key = f"image_page_{page_number}"

        if image_key in st.session_state:
            image_data = st.session_state[image_key]

            # SKIP: Failed images 
            if image_data != 'FAILED':
                try:
                    # CONVERT: Image bytes to ImageReader format
                    img_bytes = image_data.image.image_bytes
                    page_img = ImageReader(BytesIO(img_bytes))

                    # POSITION: Image in the right half of the page
                    img_size = 300 # Square image size
                    img_x = (page_width * 3 / 4) - (img_size / 2) # Center of right half
                    img_y = (page_height / 2) - (img_size / 2) # Vertically centered

                    # DRAW: The illustration
                    pdf.drawImage(page_img, img_x, img_y, width=img_size, height=img_size)
                except Exception as e:
                    # If image fails, just skip it
                    pass
            
        # PAGE NUMBER: Small page number at bottom
        pdf.setFont("Helvetica", 10)
        pdf.drawCentredString(page_width / 2, 30, f"Page {page_number}")
        # FINISH: This page and move to the next
        pdf.showPage()

    # ======== FINALIZE PDF ======== #
    # SAVE: Write all changes to the buffer
    pdf.save()

    # REWIND: Move the buffer's read position to the beginning
    buffer.seek(0)

    # RETURN: The PDF as bytes (ready for download)
    return buffer.getvalue()


########################################################################################################
############################ MAIN #######################################################################
########################################################################################################


def main():

    # Initialize a flag to prevent double-submission
    if 'processing_user_input' not in st.session_state:
        st.session_state.processing_user_input = False
    # ### --- REMOVED: input_placeholder is gone! --- ###
    # Add back the Streamlit page configuration and initialization
    

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

    if 'chat_initiated' not in st.session_state:
        st.session_state.chat_initiated = False

    if "gemini_chat" not in st.session_state:
        st.session_state.messages = []
        initialize_gemini_chat() 
        

    # --- CHAT INITIATION LOGIC: Show start button if chat hasn't begun ---
    # This block handles the initial screen and forces an exit (return) once the button is clicked or if the chat hasn't started yet.
    if not st.session_state.chat_initiated:

        # Check for button click FIRST, before creating columns
        button_clicked = False
        
        # Tip for better consistency
        st.info("💡 **Tip:** Repetitive story structures produce better visual consistency across pages.")

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
                                st.session_state.story_header,
                                st.session_state.get('story_theme', 'exciting adventure')
                            )

                    # Display the cover
                    if 'cover_image' in st.session_state:
                        cover_data = st.session_state['cover_image']
                        if cover_data == 'FAILED':
                            st.warning("Cover generation failed.")
                        else:
                            st.image(cover_data.image.image_bytes, caption="Your Story Cover")

                st.divider()

            # Info message directing users to the generate button 
            st.info("👇 Read your story below, then generate full illustrations or start over. (Limit: One full generation per 24 hours) ")

            # 🔍 DEBUG TOGGLE
            with st.expander("🔧 Developer Options"):
                st.session_state.show_debug = st.checkbox("Show image generation prompts", value=False)
                if st.session_state.get('protagonist_description'):
                    st.write("**Character Details Captured:**")
                    st.code(st.session_state.protagonist_description)
                
               # Show nuclear validation results
                if st.session_state.get('nuclear_validation_applied'):
                    st.write("**☢️ Nuclear Quality Validation:**")
                    st.success("✅ Gemini reviewed and improved the manuscript prompts")

                    if st.session_state.get('raw_manuscript_original') and st.session_state.get('raw_manuscript'):
                        with st.expander("📋 View Before/After Manuscripts"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write("**Original:**")
                                st.text_area("", st.session_state.raw_manuscript_original[:1000] + "...", height=200, key="original_ms")
                            with col2:
                                st.write("**Corrected:**")
                                st.text_area("", st.session_state.raw_manuscript[:1000] + "...", height=200, key="corrected_ms")

                # Show prompt fixes if any were made
                if st.session_state.get('prompt_fixes'):
                    st.write("**🔧 Automatic Prompt Corrections:**")
                    for fix in st.session_state['prompt_fixes']:
                        with st.expander(f"Page {fix['page']} - Fixed"):
                            st.write("❌ **Original (bad):**")
                            st.text(fix['original'][:200] + "..." if len(fix['original']) > 200 else fix['original'])
                            st.write("✅ **Corrected (good):**")
                            st.text(fix['fixed'][:200] + "..." if len(fix['fixed']) > 200 else fix['fixed'])

            # 2. Loop through each page for text and image generation/display
            for i, page in enumerate(st.session_state.parsed_pages):
                page_number = i + 1

                # Use st.container() to visually seperate each page
                with st.container(border=True):
                    st.markdown(f"**Page {page_number}**")

                    # 🔍 DEBUG: Show image prompts (toggle this on/off)
                    if st.session_state.get('show_debug', False):
                        with st.expander("🔍 Debug: View Image Prompt"):
                            st.code(page['image_prompt'], language="text")

                    # --- Check if we should generate images --- #
                    should_generate_images = st.session_state.get('generate_images', False)

                    # Create two columns for the text (left) and image (right)
                    if should_generate_images:
                        col1, col2 = st.columns([1,1])

                    else:
                        col1 = st.container()
                        col2 = None

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

                    if should_generate_images and col2 is not None:
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
                                else:
                                    st.image(image_data.image.image_bytes, caption=f"Illustration for Page {page_number}")

                            else: 
                                st.warning("Image generation failed for this page.")

            # --- Action Buttons --- #
            st.divider()

            # Disclaimer about image generation
            st.info("ℹ️ Image generation uses AI and may occasionally produce visual inconsistencies. Characters and details should be similar across pages but may not be perfectly identical.")

            # Create THREE columns to center the two buttons
            col1, col2, col3 = st.columns([1, 2, 1])

            # MIDDLE COLUMN: Both buttons centered
            with col2:
                # Check if images have been generated
                if not st.session_state.get('generate_images', False):
                    
                    # ------ CHECK RATE LIMIT BEFORE SHOWING BUTTON ------ #
                    # CALL our cooldown check function
                    can_generate, hours_left = check_generation_cooldown()

                    if can_generate:
                        # USER CAN GENERATE: Show the button
                        if st.button("🌙 Generate Full Illustrated Book 🧸", type="primary", key="generate_book_button", use_container_width=True):
                            # SAVE the current time when they click generate
                            from datetime import datetime
                            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            st.session_state.last_generation_time = current_time

                            # SET the flag to True to trigger image generation
                            st.session_state.generate_images = True

                            # RERUN to trigger image generation
                            st.rerun()

                    else:
                        # USER IN COOLDOWN: Show time remaining message instead of button
                        st.warning(f"⏰ You've used your free generation. Come back in {hours_left:.1f} hours for another!")

                        # ------ END RATE LIMIT CHECK ------ #
                # If images ARE generated, show download button
                else:
                    # DOWNLOAD PDF BUTTON
                    if st.button("📥 Download PDF Book", type="primary", key="download_pdf_button", use_container_width=True):
                        # Generate the PDF
                        with st.spinner("Creating your PDF..."):
                            # Get cover image bytes
                            cover_bytes = None
                            if 'cover_image' in st.session_state and st.session_state['cover_image'] != 'FAILED':
                                cover_bytes = st.session_state['cover_image'].image.image_bytes
                            
                            # Call PDF generation function
                            pdf_bytes = generate_pdf_book(
                                title=st.session_state.story_header,
                                cover_image_bytes=cover_bytes,
                                pages_data=st.session_state.parsed_pages
                            )

                            # Store PDF in session for download
                            st.session_state.pdf_file = pdf_bytes

                        st.success("✅ PDF ready for download!")

                    # If PDF exists, show download link
                    if 'pdf_file' in st.session_state:
                        from datetime import datetime
                        filename = f"storyteller_lab_{st.session_state.story_header.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d')}.pdf"

                        st.download_button(
                            label="💾 Save PDF to Computer",
                            data=st.session_state.pdf_file,
                            file_name=filename,
                            mime="application/pdf",
                            use_container_width=True
                        )    

                # Small spacing between buttons
                st.write("")

                # Reset button (always available)
                if st.button("🔃 Start New Story", type="secondary", key="reset_button", use_container_width=True):
                    # PRESERVE rate limit, clear everything else
                    # Save the cooldown timestamp before clearing
                    cooldown_time = st.session_state.get('last_generation_time', None)

                    # Clear all session state
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]

                    # Restore the cooldown timestamp so user can't spam by resetting 
                    if cooldown_time:
                        st.session_state.last_generation_time = cooldown_time

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

                # -------- EXTRACT CHARACTER DETAILS IMMEDIATELY -------- #
                # This catches the CHARACTER DETAILS from the very first AI response (Stage 1.5)
                if "CHARACTER DETAILS:" in ai_response and 'protagonist_description' not in st.session_state:
                    char_details_match = re.search(r"CHARACTER DETAILS:\s*(.+?)(?:\n|$)", ai_response)
                    if char_details_match:
                        st.session_state.protagonist_description = char_details_match.group(1).strip()
                        # Debug confirmation (optional - remove in production)
                        # st.toast(f"✅ Character locked: {st.session_state.protagonist_description[:50]}...")
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

                    # 2. NUCLEAR OPTION: Validate and fix the manuscript before parsing
                    corrected_manuscript = nuclear_validate_manuscript(
                    get_gemini_client(GEMINI_API_KEY),
                    raw_manuscript,
                    st.session_state.get('protagonist_description', 'the main character'),
                    st.session_state.get('story_theme', 'exciting adventure')
                )
                    
                    # Store both versions for debugging
                    st.session_state.raw_manuscript_original = raw_manuscript
                    st.session_state.raw_manuscript = corrected_manuscript
                    
                    # 3. Parse the CORRECTED manuscript
                    st.session_state.parsed_pages = parse_manuscript(corrected_manuscript)

                    # 2.5 EXTRACT STORY THEME for dynamic cover generation
                    # Analyze the first few pages to determine the main setting/theme
                    theme_keywords = {
                        'space': ['space', 'rocket', 'planet', 'star', 'moon', 'alien', 'galaxy', 'astronaut'],
                        'ocean': ['ocean', 'sea', 'fish', 'underwater', 'whale', 'coral', 'wave', 'beach'],
                        'forest': ['forest', 'tree', 'woods', 'jungle', 'animal', 'leaves', 'nature'],
                        'city': ['city', 'building', 'street', 'car', 'urban', 'downtown', 'sidewalk'],
                        'home': ['home', 'house', 'room', 'kitchen', 'bedroom', 'family'],
                        'playground': ['playground', 'park', 'swing', 'slide', 'playing', 'outside'],
                        'school': ['school', 'classroom', 'teacher', 'learn', 'friends', 'desk'],
                        'farm': ['farm', 'barn', 'tractor', 'animals', 'fields', 'country']
                    }
                    
                    # Check the manuscript text for theme keywords
                    manuscript_lower = raw_manuscript.lower()
                    theme_scores = {}
                    
                    for theme, keywords in theme_keywords.items():
                        score = sum(manuscript_lower.count(keyword) for keyword in keywords)
                        if score > 0:
                            theme_scores[theme] = score
                    
                    # Get the theme with highest score
                    if theme_scores:
                        detected_theme = max(theme_scores, key=theme_scores.get)
                        theme_descriptions = {
                            'space': 'outer space adventure with rockets, planets, and stars',
                            'ocean': 'underwater ocean adventure with sea creatures and coral',
                            'forest': 'forest adventure with tall trees and woodland creatures',
                            'city': 'city adventure with tall buildings and busy streets',
                            'home': 'cozy home setting with warm family atmosphere',
                            'playground': 'fun playground adventure with swings and friends',
                            'school': 'school adventure with learning and friendship',
                            'farm': 'farm adventure with animals and countryside'
                        }
                        st.session_state.story_theme = theme_descriptions.get(detected_theme, 'exciting adventure')
                    else:
                        st.session_state.story_theme = 'exciting adventure'

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