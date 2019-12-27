
function move_item(item, to) {
    var par = item.parentNode;
    var itr = par.removeChild(item);
    ulTo = document.getElementById(to);
    ulTo.insertBefore(itr, ulTo.firstChild);
    if(to == "shopped")
        itr.onclick = move_item_toshop;
    else if(to == "toshop")
        itr.onclick = move_item_shopped;
    document.getElementById("save_shopped").style.color = "#0000CC";
}
function move_item_shopped() {
    move_item(this, "shopped");
}
function move_item_toshop() {
    move_item(this, "toshop");
}

function init() {
    ul = document.getElementById("toshop");
    for(var i = 0; i < ul.childNodes.length; i++) {
        li = ul.childNodes[i];
        if(li.nodeType != 1)
            continue;
        if(li.nodeName != "LI")
            continue;
        li.onclick = move_item_shopped;
    }
    ul_shopped = document.getElementById("shopped");
    for(var i = 0; i < ul_shopped.childNodes.length; i++) {
        li = ul_shopped.childNodes[i];
        if(li.nodeType != 1)
            continue;
        if(li.nodeName != "LI")
            continue;
        li.onclick = move_item_toshop;
    }
}

function display_toggle(display_type) {
    spans = document.getElementsByClassName(display_type);
    for(var i = 0; i < spans.length; i++) {
        var span = spans[i];
        if(document.getElementById(display_type + "_check").checked) {
            span.style.display = "inline";
        } else {
            span.style.display = "none";
        }
    }
}

function save_shopped() {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("POST", "/manage_lists/edit_shopped", true);
    xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");

    // Go through all elems and put them into request for shopped status
    var request = "";
    ul = document.getElementById("toshop");
    for(var i = 0; i < ul.childNodes.length; i++) {
        li = ul.childNodes[i];
        if(li.nodeType != 1)
            continue;
        if(li.nodeName != "LI")
            continue;
        if(request.length > 0)
            request += "&";
        request += li.id + "=0";
    }
    ul_shopped = document.getElementById("shopped");
    for(var i = 0; i < ul_shopped.childNodes.length; i++) {
        li = ul_shopped.childNodes[i];
        if(li.nodeType != 1)
            continue;
        if(li.nodeName != "LI")
            continue;
        if(request.length > 0)
            request += "&";
        request += li.id + "=1";
    }

    xmlhttp.onreadystatechange = function() {
        if(xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            // On success "disable" button
            document.getElementById("save_shopped").style.color = "#333333";
        }
    }
    xmlhttp.send(request);
}

function save_shopping_config() {
    selectedIdx = 0
    ul_shopped = document.getElementById("shopped");
    var request = "";
    for(var i = 0; i < ul_shopped.childNodes.length; i++) {
        li = ul_shopped.childNodes[i];
        if(li.nodeType != 1)
            continue;
        if(li.nodeName != "LI")
            continue;
        request += li.title + "\n";
        selectedIdx++;
    }

    document.forms['edit_config'].elements["selected_configs"].value = request;
    document.forms['edit_config'].submit();
}

