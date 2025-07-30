#!/usr/bin/env python3
"""
Simple script to run the HACS + LangGraph example.

Usage:
    python examples/langgraph/run_demo.py

Or:
    uv run examples/langgraph/run_demo.py
"""

from graph import run_example

if __name__ == "__main__":
    try:
        final_state = run_example()
        print("\n✅ Example completed successfully!")
        print(f"Final state contains {len(final_state.get('messages', []))} messages")

    except Exception as e:
        print(f"❌ Example failed with error: {e}")
        import traceback

        traceback.print_exc()
