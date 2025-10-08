# 📖 Storyteller Lab: AI-Powered Personalized Children's Books

<p align="center">
  <img src="https://github.com/kosmickroma/storyteller-lab/blob/main/assets/storyteller_lab_logo.png?raw=true" alt="Storyteller Lab Logo - A cute owl with a graduation cap on an open book" width="300"/>
</p>

[![Powered by Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://storyteller-lab-bj2d6p4ttwm7o3gjcnd5hs.streamlit.app/)
[![GitHub Repo stars](https://img.shields.io/github/stars/kosmickroma/storyteller-lab?style=social)](https://github.com/kosmickroma/storyteller-lab)
[![Follow on Linktree](https://img.shields.io/badge/Deploy%20&%20Links-Linktree-00A97E?style=flat&logo=linktree)](https://linktr.ee/korykarp?lt_utm_source=lt_admin_share_link#510380565)

**Live Demo:** [Storyteller Lab on Streamlit](https://storyteller-lab-bj2d6p4ttwm7o3gjcnd5hs.streamlit.app/)

---

## Project Overview

**Storyteller Lab** is an innovative, proof-of-concept application designed to generate **unique, fully-illustrated, and personalized children's picture books** on demand.

Developed to showcase advanced **Prompt Engineering**, **LLM orchestration**, and **Full-Stack AI integration**, this **working project** demonstrates a viable path toward creating a marketable product. It is currently in a testing phase to continuously refine output consistency.

### 🌟 Key Features

* **High Character Consistency:** Uses a multi-stage prompt validation system to ensure the protagonist maintains a **high degree of visual consistency** (e.g., core color, clothing, species) across all 16 pages, significantly mitigating a known generative AI challenge.
    * *(Note: As an active development project, minor variances in accessories or details may still appear, which will be resolved with future model integrations.)*
* **Structured Narrative:** Enforces a rigid structure (16 pages, **AABB rhyme scheme**, Level A vocabulary) using a custom `MASTER_PROMPT` as a system instruction for the LLM.
* **Dual-Model Orchestration:** Seamlessly integrates **Gemini 2.5 Flash** for highly-constrained text generation and **Imagen 3.0** for high-quality, professional illustrations.
* **Automated Quality Control:** Includes sophisticated **RegEx and LLM-based self-validation** (`validate_and_fix_illustration_prompt` and `nuclear_validate_manuscript` functions) to correct common AI errors like passive character placement ("watching the adventure" is corrected to "standing in the adventure").
* **Future Model Integration:** The architecture is designed for easy upgrading to newer, more capable foundation models, allowing for a **premium generation tier** with improved image quality and character fidelity as new models become available.
* **Rate-Limit Management:** Implements a 24-hour generation cooldown to manage the high token and image costs associated with generating a complete, 16-image book.

---

## 🚀 Story Showcase: "Marcel Meets Dinosaurs"

This sample book illustrates the app's ability to create a consistent narrative and visual style based on simple user inputs (Protagonist: *Marcel the Badger*, Topic: *Dinosaurs*, Style: *Rhyming Adventure*).

### Cover Design
The app generates a professional cover image and overlays the title for a finished product aesthetic.

| Cover Image |
| :---: |
| <img src="https://github.com/kosmickroma/storyteller-lab/blob/main/assets/cover.jpg" width="350px"> |

### Sample Pages (Rhyme and Consistency)

The app demonstrates maintaining the character's core appearance (badger, yellow hat, blue vest, orange shorts) and the specified AABB rhyme pattern across the manuscript.

| Page 1 (A) | Page 2 (A) |
| :---: | :---: |
| **Marcel built a machine, so grand.** | **To visit an ancient, green land.** |
| <img src="https://github.com/kosmickroma/storyteller-lab/blob/main/assets/page_1.jpg" width="350px"> | <img src="https://github.com/kosmickroma/storyteller-lab/blob/main/assets/page_2.jpg" width="350px"> |

| Page 3 (B) | Page 6 (D) |
| :---: | :---: |
| **Whiz, bang, zoom! He traveled fast.** | **Its neck was long, a leafy treat.** |
| <img src="https://github.com/kosmickroma/storyteller-lab/blob/main/assets/page_3.jpg" width="350px"> | <img src="https://github.com/kosmickroma/storyteller-lab/blob/main/assets/page_6.jpg" width="350px"> |

| Page 7 (E) |
| :---: |
| **Marcel thought this dinosaur was neat.** |
| <img src="https://github.com/kosmickroma/storyteller-lab/blob/main/assets/page_7.jpg" width="350px"> |

---

## 🛠️ Technical Stack & Implementation

This project is built entirely in **Python** and deployed using **Streamlit** for rapid prototyping and interactive demonstration.

| Category | Technology | Purpose in Project |
| :--- | :--- | :--- |
| **Language** | Python 3.10+ | Core application logic and API handling. |
| **Framework** | Streamlit | Front-end UI for conversational flow and display. |
| **Text LLM** | Google **Gemini 2.5 Flash** | Narrative generation (Text & Illustration Prompts). |
| **Image Model** | Google **Imagen 3.0** | High-quality, square (1:1 aspect) picture book illustrations. |
| **Libraries** | `re`, `dotenv`, `Pillow (PIL)` | Regex for prompt correction, environment variable management, and cover image text overlay. |

### Advanced Implementation Details

The `story_generator.py` file demonstrates several best practices for production AI applications:

1.  **Stage-Based Chat:** The `MASTER_PROMPT` enforces a multi-step conversation (Stage 1 to Stage 4), preventing the LLM from trying to generate the final output too early.
2.  **Explicit System Instruction:** The instructions are highly specific, including exact formatting for the output and strict rules for illustration content (e.g., **SINGLE CHARACTER ONLY**).
3.  **Client/Resource Caching:** The `@st.cache_resource` decorator is used to efficiently manage the `genai.Client` and image data across Streamlit reruns, optimizing performance and cost.

---

## ⏭️ Future Development

This project serves as a strong foundation for a commercial product. Planned features include:

* **Tiered Generation:** Implementing features like title/text editing, different age groups, and higher image quality upon payment (to offset the cost of the 16 image generations per book).
* **Print-on-Demand Integration:** Utilizing services like Printify to allow users to purchase a physical, high-quality, printed copy of their personalized book.
* **User Authentication:** Integrating a database for tracking user history and managing the 24-hour generation cooldown properly.

---

## 🧑‍💻 About the Creator

This application was developed by **Kory R Karp** to showcase skills acquired through independent study and certification in AI and Python.

* **GitHub:** [https://github.com/kosmickroma](https://github.com/kosmickroma)
* **Contact:** The full list of professional and social links is available on my [Linktree](https://linktr.ee/korykarp?lt_utm_source=lt_admin_share_link#510380565).

Feel free to explore the code, test the live application, and provide feedback!