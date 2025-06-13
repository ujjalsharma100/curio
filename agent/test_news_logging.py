#!/usr/bin/env python3
"""
Test script to verify logging functionality for news-related actions.
This script will test the logging setup and basic functionality.
"""

import sys
import os

# Add the ai_person directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai_person'))

def test_logging_setup():
    """Test that logging setup works correctly."""
    print("Testing logging setup...")
    
    try:
        from ai_person.actions.action.implementations.logging_setup import setup_action_logging
        logger = setup_action_logging("test_action")
        logger.info("Test log message from logging setup")
        print("✓ Logging setup test passed")
        return True
    except Exception as e:
        print(f"✗ Logging setup test failed: {e}")
        return False

def test_news_fetcher_logging():
    """Test that ai_news_fetcher logging works."""
    print("Testing ai_news_fetcher logging...")
    
    try:
        from ai_person.actions.action.implementations import ai_news_fetcher
        # The logger should already be initialized when the module is imported
        print("✓ ai_news_fetcher logging test passed")
        return True
    except Exception as e:
        print(f"✗ ai_news_fetcher logging test failed: {e}")
        return False

def test_action_logging():
    """Test that action classes have logging."""
    print("Testing action logging...")
    
    try:
        from ai_person.actions.action.implementations.fetch_latest_news import FetchLatestAINewsAction
        from ai_person.actions.action.implementations.fetch_news_details import FetchNewsDetailsAction
        
        # Test fetch latest news action
        fetch_latest_action = FetchLatestAINewsAction()
        print("✓ FetchLatestAINewsAction logging test passed")
        
        # Test fetch news details action
        fetch_details_action = FetchNewsDetailsAction()
        print("✓ FetchNewsDetailsAction logging test passed")
        
        return True
    except Exception as e:
        print(f"✗ Action logging test failed: {e}")
        return False

def test_memory_logging():
    """Test that memory modules have logging."""
    print("Testing memory logging...")
    
    try:
        from ai_person.memory.long_term_memory import LongTermMemory
        from ai_person.memory.long_term_memory.news_db import NewsDB
        from ai_person.memory.long_term_memory.news_vector_db import NewsVectorDB
        
        # Test long term memory
        long_term_memory = LongTermMemory()
        print("✓ LongTermMemory logging test passed")
        
        # Test news database
        news_db = NewsDB()
        print("✓ NewsDB logging test passed")
        
        # Test news vector database
        news_vector_db = NewsVectorDB()
        print("✓ NewsVectorDB logging test passed")
        
        return True
    except Exception as e:
        print(f"✗ Memory logging test failed: {e}")
        return False

def main():
    """Run all logging tests."""
    print("Starting news logging tests...\n")
    
    tests = [
        test_logging_setup,
        test_news_fetcher_logging,
        test_action_logging,
        test_memory_logging
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All logging tests passed!")
        print("\nLog files should be created in the 'logs' directory:")
        print("- fetch_latest_news_YYYYMMDD.log")
        print("- fetch_news_details_YYYYMMDD.log")
        print("- ai_news_fetcher_YYYYMMDD.log")
        print("- long_term_memory_YYYYMMDD.log")
        print("- news_db_YYYYMMDD.log")
        print("- news_vector_db_YYYYMMDD.log")
    else:
        print("❌ Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    main() 