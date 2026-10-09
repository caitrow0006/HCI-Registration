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

    drawer = ui.left_drawer().props("width=110")
    drawer.style('background-color: #003591')

    #sidebar with leftdrawer
    with drawer:
        ui.image('images/unhlogo.png').classes('w-20')

        #way to be able to click on images
        #TODO: in future need to change this for all images and make them display a different page
        #for each respective image
        ui.interactive_image('images/tempPencil.png') \
            .on('click', lambda e: ui.notify('You clicked an Image!', timeout = 2000)).classes('w-15 cursor-pointer')
        ui.label('Register')

        ui.image('images/tempLight.png').classes('w-15')
        ui.label('Plan')

        ui.image('images/tempCal.webp').classes('w-15')
        ui.label('Schedule')

        ui.image('images/tempQuest.png').classes('w-15')
        ui.label('FAQ')

    #The main register page
    ui.label("Register!").style('font-size: 45px; font-weight: bold;')

    with ui.row().style('gap: 450px'):

        with ui.card():
            with ui.column().style('gap: 30px'):
                ui.label("Search on Course Title").style('font-size: 25px; font-weight: bold; font-family: Comic Sans MS')
                ui.input(placeholder="Ex: Math 425").classes('border-2 border-blue-500 rounded-md px-2 width-50')

                ui.label("Search on CRN").style('font-size: 25px; font-weight: bold; font-family: Comic Sans MS')
                ui.input(placeholder="Ex: 7324246").classes('border-2 border-blue-500 rounded-md px-2 width-50')

                ui.label("Search From Wishlist").style('font-size: 25px; font-weight: bold; font-family: Comic Sans MS')
                with ui.dropdown_button('Select Wishlist', auto_close=True):
                    ui.item('Wishlist 1', on_click=lambda: ui.notify('You clicked item 1'))
                    ui.item('Wishlist 2', on_click=lambda: ui.notify('You clicked item 2'))
                    ui.item('Wishlist 3', on_click=lambda: ui.notify('You clicked item 2'))
        
        with ui.column().style('gap: 300px'):
            with ui.column():
                ui.label("Results:").style('font-size: 25px; font-weight: bold; font-family: Comic Sans MS')
                ui.button("Register")
            
            ui.label("Registered For:").style('font-size: 25px; font-weight: bold; font-family: Comic Sans MS')
                

    #Button to search
    ui.button("Search", on_click=lambda: ui.notify('You have Searched'))
    #render_content()

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