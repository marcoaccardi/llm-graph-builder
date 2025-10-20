# Windows 11 Setup Guide for LLM Graph Builder

This guide provides Windows-specific instructions for setting up and running the LLM Graph Builder application.

## Prerequisites

- Python 3.11+ (with pip)
- Node.js and npm
- Git (with Git Bash recommended)
- Neo4j Community Edition 5.23+ (with APOC)
- Ollama (optional, for local LLMs)

## Backend Setup

1. **Navigate to backend directory:**
   ```cmd
   cd backend
   ```

2. **Create virtual environment:**
   ```cmd
   python -m venv .venv
   ```

3. **Activate virtual environment:**
   ```cmd
   .venv\Scripts\activate
   ```

4. **Install dependencies:**
   ```cmd
   pip install -r requirements.txt
   ```

5. **Set up environment variables:**
   - Copy `example.env` to `.env`
   - Update the `.env` file with your Neo4j connection details:
     ```env
     NEO4J_URI=neo4j://localhost:7687
     NEO4J_USERNAME=neo4j
     NEO4J_PASSWORD=your_password
     NEO4J_DATABASE=neo4j
     ```

6. **Run the backend server:**
   ```cmd
   uvicorn score:app --reload --host 0.0.0.0 --port 8000
   ```

## Neo4j Setup

1. **Download Neo4j Community Edition for Windows:**
   - Visit https://neo4j.com/download-center/
   - Download Neo4j Desktop or Community Server
   - Install following the Windows installer instructions

2. **Configure Neo4j:**
   - Navigate to your Neo4j installation directory
   - Edit the `conf/neo4j.conf` file
   - Ensure the following settings (uncomment and adjust if needed):
     ```
     dbms.default_listen_address=0.0.0.0
     dbms.connector.bolt.listen_address=:7687
     dbms.connector.http.listen_address=:7474
     ```

3. **Start Neo4j:**
   - Option 1: Using Neo4j Desktop application
   - Option 2: Using command line (from Neo4j installation bin directory):
     ```cmd
     neo4j start
     ```

4. **Verify Neo4j is running:**
   - Open browser and go to http://localhost:7474
   - Default credentials: username `neo4j`, password `neo4j` (you'll need to change on first login)

## Frontend Setup

1. **Navigate to frontend directory:**
   ```cmd
   cd frontend
   ```

2. **Install dependencies:**
   ```cmd
   npm install
   ```

3. **Create environment file:**
   - Copy `example.env` to `.env`
   - Update as needed for your configuration

4. **Run development server:**
   ```cmd
   npm run dev
   ```

## Ollama Setup (Optional)

1. **Download and install Ollama for Windows:**
   - Visit https://ollama.com/download
   - Download and run the Windows installer

2. **Start Ollama service:**
   - The service should start automatically after installation
   - Or manually start with: `ollama serve`

3. **Download a model:**
   ```cmd
   ollama pull llama3
   ```

4. **Configure backend for Ollama:**
   - Add to your backend `.env` file:
     ```env
     LLM_MODEL_CONFIG_ollama_llama3=llama3,http://localhost:11434
     ```

## Complete Startup Sequence

1. **Start Neo4j:**
   ```cmd
   # From your Neo4j installation directory
   neo4j start
   ```

2. **Start Ollama (if using):**
   ```cmd
   ollama serve
   ```

3. **Start Backend:**
   ```cmd
   cd backend
   .venv\Scripts\activate
   uvicorn score:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Start Frontend:**
   In a new terminal/command prompt:
   ```cmd
   cd frontend
   npm run dev
   ```

## Troubleshooting

### Python Virtual Environment Issues
- If you get an error about running scripts, run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` in PowerShell
- Or use Command Prompt instead of PowerShell

### Port Issues
- Make sure ports 8000 (backend) and 7474/7687 (Neo4j) are not in use
- Check with `netstat -an | findstr :8000` or equivalent

### Node/NPM Issues
- Make sure you have the latest LTS version of Node.js
- If you get permission errors, try running as administrator or use `npx` instead of `npm`

### Neo4j Common Issues
- If Neo4j fails to start, check the logs in `<neo4j-installation-dir>\logs`
- Ensure Java is installed (Neo4j requires Java 11 or 17)