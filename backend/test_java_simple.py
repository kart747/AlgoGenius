#!/usr/bin/env python3
"""Simple test to debug Java execution in SandboxManager"""

from services.sandbox_manager import SandboxManager

# Simple Java Hello World
java_code = """
public class Solution {
    public static void main(String[] args) {
        System.out.println("Hello from Java!");
    }
}
"""

print("Testing Java execution...")
print("=" * 50)

manager = SandboxManager()
result = manager.run_java(java_code)

print(f"Status: {result['status']}")
print(f"Output:\n{result['output']}")
print("=" * 50)
