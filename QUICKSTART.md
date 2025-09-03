# 🚀 **Wand AI - Quick Start Guide**

## ⚡ **Get Running in 5 Minutes!**

### **Step 1: Start the Backend (Choose One)**

#### **Option A: PowerShell Script (Easiest)**
```powershell
.\start_backend.ps1
```

#### **Option B: Windows Batch File**
```cmd
start_backend.bat
```

#### **Option C: Manual Commands**
```powershell
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### **Step 2: Test the System**

1. **Open your browser**
2. **Go to**: `http://localhost:8000/health`
3. **Expected result**: `{"status": "healthy"}`

### **Step 3: Try the Demo**

1. **Visit**: `http://localhost:8000/docs`
2. **Test endpoint**: `POST /api/v1/tasks/execute`
3. **Use this request**:
```json
{
  "task": "Summarize the last 3 quarters' financial trends and create a chart",
  "priority": "high"
}
```

## 🎯 **What You'll See**

- **5 AI Agents** working together
- **Real-time progress** updates
- **Tool usage** (Python execution, data analysis, charts)
- **Knowledge base** search and enrichment suggestions

## 🚨 **If Something Goes Wrong**

### **Common Issues**

1. **"ModuleNotFoundError: No module named 'app'"**
   - **Fix**: Use the startup scripts or ensure you're in the `backend/` directory

2. **"OPENAI_API_KEY is required"**
   - **Fix**: Create `.env` file with your API key

3. **Port 8000 already in use**
   - **Fix**: Kill existing processes or change port

### **Debug Commands**
```powershell
# Check if server is running
netstat -an | findstr :8000

# Kill all Python processes
taskkill /F /IM python.exe

# Check current directory
pwd
```

## 🎉 **You're Ready!**

Your Wand AI system is now running and ready to:
- **Execute complex business tasks** with AI agents
- **Search and enrich knowledge bases**
- **Generate insights and visualizations**
- **Provide intelligent recommendations**

---

**Need help? Check the main README.md for detailed documentation!**
