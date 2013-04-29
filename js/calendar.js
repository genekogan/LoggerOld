var curridx;

function Show(id) { 
    var item = document.getElementById(id);
    item.style.display = 'block';
}

function Hide(id) { 
    var item = document.getElementById(id);
    item.style.display = 'none';
}

function ShowHide(id) {
    var item = document.getElementById(id);
    if (item.style.display=='none')	Show(id);
    else							Hide(id);
}

function SetModify() {
	Hide('viewevent');
	Show('modifyevent');
	document.getElementById('modifyevent').innerHTML = '<iframe src="/editcalendar/?id='+curridx+'" width="100%" height="100%"></iframe><br/><a href="javascript:Hide(\'modifyevent\');">[close]</a>'
}

function SetCurrIdx(idx) { 
	curridx = idx; 
}

window.onload = function(){
	new JsDatePick({
		useMode:2,
		target:"inputDate",
		dateFormat:"%Y-%m-%d",
		cellColorScheme:"ocean_blue",
		imgPath:"/css/jsdatepick_img/"
	});
	new JsDatePick({
		useMode:2,
		target:"inputUntil",
		dateFormat:"%Y-%m-%d",
		cellColorScheme:"ocean_blue",
		imgPath:"/css/jsdatepick_img/"
	});
};
