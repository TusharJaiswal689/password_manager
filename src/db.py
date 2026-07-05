import asyncpg
import secrets
from config import db_url

class DatabaseManager:
    def __init__(self):
        self.pool = None

    async def connect(self):
        #Initializes the connection pool to PostgreSQL.
        if not self.pool:
            self.pool = await asyncpg.create_pool(dsn=db_url)

    async def close(self):
        #Closes the connection pool securely.
        if self.pool:
            await self.pool.close()

    async def setup_database(self):
        #Creates the necessary tables if they do not exist.
        async with self.pool.acquire() as conn:
            # Table 1: Vault Metadata (Stores the Master Salt)
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS vault_metadata (
                    id SERIAL PRIMARY KEY,
                    master_salt BYTEA NOT NULL
                );
            ''')
            
            # Table 2: Credentials (Stores encrypted passwords)
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS credentials (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    website TEXT NOT NULL,
                    username TEXT NOT NULL,
                    ciphertext BYTEA NOT NULL,
                    iv BYTEA NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(website, username)
                );
            ''')

    async def get_or_create_salt(self) -> bytes:
        #Fetches the global salt, or generates a new one on first run.
        async with self.pool.acquire() as conn:
            # 1. Try to fetch the existing salt (id will always be 1)
            row = await conn.fetchrow('SELECT master_salt FROM vault_metadata WHERE id = 1')
            if row:
                return row['master_salt']
            
            # 2. If no salt exists (first time running), create one and save it
            new_salt = secrets.token_bytes(16)
            await conn.execute(
                'INSERT INTO vault_metadata (id, master_salt) VALUES (1, $1)',
                new_salt
            )
            return new_salt

    async def save_credential(self, website: str, username: str, ciphertext: bytes, iv: bytes):
        #Saves a new credential or updates an existing one (UPSERT).
        async with self.pool.acquire() as conn:
            # We use ON CONFLICT to safely handle overwriting an existing password
            query = '''
                INSERT INTO credentials (website, username, ciphertext, iv)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (website, username) 
                DO UPDATE SET 
                    ciphertext = EXCLUDED.ciphertext,
                    iv = EXCLUDED.iv,
                    created_at = CURRENT_TIMESTAMP;
            '''
            # $1, $2, etc., protect against SQL injection natively in asyncpg
            await conn.execute(query, website, username, ciphertext, iv)

    async def get_credential(self, website: str, username: str):
        #Retrieves the encrypted bytes for a specific account.
        async with self.pool.acquire() as conn:
            query = '''
                SELECT ciphertext, iv 
                FROM credentials 
                WHERE website = $1 AND username = $2
            '''
            row = await conn.fetchrow(query, website, username)
            
            if row:
                return row['ciphertext'], row['iv']
            return None, None