const API_BASE = "http://localhost:8005";
let selectedWishlistCourses = [];
let currentCourses = [];

async function apiGet(path) {
  try {
    const resp = await fetch(API_BASE + path);
    if (!resp.ok) throw new Error(resp.status + " " + resp.statusText);
    return await resp.json();
  } catch (e) {
    showError("Could not reach API: " + e.message);
    return [];
  }
}


async function apiPost(path, body) {
  try {
    const resp = await fetch(API_BASE + path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!resp.ok) {
      let detail = "";
      try { detail = (await resp.json()).detail; } catch (_) {}
      showError(detail || "Request failed: " + resp.status);
      return false;
    }
    clearError();
    return true;
  } catch (e) {
    showError("Could not reach API: " + e.message);
    return false;
  }
}

//Create event listeners for search button
const searchBtn = document.getElementById("search-button");
searchBtn.addEventListener("click", searchBtnOnClick)
//searchBtn.addEventListener("hover", searchBtnOnHover)

//Search button onclick
async function searchBtnOnClick(){
  //debug
  console.log("Search button was clicked")


  const titleInput = document.getElementById("title-search-input").value.trim().toLowerCase();
  const crnInput = document.getElementById("crn-search-input").value.trim();

  const filteredCourses = currentCourses.filter((course) => {
    const matchesTitle = 
      !titleInput || 
      course.title.toLowerCase().includes(titleInput) ||
      course.department.toLowerCase().includes(titleInput);
    
    const matchesCRN = 
      !crnInput ||
      String(course.crn).includes(crnInput);

    return matchesTitle && matchesCRN;
  });

  renderSearchResults(filteredCourses);
  // //container to fill with list of elements
  // const container = document.getElementById("resultsFromSearch");
  // //api call to get sections currently available
  // const sections = await apiGet("/sections");

  // //idk what this does its in the starter code tho
  // container.replaceChildren();

  // //for each section in the list of dictionaries we create a div and a span element
  
  // for (const s of sections) {
  //   const row = el("div");
  //   row.className = "row";
  //   //display each section based on there attributes
  //   row.appendChild(el("span",
  //     `${s.department} - ${s.title} - ${s.instructor} - ${s.meets} - ${s.seats_open}/${s.capacity} seats open`))
  //   if (s.you_enrolled) {
  //     const btn = el("button", "Drop");
  //     btn.onclick = () => dropSection(s.id);
  //     row.appendChild(btn);
  //   } else {
  //     const btn = el("button", "Register");
  //     btn.onclick = () => registerSection(s.id);
  //     row.appendChild(btn);
  //   }
  //   container.appendChild(row);

}




function showError(msg) { document.getElementById("error").textContent = msg; }
function clearError() { document.getElementById("error").textContent = ""; }

async function registerSection(sectionId) {
  //console.log(sectionId)
  if (await apiPost("/register", [Number(sectionId)])) {
    renderAll()
    searchBtnOnClick();
  }
}

async function dropSection(sectionId) {
  if (await apiPost("/drop", [Number(sectionId)])) {
    renderAll()
    searchBtnOnClick();
  }
}

function el(tag, text) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  return node;
}

// async function renderSections() {
//   const container = document.getElementById("sections");
//   const sections = await apiGet("/sections");
//   container.replaceChildren();

//   for (const s of sections) {
//     const row = el("div");
//     row.className = "row";
//     row.appendChild(el("span",
//       `${s.code} - ${s.title} - ${s.instructor} - ${s.meets} - ${s.seats_open}/${s.capacity} seats open`));

//     if (s.you_enrolled) {
//       const btn = el("button", "Drop");
//       btn.onclick = () => dropSection(s.id);
//       row.appendChild(btn);
//     } else {
//       const btn = el("button", "Register");
//       btn.onclick = () => registerSection(s.id);
//       row.appendChild(btn);
//     }
//     container.appendChild(row);
//   }
// }

async function renderCurEnrollments() {
  const container = document.getElementById("cur-enrolls");
  const enrolled = await apiGet("/enrollments");
  container.replaceChildren();

  if (!enrolled.length) {
    container.appendChild(el("div", "You aren't registered for anything yet."));
    return;
  }
  for (const s of enrolled) {
    const row = el("div")

    row.style.display = "flex";
    row.style.gap = "10px";

    row.appendChild(el("div", `${s.course.department} ${s.course.course_num}.${s.course.section_num} - ${s.course.title} - ${s.course.instructor} - ( ${s.course.schedule.days}, ${Math.floor(s.course.schedule.start_hour/100)}:${String(s.course.schedule.start_hour%100).padStart(2, '0')} - ${Math.floor(s.course.schedule.end_hour/100)}:${String(s.course.schedule.end_hour%100).padStart(2, '0')} - ${s.course.schedule.building}, ${s.course.schedule.room_num} ) - ${s.course.seats_open}/${s.course.capacity} seats open`));
    const theDropButton = el("button", "Drop")
  

    //Create event listeners for each drop buttons
    theDropButton.addEventListener("click", dropButtonsOnClick)

    //TODO: Need to hook this up with cats existing popup

    const dropDialog = document.getElementById("drop-dialog");
    const dropMessage = document.getElementById("drop-message");
    const cancelDrop = document.getElementById("cancel-drop");
    const confirmDrop = document.getElementById("confirm-drop");

    //handling when drop button is clicked
    async function dropButtonsOnClick(){
        //id to drop
        const dropped = [Number(s.course.id)]

        dropMessage.textContent = `Are you sure you want to drop ${s.course.title}?`

        //display the dialog
        dropDialog.showModal();

        //Confirmed drop
        confirmDrop.onclick = async () => {
          //call api to drop id
          success = await apiPost("/drop", [Number(s.course.id)]);
          
          //rerender current courses after drop
          renderAll();
          currentCourses = await apiGet("/sections");
          renderSearchResults();
          updateRegisterButtonState();

          dropDialog.close();


        }

        cancelDrop.onclick = async () => {
          dropDialog.close();
        }




    }

    row.appendChild(theDropButton)
    container.appendChild(row)
  }
}



async function getWishLists() {
  const wishlists = await apiGet("/wishlists");
  return wishlists
}

// get wish list from API and render it
async function loadWishLists() {
  const select = document.getElementById("wishlist-search-select");
  const wishlists = await getWishLists();

  select.innerHTML = '<option value="default">No Wishlist Selected</option>';
  
  for (const w of wishlists) {
    const opt = document.createElement("option");

    opt.value = w.wishlist_id;
    opt.textContent = w.wishlist_name || `Wishlist ${w.wishlist_id}`;

    select.appendChild(opt);
  }
  // console.log(wishlists)

  currentCourses = await apiGet("/sections");

  select.addEventListener("change", async (event) => {
    const wishlistID = event.target.value;

    if (wishlistID === "default") {
      currentCourses = await apiGet("/sections");
      return;
    } else {
      currentCourses = await apiGet(`/wishlist/${wishlistID}`);
    }

    console.log(currentCourses)

    renderSearchResults(currentCourses);
  });
}

function renderSearchResults(courses) {
  const container = document.getElementById("results-course-list");

  container.replaceChildren();

  if(!courses || courses.length === 0) {
    container.appendChild(el("p", "No courses found."));
    return;
  }

  courses.forEach((course, index) => {
    const row = el("div");
    row.className = "row";

    const checkbox = el("input");
    checkbox.type = "checkbox";
    checkbox.id = `result-${index}`;
    checkbox.dataset.id = course.id;
    checkbox.dataset.enrolled = course.you_enrolled;
    checkbox.addEventListener("change", updateRegisterButtonState);

    const label = el("label");
    label.htmlFor = `result-${index}`;
    label.textContent = `${course.department} ${course.course_num}.${course.section_num} - ${course.title} - Taught by: ${course.instructor} - ( ${course.schedule.days}, ${Math.floor(course.schedule.start_hour/100)}:${String(course.schedule.start_hour%100).padStart(2, '0')} - ${Math.floor(course.schedule.end_hour/100)}:${String(course.schedule.end_hour%100).padStart(2, '0')} - ${course.schedule.building}, ${course.schedule.room_num} ) - ${course.seats_open}/${course.capacity} seats open`;

    row.appendChild(checkbox);
    row.appendChild(label);
    container.appendChild(row);
  });
}

function updateRegisterButtonState() {
  const checkboxes = document.querySelectorAll("#results-course-list input[type='checkbox']");
  const selected = Array.from(checkboxes).filter(cb => cb.checked);
  const registerBtn = document.getElementById("register-button");

  if (!registerBtn) return;

  if (selected.length === 0) {
    registerBtn.textContent = "Register (0 selected)";
    registerBtn.disabled = false;
    registerBtn.style.backgroundColor = "";
    return;
  }

  const allEnrolled = selected.every(cb => cb.dataset.enrolled === "true");
  const noneEnorlled = selected.every(cb => cb.dataset.enrolled === "false");

  if (!allEnrolled && !noneEnorlled) {
    registerBtn.textContent = "Cannot mix Reg/Drop";
    registerBtn.disabled = true;
    registerBtn.style.backgroundColor = "grey";
  } else if (allEnrolled) {
    registerBtn.textContent = `Drop (${selected.length} selected)`;
    registerBtn.disabled = false;
    registerBtn.style.backgroundColor = "red";
    registerBtn.style.color = "white";
  } else {
    registerBtn.textContent = `Register (${selected.length} selected)`;
    registerBtn.disabled = false;
    registerBtn.style.backgroundColor = "green";
    registerBtn.style.color = "white";
  }
}

const mainRegisterBtn = document.getElementById("register-button");
if (mainRegisterBtn) {
  mainRegisterBtn.addEventListener("click", async() => {
    const checkboxes = document.querySelectorAll("#results-course-list input[type='checkbox']");
    const selected = Array.from(checkboxes).filter(cb => cb.checked);

    if (selected.length === 0) {
      showError("No courses selected.");
      return;
    }

    const ids = selected.map(cb => Number(cb.dataset.id));
    const allEnrolled = selected.every(cb => cb.dataset.enrolled === "true");

    let success = false;
    if (allEnrolled) {
      // Drop req
      success = await apiPost("/drop", ids);
    } else {
      // Reg req
      success = await apiPost("/register", ids);
    }

    if (success) {
      clearError();
      renderAll();
      currentCourses = await apiGet("/sections");
      renderSearchResults();
      updateRegisterButtonState();
    }
  })
}
// async function renderAnnouncements() {
//   const container = document.getElementById("announcements");
//   const announcements = await apiGet("/announcements");
//   container.replaceChildren();

//   for (const a of announcements) {
//     container.appendChild(el("div", a.title));
//     container.appendChild(el("div", a.body));
//     container.appendChild(document.createElement("hr"));
//   }
// }

function renderAll() {
 // renderSections();
  renderCurEnrollments();
  loadWishLists();
}

renderAll();
