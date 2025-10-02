# story_generator.py


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
#### Testing Block - Run to test this function ###############
##############################################################

if __name__ == "__main__":
    parameters = get_user_inputs()
    if parameters:
        print("\n--- Parameters Captured Successfully ---")
        print(f"Protagonist: {parameters['protagonist']}")
        print(f"Topic:       {parameters['topic']}")   
        print(f"Style:       {parameters['style']}")
        print("---------------------------------------------")
        
    
