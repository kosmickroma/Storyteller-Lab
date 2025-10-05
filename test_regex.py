import re

# This is the actual text from your Stage 3 message (from earlier):
summary_text = """Okay, we have Rex the punk rock velociraptor, whose story is about going to a show, and the mood will be energetic.
The final manuscript will be **16 pages long** and will use **Level A (Pre-Reader)** vocabulary, meaning sentences will be very short (max 8 words) with strong rhythmic repetition.
Are these details correct? When you are ready, please type **'START STORY'** to begin the final manuscript creation."""

# Test the regex patterns
protagonist_match = re.search(r"we have ([^,]+),", summary_text)
topic_match = re.search(r"whose story is about ([^,]+),", summary_text)

print("Protagonist match:", protagonist_match)
if protagonist_match:
    print("  Captured:", protagonist_match.group(1))

print("\nTopic match:", topic_match)
if topic_match:
    print("  Captured:", topic_match.group(1))

# Show what the title would be
if protagonist_match and topic_match:
    protagonist = protagonist_match.group(1).strip()
    topic = topic_match.group(1).strip()
    title = f"A story about {protagonist} and {topic}"
    print("\nGenerated Title:", title)
else:
    print("\nGenerated Title: A Completed Manuscript (regex failed)")