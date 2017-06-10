function isMobile() {
	return screen.width < 700;
}

function showproject(id, pushState=true) {
	if(pushState) {
		history.pushState(null, null, '/?p='+id);    
	}
	window.scrollTo(0,0);
	let menu = document.getElementById("menu");
	let projectdiv = document.getElementById("projects");
	let projects = document.getElementsByClassName("project");
	if(!id || !document.getElementById(id)) {
		mainmenu("");
		return;
	} else {
		menu.style.display = "none";
		for (let project of projects) {
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

function constructMenuTable(listOfDivs, id, dummy_elements) {
	let table = document.getElementById(id);
	table.innerHTML = "";
	for(let i in listOfDivs) {
		const d = listOfDivs[i];
		table.appendChild(d); 
	}

	// Add padding elements
	for(let i=0;i<dummy_elements;i++) {
		let pad = document.createElement("div");
		pad.classList.add("box");
		pad.classList.add("boxpad");
		table.appendChild(pad);
	}
}

function makeProjectMenuItem(project) {
		let box = document.createElement("div");
		box.classList.add("box");
		if(project.classList.contains("topmenu")) {
			box.onclick = function() { 
				mainmenu(project.id); 
			};
		} else {
			box.onclick = function() { 
				showproject(project.id); 
			}; 
		}
		let crop = document.createElement("div");
		
		crop.classList.add("crop");
		let coverimg = document.createElement("img");
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
		let title = project.getElementsByClassName("desctitle")[0]
		let media = project.getElementsByClassName("descmedia")[0]
		let year =  project.getElementsByClassName("descyear")[0]
		if(title) box.appendChild(title.cloneNode(true));
		if(media) box.appendChild(media.cloneNode(true));
		if(year) box.appendChild(year.cloneNode(true));
		
		return box;
}

function getFilteredProjects(classname) {
	const projectContainer = document.getElementById("projects")
	const projects = projectContainer.getElementsByClassName(classname);
	let filtered_projects = [];
	for(let project of projects) {
		filtered_projects.push(makeProjectMenuItem(project));
	}
	return filtered_projects;
}

function mainmenu(classname, pushState=true) {
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
	query.split("&").forEach(function(part) {
		var item = part.split("=");
		if(item[1]) {
			item[1] = item[1].replace(/\/$/, "");
		}
		result[item[0]] = decodeURIComponent(item[1]);
	});
	return result;
}

function interpretUrlState() {
	const params = getJsonFromUrl();  
	if(params["p"]){
		showproject(params["p"], false)
	} else
	if(params["s"]){
		mainmenu(params["s"], false);
	} else {
		// Check for oldstyle URL format (existing links)
		let hash = window.location.hash.substring(1);
		if(hash) {
			window.location = "?p="+hash;
		} else {
			mainmenu("", false);
		}
	}
}

window.addEventListener('popstate', interpretUrlState);

function onDOMReady() {
	interpretUrlState();
	if (isMobile()) {
		// Make all project pages single column:
		let imagedivs = document.getElementsByClassName("image")
		for(i=0; i<imagedivs.length; ++i) {
			imagedivs[i].classList.add("wide")
		}
	}
}

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

