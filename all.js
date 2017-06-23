
// Defines what it means to present the mobile version.
function isMobile() {
  return screen.width < 700;
}


// Finds all the img elements in the div and for all those that dont have the
// src attribute set use the data-src attribute to set src. This will cause the 
// browser to actually load them.

function loadImagesInDiv(div) {
  var imgs = div.getElementsByTagName("img");
  for(var i = 0; i < imgs.length; i++) {
    var img = imgs[i];
    if(img.src == "") {
      img.src = img.getAttribute('data-src');
    }
  }
}

// Render a specific project page.
function showproject(id, pushState) {
  if(pushState) {
    history.pushState(null, null, '/?p='+id);    
  }
  window.scrollTo(0,0);
  var menu = document.getElementById("menu");
  var projectdiv = document.getElementById("projects");
  var projects = document.getElementsByClassName("project");
  var id_div = document.getElementById(id);
  if(!id || !id_div) {
    mainmenu("");
    return;
  } else {
    loadImagesInDiv(id_div);
    menu.style.display = "none";
    for (var i = 0; i < projects.length; i++) {
      var project = projects[i];
      if(project.id == id) {
        project.style.display = "block";
      } else {
        project.style.display = "none";
      }
    }
    projectdiv.style.display = "block";
  }
  hideSpinner();
}

// Show a menu grid
function constructMenuTable(listOfDivs, id, dummy_elements) {
  var table = document.getElementById(id);
  table.innerHTML = "";
  for(var i=0; i < listOfDivs.length; i++) {
    var d = listOfDivs[i];
    table.appendChild(d); 
  }

  // Add padding elements
  for(var i=0;i<dummy_elements;i++) {
    var pad = document.createElement("div");
    pad.classList.add("box");
    pad.classList.add("boxpad");
    table.appendChild(pad);
  }
}

// Create a div containing a cover picture and a title and year for 
// the project.
function makeProjectMenuItem(project) {
  var box = document.createElement("div");
  box.classList.add("box");
  if(project.classList.contains("topmenu")) {
    box.onclick = function() { 
      mainmenu(project.id); 
    };
  } else {
    box.onclick = function() { 
      showproject(project.id, true); 
    }; 
  }
  var crop = document.createElement("div");

  crop.classList.add("crop");
  var coverimg = document.createElement("img");
  cover_image = project.getElementsByClassName("coverimg");
  if (cover_image.length > 0) {
    coverimg.classList.add("coverimg");
    coverimg.src = cover_image[0].src
  } else {
    coverimg.classList.add("coverimg-auto");
    coverimg.src = project.getElementsByClassName("image")[0].src;
  }
  crop.appendChild(coverimg);
  box.appendChild(crop);
  var title = project.getElementsByClassName("desctitle")[0]
    var media = project.getElementsByClassName("descmedia")[0]
    var year =  project.getElementsByClassName("descyear")[0]
    if(title) box.appendChild(title.cloneNode(true));
  if(media) box.appendChild(media.cloneNode(true));
  if(year) box.appendChild(year.cloneNode(true));

  return box;
}

function getFilteredProjects(classname) {
  var projectContainer = document.getElementById("projects")
    var projects = projectContainer.getElementsByClassName(classname);
  var filtered_projects = [];
  for (var i = 0; i < projects.length; i++) {
    var project = projects[i];
    filtered_projects.push(makeProjectMenuItem(project));
  }
  return filtered_projects;
}

function mainmenu(classname, pushState) {
  if(pushState) {
    history.pushState(null, null, '/?s='+classname);
  }
  window.scrollTo(0,0);
  toplevel = document.getElementById("toplevel");
  menu = document.getElementById("menu");
  projectdiv = document.getElementById("projects");
  projectdiv.style.display = "none";
  if(!classname) {
    constructMenuTable(getFilteredProjects("topmenu"), "topleveltable", 0);
    toplevel.style.display = "block";
    menu.style.display = "none";
  } else {
    toplevel.style.display = "none";
    menu.style.display = "block";
    constructMenuTable(getFilteredProjects(classname), "menutable", 6);
  }
  hideSpinner();
}

function hideSpinner() {
  document.getElementById("spinner").style.display = "none";
}

function getJsonFromUrl() {
  var query = location.search.substr(1);
  var result = {};
  var split_query = query.split("&");
  for(i=0; i<split_query.length; i++) {
    var part = split_query[i];
    var item = part.split("=");
    if(item[1]) {
      item[1] = item[1].replace(/\/$/, "");
    }
    result[item[0]] = decodeURIComponent(item[1]);
  };
  return result;
}

function interpretUrlState() {
  var params = getJsonFromUrl();  
  if(params["p"]){
    showproject(params["p"], false)
  } else
    if(params["s"]){
      mainmenu(params["s"], false);
    } else {
      // Check for oldstyle URL format (existing links)
      var hash = window.location.hash.substring(1);
      if(hash) {
        window.location = "?p="+hash;
      } else {
        mainmenu("", false);
      }
    }
}

// When browser clicks "back" reinterpret state
window.addEventListener('popstate', interpretUrlState);

// Called after DOM (but not images) are loaded
function onDOMReady() {
  console.log("ONDOMREADY");
  interpretUrlState();
  if (isMobile()) {
    // Make all project pages single column:
    var imagedivs = document.getElementsByClassName("image")
      for(i=0; i<imagedivs.length; ++i) {
        imagedivs[i].classList.add("wide")
      }
  }
}

// Register onDOMReady() to be called in a cross browser way.
var alreadyrunflag=0; //flag to indicate whether target function has already been run
if (document.addEventListener) {
  document.addEventListener("DOMContentLoaded", function(){alreadyrunflag=1; onDOMReady()}, false)
} else if (document.all && !window.opera){
  document.write('<script type="text/javascript" id="contentloadtag" defer="defer" src="javascript:void(0)"><\/script>')
    var contentloadtag=document.getElementById("contentloadtag")
    contentloadtag.onreadystatechange=function(){
      if (this.readyState=="complete"){
        alreadyrunflag=1
          onDOMReady()
      }
    }
}

