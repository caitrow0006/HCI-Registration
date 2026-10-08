
SECTIONS = [
    {"id": 1, "code": "CS 212-01", "title": "Data Structures & Algorithms", "instructor": "Prof. Cash", "meets": "MWF 9:00-9:50", "capacity": 30},
    {"id": 2, "code": "CS 212-02", "title": "Data Structures & Algorithms", "instructor": "Prof. Cash", "meets": "MWF 11:00-11:50", "capacity": 30},
    {"id": 3, "code": "CS 301-01", "title": "Algorithms", "instructor": "Prof. Prine", "meets": "TTh 10:00-11:15", "capacity": 25},
    {"id": 4, "code": "CS 340-01", "title": "Human-Computer Interaction", "instructor": "Prof. Parton", "meets": "TTh 1:00-2:15", "capacity": 24},
    {"id": 5, "code": "ENGL 150-03", "title": "Technical Writing", "instructor": "Prof. Presley", "meets": "MWF 10:00-10:50", "capacity": 20},
    {"id": 6, "code": "STAT 210-01", "title": "Probability & Statistics", "instructor": "Prof. Twain", "meets": "MWF 1:00-1:50", "capacity": 35},
]

# Enrollments for the (demo) logged-in user and everyone else
ENROLLMENTS = [
    {"id": 1, "section_id": 1, "student": "you"},
    {"id": 2, "section_id": 1, "student": "Kacey Musgrave"},
    {"id": 3, "section_id": 1, "student": "Noah Kahan"},
]
_next_enrollment_id = 4