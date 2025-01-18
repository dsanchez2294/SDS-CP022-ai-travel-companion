# Welcome to the SuperDataScience Community Project!
Welcome to the AI Travel Companion repository! 🎉

This project is a collaborative initiative brought to you by SuperDataScience, a thriving community dedicated to advancing the fields of data science, machine learning, and AI. We are excited to have you join us in this journey of learning, experimentation, and growth.

# Project Scope of Works:

## Project Overview

This project involves creating an advanced AI-powered travel companion that leverages retrieval-augmented generation (RAG) to provide personalized travel assistance. The project will gather the latest ticket price data from airlines through web scraping, integrate this data with a knowledge base, and deploy the final application on Hugging Face Spaces. The AI Travel Companion will offer users dynamic ticket pricing, travel recommendations, and query-based assistance.

## Objectives

### Data Collection and Storage:
- Gather data on popular travel destinations via web scraping.
- Store the data in a structured database optimized for quick retrieval.

### AI Travel Companion Development:
- Develop a RAG pipeline that combines a travel destinations knowledge base with generative AI.
- Implement functionality to answer user queries and provide personalized travel suggestions based on travel data and other contextual inputs.

### Application Deployment:
- Build an intuitive user interface for the travel companion.
- Deploy the application on Hugging Face Spaces for global accessibility.

## Technical Requirements

### Tools and Libraries:
- **Data Collection:** BeautifulSoup, Selenium, requests.
- **Data Storage:** csv, json or vector database.
- **AI Development:** LangChain, Hugging Face Transformers, OpenAI API, Pinecone/FAISS/ChromaDB for vector search.
- **Application Deployment:** Gradio or Streamlit for user interface development; Hugging Face Spaces for hosting.

### Environment:
- Python 3.8+
- Required Libraries: pandas, langchain, transformers, gradio, openai, beautifulsoup4, selenium.

## Workflow

### Phase 1: Setup (1 Week)
- Setup of GitHub repo and project folders
- Setup of virtual environments and installation of libraries

### Phase 2: Data Collection (1 Week)
- Scrape airline ticket pricing data from multiple websites.
- Preprocess and clean the data to ensure accuracy and consistency.
- Store the ticket data in a csv or json.

### Phase 3: RAG Pipeline Development (1 Week)
- Build a retrieval module using vector search.
- Integrate a generative AI model (e.g., OpenAI GPT or Hugging Face LLMs) with the retrieval module.
- Fine-tune the pipeline to answer user queries related to flight pricing and travel planning.

### Phase 4: Application Development (1 Week)
- Create an interactive Gradio or Streamlit interface to:
  - Accept user queries about travel plans or preferences.
  - Display ticket prices, travel suggestions, and other contextual insights.
- Test the application for functionality, responsiveness, and user experience.

### Phase 5: Deployment (1 Week)
- Deploy the application on Hugging Face Spaces.

## Timeline

| Phase          | Task                                 | Duration |
|----------------|--------------------------------------|----------|
| Phase 1: Setup  | Setup of GitHub Repo & environment | Week 1   |
| Phase 2: Data  | Collect and store travel data | Week 2   |
| Phase 3: RAG   | Build RAG pipeline                  | Week 3   |
| Phase 4: App   | Build Gradio/Streamlit application   | Week 4   |
| Phase 5: Deployment | Deploy on Hugging Face Spaces     | Week 5   |

# Getting Started

Follow these steps to set up the project locally:

## 1. Fork the Repository
To work on your own copy of this project:
1. Navigate to the SDS GitHub repository for this project.  
2. Click the **Fork** button in the top-right corner of the repository page.  
3. This will create a copy of the repository under your GitHub account.

---

## 2. Clone the Repository
After forking the repository:
1. Open a terminal on your local machine.  
2. Clone your forked repository by running:
   ```bash
   git clone https://github.com/<your-username>/<repository-name>.git
   ```
3. Navigate to the project directory:
    ```bash
    cd <repository-name>
    ```

## 3. Create a virtual environment
Setup a virtual environment to isolate project dependancies
1. Run the following command in the terminal to create a virtual environment
    ```bash
    python3 -m venv .venv
    ```
2. Activate the virtual environment
  - On a mac/linux:
    ```bash
    source .venv/bin/activate
    ```
  - On a windows:
    ```
    .venv\Scripts\activate
    ```
3. Verify the virtual environment is active (the shell prompt should show (.venv))

## 4. Install dependancies
Install the required libraries for the project
1. Run the following command in the terminal to isntall dependancies from the requirements.txt file:
    ```bash
    pip install -r requirements.txt
    ```
Once the setup is complete, you can proceed with building your project
