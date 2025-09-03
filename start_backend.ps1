param(
    [string]$Environment = "development",
    [int]$Port = 8000,
    [string]$Host = "127.0.0.1"
)

$ErrorActionPreference = "Stop"

function Write-Status {
    param([string]$Message, [string]$Type = "info")
    
    $colors = @{
        "success" = "Green"
        "error" = "Red"
        "warning" = "Yellow"
        "info" = "Cyan"
    }
    
    $color = $colors[$Type] ?? "White"
    Write-Host $Message -ForegroundColor $color
}

function Test-Prerequisites {
    Write-Status "🔍 Checking system prerequisites..." "info"
    
    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python (\d+\.\d+\.\d+)") {
            $version = [version]$matches[1]
            if ($version -ge [version]"3.8.0") {
                Write-Status "✅ Python $($matches[1]) - Compatible" "success"
            } else {
                Write-Status "❌ Python $($matches[1]) - Too old (3.8+ required)" "error"
                return $false
            }
        } else {
            Write-Status "❌ Python not found or version detection failed" "error"
            return $false
        }
    } catch {
        Write-Status "❌ Python check failed: $($_.Exception.Message)" "error"
        return $false
    }
    
    if (-not (Test-Path ".\backend")) {
        Write-Status "❌ Backend directory not found!" "error"
        Write-Status "   Please ensure you're in the project root directory." "warning"
        return $false
    }
    
    if (-not (Test-Path ".\backend\app\main.py")) {
        Write-Status "❌ Backend app structure not found!" "error"
        Write-Status "   Expected: .\backend\app\main.py" "warning"
        return $false
    }
    
    if (-not (Test-Path ".\backend\.env")) {
        Write-Status "⚠️  .env file not found - API keys may not work" "warning"
        Write-Status "   Create .env with your OpenAI API key for full functionality" "info"
    } else {
        Write-Status "✅ Environment file found" "success"
    }
    
    return $true
}

function Start-BackendServer {
    param([string]$Host, [int]$Port)
    
    Write-Status "🚀 Starting Wand AI Backend Server..." "info"
    Write-Status "📍 Server: http://$Host`:$Port" "info"
    Write-Status "🔧 Environment: $Environment" "info"
    Write-Status "📁 Working Directory: $(Get-Location)\backend" "info"
    
    try {
        Set-Location ".\backend"
        
        $env:PYTHONPATH = "."
        $env:ENVIRONMENT = $Environment
        
        $serverProcess = Start-Process -FilePath "python" -ArgumentList @(
            "-m", "uvicorn", 
            "app.main:app", 
            "--host", $Host, 
            "--port", $Port,
            "--log-level", "info"
        ) -PassThru -WindowStyle Normal
        
        Write-Status "✅ Server process started (PID: $($serverProcess.Id))" "success"
        Write-Status "🌐 Access your API at: http://$Host`:$Port/docs" "success"
        Write-Status "📊 Health check: http://$Host`:$Port/health" "success"
        Write-Status "⏹️  Press Ctrl+C to stop the server" "info"
        
        # Wait for server to start
        Start-Sleep -Seconds 3
        
        # Test server health
        try {
            $response = Invoke-WebRequest -Uri "http://$Host`:$Port/health" -UseBasicParsing -TimeoutSec 10
            if ($response.StatusCode -eq 200) {
                Write-Status "✅ Server is responding successfully!" "success"
            }
        } catch {
            Write-Status "⚠️  Server may still be starting up..." "warning"
        }
        
        return $serverProcess
        
    } catch {
        Write-Status "❌ Failed to start server: $($_.Exception.Message)" "error"
        Write-Status "💡 Troubleshooting tips:" "info"
        Write-Status "   1. Ensure all dependencies are installed: pip install -r requirements.txt" "info"
        Write-Status "   2. Check if port $Port is available" "info"
        Write-Status "   3. Verify your .env configuration" "info"
        return $null
    }
}

# Main execution
try {
    Write-Status "🎯 Wand AI - Enterprise AI Workforce Platform" "info"
    Write-Status "===============================================" "info"
    
    # Validate prerequisites
    if (-not (Test-Prerequisites)) {
        Write-Status "❌ Prerequisites check failed. Please fix issues above." "error"
        exit 1
    }
    
    # Start server
    $serverProcess = Start-BackendServer -Host $Host -Port $Port
    
    if ($serverProcess) {
        Write-Status "🎉 Backend server started successfully!" "success"
        Write-Status "🚀 Your Wand AI system is now running!" "success"
        
        # Keep script alive
        try {
            $serverProcess.WaitForExit()
        } catch {
            Write-Status "ℹ️  Server process ended" "info"
        }
    } else {
        Write-Status "❌ Failed to start backend server" "error"
        exit 1
    }
    
} catch {
    Write-Status "💥 Critical error: $($_.Exception.Message)" "error"
    Write-Status "📋 Stack trace: $($_.ScriptStackTrace)" "error"
    exit 1
} finally {
    # Cleanup
    if (Test-Path ".\backend") {
        Set-Location ".\backend"
    }
}
