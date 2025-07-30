# Omnara - Agent Dashboard

A unified interface for monitoring and interacting with multiple AI agents.

## Overview
Omnara provides a web dashboard where users can:
- Monitor multiple AI agents (Claude Code, GitHub Copilot, Cursor, Codex, etc.)
- See real-time progress of agent tasks
- Answer questions from agents when they need guidance
- Send feedback and additional instructions to active agents
- View history of completed tasks and interactions
- Manage API keys for secure agent authentication

## Architecture
- **MCP Server**: Agents connect here to log progress and ask questions
- **Backend API**: FastAPI service providing data to frontend
- **Frontend**: React app with clean UI for non-technical users
- **Database**: PostgreSQL for persistent storage

```mermaid
graph TB
    subgraph "AI Agents"
        A1["Claude Code"]
        A2["GitHub Copilot"]
        A3["Cursor"]
        A4["Other Agents"]
    end
    
    subgraph "Agent Dashboard System"
        subgraph "Services"
            MCP["MCP Server<br/>Port 8080<br/>FastMCP + HTTP/SSE"]
            Backend["Backend API<br/>Port 8000<br/>FastAPI + REST"]
            Frontend["Frontend<br/>Port 3000<br/>React + Vite"]
        end
        
        subgraph "Data Layer"
            DB["PostgreSQL<br/>Port 5432<br/>Shared Database"]
        end
    end
    
    subgraph "Users"
        U1["Web Users"]
    end
    
    A1 -.->|"MCP Protocol<br/>log_step() + feedback<br/>ask_question()<br/>end_session()"| MCP
    A2 -.->|"MCP Protocol<br/>log_step() + feedback<br/>ask_question()<br/>end_session()"| MCP
    A3 -.->|"MCP Protocol<br/>log_step() + feedback<br/>ask_question()<br/>end_session()"| MCP
    A4 -.->|"MCP Protocol<br/>log_step() + feedback<br/>ask_question()<br/>end_session()"| MCP
    
    MCP <-->|"SQLAlchemy ORM<br/>Shared Models"| DB
    Backend <-->|"SQLAlchemy ORM<br/>Shared Models"| DB
    
    Frontend <-->|"REST API<br/>JSON"| Backend
    U1 <-->|"HTTP/Browser"| Frontend
    
    classDef agent fill:#e1f5fe
    classDef service fill:#f3e5f5
    classDef data fill:#e8f5e8
    classDef user fill:#fff3e0
    
    class A1,A2,A3,A4 agent
    class MCP,Backend,Frontend service
    class DB data
    class U1 user
```

## Quick Start

### Prerequisites
- Docker and Docker Compose
- OR: Python 3.12+, Node.js 18+, PostgreSQL
- Supabase account (for authentication)

### Initial Setup (First Time Only)
The frontend is maintained as a separate git repository. After cloning this repository, initialize the frontend submodule:

```bash
# Initialize and update all submodules (including frontend)
git submodule update --init --recursive

# Alternative: Only initialize the frontend submodule
git submodule update --init frontend
```

**For new team members:** Always run the submodule command after cloning this repository to populate the `frontend/` folder.

### Authentication Setup
1. Create a Supabase project at https://supabase.com
2. Enable Google OAuth provider in Authentication settings (optional)
3. Generate RSA keys for API key signing:
   ```bash
   python scripts/generate_jwt_keys.py
   ```
4. Create `.env` file with required variables (see Environment Variables section)

### Running with Docker (Recommended)
```bash
# Start all services with one command
docker compose up

# Services will be available at:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - MCP Server: http://localhost:8080
# - PostgreSQL: localhost:5432
```

### Manual Installation
```bash
# Generate JWT keys (if not done already)
python scripts/generate_jwt_keys.py

# Backend setup
cd servers
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

cd ../backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
# Create .env with your configuration
# Copy the template below and save as .env
# Edit .env with your actual values

# Initialize database
python -m shared.database.init_db

# Development tools (optional)
pip install -r requirements-dev.txt

# Set up pre-commit hooks (recommended)
make pre-commit-install
```

### Manual Running
```bash
# Terminal 1: MCP Server
cd servers
python -m mcp.server

# Terminal 2: Backend API
cd backend
python -m main

# Terminal 3: Frontend
cd frontend
npm run dev
```

## Project Structure
- `servers/` - MCP and FastAPI servers for agent communication
- `backend/` - FastAPI backend serving the web app
- `frontend/` - React frontend with shadcn/ui *(git submodule)*
- `shared/` - Shared code between services
- `scripts/` - Development scripts for linting and formatting
- `CLAUDE.md` - System design documentation
- `pyproject.toml` - Python project configuration and tool settings
- `pyrightconfig.json` - Pyright type checker configuration

## Development

### Working with the Frontend Submodule
The `frontend/` folder is a git submodule pointing to the [omnara-frontend](https://github.com/omnara-ai/omnara-frontend) repository.

```bash
# Check submodule status
git submodule status

# Update frontend to latest from remote
cd frontend
git pull origin main
cd ..
git add frontend
git commit -m "Update frontend submodule to latest"

# Switch frontend to a specific branch/commit
cd frontend
git checkout main  # or any branch/commit
cd ..
git add frontend
git commit -m "Update frontend submodule reference"

# If frontend folder is empty after pulling changes
git submodule update --init --recursive
```

**Important Notes:**
- The `frontend/` folder contains a reference to a specific commit in the omnara-frontend repo
- To update frontend code, work directly in the omnara-frontend repository
- After updating the submodule reference, commit the change in this main repository
- Never commit files directly inside `frontend/` - they belong to the submodule

### Code Quality Tools
This project uses ruff for linting/formatting and pyright for type checking, with pre-commit hooks to ensure code quality.

```bash
# Install development dependencies and set up pre-commit
make pre-commit-install

# Pre-commit hooks will automatically run on git commit
# To manually run pre-commit on all files:
make pre-commit-run

# Manual code quality commands:
make lint               # Run all checks (linting + type checking)
make format             # Auto-format code
make ruff-check         # Just ruff linting
make ruff-format-check  # Just format checking
make typecheck          # Just type checking
```

### Pre-commit Hooks
Pre-commit hooks automatically run before each commit to ensure code quality:
- **Ruff linting** - Automatically fixes common issues
- **Ruff formatting** - Ensures consistent code style
- **Pyright type checking** - Catches type errors
- **General checks** - Removes trailing whitespace, fixes end-of-file issues

If pre-commit hooks fail, the commit is blocked until issues are resolved.

### Python Version
The project uses Python 3.12. All Docker images and virtual environments should use this version.

## Environment Variables

### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/agent_dashboard

# Supabase (for web auth)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key

# JWT Keys (generate with scripts/generate_jwt_keys.py)
JWT_PRIVATE_KEY='-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----'
JWT_PUBLIC_KEY='-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----'

# Optional
API_PORT=8000
MCP_SERVER_PORT=8080
```

### Frontend (.env.local)
```bash
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
VITE_API_URL=http://localhost:8000
```

## For Agents

### Getting Started
1. Sign up at http://localhost:3000
2. Navigate to API Keys section in dashboard
3. Create a new API key
4. Configure your MCP client with the API key

### MCP Client Configuration
```json
{
  "mcpServers": {
    "omnara": {
      "type": "sse",
      "url": "http://127.0.0.1:8080/sse",
      "headers": {
        "Authorization": "Bearer TOKEN"
      }
    }
  }
}
```

Replace `TOKEN` with the API key you generated from the dashboard.

### Available Tools
- `log_step` - Log your current high-level task and receive user feedback
- `ask_question` - Ask the user for guidance (non-blocking)
- `end_session` - Mark the agent session as completed

All tools require authentication via the API key. The `log_step` tool returns any user feedback submitted since the last step, allowing agents to incorporate user instructions and corrections in real-time. The `end_session` tool should be called after the user confirms task completion to properly close the session.

## Python SDK

The Omnara package includes a Python SDK for programmatic access to the API.

### Installation
```bash
pip install omnara
```

### Quick Start
```python
from omnara import OmnaraClient

# Initialize the client
client = OmnaraClient(
    api_key="your-jwt-api-key",
    base_url="http://localhost:8080"  # or your deployed URL
)

# Log a step
response = client.log_step(
    agent_type="my-agent",
    step_description="Processing data",
    agent_instance_id=None  # Will create new instance
)

# Ask a question
answer = client.ask_question(
    agent_instance_id=response.agent_instance_id,
    question_text="Should I continue with the next step?",
    timeout=300  # 5 minutes timeout
)

# End the session
client.end_session(response.agent_instance_id)
```

### Async Client
```python
from omnara import AsyncOmnaraClient
import asyncio

async def main():
    client = AsyncOmnaraClient(api_key="your-jwt-api-key")
    
    response = await client.log_step(
        agent_type="my-agent",
        step_description="Starting async process"
    )
    
    # ... more async operations
    
    await client.end_session(response.agent_instance_id)

asyncio.run(main())
```