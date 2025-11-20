# Python FastAPI Backend

This backend replaces the Next.js API route for generating code using Gemini.

## Setup

1.  **Install Dependencies:**
    Make sure you have Python installed. Then run:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Environment Variables:**
    Ensure you have a `.env` file in the root of your project (or in this `backend` directory) with your Google API Key:
    ```
    GOOGLE_API_KEY=your_api_key_here
    ```

3.  **Run the Server:**
    Run the FastAPI server:
    ```bash
    python main.py
    ```
    Or using uvicorn directly:
    ```bash
    uvicorn main:app --reload --port 8000
    ```

The server will start at `http://localhost:8000`.
The Next.js frontend is configured to send requests to `http://localhost:8000/chat`.
