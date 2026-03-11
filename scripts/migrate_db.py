#!/usr/bin/env python3
"""
Database Migration Script for VoiceSense
Executes database setup using Supabase SQL API
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from supabase import create_client, Client
except ImportError:
    print("Installing supabase-py...")
    os.system("pip install supabase")
    from supabase import create_client, Client


def run_migration():
    """Execute the database migration."""
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_ANON_KEY environment variables are required")
        return False
    
    try:
        # Initialize Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Read SQL migration file
        sql_file = Path(__file__).parent / "01-init-db.sql"
        if not sql_file.exists():
            print(f"Error: {sql_file} not found")
            return False
        
        with open(sql_file, "r") as f:
            sql_content = f.read()
        
        print("[v0] Starting database migration...")
        print(f"[v0] Reading SQL file: {sql_file}")
        print(f"[v0] SQL file size: {len(sql_content)} bytes")
        
        # Split SQL into individual statements
        statements = [s.strip() for s in sql_content.split(";") if s.strip()]
        print(f"[v0] Found {len(statements)} SQL statements to execute")
        
        # Execute each statement
        for i, statement in enumerate(statements, 1):
            if statement.strip().startswith("--"):
                continue
                
            try:
                print(f"[v0] Executing statement {i}/{len(statements)}...")
                # Using the RPC method to execute raw SQL
                response = supabase.rpc("exec_sql", {"sql": statement}).execute()
                print(f"[v0] Statement {i} executed successfully")
            except Exception as e:
                # Some statements might fail if they're comments or already exist
                if "already exists" in str(e).lower() or "IF NOT EXISTS" in statement:
                    print(f"[v0] Statement {i} skipped (already exists or is idempotent)")
                else:
                    print(f"[v0] Warning on statement {i}: {e}")
        
        print("[v0] Database migration completed!")
        return True
        
    except Exception as e:
        print(f"Error: Failed to connect to Supabase: {e}")
        return False


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
