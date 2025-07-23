#!/usr/bin/env python3
"""
Quick focused test for key APIs
"""

import requests
import json

BACKEND_URL = "https://742fbbda-a33c-48cd-b803-8bcf74555207.preview.emergentagent.com/api"

def test_key_apis():
    print("=== Quick API Test ===")
    
    # Test 1: Dashboard Stats
    print("\n1. Testing Dashboard Stats...")
    response = requests.get(f"{BACKEND_URL}/dashboard/stats", timeout=10)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Dashboard Stats: {data}")
    else:
        print(f"❌ Dashboard Stats failed")
    
    # Test 2: Create Student
    print("\n2. Testing Student Creation...")
    student_data = {
        "student_id": "QUICK001",
        "first_name": "Quick",
        "last_name": "Test",
        "email": "quick@test.com",
        "date_of_birth": "2010-01-01",
        "gender": "male",
        "grade_level": "Grade 8"
    }
    response = requests.post(f"{BACKEND_URL}/students", json=student_data, timeout=10)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        student = response.json()
        print(f"✅ Student Created: {student['first_name']} {student['last_name']}")
        student_id = student['id']
        
        # Test 3: Get Student
        print("\n3. Testing Get Student...")
        response = requests.get(f"{BACKEND_URL}/students/{student_id}", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Student Retrieved: {response.json()['first_name']}")
        
        # Test 4: Update Student
        print("\n4. Testing Update Student...")
        update_data = {"phone": "555-1234"}
        response = requests.put(f"{BACKEND_URL}/students/{student_id}", json=update_data, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Student Updated")
        
        # Test 5: Delete Student
        print("\n5. Testing Delete Student...")
        response = requests.delete(f"{BACKEND_URL}/students/{student_id}", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Student Deleted")
    else:
        print(f"❌ Student Creation failed: {response.text}")
    
    # Test 6: Duplicate Student ID
    print("\n6. Testing Duplicate Student ID...")
    response = requests.post(f"{BACKEND_URL}/students", json=student_data, timeout=10)
    print(f"Status: {response.status_code}")
    if response.status_code == 400:
        print(f"✅ Duplicate validation working: {response.json()}")
    else:
        print(f"❌ Duplicate validation failed")
    
    # Test 7: Get Students List
    print("\n7. Testing Get Students List...")
    response = requests.get(f"{BACKEND_URL}/students", timeout=10)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        students = response.json()
        print(f"✅ Students List: {len(students)} students")
    
    # Test 8: Search Students
    print("\n8. Testing Search Students...")
    response = requests.get(f"{BACKEND_URL}/students?search=Quick", timeout=10)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        students = response.json()
        print(f"✅ Search Results: {len(students)} students")
    
    # Test 9: Create Teacher
    print("\n9. Testing Teacher Creation...")
    teacher_data = {
        "teacher_id": "TCH001",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@school.edu",
        "subject_specialization": "Mathematics"
    }
    response = requests.post(f"{BACKEND_URL}/teachers", json=teacher_data, timeout=10)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        teacher = response.json()
        print(f"✅ Teacher Created: {teacher['first_name']} {teacher['last_name']}")
    else:
        print(f"❌ Teacher Creation failed: {response.text}")
    
    # Test 10: Create Course
    print("\n10. Testing Course Creation...")
    course_data = {
        "course_code": "TEST101",
        "course_name": "Test Course",
        "description": "A test course",
        "credit_hours": 3,
        "grade_levels": ["Grade 8", "Grade 9"]
    }
    response = requests.post(f"{BACKEND_URL}/courses", json=course_data, timeout=10)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        course = response.json()
        print(f"✅ Course Created: {course['course_name']}")
    else:
        print(f"❌ Course Creation failed: {response.text}")

if __name__ == "__main__":
    test_key_apis()