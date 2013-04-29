function createCookie(name, value, days) {
    if (days) {
        var date = new Date();
        date.setTime(date.getTime()+(days*24*60*60*1000));
        var expires = "; expires="+date.toGMTString();
    }
    else var expires = "";
	document.cookie = name+"="+value+expires+"; path=/";
}
function readCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for(var i=0;i < ca.length;i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1,c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
    }
    return null;
}
function Show(id) { 
    var item = document.getElementById(id);
    item.style.display = 'block';
    createCookie('c_'+id, 1, 356);
}
function Hide(id) { 
    var item = document.getElementById(id);
    item.style.display = 'none';
    createCookie('c_'+id, 0, 356);
}
function ShowHide(id) {
    var item = document.getElementById(id);
    if (item.style.display=='none')	Show(id);
    else							Hide(id);
}
function ToggleEdit(idx, mode) {
	var item = document.getElementById('view'+idx);
	item.style.display = mode==0 ? 'block' : 'none';
	item = document.getElementById('edit'+idx);
	item.style.display = mode==0 ? 'none' : 'block';
	createCookie('c_view'+idx, 1-mode, 356);				
	createCookie('c_edit'+idx, mode, 356);				
}
function OnLoadCheck(id) {
	if (readCookie('c_'+id) == 1) {
        var item = document.getElementById(id);
        item.style.display = 'block';
	} else if (readCookie('c_'+id) == 0) {
		var item = document.getElementById(id);
        item.style.display = 'none';
	}
}