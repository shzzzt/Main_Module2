from typing import Dict, List, Optional, Any
import json
from datetime import datetime, timedelta
from .json_paths import read_json_file, write_json_file


class AttendanceService:
    """Service for handling attendance data with role-based access control"""
    
    def __init__(self):
        self.attendance_file = "attendance.json"
        self.classes_file = "classes.json"
        self.users_file = "users.json"
        
        # Initialize default data if files don't exist
        self.initialize_data()
    
    def initialize_data(self):
        """Initialize data files with default structure if they don't exist"""
        # Initialize classes
        classes = read_json_file(self.classes_file)
        if not classes:
            write_json_file(self.classes_file, {})
        
        # Initialize attendance records
        attendance = read_json_file(self.attendance_file)
        if not attendance:
            write_json_file(self.attendance_file, {"records": {}, "classes": {}})
        
        # Initialize users (for role-based access)
        users = read_json_file(self.users_file)
        if not users:
            default_users = {
                "users": {
                    "1": {"id": 1, "name": "Teacher", "role": "teacher", "classes": [1]},
                    "2": {"id": 2, "name": "Assistant", "role": "assistant", "classes": [1]},
                    "3": {"id": 3, "name": "Student 1", "role": "student", "classes": [1]},
                    "4": {"id": 4, "name": "Parent 1", "role": "parent", "children": [3]}
                }
            }
            write_json_file(self.users_file, default_users)
    
    # ========== Class Management ==========
    
    def get_class(self, class_id: int) -> Optional[Dict]:
        """Get class information"""
        classes = read_json_file(self.classes_file)
        class_str = str(class_id)
        
        if class_str in classes:
            return classes[class_str]
        
        # Create default class if not exists
        default_class = {
            "id": class_id,
            "name": f"Class {class_id}",
            "created_at": datetime.now().isoformat(),
            "students": []
        }
        
        classes[class_str] = default_class
        write_json_file(self.classes_file, classes)
        return default_class
    
    def save_class(self, class_id: int, class_data: Dict) -> bool:
        """Save class information"""
        classes = read_json_file(self.classes_file)
        classes[str(class_id)] = class_data
        return write_json_file(self.classes_file, classes)
    
    # ========== Student Management ==========
    
    def get_students_for_class(self, class_id: int) -> List[Dict]:
        """Get all students for a class"""
        class_data = self.get_class(class_id)
        if not class_data:
            return []
        
        students = class_data.get("students", [])
        
        # Add default students if none exist
        if not students:
            default_students = [
                {"id": 1, "name": "Castro, Carlos Fidel", "student_code": "S001"},
                {"id": 2, "name": "Dela Cruz, Maria Santos", "student_code": "S002"},
                {"id": 3, "name": "Reyes, Juan Pablo", "student_code": "S003"},
                {"id": 4, "name": "Santos, Ana Marie", "student_code": "S004"},
                {"id": 5, "name": "Garcia, Jose Miguel", "student_code": "S005"},
                {"id": 6, "name": "Tan, Michael Johnson", "student_code": "S006"},
                {"id": 7, "name": "Lim, Samantha Rose", "student_code": "S007"},
                {"id": 8, "name": "Nguyen, Andrew Kim", "student_code": "S008"},
                {"id": 9, "name": "Smith, Jennifer Lynn", "student_code": "S009"},
                {"id": 10, "name": "Johnson, Robert James", "student_code": "S010"}
            ]
            
            class_data["students"] = default_students
            self.save_class(class_id, class_data)
            return default_students
        
        return students
    
    def add_student_to_class(self, class_id: int, student_data: Dict) -> bool:
        """Add a student to a class"""
        class_info = self.get_class(class_id)
        if not class_info:
            return False
        
        students = class_info.get("students", [])
        
        # Generate ID if not provided
        if "id" not in student_data:
            max_id = max([s.get("id", 0) for s in students], default=0)
            student_data["id"] = max_id + 1
        
        students.append(student_data)
        class_info["students"] = students
        
        return self.save_class(class_id, class_info)
    
    # ========== Attendance Records ==========
    
    def get_attendance_for_date(self, class_id: int, date: str) -> Dict[str, Dict]:
        """Get attendance records for a specific date"""
        attendance_data = read_json_file(self.attendance_file)
        class_str = str(class_id)
        
        if class_str not in attendance_data.get("classes", {}):
            attendance_data["classes"][class_str] = {}
        
        if date not in attendance_data["classes"][class_str]:
            # Initialize with default (all present) if no records exist
            students = self.get_students_for_class(class_id)
            default_records = {}
            for student in students:
                default_records[str(student["id"])] = {
                    "student_id": student["id"],
                    "student_name": student["name"],
                    "is_present": True,  # Default to present
                    "recorded_at": datetime.now().isoformat()
                }
            attendance_data["classes"][class_str][date] = default_records
            write_json_file(self.attendance_file, attendance_data)
        
        return attendance_data["classes"][class_str][date]
    
    def save_attendance_for_date(self, class_id: int, date: str, 
                               attendance_records: List[Dict]) -> bool:
        """Save attendance records for a date"""
        attendance_data = read_json_file(self.attendance_file)
        class_str = str(class_id)
        
        if class_str not in attendance_data.get("classes", {}):
            attendance_data["classes"][class_str] = {}
        
        # Convert records to dict format
        records_dict = {}
        for record in attendance_records:
            student_id = str(record["student_id"])
            records_dict[student_id] = {
                "student_id": record["student_id"],
                "student_name": record["student_name"],
                "is_present": record["is_present"],
                "recorded_at": datetime.now().isoformat(),
                "recorded_by": "system"  # Would be user_id in real app
            }
        
        attendance_data["classes"][class_str][date] = records_dict
        
        # Also add to global records for history
        if "records" not in attendance_data:
            attendance_data["records"] = []
        
        # Add as a batch record
        batch_record = {
            "class_id": class_id,
            "date": date,
            "records": records_dict,
            "recorded_at": datetime.now().isoformat()
        }
        attendance_data["records"].append(batch_record)
        
        return write_json_file(self.attendance_file, attendance_data)
    
    # ========== History and Statistics ==========
    
    def get_attendance_history(self, class_id: int, 
                             start_date: Optional[str] = None,
                             end_date: Optional[str] = None) -> List[Dict]:
        """Get attendance history for a class within date range"""
        attendance_data = read_json_file(self.attendance_file)
        class_str = str(class_id)
        
        if class_str not in attendance_data.get("classes", {}):
            return []
        
        class_attendance = attendance_data["classes"][class_str]
        
        # Filter by date range if provided
        filtered_days = []
        for date, records in class_attendance.items():
            if start_date and date < start_date:
                continue
            if end_date and date > end_date:
                continue
            
            # Calculate statistics for this day
            present_count = sum(1 for r in records.values() if r.get("is_present", False))
            total_students = len(records)
            absent_count = total_students - present_count
            attendance_rate = (present_count / total_students * 100) if total_students > 0 else 0
            
            filtered_days.append({
                "date": date,
                "attendance": records,
                "present_count": present_count,
                "absent_count": absent_count,
                "total_students": total_students,
                "attendance_rate": round(attendance_rate, 1)
            })
        
        # Sort by date (newest first)
        filtered_days.sort(key=lambda x: x["date"], reverse=True)
        
        return filtered_days
    
    def get_student_attendance_history(self, class_id: int, student_id: int) -> List[Dict]:
        """Get attendance history for a specific student"""
        history = self.get_attendance_history(class_id)
        
        student_history = []
        for day in history:
            student_record = day["attendance"].get(str(student_id))
            if student_record:
                student_day = {
                    "date": day["date"],
                    "is_present": student_record.get("is_present", False),
                    "recorded_at": student_record.get("recorded_at")
                }
                student_history.append(student_day)
        
        return student_history
    
    def get_attendance_stats(self, class_id: int) -> Dict:
        """Get comprehensive attendance statistics for a class"""
        history = self.get_attendance_history(class_id)
        students = self.get_students_for_class(class_id)
        
        if not history or not students:
            return {}
        
        total_days = len(history)
        total_present = sum(day["present_count"] for day in history)
        total_absent = sum(day["absent_count"] for day in history)
        
        # Calculate student-specific stats
        student_stats = []
        for student in students:
            student_id = str(student["id"])
            present_days = sum(1 for day in history 
                             if day["attendance"].get(student_id, {}).get("is_present", False))
            absent_days = total_days - present_days
            attendance_rate = (present_days / total_days * 100) if total_days > 0 else 0
            
            student_stats.append({
                "student_id": student["id"],
                "student_name": student["name"],
                "student_code": student.get("student_code", ""),
                "present_days": present_days,
                "absent_days": absent_days,
                "attendance_rate": round(attendance_rate, 1),
                "status": "Good" if attendance_rate >= 90 else 
                         "Warning" if attendance_rate >= 75 else 
                         "Critical"
            })
        
        # Calculate average attendance
        average_attendance = (total_present / (total_present + total_absent) * 100) if (total_present + total_absent) > 0 else 0
        
        # Get perfect attendance students
        perfect_attendance = [s for s in student_stats if s["absent_days"] == 0]
        
        # Get attendance by day (last 7 days)
        recent_days = history[:7]
        attendance_by_day = [
            {"date": day["date"], "rate": day["attendance_rate"]}
            for day in recent_days
        ]
        
        return {
            "total_students": len(students),
            "total_days": total_days,
            "total_present": total_present,
            "total_absent": total_absent,
            "average_attendance": round(average_attendance, 1),
            "perfect_attendance_count": len(perfect_attendance),
            "student_performance": student_stats,
            "attendance_rate_by_day": attendance_by_day
        }
    
    def get_student_attendance_stats(self, class_id: int, student_id: int) -> Dict:
        """Get attendance statistics for a specific student"""
        history = self.get_attendance_history(class_id)
        student_history = self.get_student_attendance_history(class_id, student_id)
        
        if not history or not student_history:
            return {}
        
        # Calculate streaks
        current_streak = 0
        for record in reversed(student_history):
            if record["is_present"]:
                current_streak += 1
            else:
                break
        
        # Calculate stats
        total_days = len(history)
        present_days = sum(1 for record in student_history if record["is_present"])
        absent_days = total_days - present_days
        attendance_rate = (present_days / total_days * 100) if total_days > 0 else 0
        
        # Get recent attendance
        recent_attendance = student_history[:7]
        
        return {
            "total_days": total_days,
            "present_days": present_days,
            "absent_days": absent_days,
            "attendance_rate": round(attendance_rate, 1),
            "current_streak": current_streak,
            "recent_attendance": recent_attendance
        }
    
    def generate_attendance_report(self, class_id: int, 
                                 start_date: str, end_date: str) -> Dict:
        """Generate detailed attendance report for date range"""
        history = self.get_attendance_history(class_id, start_date, end_date)
        stats = self.get_attendance_stats(class_id)
        
        if not history:
            return {}
        
        # Get student performance for the date range
        students = self.get_students_for_class(class_id)
        student_performance = []
        
        for student in students:
            student_id = str(student["id"])
            present_days = sum(1 for day in history 
                             if day["attendance"].get(student_id, {}).get("is_present", False))
            total_days_in_range = len(history)
            absent_days = total_days_in_range - present_days
            attendance_rate = (present_days / total_days_in_range * 100) if total_days_in_range > 0 else 0
            
            student_performance.append({
                "student_id": student["id"],
                "student_name": student["name"],
                "student_code": student.get("student_code", ""),
                "present_days": present_days,
                "absent_days": absent_days,
                "attendance_rate": round(attendance_rate, 1),
                "status": "Good" if attendance_rate >= 90 else 
                         "Warning" if attendance_rate >= 75 else 
                         "Critical"
            })
        
        return {
            "summary": {
                "class_id": class_id,
                "start_date": start_date,
                "end_date": end_date,
                "total_students": len(students),
                "total_days": len(history),
                "days_with_attendance": len(history),
                "average_attendance": stats.get("average_attendance", 0)
            },
            "student_performance": student_performance,
            "daily_summary": [
                {
                    "date": day["date"],
                    "present_count": day["present_count"],
                    "absent_count": day["absent_count"],
                    "attendance_rate": day["attendance_rate"]
                }
                for day in history
            ]
        }
    def get_student_by_user_id(self, class_id: int, user_id: int) -> Optional[Dict]:
        """Get a specific student by user ID"""
        students = self.get_students_for_class(class_id)
        
        for student in students:
            if student.get("user_id") == user_id:
                return student
        
        return None