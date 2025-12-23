# Studio TZ - AI-Powered Website Builder

Transform your ideas into production-ready websites using natural language.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.9+
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/bhargavtz/studio-tz.git
cd studio-tz

# Set up backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Add your GROQ_API_KEY to .env

# Set up frontend
cd ../frontend
npm install
```

### Running the Application

```bash
# In one terminal - start backend
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# In another terminal - start frontend
cd frontend
npm run dev
```

Access the application at: http://localhost:3000

## ✨ Features

- **Natural Language Interface**: Describe your website in plain English
- **AI Domain Detection**: Automatically understands your business type
- **Smart Questioning**: Asks relevant questions to gather requirements
- **Visual Blueprint**: Preview your website structure before generation
- **Real Code Generation**: Produces clean HTML, CSS, and JavaScript
- **Live Editing**: Chat-based modifications in real-time
- **One-Click Download**: Export your complete website as ZIP

## 📂 Project Structure

```
studio-tz/
├── backend/          # FastAPI + LangGraph backend
│   ├── app/          # Main application code
│   ├── .env          # Environment variables
│   └── requirements.txt
├── frontend/         # Next.js 14 frontend
│   ├── src/          # React components
│   ├── public/       # Static assets
│   └── package.json
└── README.md         # This file
```

## 🔧 Configuration

Edit the `.env` file in the backend directory:

```env
# LLM Configuration
GROQ_API_KEY=your_api_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true

# CORS Origins
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Projects Directory
PROJECTS_DIR=./projects
```

## 🛠️ Technology Stack

**Frontend:**
- Next.js 14 (App Router)
- React 18+
- TypeScript
- CSS Modules
- Tailwind CSS

**Backend:**
- FastAPI
- LangChain + LangGraph
- Groq LLM
- Python 3.9+

## 📖 API Documentation

### Key Endpoints

- `POST /api/session/create` - Create new website session
- `POST /api/intent` - Process user intent
- `GET /api/questions/{session_id}` - Get domain-specific questions
- `POST /api/answers/{session_id}` - Submit answers
- `GET /api/blueprint/{session_id}` - View website blueprint
- `POST /api/generate/{session_id}` - Generate website
- `POST /api/edit/{session_id}/chat` - Chat-based editing
- `GET /api/download/{session_id}` - Download project

## 🎯 Use Cases

Perfect for:
- Small business owners who need a website quickly
- Entrepreneurs launching new ventures
- Developers prototyping website ideas
- Non-technical users who want professional websites
- Agencies creating client websites faster

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For issues, questions, or feature requests:
- Open an issue on GitHub
- Contact: bhargavtz@gmail.com
