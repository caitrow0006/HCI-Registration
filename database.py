# ---------------------------------------------------------------------
# In-memory "database"
# ---------------------------------------------------------------------

#@Caitriona
class Schedule(BaseModel):
    building: str
    days: str
    room_num: str
    start_hour: int #use 24 hour time (ex 2015 = 8:15 pm)
    end_hour: int #use 24 hour time

class Course(BaseModel):
    id: int
    department: str
    course_num: int
    section_num: int
    title: str
    instructor: str
    time: Schedule
    capacity: int
    
class Enrollment(BaseModel):
    id: int
    course: Course
    student: str #just placeholder for now. may or may not be used later.
  
#SECTIONS defines a list of course objects
SECTIONS = [
    Course(id=1, department="MATH", course_num=425, section_num=1, title="Calculus I", instructor="John McClain", Schedule(building="Demeritt", days="MWF", room_num="311", start_hour=0910, end_hour=1000), capacity=25),
    Course(id=2, department="MATH", course_num=425, section_num=2, title="Calculus I", instructor="Adam Boucher", Schedule(building="Parsons", days="MWF", room_num="N108", start_hour=1310, end_hour=1400), capacity=20),
    Course(id=3, department="MATH", course_num=425, section_num=3, title="Calculus I", instructor="Adam Boucher", Schedule(building="Spaulding", days="TR", room_num="145", start_hour=0810, end_hour=0930), capacity=30),
    Course(id=4, department="PHYS", course_num=407, section_num=1, title="Physics I", instructor="Jiadong Zang", Schedule(building="Demeritt", days="TR", room_num="311", start_hour=1510, end_hour=1630), capacity=25),
    Course(id=5, department="PHYS", course_num=408, section_num=1, title="Physics II", instructor="Jiadong Zang", Schedule(building="Demeritt", days="MWF", room_num="110", start_hour=0810, end_hour=0900), capacity=50),
    Course(id=6, department="CS", course_num=415, section_num=1, title="Introduction to Computer Science I", instructor="Jason Reeves", Schedule(building="Kingsbury", days="MWF", room_num="N101", start_hour=1210, end_hour=1300), capacity=20),
    Course(id=7, department="CS", course_num=415, section_num=2, title="Introduction to Computer Science I", instructor="Jason Reeves", Schedule(building="Kingsbury", days="MWF", room_num="N101", start_hour=1310, end_hour=1400), capacity=20),
    Course(id=8, department="CS", course_num=416, section_num=1, title="Introduction to Computer Science II", instructor="Michael Kulik", Schedule(building="Hamilton Smith", days="MWF", room_num="135", start_hour=1410, end_hour=1500), capacity=30),
    Course(id=9, department="CS", course_num=416, section_num=2, title="Introduction to Computer Science II", instructor="Michael Kulik", Schedule(building="Parsons", days="MWF", room_num="G04", start_hour=1010, end_hour=1100), capacity=25),
    Course(id=10, department="CS", course_num=416, section_num=3, title="Introduction to Computer Science II", instructor="Matthew Plumlee", Schedule(building="Kingsbury", days="TR", room_num="328", start_hour=1110, end_hour=1230), capacity=25),
    Course(id=11, department="CS", course_num=520, section_num=1, title="Computer Organization and System-Level Programming", instructor="Arvind Narayan", Schedule(building="Kingsbury", days="TR", room_num="S145", start_hour=0940, end_hour=1100), capacity=70),
    Course(id=12, department="CS", course_num=720, section_num=1, title="Systems Programming", instructor="Arvind Narayan", Schedule(building="Kingsbury", days="MWF", room_num="N133", start_hour=0910, end_hour=1000), capacity=15),
    Course(id=13, department="CS", course_num=760, section_num=1, title="Human-Computer Interaction", instructor="Laura South", Schedule(building="Kingsbury", days="MWF", room_num="N133", start_hour=1110, end_hour=1200), capacity=20),
    Course(id=14, department="CS", course_num=760, section_num=2, title="Human-Computer Interaction", instructor="Laura South", Schedule(building="Kingsbury", days="MWF", room_num="N113", start_hour=1210, end_hour=1300), capacity=20),
    Course(id=15, department="CS", course_num=799, section_num=1, title="Thesis", instructor="Dongpeng Xu", Schedule(building="N/A", days="TBA", room_num="N/A", start_hour=0000, end_hour=0000), capacity=1)
]

# Enrollments for the (demo) logged-in user and everyone else
ENROLLMENTS = [
    Enrollment(id=1, course=SECTIONS[1], student="You"),
    Enrollment(id=2, course=SECTIONS[15], student="You")
]
_next_enrollment_id = 3
