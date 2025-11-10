"""Simple Supabase database schema validation"""
from backend.core.database import get_supabase_admin
from supabase import Client


def test_tables_exist():
    """Test that all 8 tables are created by querying them"""
    supabase = get_supabase_admin()
    
    tables = [
        'users',
        'libraries',
        'books',
        'kb_items',
        'runs',
        'artifacts',
        'reminders',
        'audits'
    ]
    
    print("[START] Testing Supabase database schema...\n")
    
    success_count = 0
    for table in tables:
        try:
            # Try to query the table (limit 0 to avoid data)
            result = supabase.table(table).select("*").limit(0).execute()
            print(f"[OK] Table '{table}' exists")
            success_count += 1
        except Exception as e:
            print(f"[FAIL] Table '{table}' not found: {e}")
    
    print(f"\n[SUMMARY] {success_count}/{len(tables)} tables verified")
    
    if success_count == len(tables):
        print("[SUCCESS] All tables exist!")
        return True
    else:
        print(f"[FAIL] {len(tables) - success_count} tables missing")
        return False


def test_kb_items_sample():
    """Test kb_items table has correct structure"""
    supabase = get_supabase_admin()
    
    try:
        # Query kb_items with limit 1 to check structure
        result = supabase.table("kb_items").select("*").limit(1).execute()
        
        if result.data and len(result.data) > 0:
            sample = result.data[0]
            required_fields = [
                'kb_id', 'domain', 'type', 'anchor_id', 
                'content', 'is_fusion', 'reference_books'
            ]
            
            for field in required_fields:
                if field in sample:
                    print(f"[OK] kb_items.{field} exists")
                else:
                    print(f"[WARN] kb_items.{field} missing")
        else:
            print("[INFO] kb_items table is empty (expected for new DB)")
        
        return True
    except Exception as e:
        print(f"[FAIL] kb_items test failed: {e}")
        return False


def test_database_connection():
    """Test basic database connection"""
    supabase = get_supabase_admin()
    
    try:
        # Simple query to test connection
        result = supabase.table("kb_items").select("count").limit(0).execute()
        print("[OK] Database connection successful")
        return True
    except Exception as e:
        print(f"[FAIL] Database connection failed: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Supabase Database Schema Validation")
    print("=" * 60 + "\n")
    
    # Test 1: Connection
    test_database_connection()
    print()
    
    # Test 2: Tables exist
    tables_ok = test_tables_exist()
    print()
    
    # Test 3: KB Items structure
    test_kb_items_sample()
    print()
    
    if tables_ok:
        print("=" * 60)
        print("[PASS] Database schema validation complete!")
        print("=" * 60)
        exit(0)
    else:
        print("=" * 60)
        print("[FAIL] Database schema validation failed!")
        print("=" * 60)
        exit(1)

