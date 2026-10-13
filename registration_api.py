"""
registration_api.py

A mock backend for a course registration portal: browse course
sections with live seat counts, register/drop, see your current
schedule, and read registration-related announcements.

Run with:
    pip install fastapi uvicorn
    python registration_api.py

Then API will be available at http://localhost:8005

Endpoints:
    GET  /sections
    GET  /sections/{section_id}
    GET  /my-schedule
    GET  /wishlist/{wishlist_id}
    POST /register   body: {"section_id": int}
    POST /drop       body: {"section_id": int}
    GET  /announcements
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import SECTIONS, ENROLLMENTS, Course, Enrollment

app = FastAPI(title="Mock Course Registration API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------

def _get_section_or_404(section_id: int) -> dict:
    for s in SECTIONS:
        if s.id == section_id:
            return s
    raise HTTPException(status_code=404, detail="Section not found")

def _enrolled_count(section_id: int) -> int:
    return sum(1 for e in ENROLLMENTS if e.course.id == section_id)

def _is_enrolled(section_id: int, student: str = "you") -> bool:
    return any(e.course.id == section_id and e.student.lower() == student.lower() for e in ENROLLMENTS)

def _summarize_section(s: Course) -> dict:
    enrolled = _enrolled_count(s.id)
    summary = s.model_dump()
    summary["enrolled"] = enrolled
    summary["seats_open"] = s.capacity - enrolled
    summary["you_enrolled"] = _is_enrolled(s.id)
    return summary

def _reindex_enrollments():
    for idx, e in enumerate(ENROLLMENTS, start=1):
        e.id = idx

# Endpoints

@app.get("/sections")
def list_sections():
    return [_summarize_section(s) for s in SECTIONS]

# @app.get("/sections/{section_id}")
# def get_section(section_id: int):
#     return _summarize_section(_get_section_or_404(section_id))

# need to modify later
# @app.get("/wishlist/{wishlist_id}")
# def get_wishlist(wishlist_id: int):
#     wishlist = []
#     for w in WISHLIST:
#         if w.id == wishlist_id:
#             for section_id in w.course.id:
#                 section = _get_section_or_404(section_id)
#                 wishlist.append(section)
#     return [_summarize_section(s) for s in wishlist]

# my-schdule == enrollments
@app.get("/enrollments")
def get_my_schedule():
    return [
        {
            "enrollment_id": e.id,
            "student": e.student,
            "course": _summarize_section(_get_section_or_404(e.course.id)),
        }
        for e in ENROLLMENTS if e.student.lower() == "you"
    ]

@app.post("/register/{section_id}")
def register(section_id: int):
    section = _get_section_or_404(section_id)
    if _is_enrolled(section.id):
        raise HTTPException(status_code=400, detail="Already registered for this section")
    if _enrolled_count(section.id) >= section.capacity:
        raise HTTPException(status_code=400, detail=f'{section.department} ({section.course_num}, {section.section_num}) is full')

    new_enrollment = Enrollment(id=len(ENROLLMENTS) + 1, course=section, student="You")
    ENROLLMENTS.append(new_enrollment)
    _reindex_enrollments()
    return new_enrollment

@app.delete("/drop/{section_id}")
def drop(section_id: int):
    for i, e in enumerate(ENROLLMENTS):
        if e.course.id == section_id and e.student.lower() == "you":
            ENROLLMENTS.pop(i)
            _reindex_enrollments()
            return {"dropped": section_id}
    raise HTTPException(status_code=404, detail="You are not registered for this section")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8005)
