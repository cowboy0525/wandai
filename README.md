# Wand AI - Multi-Agent Knowledge Base with Task Execution

## 🚀 **Project Overview**

**Wand AI** is a comprehensive AI system that combines **Multi-Agent Task Solver** (Challenge 1) and **AI-Powered Knowledge Base Search & Enrichment** (Challenge 2) into a single, powerful platform.

### ✨ **Key Features**

- **🤖 Multi-Agent Orchestration**: 5 specialized AI agents working together
- **🔧 Real Tool Integration**: 7 functional tools (Python executor, data analysis, charts, web search, etc.)
- **📚 Intelligent Knowledge Base**: RAG pipeline with completeness checking and enrichment suggestions
- **🔄 Context Sharing**: Intelligent context management between agents
- **🛡️ Hallucination Prevention**: Output validation and fact-checking
- **📊 Progress Tracking**: Real-time visibility into agent execution

## 🏗️ **Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   AI Services   │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (OpenAI)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Agents        │
                       │ • Planner       │
                       │ • Research      │
                       │ • Analysis      │
                       │ • Creator       │
                       │ • Coordinator   │
                       └─────────────────┘
```

## 🚀 **Quick Start**

### **Option 1: PowerShell Script (Recommended)**
```powershell
.\start_backend.ps1
```

### **Option 2: Windows Batch File**
```cmd
start_backend.bat
```

### **Option 3: Manual Commands**
```powershell
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### **Option 4: Project Root Script**
```powershell
python main.py
```

## 📋 **Prerequisites**

1. **Python 3.8+** installed
2. **OpenAI API Key** in `.env` file
3. **Required packages** (install with `pip install -r backend/requirements.txt`)

## 🔧 **Setup Instructions**

### **Step 1: Environment Setup**
```bash
# Create .env file manually

# Edit .env and add your OpenAI API key
OPENAI_API_KEY=your_api_key_here
```

### **Step 2: Install Dependencies**
```bash
cd backend
pip install -r requirements.txt
```

### **Step 3: Start Backend**
```bash
# Use one of the startup methods above
```

### **Step 4: Start Frontend (Optional)**
```bash
cd frontend
npm install
npm start
```

## 🧪 **Testing the System**

### **Backend Health Check**
- **URL**: `http://localhost:8000/health`
- **Expected**: `{"status": "healthy"}`

### **API Documentation**
- **URL**: `http://localhost:8000/docs`
- **Features**: Interactive API testing with Swagger UI

### **Test Business Request**
```
"Summarize the last 3 quarters' financial trends and create a chart"
```

## 🚨 **Troubleshooting**

### **Common Issues & Solutions**

#### **1. ModuleNotFoundError: No module named 'app'**
**Problem**: Server running from wrong directory
**Solution**: Use the startup scripts or ensure you're in the `backend/` directory

#### **2. PowerShell && Syntax Error**
**Problem**: PowerShell doesn't support `&&`
**Solution**: Use `;` instead or use the provided startup scripts

#### **3. Missing OpenAI API Key**
**Problem**: `OPENAI_API_KEY is required` error
**Solution**: Create `.env` file with your API key

#### **4. Port Already in Use**
**Problem**: Port 8000 is occupied
**Solution**: Change port in startup command or kill existing processes

### **Debug Commands**
```powershell
# Check if server is running
netstat -an | findstr :8000

# Kill Python processes
taskkill /F /IM python.exe

# Check current directory
pwd
```

## 📚 **API Endpoints**

### **Core Endpoints**
- `GET /health` - System health check
- `POST /api/v1/tasks/execute` - Execute business task with agents
- `POST /api/v1/knowledge/search` - Search knowledge base
- `POST /api/v1/knowledge/upload` - Upload documents
- `GET /api/v1/agents/status` - Get agent status

### **Agent Endpoints**
- `POST /api/v1/agents/planner/execute` - Execute planning agent
- `POST /api/v1/agents/research/execute` - Execute research agent
- `POST /api/v1/agents/analysis/execute` - Execute analysis agent
- `POST /api/v1/agents/creator/execute` - Execute creator agent
- `POST /api/v1/agents/coordinator/execute` - Execute coordinator agent

## 🎯 **Challenge Requirements Status**

### **Challenge 1: Multi-Agent Task Solver ✅ COMPLETE**
- ✅ Input: Text-based business requests
- ✅ Planning: Agent orchestration with role definitions
- ✅ Execution: Multiple specialized agents
- ✅ Aggregation: Results combination with context sharing
- ✅ Visibility: Progress updates and status tracking
- ✅ Tool Usage: 7 real tools integrated
- ✅ Context Sharing: Between agents with intelligent filtering
- ✅ Hallucination Prevention: Output validation and fact-checking

### **Challenge 2: AI-Powered Knowledge Base ✅ COMPLETE**
- ✅ Document Upload & Storage: ChromaDB with embeddings
- ✅ Natural Language Search: Semantic search with relevance scoring
- ✅ AI-Generated Answers: OpenAI integration with RAG pipeline
- ✅ Completeness Check: AI detects missing information
- ✅ Enrichment Suggestions: Specific recommendations for knowledge gaps
- ✅ Structured Output: JSON with confidence, missing_info, suggestions

## 🚀 **Advanced Features**

### **Beyond Requirements**
- **Intelligent Context Management**: Smart filtering and summarization
- **Performance Metrics**: Agent success rates and execution tracking
- **Error Recovery**: Graceful handling of failures
- **Scalable Architecture**: Easy to extend with new agents and tools
- **Production Ready**: Proper logging, error handling, and configuration

## 📝 **Development Notes**

### **Design Decisions**
- **FastAPI**: Chosen for async support and automatic API documentation
- **ChromaDB**: Vector database for semantic search and similarity
- **OpenAI Integration**: Leverages latest LLM capabilities
- **Modular Architecture**: Easy to add new agents and tools

### **Trade-offs Made**
- **24h Constraint**: Focused on core functionality over extensive testing
- **UI Complexity**: Basic React interface to prioritize backend logic
- **Error Handling**: Basic error handling with room for improvement
- **Testing**: Manual testing over automated test suites

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 **Support**

If you encounter issues:
1. Check the troubleshooting section above
2. Review the API documentation at `/docs`
3. Check the logs for detailed error messages
4. Ensure all prerequisites are met

---

**🎉 Your Wand AI system is ready to revolutionize enterprise AI workflows!**
# wandai
# wandai
# wandai
