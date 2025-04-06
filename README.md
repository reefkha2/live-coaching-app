# Live Coaching Assistant

A Streamlit application designed to assist specialists in coaching sessions with victims. The app provides real-time AI-powered coaching suggestions and session summarization.

## Features

- 🧕🏼 Mock victim conversations for training purposes
- 🧠 AI-powered coaching suggestions
- 📝 Session summarization and feedback
- 💬 Custom victim responses for scenario training
- 📊 Case history and profile management

## Setup

1. Clone the repository
```bash
git clone https://github.com/yourusername/live-coaching-app.git
cd live-coaching-app
```

2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run the application
```bash
streamlit run app.py
```

## Usage

1. Enter a Case ID in the sidebar
2. Load the victim profile
3. Start a conversation using either the mock victim or custom victim response
4. Receive AI coaching suggestions
5. End the session to generate a summary

## Technologies

- Streamlit for the user interface
- AWS Bedrock for AI-powered coaching
- AWS API Gateway and Lambda for backend services
