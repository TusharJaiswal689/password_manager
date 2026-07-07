import asyncpg
import secrets
from config import db_url
from crypto import generate_auth_hash

class DatabaseManager:
    def __init__(self):
        self.pool = None

    async def connect(self):
        # Initializes the connection pool to PostgreSQL.
        if not self.pool:
            self.pool = await asyncpg.create_pool(dsn=db_url)

    async def close(self):
        # Closes the connection pool securely.
        if self.pool:
            await self.pool.close()

    async def setup_database(self):
        # Creates the necessary tables if they do not exist.
        async with self.pool.acquire() as conn:
            # Table 1: Vault Metadata (Stores the Master Salt, Auth Salt, and Auth Hash)
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS vault_metadata (
                    id SERIAL PRIMARY KEY,
                    master_salt BYTEA NOT NULL,
                    auth_salt BYTEA NOT NULL,
                    auth_hash BYTEA NOT NULL
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

    async def authenticate_or_setup(self, master_password: str) -> bytes:
        """
        Validates the master password against the stored hash. 
        If no hash exists (first run), it creates the salts and sets up the vault.
        Returns the master_salt needed for AES key derivation.
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('SELECT master_salt, auth_salt, auth_hash FROM vault_metadata WHERE id = 1')
            
            if row:
                # 1. Database exists, verify the password
                test_hash = generate_auth_hash(master_password, row['auth_salt'])
                
                # securely compare the hashes to prevent timing attacks
                if secrets.compare_digest(test_hash, row['auth_hash']):
                    return row['master_salt']
                else:
                    raise ValueError("Incorrect Master Password!")
            
            # 2. First time running: Setup the vault metadata
            new_master_salt = secrets.token_bytes(16)
            new_auth_salt = secrets.token_bytes(16)
            new_auth_hash = generate_auth_hash(master_password, new_auth_salt)
            
            await conn.execute(
                'INSERT INTO vault_metadata (id, master_salt, auth_salt, auth_hash) VALUES (1, $1, $2, $3)',
                new_master_salt, new_auth_salt, new_auth_hash
            )
            return new_master_salt

    async def save_credential(self, website: str, username: str, ciphertext: bytes, iv: bytes):
        # Saves a new credential or updates an existing one (UPSERT).
        async with self.pool.acquire() as conn:
            query = '''
                INSERT INTO credentials (website, username, ciphertext, iv)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (website, username) 
                DO UPDATE SET 
                    ciphertext = EXCLUDED.ciphertext,
                    iv = EXCLUDED.iv,
                    created_at = CURRENT_TIMESTAMP;
            '''
            await conn.execute(query, website, username, ciphertext, iv)

    async def get_credential(self, website: str, username: str):
        # Retrieves the encrypted bytes for a specific account.
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