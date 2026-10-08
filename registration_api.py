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
    POST /register   body: {"section_id": int}
    POST /drop       body: {"section_id": int}
    GET  /announcements
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Mock Course Registration API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------
# In-memory "database"
# ---------------------------------------------------------------------

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

# ---------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------

class RegisterRequest(BaseModel):
    section_id: int

class DropRequest(BaseModel):
    section_id: int

def _get_section_or_404(section_id: int) -> dict:
    for s in SECTIONS:
        if s["id"] == section_id:
            return s
    raise HTTPException(status_code=404, detail="Section not found")

def _enrolled_count(section_id: int) -> int:
    return sum(1 for e in ENROLLMENTS if e["section_id"] == section_id)

def _is_enrolled(section_id: int, student: str = "you") -> bool:
    return any(e["section_id"] == section_id and e["student"] == student for e in ENROLLMENTS)

def _summarize_section(s: dict) -> dict:
    enrolled = _enrolled_count(s["id"])
    summary = dict(s)
    summary["enrolled"] = enrolled
    summary["seats_open"] = s["capacity"] - enrolled
    summary["you_enrolled"] = _is_enrolled(s["id"])
    return summary

@app.get("/sections")
def list_sections():
    return [_summarize_section(s) for s in SECTIONS]

@app.get("/sections/{section_id}")
def get_section(section_id: int):
    return _summarize_section(_get_section_or_404(section_id))

//will need to modify later
@app.get("/my-schedule")
def get_my_schedule():
    mine = [e for e in ENROLLMENTS if e["student"] == "you"]
    enriched = []
    for e in mine:
        section = _get_section_or_404(e["section_id"])
        enriched.append({**e, **_summarize_section(section)})
    return enriched

@app.post("/register")
def register(req: RegisterRequest):
    global _next_enrollment_id
    section = _get_section_or_404(req.section_id)
    if _is_enrolled(section["id"]):
        raise HTTPException(status_code=400, detail="Already registered for this section")
    if _enrolled_count(section["id"]) >= section["capacity"]:
        raise HTTPException(status_code=400, detail=f'{section["code"]} is full')

    new_enrollment = {"id": _next_enrollment_id, "section_id": section["id"], "student": "you"}
    ENROLLMENTS.append(new_enrollment)
    _next_enrollment_id += 1
    return new_enrollment

@app.post("/drop")
def drop(req: DropRequest):
    for i, e in enumerate(ENROLLMENTS):
        if e["section_id"] == req.section_id and e["student"] == "you":
            ENROLLMENTS.pop(i)
            return {"dropped": req.section_id}
    raise HTTPException(status_code=404, detail="You are not registered for this section")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8005)
