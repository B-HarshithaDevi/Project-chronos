# Project Chronos — AI Archeologist

Project Chronos is a web-based tool that uses the **Gemini API** to act as an "AI Archeologist," specializing in deciphering fragmented historical web text and digital slang.

It takes a cryptic fragment (e.g., full of acronyms and old slang) and provides three things:

1.  **Reconstructed Text:** A coherent sentence where acronyms and slang are expanded and explained.
2.  **Corrected Phrase:** A concise, modern-English rewrite.
3.  **Contextual Sources:** A list of 5 relevant URLs found via the Gemini API's integrated Google Search tool.

Team
* *Student Name(s):* [Bandaru Harshitha devi,Mantena kushi varma,Tejaswi reddy,Avanika]
* *Student ID(s):* [se24uari063,se24uari008,se24uecm019,se24uecm018]


## 🛠️ Setup and Installation

### Prerequisites

* Python 3.8+
* A **Gemini API Key** (Get one from [Google AI Studio](https://makersuite.google.com/app/apikey))

### Steps

1.  **Clone the Repository:**
    ```bash
    git clone [your-repo-url]
    cd [your-repo-name]
    ```

2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use: venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure API Key:**
    Create a file named **`.env`** in the root directory and add your API key:
    ```
    # .env
    GEMINI_API_KEY="YOUR_API_KEY_HERE"

    # Optional: Change the default model
    # GEMINI_MODEL="gemini-2.5-flash"
    ```

## ▶️ Running the Application

Execute the main Python file. The Flask application will start a local server.

```bash
python your_app_file_name.py # Replace 'your_app_file_name.py' with the actual filename
