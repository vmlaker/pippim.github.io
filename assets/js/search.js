// From: https://stackoverflow.com/a/12393346/6929343
window.MyLib = {}; // global Object container; don't use var
MyLib.search_words = null         // global context
MyLib.earch_urls = null           //   "      "

// From: https://stackoverflow.com/a/55784549/6929343
// MyLib.search_words = load('https://raw.githubusercontent.com/pippim/pippim.github.io/main/assets/json/search_include.json')
// MyLib.search_urls = load('https://raw.githubusercontent.com/pippim/pippim.github.io/main/assets/json/search_url.json')

async function load_search_objects() {
    MyLib.search_words = load('https://raw.githubusercontent.com/pippim/pippim.github.io/main/assets/json/search_include.json')
    console.log(MyLib.search_words["brightness"]);
    MyLib.search_urls = load('https://raw.githubusercontent.com/pippim/pippim.github.io/main/assets/json/search_url.json')
    console.log(MyLib.search_urls[1000]);
}

async function load(url) {
    let obj = null;

    try {
        obj = await (await fetch(url)).json();
    } catch(e) {
        console.log('load error: object could not be fetched.');
    }

    return obj
}

async function load_search_objects_old() {
    let url = 'https://raw.githubusercontent.com/pippim/pippim.github.io/main/assets/json/search_include.json';
    let search_words = null;

    try {
        search_words = await (await fetch(url)).json();
    } catch(e) {
        console.log('error: search_words could not be loaded.');
    }

    console.log(search_words["brightness"]);

    let url2 = 'https://raw.githubusercontent.com/pippim/pippim.github.io/main/assets/json/search_url.json';
    let search_urls = null;

    try {
        search_urls = await (await fetch(url2)).json();
    } catch(e) {
        console.log('error: search_urls could not be loaded.');
    }

    console.log(search_urls[1000]);
}

// load_search_objects();  // Do we really need this here?
