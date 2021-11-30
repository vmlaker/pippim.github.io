// global variables
var fm_state = "None";
var fm_button = "None";

function setCookie(cname,cvalue,exdays) {
  const d = new Date();
  d.setTime(d.getTime() + (exdays*24*60*60*1000));
  let expires = "expires=" + d.toGMTString();
  document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(cname) {
  let name = cname + "=";
  let decodedCookie = decodeURIComponent(document.cookie);
  let ca = decodedCookie.split(';');
  for(let i = 0; i < ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

function checkCookie() {
  // do not use "let fm_state =" that makes variable local
  fm_state = getCookie("fm_state");
  if (fm_state != "") {
    // window.alert("Front Matter state is: " + fm_state);
    if (fm_state == "Less") {
      // Do not use: "var fm_button =" that makes variable local
      fm_button = "More";
      // $('#hidden_front_matter').hide();
      }
    else {
      fm_button = "Less";
      // $('#hidden_front_matter').show();
      }
  }
  else {
    setCookie("fm_state", "Less", 30);
    fm_state = "Less";
    fm_button = "More";
    // $('#hidden_front_matter').hide();
  }
  return fm_button; // return value not used anymore but leave it
}

function fm_toggle() {
  //if (fm_state != "") {
  //  window.alert("State before eating cookie: " + fm_state);
  //}
  //else {
  //  window.alert("fm_state is null");
  //}
  // do not use "let fm_state =" that makes variable local
  //fm_state = getCookie("fm_state");
  //window.alert("State after eathing cookie: " + fm_state);
  if (fm_state == "Less") {
    setCookie("fm_state", "More", 30);
    // $('#hidden_front_matter').hide();
  }
  else {
    setCookie("fm_state", "Less", 30);
    // $('#hidden_front_matter').show();
  }
  window.location.reload();
  // If we needed to force the document to be fetched from the
  // web server again (such as where the document contents
  // change dynamically but cache control headers are not
  // configured properly), Firefox supports a non-standard
  // parameter that can be set to true to bypass the cache:
  //window.location.reload(true);
}
