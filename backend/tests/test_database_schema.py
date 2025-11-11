"""Test Supabase database schema and RLS policies"""
import pytest
from backend.core.database import get_supabase_admin
from supabase import Client


@pytest.fixture
def supabase_admin() -> Client:
    """Get Supabase admin client (bypasses RLS)"""
    return get_supabase_admin()


def test_tables_exist(supabase_admin: Client):
    """Test that all 8 tables are created"""
    # Query information_schema to check tables
    result = supabase_admin.rpc(
        'exec_sql',
        {
            'query': """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """
        }
    ).execute()
    
    table_names = [row['table_name'] for row in result.data]
    
    expected_tables = [
        'artifacts',
        'audits',
        'books',
        'kb_items',
        'libraries',
        'reminders',
        'runs',
        'users'
    ]
    
    for table in expected_tables:
        assert table in table_names, f"Table {table} not found"
    
    print(f"[PASS] All {len(expected_tables)} tables exist")


def test_indexes_exist(supabase_admin: Client):
    """Test that indexes are created"""
    result = supabase_admin.rpc(
        'exec_sql',
        {
            'query': """
                SELECT indexname, tablename 
                FROM pg_indexes 
                WHERE schemaname = 'public'
                AND indexname LIKE 'idx_%'
                ORDER BY tablename, indexname
            """
        }
    ).execute()
    
    indexes = result.data
    
    # Check key indexes
    index_names = [idx['indexname'] for idx in indexes]
    
    expected_indexes = [
        'idx_libraries_user',
        'idx_books_library',
        'idx_kb_items_domain',
        'idx_kb_items_anchor',
        'idx_runs_user',
        'idx_runs_status',
        'idx_artifacts_run',
        'idx_reminders_user_active',
        'idx_audits_run'
    ]
    
    for idx in expected_indexes:
        assert idx in index_names, f"Index {idx} not found"
    
    print(f"[PASS] All {len(expected_indexes)} indexes exist")


def test_rls_enabled(supabase_admin: Client):
    """Test that RLS is enabled on all tables"""
    result = supabase_admin.rpc(
        'exec_sql',
        {
            'query': """
                SELECT tablename, rowsecurity 
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY tablename
            """
        }
    ).execute()
    
    tables = result.data
    
    for table in tables:
        assert table['rowsecurity'] is True, f"RLS not enabled on {table['tablename']}"
    
    print(f"[PASS] RLS enabled on all {len(tables)} tables")


def test_rls_policies_exist(supabase_admin: Client):
    """Test that RLS policies are created"""
    result = supabase_admin.rpc(
        'exec_sql',
        {
            'query': """
                SELECT COUNT(*) as policy_count
                FROM pg_policies 
                WHERE schemaname = 'public'
            """
        }
    ).execute()
    
    policy_count = result.data[0]['policy_count']
    
    # We have multiple policies per table
    assert policy_count >= 15, f"Expected at least 15 policies, found {policy_count}"
    
    print(f"[PASS] {policy_count} RLS policies created")


def test_foreign_keys_exist(supabase_admin: Client):
    """Test that foreign keys are created"""
    result = supabase_admin.rpc(
        'exec_sql',
        {
            'query': """
                SELECT
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                    AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_schema = 'public'
                ORDER BY tc.table_name, kcu.column_name
            """
        }
    ).execute()
    
    foreign_keys = result.data
    
    # Check key foreign keys
    fk_map = {fk['table_name']: fk['column_name'] for fk in foreign_keys}
    
    assert fk_map.get('libraries') == 'user_id', "libraries.user_id FK not found"
    assert fk_map.get('books') == 'library_id', "books.library_id FK not found"
    assert fk_map.get('runs') == 'user_id', "runs.user_id FK not found"
    assert fk_map.get('artifacts') == 'run_id', "artifacts.run_id FK not found"
    
    print(f"[PASS] {len(foreign_keys)} foreign keys created")


def test_kb_items_check_constraint(supabase_admin: Client):
    """Test that kb_items.domain has CHECK constraint"""
    result = supabase_admin.rpc(
        'exec_sql',
        {
            'query': """
                SELECT
                    tc.constraint_name,
                    cc.check_clause
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.check_constraints AS cc
                    ON tc.constraint_name = cc.constraint_name
                WHERE tc.table_name = 'kb_items'
                AND tc.constraint_type = 'CHECK'
                AND cc.check_clause LIKE '%domain%'
            """
        }
    ).execute()
    
    assert len(result.data) > 0, "kb_items.domain CHECK constraint not found"
    
    check_clause = result.data[0]['check_clause']
    
    # Check that all 4 domains are in the constraint
    required_domains = ['경제경영', '과학기술', '역사사회', '인문자기계발']
    for domain in required_domains:
        assert domain in check_clause, f"Domain '{domain}' not in CHECK constraint"
    
    print(f"[PASS] kb_items.domain CHECK constraint verified")


def test_runs_status_check_constraint(supabase_admin: Client):
    """Test that runs.status has CHECK constraint"""
    result = supabase_admin.rpc(
        'exec_sql',
        {
            'query': """
                SELECT
                    tc.constraint_name,
                    cc.check_clause
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.check_constraints AS cc
                    ON tc.constraint_name = cc.constraint_name
                WHERE tc.table_name = 'runs'
                AND tc.constraint_type = 'CHECK'
                AND cc.check_clause LIKE '%status%'
            """
        }
    ).execute()
    
    assert len(result.data) > 0, "runs.status CHECK constraint not found"
    
    check_clause = result.data[0]['check_clause']
    
    # Check that all statuses are in the constraint
    required_statuses = ['pending', 'running', 'completed', 'failed']
    for status in required_statuses:
        assert status in check_clause, f"Status '{status}' not in CHECK constraint"
    
    print(f"[PASS] runs.status CHECK constraint verified")


if __name__ == "__main__":
    """Run tests directly"""
    print("[START] Testing Supabase database schema...\n")
    
    admin = get_supabase_admin()
    
    try:
        test_tables_exist(admin)
        test_indexes_exist(admin)
        test_rls_enabled(admin)
        test_rls_policies_exist(admin)
        test_foreign_keys_exist(admin)
        test_kb_items_check_constraint(admin)
        test_runs_status_check_constraint(admin)
        
        print("\n[SUCCESS] All database schema tests passed!")
        
    except AssertionError as e:
        print(f"\n[FAIL] {e}")
        raise
    except Exception as e:
        print(f"\n[ERROR] {e}")
        raise

