// The Cookie Machine (TCM for short)

// Draggable window: https://www.w3schools.com/howto/howto_js_draggable.asp
// Make the DIV element draggable:
dragElement(document.getElementById("tcm_window"));

function dragElement(elmnt) {
  var pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
  // Reset right property to allow window moving NOT WORKING
  elmnt.style.removeProperty('right')
  elmnt.style.removeProperty('margin-top')
  if (elmnt == null) {
    console.log('elmnt is null');
    return
  }

  if (document.getElementById(elmnt.id + "header")) {
    // if present, the header is where you move the DIV from:
    document.getElementById(elmnt.id + "header").onmousedown = dragMouseDown;
  } else {
    // otherwise, move the DIV from anywhere inside the DIV:
    elmnt.onmousedown = dragMouseDown;
  }

  function dragMouseDown(e) {
    e = e || window.event;
    e.preventDefault();
    // get the mouse cursor position at startup:
    pos3 = e.clientX;
    pos4 = e.clientY;
    document.onmouseup = closeDragElement;
    // call a function whenever the cursor moves:
    document.onmousemove = elementDrag;
  }

  function elementDrag(e) {
    e = e || window.event;
    e.preventDefault();
    // calculate the new cursor position:
    pos1 = pos3 - e.clientX;
    pos2 = pos4 - e.clientY;
    pos3 = e.clientX;
    pos4 = e.clientY;
    // set the element's new position:
    elmnt.style.top = (elmnt.offsetTop - pos2) + "px";
    elmnt.style.left = (elmnt.offsetLeft - pos1) + "px";
  }

  function closeDragElement() {
    // stop moving when mouse button is released:
    document.onmouseup = null;
    document.onmousemove = null;
  }
}

document.querySelector('#tcm_button').addEventListener('click', () => {
  // Hide tcm_window
  document.querySelector('#tcm_window').style.display = "block";
  // Make tcm_button invisible
  document.querySelector('#tcm_button').style.cssText = `
    color: #FFFFFF00;
    border: none;`;
});

document.querySelector('#tcm_window_close').addEventListener('click', () => {
  // Hide tcm_window
  document.querySelector('#tcm_window').style.display = "none";
  // Make tcm_button visible
  document.querySelector('#tcm_button').style.cssText = `
    color: #FFFFFF;
    border: 2px solid white;`;
});

var website_tree = []

document.querySelector('#tcm_display_cloud').addEventListener('click', () => {
    // TODO: rename search_url.json to search_urls.json
    // load_website_tree();
    getJSON('https://raw.githubusercontent.com/pippim/pippim.github.io/main/assets/json/website_tree.json')
      .then(console.log('load_website_tree: ' + website_tree);
});

async function load_website_tree() {
    website_tree = await this.getJSON('https://raw.githubusercontent.com/pippim/pippim.github.io/main/assets/json/website_tree.json');
}

/* End of /assets/js/theCookieMachine.js */
