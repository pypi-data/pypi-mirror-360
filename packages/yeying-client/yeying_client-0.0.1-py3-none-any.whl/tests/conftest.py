# -*- coding:utf-8 -*-
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# conftest.py
def pytest_sessionfinish(session, exitstatus):
    """在整个测试会话结束时执行"""
    print("\n=== EXECUTING FINAL CLEANUP ===")
    print(session)
    print(exitstatus)
