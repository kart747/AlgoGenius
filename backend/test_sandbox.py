#!/usr/bin/env python3
"""
Test script for SandboxManager class.
Tests code execution in Python, C++, and Java containers.
"""

from services.sandbox_manager import SandboxManager


def main():
    # Initialize the SandboxManager
    manager = SandboxManager()
    
    # ==============================
    # Test 1: Python
    # ==============================
    print("=" * 50)
    print("---- PYTHON ----")
    print("=" * 50)
    
    python_code = """
print("Hello, World from Python!")
print("Python sandbox is working correctly.")
for i in range(1, 4):
    print(f"Count: {i}")
"""
    
    result = manager.run_python(python_code)
    print(f"Status: {result['status']}")
    print(f"Output:\n{result['output']}")
    print()
    
    # ==============================
    # Test 2: C++
    # ==============================
    print("=" * 50)
    print("---- C++ ----")
    print("=" * 50)
    
    cpp_code = """
#include <iostream>
using namespace std;

int main() {
    cout << "Hello, World from C++!" << endl;
    cout << "C++ sandbox is working correctly." << endl;
    for(int i = 1; i <= 3; i++) {
        cout << "Count: " << i << endl;
    }
    return 0;
}
"""
    
    result = manager.run_cpp(cpp_code)
    print(f"Status: {result['status']}")
    print(f"Output:\n{result['output']}")
    print()
    
    # ==============================
    # Test 3: Java
    # ==============================
    print("=" * 50)
    print("---- JAVA ----")
    print("=" * 50)
    
    java_code = """
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, World from Java!");
        System.out.println("Java sandbox is working correctly.");
        for(int i = 1; i <= 3; i++) {
            System.out.println("Count: " + i);
        }
    }
}
"""
    
    result = manager.run_java(java_code)
    print(f"Status: {result['status']}")
    print(f"Output:\n{result['output']}")
    print()
    
    # ==============================
    # Test 4: Error Handling (Python with syntax error)
    # ==============================
    print("=" * 50)
    print("---- ERROR TEST (Python with syntax error) ----")
    print("=" * 50)
    
    error_code = """
print("This will fail")
print(undefined_variable)  # This variable doesn't exist
"""
    
    result = manager.run_python(error_code)
    print(f"Status: {result['status']}")
    print(f"Output:\n{result['output']}")
    print()
    
    print("=" * 50)
    print("All tests completed!")
    print("=" * 50)


if __name__ == "__main__":
    main()
