---
---
/* ============================================================================

    /assets/js/sound.js

    ONLY for webpages that need it, include this script to preload (fetch)
    sound files (audio files).

    Source Code Credit (heavily modified after copying though):

        https://staxmanade.com/2015/11/
            how-to-base64-and-save-a-binary-audio-file-to-local-storage-and-
            play-it-back-in-the-browser/

    Sound file: Alarm_01.wav from Scorpion2185. GPL3 license.

    Temporary usage as BBC commercial license investigated. May be easier to
    simply record a Dollar-rama alarm clock from China. In the meantime,
    here is credit to the BBC (British Broadcasting Corporation):

    SOURCE: https://sound-effects.bbcrewind.co.uk/search?q=alarm%20clock&resultSize=40

    Alarm_03.mp3 = Clocks - Domestic clock striking three o'clock.
                            (Domestic clock with bell.)
                 Filename - bbc_clocks---d_07022030.mp3
    Alarm_05.mp3 = Clocks - Domestic clock striking five o'clock.
                            (Domestic clock with bell.)
                 Filename - bbc_clocks---d_07022056.mp3
    Alarm_12.mp3 = Clocks - Domestic clock striking twelve o'clock.
                            (Domestic clock with bell.)
                 Filename - bbc_clocks---d_07022051.mp3
============================================================================ */

// TODO: Ensure Sound filenames don't contain "|"

// Session Storage statistics. stockNames match ID Name on screen
const stockNames = ["Alarm_01.wav", "Alarm_01.mp3",
                    "Alarm_03.mp3", "Alarm_05.mp3", "Alarm_12.mp3"];
const stockPrefix = "{{ site.url }}/assets/sound/";
var customNames = []

function loadStockNames () {
    // If stock name isn't in local storage, fetch it from website
    for (var i = 0; i < stockNames.length; i++) {
        var localItem = JSON.parse(localStorage.getItem(stockNames[i]));
        if (localItem === null) { fetch_sound(stockNames[i]); }
        else { setSoundSource(stockNames[i], localItem); }
    }
}

const CUSTOM_SOUNDS = "custom_sounds";
const CUSTOM_SOUND_ROOT = "Custom";
const CUSTOM_SOUND_SEP = "_";
const CUSTOM_SOUND_DIGITS = 3;  // E.G. "Custom_001" to "Custom_999"
var customSounds = {
    count: 0,
    nextNumber: 1,
    firstKey: "Custom_999",
    lastKey: "Custom_000",
    sounds: {}
}

/*  The key "Custom_999" has to be used instead of the audio filename.
    There is no guarantee the filename doesn't match an internal HTML ID tag.
    ID tags must always be unique so a custom key is used.
*/
var sound = {
    key: "Custom_000",
    name: "Some alarm filename.wav",
    size: 0,
    type: "audio/x-wav",
    timeAdded: 0
}

function loadCustomNames () {
    let stored = JSON.parse(localStorage.getItem(CUSTOM_SOUNDS));
    if (stored === null) {
        // First time on this browser, create new Custom Sound Controls
        localStorage.setItem(CUSTOM_SOUNDS, JSON.stringify(customSounds));
        customSounds = JSON.parse(localStorage.getItem(CUSTOM_SOUNDS));
    } else { customSounds = Object.assign({}, stored); }

    customNames = []
    for (const key of Object.keys(customSounds.sounds)) {
        customNames.push(key)
    }
}

loadCustomNames();

document.addEventListener("DOMContentLoaded", function(event){
    // Must wait due to error: Uncaught TypeError: audioControl is null
    loadStockNames();
});

async function fetch_sound(name) {
    // Get sound file from website and add to localStorage
    fetch(stockPrefix + name)
    .then((response)=>response.blob())
    .then((results)=>{
        // Create asynchronous 'reader' and listen for it to finish
        var reader = new FileReader();
        reader.addEventListener("loadend", function() {
            var base64FileData = reader.result.toString();
            var mediaFile = {
              fileUrl: name,
              size: results.size,
              type: results.type,
              src: base64FileData
            };
            localStorage.setItem(name, JSON.stringify(mediaFile));
            var reReadItem = JSON.parse(localStorage.getItem(name));
            setSoundSource(name, reReadItem)
        });
        // Above listener is executed when below reader completes
        reader.readAsDataURL(results);
    });
}

function setSoundSource (name, item) {
    audioControl = document.getElementById(name);
    audioControl.src = item.src;
    // May 14, 2022, random wav files getting 6 hours, 45 minutes and 48 seconds
    // Each page refresh cycles between correct duration and bogus duration.
    // So hard code the audio type in hopes it fixes this random error
    audioControl.type = item.type
    // https://stackoverflow.com/a/51745288/6929343
    // Below simply sets known duration to 0:0:0 and doesn't change behavior
    //audioControl.preload = "none"
}

function playSoundSource (name) {
    // Called by tim-ta.js
    audioControl = document.getElementById(name);
    audioControl.play();
}

/* End of /assets/js/sound.js */