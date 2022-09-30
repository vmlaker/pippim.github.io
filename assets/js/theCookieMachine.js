---
---
// The Cookie Machine (TCM for short)

// Note: Requires search.js to be loaded first for global variables

// Button Image source: https://www.cleanpng.com/free/

// imported functions.  Parent needs <script type="module"...
// See: /_layouts +> /default.html, / hrb.html, /program.html, etc.
import {processHyperlinkRecipe} from './hyperlinkRecipe.js';
//  Move below to tcm-common-code.js
// import { getCookie , setCookie } from './theCookieJar.js';

/* include tcm-common-code.js code shared by:
    /assets/js/theCookieMachine.js - Draggable Modal Dialog
    /tcm.md - The Cookie Machine documentation webpage

*/
{% include tcm-common-code.js %}
{% include draggable-window.js %}

// Webpage (hrb.md) may have <div id="hrb_body" defined. If so populate it
window.addEventListener('DOMContentLoaded', (event) => {
    // https://stackoverflow.com/a/42526074/6929343
    var myEle = document.getElementById("hrb_body");
    if(myEle != null){
        processHyperlinkRecipe('hrb_body');
    }
});

// Draggable window: https://www.w3schools.com/howto/howto_js_draggable.asp
// Make the DIV element draggable (_includes/draggable-window.js):
dragElement(document.getElementById("tcm_window"))

// Loop through all class named .tcm-button
var tcmButtonClassNdx; // Global variable
for (var ndx = 0; ndx < tcmButtonClasses.length; ndx++) {
    tcmButtonClassNdx = ndx  // When async listener runs, ndx is end of loop = 2 not 1
    tcmButtonClasses[ndx].addEventListener('click', () => {
        // Display the TCM draggable window
        document.querySelector('#tcm_window').style.cssText = `
            display: flex;
            flex-direction: column;
        `;
        // Remove the TCM Button so it can't be clicked again
        tcmButtonClasses[tcmButtonClassNdx].style.cssText = cssTcmButtonHide()
    });
}

function cssTcmButtonHide () {
    // TCM Page Header TCM Button CSS text set by /assets/css/style.scss .tcm-button {}
    // and /_includes/tcm-common-code.js/cssTextButtonShow()
    return `
        opacity: 0.0;
        background: transparent;
        background-image: none;
        border: none;
    `
}

document.querySelector('#tcm_window_close').addEventListener('click', () => {
    // Hide tcm_window
    document.querySelector('#tcm_window').style.display = "none";
    // Make tcmButtonClasses (main page header) visible?
    if (vis_this_page == "true") { makeTcmButtonVisible() }
});

const b = document.getElementById('tcm_window_body')  // Website tree entries html codes

document.querySelector('#tcm_display_home').addEventListener('click', () => {
    // arrConfigYml in search.js required by two TCM Window Buttons - Home & Webpage Info
    var html = htmlFrontMatter(arrConfigYml, "Site Front Matter ('_config.yml')");
    b.innerHTML = html; // Update TCM Window body
});

document.querySelector('#tcm_display_cloud').addEventListener('click', () => {
    // Display Website Tree
    fetch(raw_url + '/assets/json/website_tree.json')
      .then((response) => response.json())
      .then((website_tree) => {
        var html = htmlWebsiteTree(website_tree);
        b.innerHTML = html; // Update TCM Window body
      });
});

document.querySelector('#tcm_display_local').addEventListener('click', () => {
    // Display cookies and cache (WIP)
    var html = htmlVisibilitySwitches();
    html += htmlSearchStats();
    html += htmlLocalStorage();
    html += htmlScreenInfo();
    b.innerHTML = html;

    table_sort()  // Call to tcm-common-code.js
    /*  Process TCM Window Button Visibility slider switches - shared  with ~/tcm.md
        USE: % include tcm-common-code.js %} */
    tcmButtonVisibility()
});

document.querySelector('#tcm_hyperlink_recipe').addEventListener('click', () => {
    processHyperlinkRecipe('tcm_window_body');
});

document.querySelector('#tcm_webpage_info').addEventListener('click', () => {
    // Display webpage info - filename, front matter and text (WIP)
    // raw_url set in search.js loaded before us
    var urlMarkdown = getMarkdownFilename();

    fetch(urlMarkdown)
        .then((response) => response.text())
        .then((results) => {
            var results = results.split("\n")  // Convert string into array
            var front_yml = getFrontMatter(results)
            var html = htmlFrontMatter(front_yml, "Current Webpage Front Matter");
            html += htmlWindowInfo();
            html += htmlNavigatorInfo();
            b.innerHTML = html; // Update TCM Window body
        });
});

document.querySelector('#tcm_cookie_jar').addEventListener('click', () => {
    // Display webpage info - filename, front matter and text (WIP)
    // raw_url set in search.js loaded before us
    // https://www.javascripttutorial.net/web-apis/javascript-notification/
    var html = '<div class="container">\n' +
               '<h1>JavaScript Notification API Demo</h1>\n' +
               '<div class="error"></div>\n' +
               '</div>'
    var fileDownload="https://pippim.com/assets/img/TCM Header with Gingerbread Man.png"
    //alert('About to download ' + fileDownload);
    b.innerHTML = html;
    // https://developer.mozilla.org/en-US/docs/Web/HTML/Element/a#attributes
    //let downloading = downloads.download({url: fileDownload})
    //console.log("downloading: " + downloading)

    // Notifications
    (async () => {
        // create and show the notification
        const showNotification = () => {
            // create a new notification
            const notification = new Notification('{{ site.title }} Timed Tasks', {
                body: 'File has been downloaded.',
                icon: '{{ site.url }}/favicon.png'
            });

            // close the notification after 10 seconds
            setTimeout(() => {
                notification.close();
            }, 10 * 1000);

            // navigate to a URL when clicked
            notification.addEventListener('click', () => {

                window.open('https://www.javascripttutorial.net/web-apis/javascript-notification/', '_blank');
            });
        }

        // show an error message
        const showError = () => {
            const error = document.querySelector('.error');
            error.style.display = 'block';
            error.textContent = 'You blocked the notifications';
        }

        // check notification permission
        let granted = false;

        if (Notification.permission === 'granted') {
            granted = true;
        } else if (Notification.permission !== 'denied') {
            let permission = await Notification.requestPermission();
            granted = permission === 'granted' ? true : false;
        }

        // show notification or error
        granted ? showNotification() : showError();

    })();
});

function introduction_to_html() {
    var html = "<p>";
    html += "<h3>The Cookie Machine (TCM) Future Applications:</h3>\n";
    html += "  ☑ View cookies used on the {{ site.title }} website.<br>\n";
    html += "  ☑ Send cookie via mail. For backup or sharing.<br>\n";
    html += "  ☑ Receive cookie via mail. From yourself or colleague.<br>\n";
    html += "  ☑ Countdown Timers. For multi-phase time sensitive missions.<br>\n";
    html += "  ☑ And in the future... Other ways of sharing/using Cookies.\n";
    html += "</p>";
    b.innerHTML = html;              // Update TCM Window body
}

introduction_to_html()  // Load immediately

/* MISCELLANEOUS GLOBAL FUNCTIONS AND VARIABLES
*/

// COPY ROUGE CODE BLOCKS

const copyButtonLabel = "Copy 📋";
let blocks = document.querySelectorAll("div.highlight")  // Rouge second level out of three

blocks.forEach((block) => {
    // only add button if browser supports Clipboard API
    if (navigator.clipboard) {
        block.classList.add("rouge-code-block")
        let copyRougeButton = document.createElement("button")
        // Remove ', "page-header-button"' or replace with your own button styling class name
        copyRougeButton.classList.add("copy-rouge-button", "page-header-button")
        copyRougeButton.innerText = copyButtonLabel
        copyRougeButton.setAttribute('title', 'Copy code to clipboard')
        copyRougeButton.setAttribute('aria-label', "Copy code to clipboard")
        copyRougeButton.addEventListener("click", copyRougeCode)
        block.appendChild(copyRougeButton)
    }
});

async function copyRougeCode(event) {
    const button = event.srcElement
    const pre = button.parentElement
    let code = pre.querySelector("code")
    let text = code.innerText
    await navigator.clipboard.writeText(text)

    button.innerText = "Copied ✔️"
    setTimeout(()=> {
        button.innerText = copyButtonLabel
    },1000)
}

// Assign tooltip (title=) to section navigation bar buttons
set_hdr_tooltips();
// Add tooltips to hdr-bar buttons on all blog post pages with navigation buttons
function set_hdr_tooltips () {
    var hdr_bars = document.getElementsByClassName('hdr-bar');
    var hdr_bars_cnt = hdr_bars.length;
    // console.log("hdr_bars_cnt: " + hdr_bars_cnt);
    // var newTextForNotesClass = "This is the new title text for the notes-class-name group.";

    var anchors = document.querySelectorAll('.hdr-bar > a');
    for (var i = 0; i < anchors.length; i++) {
        var itm = anchors[i]
        var h = itm.href;           // Get href ID
        var t = itm.text;           // Get link text
        // console.log("text: " + t);
        var title = "";

        if      (t == 'Top')  { title = "Go to top of page"; }
        else if (t == 'ToS')  { title = "Go to top of section"; }
        else if (t == 'ToC')  { title = "Go to Table of Contents"; }
        else if (t == 'Skip') { title = "Skip this section and go to next section"; }
        else    { console.log("Unknown link text: " + t + " href: " + h); }

        if (title != "") { itm.title = title; }
    }
}

// Color Schemes
var colorSchemeCayman = {
    "--nav-button-bg-color": "#F0FFF0",
    "--msgq-error-bg-color": "#f44336",
    "--msgq-warning-bg-color": "#ff9800",
    "--msgq-info-bg-color": "#2196F3",
    "--msgq-success-bg-color": "#04AA6D",
    "--msgq-body-bg-color": "#f1f1f1",
    "--msgq-border-color": "#d3d3d3",
    "--header-accent-color": "#FFFF00",
    "--button-focus-color": "#1E90FF",
    "--progress-bar-color": "#008000",
    "--flash-bg-color": "#808080",
    "--boldest-color": "#000000",
    "--link-visited": "#800080",
    "--header-heading-color": "#ffffff",
    "--header-bg-color": "#159957",
    "--header-bg-color-secondary": "#155799",
    "--section-headings-color": "#159957",
    "--body-text-color": "#606c71",
    "--body-bg-color": "#ffffff",
    "--body-link-color": "#1e6bb8",
    "--body-link-inverted-color": "#e19447",
    "--blockquote-text-color": "#819198",
    "--code-bg-color": "#f3f6fa",
    "--code-text-color": "#567482",
    "--border-color": "#dce6f0",
    "--table-border-color": "#e9ebec",
    "--hr-border-color": "#eff0f1",
    "--kbd-background-color": "#fafbfc",
    "--kbd-border-color": "#c6cbd1",
    "--kbd-border-bottom-color": "#959da5",
    "--kbd-box-shadow-color": "#959da5",
    "--kbd-color": "#444d56"
}

var colorSchemeDark = {
    "--nav-button-bg-color": "#F0FFF0",
    "--msgq-error-bg-color": "#f44336",
    "--msgq-warning-bg-color": "#ff9800",
    "--msgq-info-bg-color": "#2196F3",
    "--msgq-success-bg-color": "#04AA6D",
    "--msgq-body-bg-color": "#3131f1",
    "--msgq-border-color": "#3333d3",
    "--header-accent-color": "#FFFF00",
    "--button-focus-color": "#1E90FF",
    "--progress-bar-color": "#008000",
    "--flash-bg-color": "#808080",
    "--boldest-color": "#000000",
    "--link-visited": "#800080",
    "--header-heading-color": "#ffffff",
    "--header-bg-color": "#159957",
    "--header-bg-color-secondary": "#155799",
    "--section-headings-color": "#159957",
    "--body-text-color": "#e0ece1",
    "--body-bg-color": "#101010",
    "--body-link-color": "#1e6bb8",
    "--body-link-inverted-color": "#e19447",
    "--blockquote-text-color": "#819198",
    "--code-bg-color": "#f3f6fa",
    "--code-text-color": "#567482",
    "--border-color": "#dce6f0",
    "--table-border-color": "#e9ebec",
    "--hr-border-color": "#eff0f1",
    "--kbd-background-color": "#fafbfc",
    "--kbd-border-color": "#c6cbd1",
    "--kbd-border-bottom-color": "#959da5",
    "--kbd-box-shadow-color": "#959da5",
    "--kbd-color": "#444d56"
}

// TEST list the color scheme

console.log("colorSchemeCayman.length:", colorSchemeCayman.length)
for (const key of Object.keys(colorSchemeCayman)) {
    if (key.startsWith("fail_test")) continue  // Ignore test fail data
    console.log(key, colorSchemeCayman[key], getColorCode(colorSchemeCayman, key))
}

function getColorCode(scheme, key) {
    // Get the styles (properties and values) for the root
    const rootElm = document.querySelector(':root')  // Will not work for popup
    const rs = getComputedStyle(rootElm)
    const value = scheme[key]
    // Alert the value of the --blue variable
    // console.log("The value of " + key + " is: " + value)
    return value
}

// Create a function for setting a variable value
function setColorCode(scheme, key) {
    // Set the value of variable --msgq-error-bg-color to another value (in this case "lightblue")
    const rootElm = document.querySelector(':root')  // Will not work for popup
    const value = scheme[key]
    if (value === null) return
    rootElm.style.setProperty(key, value);
}

/* End of /assets/js/theCookieMachine.js */