"""
registration_starter.py

A simple NiceGUI frontend that pulls data from registration_api.py 
and renders a basic course registration portal: browse sections, 
register/drop, see your schedule, and read announcements.

Run with:
    pip install nicegui requests
    python registration_api.py    # in one terminal
    python registration_ui.py          # in another terminal

Then http://localhost:8084 will automatically open.
"""

import requests
from nicegui import ui

API_BASE = "http://localhost:8005"

def api_get(path: str):
    try:
        resp = requests.get(f"{API_BASE}{path}", timeout=5)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        ui.notify(f"Could not reach API: {e}", type="negative")
        return []

def api_post(path: str, json: dict):
    try:
        resp = requests.post(f"{API_BASE}{path}", json=json, timeout=5)
        resp.raise_for_status()
        return True
    except requests.RequestException as e:
        detail = ""
        try:
            detail = e.response.json().get("detail", "")
        except Exception:
            pass
        ui.notify(detail or f"Request failed: {e}", type="negative")
        return False

def register_section(section_id: int):
    if api_post("/register", {"section_id": section_id}):
        ui.notify("Registered", type="positive")
        render_content.refresh()

def drop_section(section_id: int):
    if api_post("/drop", {"section_id": section_id}):
        ui.notify("Dropped", type="warning")
        render_content.refresh()

@ui.page("/")
def main_page():
    render_content()

@ui.refreshable
def render_content():
    ui.label("Course Registration").classes("text-2xl")

    with ui.row().classes("w-full no-wrap"):
        with ui.column().classes("w-1/2 p-2"):
            render_sections()
        with ui.column().classes("w-1/2 p-2"):
            render_my_schedule()
            render_announcements()

def render_sections():
    ui.label("Available Sections").classes("text-lg")
    sections = api_get("/sections")
    for s in sections:
        with ui.row().classes("items-center"):
            label = (
                f'{s["code"]} - {s["title"]} - {s["instructor"]} - {s["meets"]} '
                f'- {s["seats_open"]}/{s["capacity"]} seats open'
            )
            ui.label(label)
            if s["you_enrolled"]:
                ui.button("Drop", on_click=lambda sid=s["id"]: drop_section(sid))
            else:
                ui.button("Register", on_click=lambda sid=s["id"]: register_section(sid))

def render_my_schedule():
    ui.label("My Schedule").classes("text-lg")
    schedule = api_get("/my-schedule")
    if not schedule:
        ui.label("You aren't registered for anything yet.")
        return
    for s in schedule:
        ui.label(f'{s["code"]} - {s["title"]} - {s["meets"]}')

def render_announcements():
    ui.label("Announcements").classes("text-lg")
    announcements = api_get("/announcements")
    for a in announcements:
        ui.label(a["title"])
        ui.label(a["body"])
        ui.separator()

ui.run(port=8084, title="Course Registration")