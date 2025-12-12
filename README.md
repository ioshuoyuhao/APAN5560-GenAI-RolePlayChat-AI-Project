# APAN5560-GenAI-RolePlayChat-AI-Project

RPGChat.AI caters to a wide range of user needs—relaxation, inspiration, or role-playing—offering a platform where creativity meets intelligence. Through this innovative conversational experience, users can explore endless narrative possibilities and enjoy truly personalized communication.

---

## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/APAN5560-GenAI-RolePlayChat-AI-Project.git
cd APAN5560-GenAI-RolePlayChat-AI-Project

# Set up environment
cp .env.example .env              # Create env file (edit as needed)
docker compose up -d db           # Start PostgreSQL + pgvector database

# Backend: Install dependencies and run
uv sync
cd back-end && uv run alembic upgrade head && cd ..  # Run migrations
uv run fastapi dev back-end/app/main.py

# Frontend: In a separate terminal
cd front-end && npm install && npm run dev
```

| Service | URL |
|---------|-----|
| Backend API | http://127.0.0.1:8000 |
| API Docs | http://127.0.0.1:8000/docs |
| Frontend | http://localhost:5173 |

---

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- [Docker](https://docs.docker.com/get-docker/) (for PostgreSQL + pgvector)
- [Node.js 18+](https://nodejs.org/) (for frontend)

---

## Project Structure

```
├── back-end/
│   ├── app/
│   │   ├── core/            # Config & database setup
│   │   ├── models/          # SQLAlchemy models (Character, Conversation, Message, etc.)
│   │   ├── routers/         # API route handlers (discover, characters, conversations)
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── services/        # Business logic (LLMClient, PromptOrchestrator, Chunker)
│   │   └── main.py          # FastAPI app entry point
│   ├── alembic/             # Database migrations
│   └── alembic.ini          # Alembic config
├── front-end/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components (Home, Discover, Chat, etc.)
│   │   ├── App.tsx          # Main app with routing
│   │   └── main.tsx         # Entry point
│   ├── package.json         # npm dependencies
│   └── tailwind.config.js   # TailwindCSS config
├── data model/              # ML training scripts
├── character cards/         # Character definitions
├── datasets/                # Training data
├── docker-compose.yml       # Database container
├── .env.example             # Environment variables template
├── pyproject.toml           # Backend dependencies (uv)
└── requirements.txt         # Backend dependencies (pip)
```

---

## Install Dependencies

**Using uv** (Preferred, reads from `pyproject.toml`):
```bash
uv sync                    # Install all dependencies
uv sync --extra dev        # Include dev dependencies (pytest, httpx)
```

**Using pip** (reads from `requirements.txt`):
```bash
python -m venv .venv && source .venv/bin/activate  # Create & activate venv
pip install -r requirements.txt                     # Install dependencies
```

---

## Database Setup

```bash
# Start PostgreSQL + pgvector container
docker compose up -d db

# Run database migrations (from back-end directory)
cd back-end && uv run alembic upgrade head && cd ..

# Stop database
docker compose down

# View database logs
docker compose logs db

# Reset database (removes all data)
docker compose down -v && docker compose up -d db
```

Database connection: `postgresql://rpgchat:rpgchat@localhost:5433/rpgchat`

> **Note:** Using port 5433 to avoid conflicts with existing PostgreSQL instances on port 5432.

### Database Migrations (Alembic)

```bash
cd back-end

# Generate new migration after model changes
uv run alembic revision --autogenerate -m "describe changes"

# Apply migrations
uv run alembic upgrade head

# Rollback last migration
uv run alembic downgrade -1

# View migration history
uv run alembic history
```

---

## Frontend Development

```bash
cd front-end

# Install dependencies
npm install

# Start dev server (hot reload)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

Frontend: http://localhost:5173 (or next available port)

---

## Backend Development

```bash
# Add new dependency (updates pyproject.toml & uv.lock)
uv add <package>

# Add dev-only dependency
uv add --dev <package>

# Run tests
uv run pytest

# Run app (dev mode with hot reload)
uv run fastapi dev back-end/app/main.py

# Run app (production mode)
uv run fastapi run back-end/app/main.py --port 8000
```
------------------------------------------------------------
 ( New Update for project documentation)
# RPGChat.AI

RPGChat.AI is a web-based, AI-driven role-play chat application inspired by SillyTavern.  
It focuses on **tavern-style character role-play, OpenAI-compatible LLM APIs, and RAG with pgvector**, built as a compact but realistic GenAI system for coursework.

The project is intentionally scoped as an **MVP** suitable for a semester project, while being extensible enough for future features (long-term memory, masks, multi-character chats, etc.).

---

## 1. Project Goals

- Provide a **web app demo** where users:
  - Import character cards (JSON + PNG) compatible with SillyTavern-style formats.
  - Configure an OpenAI-compatible LLM API (DeepSeek, Doubao, custom HF, etc.).
  - Chat with characters in a rich tavern-RP style.
  - Attach knowledge bases and perform **RAG** using PostgreSQL + pgvector.

- Demonstrate end-to-end **LLM application engineering**:
  - Fine-tuned / custom model hosted on Hugging Face or another OpenAI-compatible API.
  - Prompt orchestration (global + character-level prompts).
  - Vector retrieval with pgvector.
  - FastAPI backend + Docker deployment.

---

## 2. MVP Feature Scope

### 2.1 Included (MVP)

1. **Character Card Import**
   - Import character cards by JSON + PNG pair.
   - Basic character editing: name, description, first message, personality, scenario, example dialogues, system prompt.
   - Compatibility with SillyTavern-style card schema (simplified).

2. **Discover Page (Official Characters)**
   - Grid of 1–N official demo characters.
   - Each card: avatar, name, short tagline.
   - Actions:
     - **Download** JSON + PNG as a zip.
     - **Import & start chat** → creates local character + new conversation.

3. **Character Management**
   - Characters page: list of locally imported characters.
   - Favorite toggle (⭐).
   - Click character → open/continue conversation.

4. **Chat & Conversation Management**
   - Left sidebar: conversation list for current user.
   - Right side: main chat UI with:
     - Streaming or chunked responses.
     - Standard chat bubbles (user vs character).
   - New conversation can be created for a chosen character and API provider.

5. **Per-Dialogue Settings**
   - Select character (for this conversation).
   - Select API provider (OpenAI-compatible backend).
   - Attach one or more knowledge bases.
   - RAG knobs:
     - Similarity threshold (0.0–1.0, default 0.5).
     - Top-K retrieved documents (default 5).
   - Prompt configuration tabs:
     - Basic uses global prompt templates (see below).
     - Local overrides are optional (stretch).

6. **Global Settings Page**
   - **API Providers tab**
     - Create / edit OpenAI-compatible providers:
       - Name
       - Base URL (e.g. `https://api.siliconflow.cn/v1`)
       - API key
       - Chat model id (e.g. `deepseek-ai/DeepSeek-V3.2`)
       - Embedding model id (e.g. `BAAI/bge-m3`)
     - Mark one provider as **active** (default).
     - **Test API** function (non-stream test call + latency report).
   - **Knowledge Base tab**
     - Create KBs.
     - Upload documents (markdown / txt / pdf).
     - Documents are chunked, embedded, and stored with pgvector.
   - **Prompt Templates tab**
     - 8 global templates:
       1. Global system prompt  
       2. Real-world time prompt  
       3. Role-play meta prompt  
       4. Dialogue system prompt  
       5. Character config prompt  
       6. Character personality prompt  
       7. Scene prompt  
       8. Example dialogues prompt  
     - For each:
       - Read-only **default prompt** (shipped with app).
       - Editable **custom prompt** (user override).
       - Buttons: Copy default → custom, Save, Reset.

7. **RAG with PostgreSQL + pgvector**
   - Knowledge base documents stored in `kb_documents` with `VECTOR` column.
   - During chat, backend:
     - Builds a query embedding.
     - Runs similarity search via pgvector.
     - Injects top-K snippets into the prompt.

8. **OpenAI-compatible LLM API Layer**
   - Single unified client for providers implementing the OpenAI chat/completions API.
   - Supports:
     - Commercial APIs (DeepSeek via SiliconFlow, Doubao, etc.)
     - Custom fine-tuned model served behind an OpenAI-style endpoint (e.g. HuggingFace + TGI wrapper).

---

### 2.2 Explicitly Out of Scope (for MVP)

The following features are intentionally **cut** or reduced for the course project (can be written as “future work”):

- Story mode / story book editing.
- Mask system / user personas.
- Long-term memory timeline and full-text search over message history.
- Voice input / TTS / image generation.
- World-info / lorebook UI.
- Multi-bot group chats.
- Automatic title summarization of chats using a second model.

---

## 3. User Workflows

### 3.1 First-Time Setup

1. Open RPGChat.AI in browser.
2. Navigate to **Settings → API Providers**.
3. Click “Add provider” and create an entry, e.g.:

   - Name: `SiliconFlow DeepSeek`
   - Base URL: `https://api.siliconflow.cn/v1`
   - API key: (user’s key)
   - Chat model id: `deepseek-ai/DeepSeek-V3.2`
   - Embedding model id: `BAAI/bge-m3`

4. Click **Test API** → confirm success.
5. Mark provider as **Active**.

### 3.2 Importing a Character and Starting Chat

1. Go to **Discover**.
2. Choose a character card and click **Import & Start Chat**.
3. Backend:
   - Downloads JSON + PNG metadata for that character.
   - Inserts into `characters` table.
   - Creates a new conversation row.
4. Browser navigates to **Chat** page:
   - Left: conversation list.
   - Right: chat UI for this conversation + character.

### 3.3 Configuring Knowledge Base for a Character/Chat

1. Go to **Settings → Knowledge Base**.
2. Create KB “Tavern Lore”.
3. Upload markdown or txt files.
4. Backend embeds and indexes documents (pgvector).
5. In a chat’s **Dialogue Settings**:
   - Attach “Tavern Lore” KB.
   - Set similarity threshold and top-K.
6. During conversation, messages are enriched with retrieved snippets.

### 3.4 Customizing Prompt Behavior

1. Open **Settings → Prompt Templates**.
2. Click “Role-play meta prompt”.
3. Review default text (e.g. Tavern RP style with `{{char}}` and `{{user}}` placeholders).
4. Click “Copy to custom”.
5. Edit custom prompt to match the project’s style.
6. Save. All future chats will use the customized template.

---

## 4. System Architecture

### 4.1 Tech Stack

- **Frontend**
  - Vite + React
  - TypeScript
  - TailwindCSS (dark, modern aesthetic)

- **Backend**
  - Python 3.11+
  - FastAPI + uvicorn
  - Pydantic (request/response models & validation)
  - SQLAlchemy (DB ORM)

- **Database**
  - PostgreSQL
  - pgvector extension for vector similarity search

- **LLM Backends (OpenAI-compatible)**
  - DeepSeek (via SiliconFlow API)
  - ByteDance / Doubao (if OpenAI-style endpoint)
  - Custom 8B fine-tuned model hosted on Hugging Face Hub with an OpenAI-compatible gateway

- **Infrastructure**
  - Docker & docker-compose
  - `.env` for secrets (API keys, DB URL, etc.)

---

### 4.2 High-Level Diagram

```text
[Browser (React)]  ←→  [FastAPI backend]  ←→  [PostgreSQL + pgvector]
                               │
                               └→  [OpenAI-compatible LLM APIs]
                                      (DeepSeek / Doubao / Custom HF)
```
## 5. Data Model (Initial Draft)
This is a simplified SQL schema; in the real project we use SQLAlchemy models.
### 5.1 Characters & Conversations
CREATE TABLE characters (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    avatar_url TEXT,                     -- or local file path
    description TEXT,                    -- high-level character desc
    first_message TEXT,                  -- opening line
    personality_prompt TEXT,             -- personality
    scenario_prompt TEXT,                -- scene / world
    example_dialogues_prompt TEXT,       -- few-shot examples
    system_prompt TEXT,                  -- character-specific system
    card_json JSONB,                     -- raw JSON from card
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    character_id INT REFERENCES characters(id) ON DELETE SET NULL,
    api_provider_id INT REFERENCES api_providers(id),
    title TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INT REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user','assistant','system')),
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
### 5.2 API Providers
CREATE TABLE api_providers (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    base_url TEXT NOT NULL,
    api_key TEXT NOT NULL,
    chat_model_id TEXT NOT NULL,
    embedding_model_id TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
### 5.3 Knowledge Base & pgvector
CREATE TABLE knowledge_bases (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Each row typically represents one text chunk
CREATE TABLE kb_documents (
    id SERIAL PRIMARY KEY,
    kb_id INT REFERENCES knowledge_bases(id) ON DELETE CASCADE,
    source_filename TEXT,
    chunk_index INT,
    chunk_text TEXT NOT NULL,
    embedding VECTOR(1024) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
### 5.4 Prompt Templates
CREATE TABLE prompt_templates (
    key TEXT PRIMARY KEY,          -- e.g. "global_system", "scene"
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    default_prompt TEXT NOT NULL,
    custom_prompt TEXT
);

## 6. REST API Design (FastAPI Sketch)
This section lists the core endpoints. Names may be refined later but should be close.
### 6.1 Discover
GET /api/discover/characters


List official demo characters.


GET /api/discover/characters/{id}


Get metadata for a single official character.


POST /api/discover/characters/{id}/import


Import official character into local DB and start a conversation.


Response: { "character_id": 42, "conversation_id": 99 }


GET /api/discover/characters/{id}/download


Download JSON + PNG as a zip.



### 6.2 Characters & Conversations
GET /api/characters


GET /api/characters/{id}


PUT /api/characters/{id} (edit fields)


POST /api/characters/import-local


Import character from uploaded JSON + PNG.


GET /api/conversations


POST /api/conversations


Create conversation { character_id, api_provider_id, kb_ids? }.


GET /api/conversations/{id}/messages


POST /api/conversations/{id}/messages


Body: { "content": "... user text ..." }


Backend:


Saves user message.


Builds full prompt:


Global templates (1–8).


Character data.


RAG snippets (if KB attached).


Conversation history (truncated to context window).


Calls selected LLM provider.


Streams or returns assistant message.


Saves assistant message.



### 6.3 Settings: API Providers
GET /api/settings/api-providers


POST /api/settings/api-providers


GET /api/settings/api-providers/{id}


PUT /api/settings/api-providers/{id}


DELETE /api/settings/api-providers/{id} (optional)


POST /api/settings/api-providers/{id}/activate


POST /api/settings/api-providers/{id}/test



### 6.4 Settings: Knowledge Base
GET /api/settings/knowledge-bases


POST /api/settings/knowledge-bases


GET /api/settings/knowledge-bases/{kb_id}


DELETE /api/settings/knowledge-bases/{kb_id}


POST /api/settings/knowledge-bases/{kb_id}/documents (multipart upload)


DELETE /api/settings/knowledge-bases/{kb_id}/documents/{doc_id} (optional)



### 6.5 Settings: Prompt Templates
GET /api/settings/prompt-templates


GET /api/settings/prompt-templates/{key}


PUT /api/settings/prompt-templates/{key}  – set custom prompt


DELETE /api/settings/prompt-templates/{key} – reset to default



## 7. Prompt Orchestration (Conceptual)
For each assistant reply, backend builds messages like:
[
  # 1. global system prompt
  {"role": "system", "content": global_system_prompt},

  # 2. real-world time
  {"role": "system", "content": real_time_prompt},   # e.g. “Today is 2025-04-01 …”

  # 3. role-play meta
  {"role": "system", "content": roleplay_meta_prompt},

  # 4. dialogue system
  {"role": "system", "content": dialogue_system_prompt},

  # 5–7. character-related info
  {"role": "system", "content": character_config_prompt},
  {"role": "system", "content": character_personality_prompt},
  {"role": "system", "content": scene_prompt},

  # 8. example dialogues (optional, only when context budget allows)
  {"role": "system", "content": example_dialogues_prompt},

  # 9. RAG snippets, if any
  {"role": "system", "content": rag_snippets_prompt},

  # 10. truncated chat history
  *history_messages,

  # 11. latest user message
  {"role": "user", "content": user_input}
]
Then we call the selected provider’s OpenAI-compatible endpoint:
POST {base_url}/chat/completions
{
  "model": chat_model_id,
  "messages": [...],
  "stream": true/false
}

## 8. Local Development & Deployment
### 8.1 Prerequisites
Python 3.12+


Docker & docker-compose


Node.js 18+ (for Vite/React dev server)


### 8.2 Environment Variables (
.env
)
# Backend
DATABASE_URL=postgresql+psycopg2://user:password@db:5432/rpgchat
SECRET_KEY=some_random_secret

# Optional default provider (for local testing)
DEFAULT_API_BASE_URL=https://api.siliconflow.cn/v1
DEFAULT_API_KEY=sk-xxxx
DEFAULT_CHAT_MODEL_ID=deepseek-ai/DeepSeek-V3.2
DEFAULT_EMBEDDING_MODEL_ID=BAAI/bge-m3
Important:
.env must be git-ignored. API keys are never committed to GitHub.
TAs receive keys via email or separate channel, as per course instructions.
8.3 Running with Docker Compose
# 1. Clone repository
git clone https://github.com/your-org/RPGChat.AI.git
cd RPGChat.AI

# 2. Create .env in project root (see above)

# 3. Start services
docker compose up --build
Backend: FastAPI served by uvicorn at http://localhost:8000


Frontend: Vite dev server at e.g. http://localhost:5173


PostgreSQL: exposed on port 5432 (optional)


### 8.4 Backend: Local Dev without Docker (optional)
cd backend
pip install -r requirements.txt
alembic upgrade head   # run migrations
uvicorn app.main:app --reload --port 8000

## 9. Testing & Evaluation
Unit tests


API provider client (OpenAI-compatible wrapper).


Prompt template loading & merging.


RAG retrieval (test similarity ranking with small fake corpus).


Integration tests


Full chat roundtrip: REST call → LLM mock → DB write.


Knowledge base upload → embedding → retrieval.


Manual UX testing


Character import from Discover and from local JSON + PNG.


Switching between different API providers (e.g. DeepSeek vs local HF).


Adjusting RAG thresholds and checking impact on answer quality.



## 10. Future Work
Story mode & branching narratives.


Multi-character rooms and character-to-character interactions.


Richer long-term memory with SQLite FTS over messages.


Voice and image modalities.


Role card editor with AI assistance (help user write better character card prompts).


---
