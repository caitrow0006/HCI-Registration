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
query = None
options = []
selected = []
enrollments = []
wishlists = []
register_button = None

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
        
def api_delete(path:str , json: dict):
    try:
        resp = requests.delete(f"{API_BASE}{path}", json=json, timeout=5)
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
    global search_results
    global query
    query = (course_title, crn)
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
        search_results = sections.copy()
        ui.notify("ERROR: Nothing was entered into search. Enter a course name (ex. Math425.01) or a 5 digit crn (ex. 12345)")
        #return
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
    
def toggle_register_button(e=None):
    #https://nicegui.io/documentation/generic_events

    global selected
    selected = [item for item in options if item[1].value] #selected is checked items only
    #ui.notify(selected)
    num_checked = len(selected)
    num_enrolled = 0;
    for item in selected:
        if item[0]["you_enrolled"]:
            num_enrolled = num_enrolled + 1
    #ui.notify(num_checked)
    #ui.notify(num_enrolled)

    #nothing selected or number enrooled selection is less than num total selections
    if num_checked == 0 or 0 < num_enrolled < num_checked:
        register_button.disable()
        #https://nicegui.io/documentation/button
        register_button.props("color=grey")
        register_button.set_text(f"Register ({num_checked} selected)")
        
    #all selected are ones you arent enrolled in
    elif num_enrolled == 0:
        ui.notify("all selection are not enrolled in")
        register_button.enable()
        register_button.props("color=blue")
        register_button.set_text(f"Register ({num_checked} selected)")
     
    #all selected one we are enrolled in
    else:
        register_button.enable()
        register_button.props("color=red")
        register_button.set_text(f"Drop ({num_checked} selected)")
    
    #ui.notify(selected)

def get_wishlists():
    global wishlists
    wishlists = api_get("/wishlists")

def get_wishlist_courses(wishlist_id:int):
    global search_results
    search_results.clear()
    wishlist_courses = api_get(f"/wishlist/{wishlist_id}")
    for result in wishlist_courses:
        search_results.append(result)
    render_search_results.refresh()
        
@ui.refreshable
def render_search_results():
    options.clear()
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
        with ui.row().classes("w-full items-center no-wrap bg-gray-100 rounded") as row:
            #checkbox = ui.checkbox()
            checkbox = ui.checkbox(on_change=toggle_register_button)
            label = ui.label(
                f"{department}{course_num} {title} Section: {section_num} Taught by: {instructor}"
            ).classes("flex-grow") #fill available space
        options.append((result, checkbox, label))
        
    #check since i declared it as none uptop
    if register_button is not None:
        toggle_register_button()

def add_drop_selections():
    for item in selected:
        is_add = False
        is_drop = False
        #should all be either add or drop, but it's good to check anyways
        if item[0]["you_enrolled"]:
            is_drop = True
        else:
            is_add = True
            
    #ui.notify(selected)
    if is_add and is_drop:
        #TODO: Handle error better..?
        ui.notify("Error: Selected courses contain a mix of registered and unregistered courses.")
    elif is_add:
        register_selected()
    elif is_drop:
        drop_selected()
    else:
        ui.notify("Error: Nothing selected")
        
    #TODO: Not sure of this is right
    get_sections(query[0], query[1])
    get_enrollments()
        
def register_selected():
    #ui.notify(selected)
    ids = [int(item[0]["id"]) for item in selected]
    if not ids:
        ui.notify("No courses selected for registration.", type="warning")
        return
    response = api_post("/register", ids)
    if response:
        ui.notify("Registered", type="positive")
            #render_enrollments.refresh()
            #render_search_results.refresh()
    #TODO: Not sure of this is right
    get_enrollments()

def drop_selected():
    ids = [int(item[0]["id"]) for item in selected]
    if not ids:
        ui.notify("No courses selected for dropping.", type="warning")
        return
    #ui.notify(selected)
    response = api_delete("/drop", ids)

    if response:
        ui.notify("Dropped", type="positive")
            #render_enrollments.refresh()
            #render_search_results.refresh()
        get_enrollments()

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

def get_enrollments():
    global enrollments
    enrollments = api_get("/enrollments")
    render_enrollments.refresh()
        
@ui.refreshable
def render_enrollments():
    course = []
    title = ""
    department = ""
    course_num = ""
    section_num = ""
    for enrollment in enrollments:
        course = enrollment['course']
        title = course['title']
        department = course['department']
        course_num = str(course['course_num'])
        section_num = str(course['section_num'])
        instructor = str(course['instructor'])
        ui.label(f"{department}{course_num} {title} Section: {section_num} Taught by: {instructor}")

def render_register_page():
    #to overshadow the one uptop
    global register_button
    
    #The main register page
    with ui.row().classes('w-full pl-4'):
        with ui.row().classes('w-full bg-blue-100 p-4'):
            ui.label("Register").style('font-size: 45px; font-weight: bold; font-family: Arial')

    with ui.row().classes('w-screen h-screen p-4'):    
        # Column 1
        with ui.column().classes("w-4/10 h-[600px] bg-blue-100 p-4"):
            ui.label("Search on Course Title").style('font-size: 25px; font-weight: bold; font-family: Arial')
            course_name_input = ui.input(placeholder="Ex: Math 425").classes('bg-white border-2 border-blue-500 rounded-md px-2 width-50')

            ui.label("Search on CRN").style('font-size: 25px; font-weight: bold; font-family: Arial')
            crn_input = ui.input(placeholder="Ex: 73242").classes('bg-white border-2 border-blue-500 rounded-md px-2 width-50')

            ui.label("Search From Wishlist").style('font-size: 25px; font-weight: bold; font-family: Arial')
            with ui.dropdown_button('Select Wishlist', auto_close=True):
                wishlists = api_get("/wishlists")
                if not wishlists:
                    ui.item('No Wishlists Available')
                else:
                    for w in wishlists:
                        w_id = w.get("wishlist_id")
                        w_name = w.get("wishlist_name", f"Wishlist {w_id}")
                        ui.item(
                            w_name, 
                            on_click=lambda wid=w_id, wname=w_name: get_wishlist_courses(wid)
                        )
            
            #Button to search
            search_sections_btn = ui.button("Search", on_click=lambda: (get_sections(course_name_input.value, crn_input.value))).classes('w-25 h-12 ml-auto mt-40')
            #render_content()
                
        
        with ui.column().classes("w-5/10 h-[600px] bg-blue-100 p-4"):
            with ui.card().classes('w-full h-3/5'):
                ui.label("Results:").style('font-size: 25px; font-weight: bold; font-family: Arial')
                with ui.scroll_area():
                    render_search_results()
                register_button = ui.button("Register", on_click=lambda: ( (get_enrollments(), add_drop_selections())
                ))
                toggle_register_button()

            with ui.card().classes('w-full h-1/2'):
                ui.label("Registered For:").classes("mt-6").style('font-size: 25px; font-weight: bold; font-family: Arial')
                render_enrollments()
@ui.page("/")
def main_page():
    render_sidebar()
    render_register_page()
    ui.query('body').style('margin: 0; overflow: hidden;')
    
             

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
