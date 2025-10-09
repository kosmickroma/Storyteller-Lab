# 📖 Storyteller Lab: AI-Powered Personalized Children's Books
<div align="center">
<img src="https://raw.githubusercontent.com/kosmickroma/Storyteller-Lab/main/assets/storyteller_lab_logo.png" alt="Storyteller Lab Logo" width="300"/>
Show Image
Show Image
Show Image
Try the Live Demo →
</div>

🎯 What This Does
Creates personalized, illustrated children's books in seconds. You provide:

Character name & description
Story topic
Style preference

The AI generates a complete 16-page book with consistent artwork.
🔥 The Hard Problem I Solved
Challenge: AI image generators struggle with character consistency across multiple images.
My Solution:

Multi-stage prompt validation system
RegEx-based quality control
LLM self-correction loops
Explicit attribute enforcement in system prompts

Result: 90%+ visual consistency across 16 generated images.

🚀 Live Example: "Marcel Meets Dinosaurs"
<div align="center">
Cover Design
<img src="https://raw.githubusercontent.com/kosmickroma/Storyteller-Lab/main/assets/cover.png" width="400" alt="Book cover showing Marcel the Badger"/>
Professional cover with AI-generated image and text overlay
Sample Pages Showing Character Consistency
<table>
<tr>
<td align="center" width="50%">
<img src="https://raw.githubusercontent.com/kosmickroma/Storyteller-Lab/main/assets/page_1.png" width="350" alt="Page 1"/>
<br/>
<strong>Page 1 (Rhyme A)</strong>
<br/>
<em>"Marcel built a machine, so grand."</em>
</td>
<td align="center" width="50%">
<img src="https://raw.githubusercontent.com/kosmickroma/Storyteller-Lab/main/assets/page_2.png" width="350" alt="Page 2"/>
<br/>
<strong>Page 2 (Rhyme A)</strong>
<br/>
<em>"To visit an ancient, green land."</em>
</td>
</tr>
<tr>
<td align="center">
<img src="https://raw.githubusercontent.com/kosmickroma/Storyteller-Lab/main/assets/page_3.png" width="350" alt="Page 3"/>
<br/>
<strong>Page 3 (Rhyme B)</strong>
<br/>
<em>"Whiz, bang, zoom! He traveled fast."</em>
</td>
<td align="center">
<img src="https://raw.githubusercontent.com/kosmickroma/Storyteller-Lab/main/assets/page_6.png" width="350" alt="Page 6"/>
<br/>
<strong>Page 6 (Rhyme D)</strong>
<br/>
<em>"Its neck was long, a leafy treat."</em>
</td>
</tr>
</table>
<img src="https://raw.githubusercontent.com/kosmickroma/Storyteller-Lab/main/assets/page_7.png" width="400" alt="Page 7"/>
Page 7 (Rhyme E) - "Marcel thought this dinosaur was neat."

Notice: Marcel's yellow hat, blue vest, and orange shorts stay consistent across all pages!

</div>

🛠️ Technical Stack
Frontend:       Streamlit
Text AI:        Google Gemini 2.5 Flash  
Image AI:       Google Imagen 3.0
Language:       Python 3.10+
Key Libraries:  Pillow (PIL), regex, python-dotenv
Why These Choices?

Gemini 2.5 Flash: Fast, structured output, perfect for constrained generation
Imagen 3.0: High-quality images, excellent at following detailed prompts
Streamlit: Rapid prototyping, easy deployment, interactive UI


💡 Key Technical Features
1. Advanced Prompt Engineering
The MASTER_PROMPT enforces strict structure using a multi-stage conversation flow:
pythonStage 1: Character definition (species, colors, clothing)
Stage 2: Story topic and style selection  
Stage 3: Manuscript generation (16 pages, AABB rhyme scheme)
Stage 4: Illustration prompt generation (single character focus)
This prevents the LLM from generating output prematurely and ensures consistent character attributes.
2. Automated Quality Validation Pipeline
pythonvalidate_and_fix_illustration_prompt()
├── RegEx checks for common AI errors
├── Corrects passive descriptions ("watching" → "standing in")
└── Enforces character consistency rules

nuclear_validate_manuscript()  
├── Verifies exactly 16 pages
├── Validates AABB rhyme scheme
└── Checks age-appropriate vocabulary (Level A)
3. Production-Ready Architecture

✅ Rate limiting (24-hour generation cooldown)
✅ Cost optimization (Streamlit caching with @st.cache_resource)
✅ Error handling with user-friendly feedback
✅ Scalable design for easy model upgrades


🎯 Business Viability
This is a proof-of-concept with commercial potential.
Monetization Strategy
TierFeaturesPriceFree1 book/24hrs, standard quality$0PremiumUnlimited books, high-res images, editable text$9.99/moPrintPhysical book via print-on-demand$19.99/book
Market Opportunity

Parents seek personalized content for children
No technical knowledge required - accessible to everyone
Low infrastructure costs, highly scalable
Print-on-demand integration adds revenue stream


📚 What I Learned Building This
Technical Insights

Multi-model orchestration requires careful design - Getting Gemini and Imagen to work together seamlessly required explicit system instructions and validation layers
Consistency is harder than quality - Individual images look great, but maintaining character consistency across 16 generations required RegEx validation, LLM self-correction, and explicit attribute tracking
Production thinking from day one - Implemented rate limits, caching, and cost management before launching, not after
User experience drives adoption - Simple inputs (3 questions) + beautiful outputs (professional book) = high engagement

Challenges Overcome

Challenge: Imagen sometimes ignored character attributes in prompts
Solution: Multi-stage validation that catches and corrects errors before generation
Challenge: Managing API costs for 16 image generations per book
Solution: Implemented 24-hour cooldown and efficient caching strategies


🚀 Try It Yourself
Launch the Live App →
Run Locally
bash# Clone the repository
git clone https://github.com/kosmickroma/Storyteller-Lab.git
cd Storyteller-Lab

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
echo "GOOGLE_API_KEY=your_api_key_here" > .env

# Run the app
streamlit run story_generator.py
You'll need a Google API key with access to Gemini and Imagen APIs.

🔮 Roadmap
Short Term (Next 2 Months)

 Title and text editing before generation
 Multiple illustration styles (watercolor, cartoon, realistic)
 Different age groups (board books, early readers, chapter books)

Medium Term (3-6 Months)

 User authentication and generation history
 Save and share books with unique URLs
 Export options (ePub, Kindle format)

Long Term (6+ Months)

 Print-on-demand integration (Printify/Lulu)
 Premium tier with GPT-4 + DALL-E 3 for higher quality
 Multi-language support
 Mobile app (iOS/Android)


👨‍💻 About Me
Kory R Karp | Aspiring AI Engineer
I built Storyteller Lab to demonstrate:

✅ Advanced prompt engineering and LLM orchestration
✅ Multi-model AI system design
✅ Full-stack AI application development
✅ Production-ready thinking (cost, performance, UX)

I'm currently seeking entry-level AI/ML Engineer or Python Developer roles (remote preferred).
Connect With Me

🔗 LinkedIn
💻 GitHub Portfolio
🌐 All Links
📧 kosmickroma@gmail.com


📄 License
This project is available under the MIT License. See LICENSE file for details.

<div align="center">
⭐ Star this repo if you find it interesting!
Built with ❤️ and a lot of prompt iteration
Showcasing the intersection of AI capabilities and practical application development
</div>