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

from fastapi import Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import SECTIONS, ENROLLMENTS, WISHLIST, Course, Enrollment, Wishlist_item
from typing import List

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

def _time_conflict_detector(sched1: Course, sched2: Course) -> bool:
    if sched1.schedule.days == "TBA" or sched2.schedule.days == "TBA" or sched1.schedule.start_hour == 0 or sched2.schedule.start_hour == 0:
        return False
    
    # check if the two schedules have any overlapping days
    has_day_overlap = any(day in sched2.schedule.days for day in sched1.schedule.days)
    if not has_day_overlap:
        return False

    # check if the two schedules have overlapping times
    return (sched1.schedule.start_hour < sched2.schedule.end_hour) and (sched2.schedule.start_hour < sched1.schedule.end_hour)
# Endpoints

@app.get("/sections")
def list_sections():
    return [_summarize_section(s) for s in SECTIONS]

# @app.get("/sections/{section_id}")
# def get_section(section_id: int):
#     return _summarize_section(_get_section_or_404(section_id))

# get wishlist
@app.get("/wishlists")
def wishlists():
    return [
        {
            "wishlist_id": w.id,
            "wishlist_name": w.wishlist,
        }
        for w in WISHLIST
    ]

# get specific wishlist by id, return list of courses in that wishlist
@app.get("/wishlist/{wishlist_id}")
def get_wishlist(wishlist_id: int):
    wishlist = []
    for w in WISHLIST:
        if w.id == wishlist_id:
            for section in w.course:
                wishlist.append(section)
            break
    return [_summarize_section(s) for s in wishlist]

# my-schdule == enrollments
@app.get("/enrollments")
def get_my_schedule():
    return [
        {
            "enrollment_id": e.id,
            "student": e.student,
            "course": _summarize_section(e.course),
        }
        for e in ENROLLMENTS if e.student.lower() == "you"
    ]

@app.post("/register")
def register(section_id: list[int] = Body(...)):
    section_to_register = []
    for sid in section_id:
        section = _get_section_or_404(sid)
        if _is_enrolled(section.id):
            raise HTTPException(status_code=400, detail="Already registered for this section")
        if _enrolled_count(section.id) >= section.capacity:
            raise HTTPException(
                status_code=400, 
                detail=f'{section.department} ({section.course_num}, {section.section_num}) is full'
            )
        for e in ENROLLMENTS:
            if _time_conflict_detector(section, e.course) and e.student.lower() == "you":
                raise HTTPException(
                    status_code=400,
                    detail=f'{section.title} ({section.department} {section.course_num}, {section.section_num}) Time conflict with {e.course.title} ({e.course.department} {e.course.course_num}, {e.course.section_num})'
                )

        for prev_section in section_to_register:
            if _time_conflict_detector(section, prev_section):
                raise HTTPException(
                    status_code=400,
                    detail=f'{section.title} ({section.department} {section.course_num}, {section.section_num}) Time conflict with {prev_section.title} ({prev_section.department} {prev_section.course_num}, {prev_section.section_num})'
                )
        section_to_register.append(section)
    new_enrollments = []
    for section in section_to_register:
        new_enrollment = Enrollment(id=len(ENROLLMENTS) + 1, course=section, student="You")
        ENROLLMENTS.append(new_enrollment)
        new_enrollments.append(new_enrollment)

    _reindex_enrollments()
    return new_enrollments

@app.delete("/drop")
def drop(section_id: list[int] = Body(...)):
    dropped_sections = []
    for sid in section_id:
        for i, e in enumerate(ENROLLMENTS):
            if e.course.id == sid and e.student.lower() == "you":
                ENROLLMENTS.pop(i)
                dropped_sections.append(sid)
                break
    _reindex_enrollments()
    return {"dropped": dropped_sections}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8005)
