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
import re
from nicegui import ui

API_BASE = "http://localhost:8005"
search_results = []

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
      
def search_on_crn(sections:dict, filtered:dict, crn:int):
    #ui.notify("searching on crn")
    if (crn.isnumeric() == False) or (len(crn) != 5):
        #TODO: INFORM USER OF ERROR
        ui.notify("ERROR: Invalid CRN entered. Must be a 5 digit number.")
    else:
        for section in sections:
            if (section["crn"] != int(crn)):
                if section in filtered:
                    filtered.remove(section)
    #ui.notify(filtered);
    
def search_on_name(sections:dict, filtered:dict, course_title:str):
    #ui.notify("searching on title")
    """
    from Regex 101:
    1st Alternative
    [\s\W_]+
        + --> matches at least one character from the set below:
        \s --> any whitespace character
        \W --> any non-word character (punctuation)
        _ --> the literal _ (9510 / 1378 / 5F16)
    2nd Alternative
    (?<=[a-zA-Z])(?=\d)
        Positive Lookbehind --> (?<=)
            [a-zA-Z] --> a-z and A-Z
        Positive Lookahead --> (?=)
            \d --> is digit (number)
    3rd Alternative
    (?<=\d)(?=[a-zA-Z])
        Positive Lookbehind --> (?<=)
            \d --> is digit (number)
        Positive Lookahead --> (?=)
            [a-zA-Z] --> a-z and A-Z
    """
    #split input --> be liberal in what you accept
    search_split = re.split(r'[\s\W_]+|(?<=[a-zA-Z])(?=\d)|(?<=\d)(?=[a-zA-Z])', course_title) #splits on space or period
    #ui.notify(search_split) #debugging
    
    #filter courses
    for section in sections:
        #ui.notify(section)
        for token in search_split:
            if (token.isnumeric() == False):
                #ui.notify("token not numeric: " + token)
                if (section["department"] != token.upper()): #TODO: convert to upper for flexibility!
                    if section in filtered:
                        filtered.remove(section)
                    
            elif len(token) == 3: #course numbers are always 3 digits
                #ui.notify("course num token: " + token + str(section["course_num"]))
                if (str(section["course_num"]) != token):
                    if section in filtered:
                        filtered.remove(section)
                    
            elif len(token) < 3: #section numbers are always 2 or less digits
                if (section["section_num"] != int(token)):
                    if section in filtered:
                        filtered.remove(section)
                    
            else:
                #invalid token, skip
                #ui.notify("invalid token: " + token)
                continue;
                    
    #ui.notify(filtered)
    
#TODO: get rid of ui.notify debugging calls
def get_sections(course_title: str, crn: str):
    sections = api_get("/sections");
    search_results.clear()
    filtered = sections.copy()
    filter_issue = "No such courses exist. Please search for a different course."
    #ui.notify(sections)
    #ui.notify(course_title)
    #ui.notify(crn)
    
    #nothing was entered
    if crn == "" and course_title == "":
        #TODO: handle error better
        ui.notify("ERROR: Nothing was entered into search. Enter a course name (ex. Math425.01) or a 5 digit crn (ex. 12345)")
        return
    #no crn was entered
    elif crn == "":
        search_on_name(sections, filtered, course_title)
          
    #no course title was entered
    elif course_title == "":
        search_on_crn(sections, filtered, crn)
        
    else: #both fields, default is to search on CRN
        #search first on CRN
        search_on_crn(sections, filtered, crn)
        #if that search yeilded nothing, search on name
        if len(filtered) == 0:
            filtered = sections.copy()
            search_on_name(sections, filtered, course_title)
            
    if len(filtered) == 0:
        #TODO: handle error better?
        ui.notify(filter_issue)
     
    for result in filtered:
        search_results.append(result)
    
    render_search_results.refresh()
        
@ui.refreshable
def render_search_results():
    course = []
    title = ""
    department = ""
    course_num = ""
    section_num = ""
#    ui.notify("search result: " )
#    ui.notify(search_results )
    for result in search_results:
        title = result['title']
        department = result['department']
        course_num = str(result['course_num'])
        section_num = str(result['section_num'])
        instructor = str(result['instructor'])
        #TODO:Add selectable radio buttons
        #ui.notify(f"{department}{course_num} {title} Section: {section_num} Taught by: {instructor}")
        ui.label(f"{department}{course_num} {title} Section: {section_num} Taught by: {instructor}")


def register_section(section_id: int):
    if api_post("/register", {"section_id": section_id}):
        ui.notify("Registered", type="positive")
        render_content.refresh()

def drop_section(section_id: int):
    if api_post("/drop", {"section_id": section_id}):
        ui.notify("Dropped", type="warning")
        render_content.refresh()

def render_sidebar():
    drawer = ui.left_drawer().props("width=110")
    drawer.style('background-color: #003591')

    #sidebar with leftdrawer
    with drawer.classes("w-1/10 items-center"):
        ui.image('images/unh_logo.png').classes('w-20')

        #way to be able to click on images
        #TODO: in future need to change this for all images and make them display a different page
        #for each respective image
        ui.interactive_image('images/pencil.png') \
            .on('click', lambda e: ui.notify('You clicked an Image!', timeout = 2000)).classes('w-full cursor-pointer')
        ui.label('Register').classes('text-white').style("font-weight: bold;")

        ui.image('images/light.png').classes('w-full')
        ui.label('Plan').classes('text-white').style("font-weight: bold;")

        ui.image('images/calendar.png').classes('w-full')
        ui.label('Schedule').classes('text-white').style("font-weight: bold;")

        ui.image('images/question.png').classes('w-full')
        ui.label('FAQ').classes('text-white').style("font-weight: bold;")    

def render_register_page():
    #The main register page
    with ui.row().classes('w-full bg-blue-100 p-4'):
        ui.label("Register").style('font-size: 45px; font-weight: bold; font-family: Arial')

    with ui.row().classes('w-screen h-screen p-4'):    
        # Column 1
        with ui.column().classes("w-4/10 h-full bg-blue-100 p-4"):
            ui.label("Search on Course Title").style('font-size: 25px; font-weight: bold; font-family: Arial')
            course_name_input = ui.input(placeholder="Ex: Math 425").classes('bg-white border-2 border-blue-500 rounded-md px-2 width-50')

            ui.label("Search on CRN").style('font-size: 25px; font-weight: bold; font-family: Arial')
            crn_input = ui.input(placeholder="Ex: 73242").classes('bg-white border-2 border-blue-500 rounded-md px-2 width-50')

            ui.label("Search From Wishlist").style('font-size: 25px; font-weight: bold; font-family: Arial')
            with ui.dropdown_button('Select Wishlist', auto_close=True):
                ui.item('Wishlist 1', on_click=lambda: ui.notify('You clicked item 1'))
                ui.item('Wishlist 2', on_click=lambda: ui.notify('You clicked item 2'))
                ui.item('Wishlist 3', on_click=lambda: ui.notify('You clicked item 2'))            
            
            #Button to search
            search_sections_btn = ui.button("Search", on_click=lambda: (get_sections(course_name_input.value, crn_input.value))).classes('w-25 h-12 ml-auto mt-40')
            #render_content()
                
        
        with ui.column().classes("w-5/10 h-full bg-blue-100 p-4"):
            with ui.card().classes('w-full h-2/5'):
                ui.label("Results:").style('font-size: 25px; font-weight: bold; font-family: Arial')
                render_search_results()
                ui.button("Register")

            with ui.card().classes('w-full h-1/2'):
                ui.label("Registered For:").classes("mt-6").style('font-size: 25px; font-weight: bold; font-family: Arial')
@ui.page("/")
def main_page():
    render_sidebar()
    render_register_page()
    
             

# @ui.refreshable
# def render_content():
#     ui.label("Course Registration").classes("text-2xl")

#     with ui.row().classes("w-full no-wrap"):
#         with ui.column().classes("w-1/2 p-2"):
#             render_sections()
#         with ui.column().classes("w-1/2 p-2"):
#             render_my_schedule()
#             render_announcements()

# def render_sections():
#     ui.label("Available Sections").classes("text-lg")
#     sections = api_get("/sections")
#     for s in sections:
#         with ui.row().classes("items-center"):
#             label = (
#                 f'{s["code"]} - {s["title"]} - {s["instructor"]} - {s["meets"]} '
#                 f'- {s["seats_open"]}/{s["capacity"]} seats open'
#             )
#             ui.label(label)
#             if s["you_enrolled"]:
#                 ui.button("Drop", on_click=lambda sid=s["id"]: drop_section(sid))
#             else:
#                 ui.button("Register", on_click=lambda sid=s["id"]: register_section(sid))

# def render_my_schedule():
#     ui.label("My Schedule").classes("text-lg")
#     schedule = api_get("/my-schedule")
#     if not schedule:
#         ui.label("You aren't registered for anything yet.")
#         return
#     for s in schedule:
#         ui.label(f'{s["code"]} - {s["title"]} - {s["meets"]}')

# def render_announcements():
#     ui.label("Announcements").classes("text-lg")
#     announcements = api_get("/announcements")
#     for a in announcements:
#         ui.label(a["title"])
#         ui.label(a["body"])
#         ui.separator()

ui.run(port=8084, title="Course Registration")
