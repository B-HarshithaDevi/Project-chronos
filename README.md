# Project Chronos: The AI Archaeologist

## 1. Project Overview

Project Chronos is an AI tool designed to reconstruct fragmented, obscure, or incomplete historical digital text. It achieves this by:
1.  Using the **Google Gemini API** to expand digital slang, explain cultural context, and fill in missing information.
2.  Fetching a list of **verifiable contextual sources** from the web to support the reconstruction, fulfilling the role of a digital archaeologist.

## 2. Team
* **Student Name(s):** [Bandaru Harshitha Devi,Mantena Kushi Varma,Tejaswi Reddy Vutukuru,Avanika Kademgari]
* **Student ID(s):** [se24uari063,se24uari008,se24uecm019,se24uecm018]

---

## 3. Setup Instructions

A clean, dedicated environment is required to run this project.

### A. Environment Setup
1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/B-HarshithaDevi/Project-chronos.git]
    cd project_chronos
    ```

2.  **Create and Activate Virtual Environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On macOS/Linux
    # .venv\Scripts\activate.bat # On Windows Command Prompt
    ```

3.  **Install Dependencies:**
    All necessary Python libraries are listed in `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```

### B. API Key Configuration (Crucial)

**NOTE:** This project requires a **Google Gemini API Key**.

1.  **Get Key:** Obtain your key from the Google AI Studio developer page.
2.  **Security:** Your repository includes a `.gitignore` file that excludes the `.env` file for security.
3.  **Set Key:** Open the separate `.env` file and add your key in the exact format shown below, replacing the placeholder:
    ```env
    GEMINI_API_KEY="AIzaSyDCYYpuPZhjmRYAecAhmvFdW92HoF9r1Fw"
    ```

## 4. Usage Guide

The application is run directly from the command line, taking the fragmented text as an argument in quotes.

### 📝 Command Syntax:

```bash
python main.py "<The Fragmented/Cryptic Sentence>"
