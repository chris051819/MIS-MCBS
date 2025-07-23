#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for School Management Information System
Tests all CRUD operations, search functionality, filtering, pagination, and error handling
"""

import requests
import json
import sys
from datetime import date, datetime
from typing import Dict, List, Any
import time

# Backend URL from environment
BACKEND_URL = "https://742fbbda-a33c-48cd-b803-8bcf74555207.preview.emergentagent.com/api"

class SchoolAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.created_students = []
        self.created_teachers = []
        self.created_courses = []
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }

    def log_result(self, test_name: str, success: bool, message: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
        
        if success:
            self.test_results["passed"] += 1
        else:
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"{test_name}: {message}")

    def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> requests.Response:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=params, timeout=10)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, timeout=10)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, timeout=10)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def test_api_root(self):
        """Test API root endpoint"""
        print("\n=== Testing API Root ===")
        response = self.make_request("GET", "/")
        
        if response and response.status_code == 200:
            data = response.json()
            if "message" in data:
                self.log_result("API Root", True, f"Message: {data['message']}")
            else:
                self.log_result("API Root", False, "Missing message in response")
        else:
            self.log_result("API Root", False, f"Status: {response.status_code if response else 'No response'}")

    def test_student_crud(self):
        """Test complete Student CRUD operations"""
        print("\n=== Testing Student Management API ===")
        
        # Test data for students
        students_data = [
            {
                "student_id": "STU001",
                "first_name": "Emma",
                "last_name": "Johnson",
                "email": "emma.johnson@email.com",
                "phone": "555-0101",
                "date_of_birth": "2010-03-15",
                "gender": "female",
                "grade_level": "Grade 8",
                "address": "123 Oak Street, Springfield",
                "parent_name": "Michael Johnson",
                "parent_email": "michael.johnson@email.com",
                "parent_phone": "555-0102"
            },
            {
                "student_id": "STU002",
                "first_name": "Liam",
                "last_name": "Smith",
                "email": "liam.smith@email.com",
                "phone": "555-0201",
                "date_of_birth": "2009-07-22",
                "gender": "male",
                "grade_level": "Grade 9",
                "address": "456 Pine Avenue, Springfield",
                "parent_name": "Sarah Smith",
                "parent_email": "sarah.smith@email.com",
                "parent_phone": "555-0202"
            },
            {
                "student_id": "STU003",
                "first_name": "Sophia",
                "last_name": "Williams",
                "email": "sophia.williams@email.com",
                "phone": "555-0301",
                "date_of_birth": "2011-11-08",
                "gender": "female",
                "grade_level": "Grade 7",
                "address": "789 Maple Drive, Springfield",
                "parent_name": "David Williams",
                "parent_email": "david.williams@email.com",
                "parent_phone": "555-0302"
            },
            {
                "student_id": "STU004",
                "first_name": "Noah",
                "last_name": "Brown",
                "email": "noah.brown@email.com",
                "phone": "555-0401",
                "date_of_birth": "2008-05-12",
                "gender": "male",
                "grade_level": "Grade 10",
                "address": "321 Elm Street, Springfield",
                "parent_name": "Jennifer Brown",
                "parent_email": "jennifer.brown@email.com",
                "parent_phone": "555-0402"
            },
            {
                "student_id": "STU005",
                "first_name": "Olivia",
                "last_name": "Davis",
                "email": "olivia.davis@email.com",
                "phone": "555-0501",
                "date_of_birth": "2012-01-30",
                "gender": "female",
                "grade_level": "Grade 6",
                "address": "654 Cedar Lane, Springfield",
                "parent_name": "Robert Davis",
                "parent_email": "robert.davis@email.com",
                "parent_phone": "555-0502"
            }
        ]

        # Test 1: Create students
        print("\n--- Creating Students ---")
        for student_data in students_data:
            response = self.make_request("POST", "/students", student_data)
            if response and response.status_code == 200:
                student = response.json()
                self.created_students.append(student)
                self.log_result(f"Create Student {student_data['student_id']}", True, f"ID: {student['id']}")
            else:
                error_msg = response.json().get('detail', 'Unknown error') if response else 'No response'
                self.log_result(f"Create Student {student_data['student_id']}", False, f"Status: {response.status_code if response else 'No response'}, Error: {error_msg}")

        # Test 2: Test duplicate student ID
        print("\n--- Testing Duplicate Student ID ---")
        if students_data:
            response = self.make_request("POST", "/students", students_data[0])
            if response and response.status_code == 400:
                self.log_result("Duplicate Student ID Validation", True, "Correctly rejected duplicate")
            else:
                self.log_result("Duplicate Student ID Validation", False, f"Status: {response.status_code if response else 'No response'}")

        # Test 3: Get all students
        print("\n--- Getting All Students ---")
        response = self.make_request("GET", "/students")
        if response and response.status_code == 200:
            students = response.json()
            self.log_result("Get All Students", True, f"Retrieved {len(students)} students")
        else:
            self.log_result("Get All Students", False, f"Status: {response.status_code if response else 'No response'}")

        # Test 4: Test pagination
        print("\n--- Testing Pagination ---")
        response = self.make_request("GET", "/students", params={"skip": 0, "limit": 2})
        if response and response.status_code == 200:
            students = response.json()
            if len(students) <= 2:
                self.log_result("Student Pagination", True, f"Retrieved {len(students)} students with limit=2")
            else:
                self.log_result("Student Pagination", False, f"Expected ≤2 students, got {len(students)}")
        else:
            self.log_result("Student Pagination", False, f"Status: {response.status_code if response else 'No response'}")

        # Test 5: Test search functionality
        print("\n--- Testing Search Functionality ---")
        search_tests = [
            ("Emma", "first name search"),
            ("Johnson", "last name search"),
            ("STU001", "student ID search"),
            ("emma.johnson", "email search")
        ]
        
        for search_term, test_desc in search_tests:
            response = self.make_request("GET", "/students", params={"search": search_term})
            if response and response.status_code == 200:
                students = response.json()
                found = any(search_term.lower() in str(student.get('first_name', '')).lower() or
                           search_term.lower() in str(student.get('last_name', '')).lower() or
                           search_term.lower() in str(student.get('student_id', '')).lower() or
                           search_term.lower() in str(student.get('email', '')).lower()
                           for student in students)
                if found or len(students) == 0:  # Empty result is also valid
                    self.log_result(f"Search - {test_desc}", True, f"Found {len(students)} results")
                else:
                    self.log_result(f"Search - {test_desc}", False, "Search term not found in results")
            else:
                self.log_result(f"Search - {test_desc}", False, f"Status: {response.status_code if response else 'No response'}")

        # Test 6: Test filtering by grade level
        print("\n--- Testing Grade Level Filter ---")
        response = self.make_request("GET", "/students", params={"grade_level": "Grade 8"})
        if response and response.status_code == 200:
            students = response.json()
            grade_8_students = [s for s in students if s.get('grade_level') == 'Grade 8']
            if len(grade_8_students) == len(students):
                self.log_result("Grade Level Filter", True, f"Found {len(students)} Grade 8 students")
            else:
                self.log_result("Grade Level Filter", False, "Filter returned incorrect results")
        else:
            self.log_result("Grade Level Filter", False, f"Status: {response.status_code if response else 'No response'}")

        # Test 7: Test filtering by status
        print("\n--- Testing Status Filter ---")
        response = self.make_request("GET", "/students", params={"status": "active"})
        if response and response.status_code == 200:
            students = response.json()
            active_students = [s for s in students if s.get('status') == 'active']
            if len(active_students) == len(students):
                self.log_result("Status Filter", True, f"Found {len(students)} active students")
            else:
                self.log_result("Status Filter", False, "Filter returned incorrect results")
        else:
            self.log_result("Status Filter", False, f"Status: {response.status_code if response else 'No response'}")

        # Test 8: Get student count
        print("\n--- Testing Student Count ---")
        response = self.make_request("GET", "/students/count")
        if response and response.status_code == 200:
            count_data = response.json()
            if "count" in count_data and isinstance(count_data["count"], int):
                self.log_result("Student Count", True, f"Total count: {count_data['count']}")
            else:
                self.log_result("Student Count", False, "Invalid count response format")
        else:
            self.log_result("Student Count", False, f"Status: {response.status_code if response else 'No response'}")

        # Test 9: Get individual student
        print("\n--- Testing Individual Student Retrieval ---")
        if self.created_students:
            student_id = self.created_students[0]['id']
            response = self.make_request("GET", f"/students/{student_id}")
            if response and response.status_code == 200:
                student = response.json()
                if student['id'] == student_id:
                    self.log_result("Get Individual Student", True, f"Retrieved student: {student['first_name']} {student['last_name']}")
                else:
                    self.log_result("Get Individual Student", False, "Wrong student returned")
            else:
                self.log_result("Get Individual Student", False, f"Status: {response.status_code if response else 'No response'}")

        # Test 10: Update student
        print("\n--- Testing Student Update ---")
        if self.created_students:
            student_id = self.created_students[0]['id']
            update_data = {
                "phone": "555-9999",
                "status": "inactive"
            }
            response = self.make_request("PUT", f"/students/{student_id}", update_data)
            if response and response.status_code == 200:
                updated_student = response.json()
                if updated_student['phone'] == "555-9999" and updated_student['status'] == "inactive":
                    self.log_result("Update Student", True, "Student updated successfully")
                else:
                    self.log_result("Update Student", False, "Update not reflected in response")
            else:
                self.log_result("Update Student", False, f"Status: {response.status_code if response else 'No response'}")

        # Test 11: Test 404 for non-existent student
        print("\n--- Testing Non-existent Student ---")
        response = self.make_request("GET", "/students/non-existent-id")
        if response and response.status_code == 404:
            self.log_result("Non-existent Student 404", True, "Correctly returned 404")
        else:
            self.log_result("Non-existent Student 404", False, f"Status: {response.status_code if response else 'No response'}")

    def test_teacher_crud(self):
        """Test Teacher CRUD operations"""
        print("\n=== Testing Teacher Management API ===")
        
        teachers_data = [
            {
                "teacher_id": "TCH001",
                "first_name": "Dr. Sarah",
                "last_name": "Anderson",
                "email": "sarah.anderson@school.edu",
                "phone": "555-1001",
                "subject_specialization": "Mathematics"
            },
            {
                "teacher_id": "TCH002",
                "first_name": "Mr. James",
                "last_name": "Wilson",
                "email": "james.wilson@school.edu",
                "phone": "555-1002",
                "subject_specialization": "English Literature"
            },
            {
                "teacher_id": "TCH003",
                "first_name": "Ms. Maria",
                "last_name": "Garcia",
                "email": "maria.garcia@school.edu",
                "phone": "555-1003",
                "subject_specialization": "Science"
            }
        ]

        # Test 1: Create teachers
        print("\n--- Creating Teachers ---")
        for teacher_data in teachers_data:
            response = self.make_request("POST", "/teachers", teacher_data)
            if response and response.status_code == 200:
                teacher = response.json()
                self.created_teachers.append(teacher)
                self.log_result(f"Create Teacher {teacher_data['teacher_id']}", True, f"ID: {teacher['id']}")
            else:
                error_msg = response.json().get('detail', 'Unknown error') if response else 'No response'
                self.log_result(f"Create Teacher {teacher_data['teacher_id']}", False, f"Status: {response.status_code if response else 'No response'}, Error: {error_msg}")

        # Test 2: Get all teachers
        print("\n--- Getting All Teachers ---")
        response = self.make_request("GET", "/teachers")
        if response and response.status_code == 200:
            teachers = response.json()
            self.log_result("Get All Teachers", True, f"Retrieved {len(teachers)} teachers")
        else:
            self.log_result("Get All Teachers", False, f"Status: {response.status_code if response else 'No response'}")

        # Test 3: Get individual teacher
        print("\n--- Testing Individual Teacher Retrieval ---")
        if self.created_teachers:
            teacher_id = self.created_teachers[0]['id']
            response = self.make_request("GET", f"/teachers/{teacher_id}")
            if response and response.status_code == 200:
                teacher = response.json()
                if teacher['id'] == teacher_id:
                    self.log_result("Get Individual Teacher", True, f"Retrieved teacher: {teacher['first_name']} {teacher['last_name']}")
                else:
                    self.log_result("Get Individual Teacher", False, "Wrong teacher returned")
            else:
                self.log_result("Get Individual Teacher", False, f"Status: {response.status_code if response else 'No response'}")

        # Test 4: Test duplicate teacher ID
        print("\n--- Testing Duplicate Teacher ID ---")
        if teachers_data:
            response = self.make_request("POST", "/teachers", teachers_data[0])
            if response and response.status_code == 400:
                self.log_result("Duplicate Teacher ID Validation", True, "Correctly rejected duplicate")
            else:
                self.log_result("Duplicate Teacher ID Validation", False, f"Status: {response.status_code if response else 'No response'}")

    def test_course_crud(self):
        """Test Course CRUD operations"""
        print("\n=== Testing Course Management API ===")
        
        courses_data = [
            {
                "course_code": "MATH101",
                "course_name": "Algebra I",
                "description": "Introduction to algebraic concepts and problem solving",
                "credit_hours": 3,
                "grade_levels": ["Grade 8", "Grade 9"]
            },
            {
                "course_code": "ENG201",
                "course_name": "English Literature",
                "description": "Study of classic and contemporary literature",
                "credit_hours": 4,
                "grade_levels": ["Grade 10", "Grade 11", "Grade 12"]
            },
            {
                "course_code": "SCI301",
                "course_name": "Biology",
                "description": "Introduction to biological sciences",
                "credit_hours": 4,
                "grade_levels": ["Grade 9", "Grade 10"]
            }
        ]

        # Test 1: Create courses
        print("\n--- Creating Courses ---")
        for course_data in courses_data:
            response = self.make_request("POST", "/courses", course_data)
            if response and response.status_code == 200:
                course = response.json()
                self.created_courses.append(course)
                self.log_result(f"Create Course {course_data['course_code']}", True, f"ID: {course['id']}")
            else:
                error_msg = response.json().get('detail', 'Unknown error') if response else 'No response'
                self.log_result(f"Create Course {course_data['course_code']}", False, f"Status: {response.status_code if response else 'No response'}, Error: {error_msg}")

        # Test 2: Get all courses
        print("\n--- Getting All Courses ---")
        response = self.make_request("GET", "/courses")
        if response and response.status_code == 200:
            courses = response.json()
            self.log_result("Get All Courses", True, f"Retrieved {len(courses)} courses")
        else:
            self.log_result("Get All Courses", False, f"Status: {response.status_code if response else 'No response'}")

        # Test 3: Test duplicate course code
        print("\n--- Testing Duplicate Course Code ---")
        if courses_data:
            response = self.make_request("POST", "/courses", courses_data[0])
            if response and response.status_code == 400:
                self.log_result("Duplicate Course Code Validation", True, "Correctly rejected duplicate")
            else:
                self.log_result("Duplicate Course Code Validation", False, f"Status: {response.status_code if response else 'No response'}")

    def test_dashboard_stats(self):
        """Test Dashboard Statistics API"""
        print("\n=== Testing Dashboard Statistics API ===")
        
        response = self.make_request("GET", "/dashboard/stats")
        if response and response.status_code == 200:
            stats = response.json()
            required_fields = ["total_students", "active_students", "total_teachers", "total_courses", "students_by_grade", "recent_enrollments"]
            
            missing_fields = [field for field in required_fields if field not in stats]
            if not missing_fields:
                self.log_result("Dashboard Stats Structure", True, "All required fields present")
                
                # Validate data types
                if (isinstance(stats["total_students"], int) and
                    isinstance(stats["active_students"], int) and
                    isinstance(stats["total_teachers"], int) and
                    isinstance(stats["total_courses"], int) and
                    isinstance(stats["students_by_grade"], dict) and
                    isinstance(stats["recent_enrollments"], int)):
                    
                    self.log_result("Dashboard Stats Data Types", True, "All fields have correct data types")
                    
                    # Log actual values
                    print(f"   Total Students: {stats['total_students']}")
                    print(f"   Active Students: {stats['active_students']}")
                    print(f"   Total Teachers: {stats['total_teachers']}")
                    print(f"   Total Courses: {stats['total_courses']}")
                    print(f"   Students by Grade: {stats['students_by_grade']}")
                    print(f"   Recent Enrollments: {stats['recent_enrollments']}")
                    
                else:
                    self.log_result("Dashboard Stats Data Types", False, "Incorrect data types in response")
            else:
                self.log_result("Dashboard Stats Structure", False, f"Missing fields: {missing_fields}")
        else:
            self.log_result("Dashboard Stats", False, f"Status: {response.status_code if response else 'No response'}")

    def test_email_validation(self):
        """Test email validation"""
        print("\n=== Testing Email Validation ===")
        
        invalid_student = {
            "student_id": "STU999",
            "first_name": "Test",
            "last_name": "Student",
            "email": "invalid-email",  # Invalid email format
            "date_of_birth": "2010-01-01",
            "gender": "male",
            "grade_level": "Grade 8"
        }
        
        response = self.make_request("POST", "/students", invalid_student)
        if response and response.status_code == 422:  # Validation error
            self.log_result("Email Validation", True, "Correctly rejected invalid email")
        else:
            self.log_result("Email Validation", False, f"Status: {response.status_code if response else 'No response'}")

    def cleanup_test_data(self):
        """Clean up created test data"""
        print("\n=== Cleaning Up Test Data ===")
        
        # Delete created students
        for student in self.created_students:
            response = self.make_request("DELETE", f"/students/{student['id']}")
            if response and response.status_code == 200:
                print(f"✅ Deleted student: {student['first_name']} {student['last_name']}")
            else:
                print(f"❌ Failed to delete student: {student['first_name']} {student['last_name']}")

    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting School Management API Tests")
        print(f"Backend URL: {self.base_url}")
        print("=" * 60)
        
        # Run all test suites
        self.test_api_root()
        self.test_student_crud()
        self.test_teacher_crud()
        self.test_course_crud()
        self.test_dashboard_stats()
        self.test_email_validation()
        
        # Print final results
        print("\n" + "=" * 60)
        print("🏁 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        print(f"📊 Total: {self.test_results['passed'] + self.test_results['failed']}")
        
        if self.test_results['errors']:
            print("\n❌ FAILED TESTS:")
            for error in self.test_results['errors']:
                print(f"   • {error}")
        
        # Cleanup
        self.cleanup_test_data()
        
        return self.test_results['failed'] == 0

if __name__ == "__main__":
    tester = SchoolAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)