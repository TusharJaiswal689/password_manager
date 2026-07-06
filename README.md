# Local Password Manager MCP Server 🔐

A highly secure, locally-hosted Password Manager designed specifically for AI agents via the Model Context Protocol (MCP). 

This server allows local LLMs (like Llama 3 or Qwen via Ollama) or cloud models (via Claude Desktop/Cline) to autonomously generate, encrypt, save, and retrieve passwords. It features strict Pydantic data validation, AES encryption, asynchronous PostgreSQL storage, and an out-of-band GUI prompt to keep your Master Password completely hidden from the AI.

## 🚀 Features

* **AI-Native Interface:** Fully compatible with the Model Context Protocol (FastMCP).
* **Zero-Knowledge AI:** The AI agent can manage passwords but NEVER sees your Master Password. Authentication happens via a native OS (Tkinter) popup.
* **Strict Schema Validation:** Uses Pydantic to ensure the LLM respects password length, symbol counts, and formatting requirements.
* **Secure Clipboard Management:** Automatically copies retrieved passwords to your clipboard and securely clears them.
* **100% Local & Private:** Designed to run seamlessly with local models (like `qwen2.5-coder:7b`) so your credentials never leave your machine.

## 📂 Project Structure

* **`server.py`**: The main FastMCP server application that exposes the `create_new_password` and `get_password` tools to the AI client.
* **`crypto.py`**: The core cryptography engine. Handles secure random password generation, Master Key derivation (using salts), and AES encryption/decryption.
* **`db.py`**: Asynchronous PostgreSQL database manager. Handles connection pooling, table setup, and secure credential upserts using `asyncpg`.
* **`schema.py`**: Pydantic data models used to enforce strict input validation on the LLM's tool calls.
* **`config.py`**: Environment configuration loader. Dynamically builds the safe database URL connection string.
* **`clipboard.py`**: Utility to securely paste decrypted passwords to the system clipboard for immediate user use.

## 🛠️ Prerequisites

* **Python 3.10+**
* **PostgreSQL** (Running locally)
* **An MCP Client** (e.g., Cline, Claude Desktop, Cursor)

## ⚙️ Installation & Setup

1. **Clone or Download the Repository**
2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt

## Database Setup:

Open pgAdmin or psql and create a new database for the manager: CREATE DATABASE password_manager;

## Environment Variable

DB_USER=
DB_PASSWORD=
DB_HOST=127.0.0.1 (dont use "localhost")
DB_PORT=
DB_NAME=

## Connecting to MCP Client

1- Go to the mcp settings of ur llm client (ex: cline on vscode)
2- open config-mcp-settings.json or similar file
3- add following details:
{
  "mcpServers": {
    "local-password-manager": {
      "command": "python",
      "args": [
        "absolute\\path\\to\\your\\server.py"
      ]
    }
  }
} #make sure to use \\ instead of single \

## Example Usage Prompts

1- "Generate a highly secure password for my GitHub account (user@email.com). Make it 24 characters long with 4 symbols."
2- "I need to log into Netflix. Please get my password for account Tushar/tushar@gmail.com"

## Security Disclaimer

This project is designed for local, private use. Ensure your PostgreSQL instance is properly secured and your .env file is never committed to public version control.