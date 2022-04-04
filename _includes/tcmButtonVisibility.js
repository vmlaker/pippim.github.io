/* /_includes/tcmButtonVisibility.js code shared by:
    /assets/js/theCookieMachine.js - Draggable Modal Dialog
    /tcm.md - The Cookie Machine documentation webpage
*/

/* Display visibility switches and search statistics */
var configYml = []          // Array containing _config.yml
var flagPostsByYear = null  // true or false from _config.yml key posts_by_year

// Fetch config.yml from internet or session Storage
var config_yml = [];  // config_yml is raw text and configYml is an array
if (sessionStorage.config_yml === undefined) { load_config_yml(); }
else { config_yml = sessionStorage.getItem('config_yml'); }

function buildConfigYml () {
    // Sets global array configYml and flagPostsByYear used by two functions
    // NOTE: Cannot call on page load because fetch is running asynchronously
    configYml = config_yml.split("\n")  // Convert string into array
    // Set flagPostsByYear flag
    flagPostsByYear = "false";
    for (var i = 0; i < configYml.length; i++) {
        var ymlKeyValue = configYml[i].split(':');
        if (ymlKeyValue.length == 2 && !ymlKeyValue[0].startsWith('#')) {
            if (ymlKeyValue[0] == "posts_by_year") {
                flagPostsByYear = ymlKeyValue[1].trim();
                break } } }
}

function htmlVisibilitySwitches () {
    var html = "<h3>Local Storage and Cookies</h3>";
    html += "After closing this window, the TCM button will be:<br>"
    html += "&emsp; Visible on this webpage? " +
            '<img class="with-action" id="switch_this_page" ' +
            'src="{{ site.url }}/assets/img/icons/switch_off_left.png" /><br>'
    html += "&emsp; Visible on all webpages? " +
            '<img class="with-action" id="switch_all_pages" ' +
            'src="{{ site.url }}/assets/img/icons/switch_off_left.png" /><br>'
    html += "&emsp; Visible on all sessions? " +
            '<img class="with-action" id="switch_all_sessions" ' +
            'src="{{ site.url }}/assets/img/icons/switch_off_left.png" /><br>'
    return html
}

function htmlSearchStats() {
    /* return html code <table> <td> for:
        Statistic Key       Statistic Value
        timeCreated         999999?
        Search Words Count  888,888
    */
    var html = "<h3>Search Engine Statistics</h3>"
    html += '<table id="statTable">\n' ;
    // Statistics Table heading
    html += '  <tr><th>Statistic Key</th>\n' +
            '  <th>Statistic Value</th></tr>\n';

    for (const [key, value] of Object.entries(search_stats)) {
        html += '  <tr><td>' + key + '</td>\n' ;
        // TODO: Need database of object keys and their value format
        // If greater than 123 MB it's a Unix Date in Epoch
        var d = new Date(value);
        html += '  <td>';  // Start of table cell
        // html += value.toLocaleString();
        if (value < 123456789) { html += value.toLocaleString(); }
        else { html += d.toLocaleDateString() +  ' ' + d.toLocaleTimeString() }
        html += '</td></tr>\n';  // End of table cell and table row
    }
    html += '</table>\n';     // End of our table and form

    // TODO: Move next 9 lines to a shared function
    // Heading: "999 Pippim website entries found." <h3> styling
    html += '<style>\n#statTable th, #statTable td {\n' +
            '  padding: 0 .5rem;\n' +
            '}\n'
    html += '</style>'  // Was extra \n causing empty space at bottom?
    return html; // Update TCM Window body
}

function tcmButtonVisibility() {
    // Initialize switches with values after HTML declared with IDs
    switch_init("switch_this_page", vis_this_page);
    switch_init("switch_all_pages", vis_all_pages);
    switch_init("switch_all_sessions", vis_all_sessions);

    // Toggle switch on/off with button click
    document.getElementById("switch_this_page").addEventListener('click', () => {
        switch_toggle("switch_this_page");
        // If invisible this page, then invisible everywhere
        if (vis_this_page == "false") {
            switch_set("switch_all_pages", "false");
            switch_set("switch_all_sessions", "false");
        }
    });

    document.getElementById("switch_all_pages").addEventListener('click', () => {
        switch_toggle("switch_all_pages");
        // switched on force page visible or off force sessions invisible
        if (vis_all_pages == "true") { switch_set("switch_this_page", "true"); }
        if (vis_all_pages == "false") { switch_set("switch_all_sessions", "false"); }
    });

    document.getElementById("switch_all_sessions").addEventListener('click', () => {
        switch_toggle("switch_all_sessions");
        // If visible all sessions then force visible all pages
        if (vis_all_sessions == "true") {
            switch_set("switch_this_page", "true");
            switch_set("switch_all_pages", "true");
        }
    });

}

var vis_this_page = "true";     // Global default for exiting TCM Window.
var vis_all_pages = sessionStorage.vis_all_pages;
if (vis_all_pages === undefined) { vis_all_pages = "false" }
var vis_all_sessions = getCookie("vis_all_sessions")
// getCookie() will return "" when cookie is undefined.
if (vis_all_sessions == "") { vis_all_sessions = "false" }
// if All sessions were forced on by another session, set our session "true"
if (vis_all_sessions == "true") {
    vis_all_pages = "true"  // Force to "true" just in case it was "false"
    sessionStorage.vis_all_pages = vis_all_pages;
    makeTcmButtonVisible();
}

var switch_on_image = "{{ site.url }}/assets/img/icons/switch_on_right.png"
var switch_off_image = "{{ site.url }}/assets/img/icons/switch_off_left.png"

function makeTcmButtonVisible () {
  // Make #tcm_button at Top of Page (header section) visible
  document.getElementById('tcm_button').style.cssText = `
    opacity: 1.0;
    border: thin solid black;
    border-radius: .5rem;
    background-image: url({{ site.url }}/assets/img/icons/gingerbread_3.png),
                      url({{ site.url }}/assets/img/icons/button_background.png);
    background-repeat: no-repeat;
    background-size: cover;
  `;
}

var objTcmVisById = {};  // Current state (on/"true" or off/"false") by id

function switch_init(id, bool) {
    /* Each switch in object dictionary with element and true/false setting */
    objTcmVisById[id] = {
        'element': document.getElementById(id),
        'setting': "false"
    };
    switch_set(id, bool);
}

function switch_set(id, bool) {
    objTcmVisById[id].setting = bool; 
    if (bool == "true" ) { objTcmVisById[id].element.src = switch_on_image;
                           objTcmVisById[id].element.title = "Click to switch off"; }
                    else { objTcmVisById[id].element.src = switch_off_image;
                           objTcmVisById[id].element.title = "Click to switch on"; }
    if (id == "switch_this_page") { vis_this_page = bool; }
    if (id == "switch_all_pages") {
        vis_all_pages = bool;
        sessionStorage.vis_all_pages = vis_all_pages;
    }
    if (id == "switch_all_sessions") {
        vis_all_sessions = bool;
        setCookie("vis_all_sessions", vis_all_sessions, 30);
    }
}

function check_all_switches() {
    vis_this_page = objTcmVisById["switch_this_page"].setting;
    vis_all_pages = objTcmVisById["switch_all_pages"].setting;
    vis_all_sessions = objTcmVisById["switch_all_sessions"].setting;
}

function switch_toggle(id) {
    if (objTcmVisById[id].setting == "true") { switch_set(id, "false"); }
                                        else { switch_set(id, "true"); }
}



/* End of /_includes/tcm_button_visibility.js */