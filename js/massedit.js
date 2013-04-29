var saveInterval = 60000;
var currInterval = 0;

// saving cookies
function cookieSave(name, k)
{
	document.cookie = name + "=" + escape(k);
}

function cookieLoad(name)
{
	var search = name + "=";
	if (document.cookie.length > 0)
	{
		offset = document.cookie.indexOf(search);
		if (offset != -1) {
			offset += search.length;
			end = document.cookie.indexOf(";", offset);
			if (end == -1) {
				end = document.cookie.length;
			}
			return unescape(document.cookie.substring(offset, end));
		}
	}
	return '';
}

// restrict size of text area to 2500 characters (much more cant be saved as cookie)
function maxLength(el) {    
    if (!('maxLength' in el)) {
        var max = el.attributes.maxLength.value;
        el.onkeypress = function () {
            if (this.value.length >= max) return false;
        };
    }
}

// functions for saving state of textarea in cookie
function saveTextState()
{
    var el=document.getElementById('backlog');
	cookieSave('backlog',el.value);
}

function startSavingLoop() {
    if (currInterval > 0) clearInterval(currInterval);
    currInterval = setInterval( "saveTextState()", saveInterval );
}

// initialize everything
window.onload = function() {
	document.getElementById('save').onclick=function() {
		saveTextState();
	}
	document.getElementById('backlog').value=cookieLoad('backlog');
	maxLength(document.getElementById("backlog"));
	startSavingLoop();
}



