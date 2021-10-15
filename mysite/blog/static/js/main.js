// fade out message alerts
function fade_alerts() {
    let alerts = document.getElementsByClassName("alert msg");
        var i = alerts.length;
    let time;
    for (let elem of alerts) {
        i--;
        time = 5000 + (1000 * i);
        setTimeout(function () {
            elem.parentElement.removeChild(elem);
        }, time);
    }
}

// call fade out after DOMContentLoaded
window.addEventListener('DOMContentLoaded', (event) => {
    fade_alerts();
});

//Resizes textarea vertically
function auto_grow(element) {
    element.style.height = "5px";
    element.style.height = (element.scrollHeight)+"px";
}

function preventLineBreak(e) {
    if (e.keyCode == 13) e.preventDefault();
}

function addStylesToEditorFrame() {
    const editor_frame = frames['id_content_ifr']
    if (editor_frame) {
        const themeLink = editor_frame.contentDocument.createElement("link");
        themeLink.href = "/static/css/themes.css";
        themeLink.rel = "stylesheet";
        themeLink.type = "text/css";
        editor_frame.contentDocument.head.appendChild(themeLink);

        if (localStorage.getItem('mode') === 'dark'){
            editor_frame.contentDocument.body.classList.remove('light');
            editor_frame.contentDocument.body.classList.add('dark');
        }
        else {
            editor_frame.contentDocument.body.classList.remove('dark');
            editor_frame.contentDocument.body.classList.add('light')
        }


        if (!editor_frame.contentDocument.getElementById('iframe-resizer')) {
           const gistHeightScript = editor_frame.contentDocument.createElement("script");
            gistHeightScript.setAttribute('id', 'iframe-resizer')
            gistHeightScript.innerHTML = "window.addEventListener('message', function(e) {\n" +
                "\t\tlet message = e.data;\n" +
                "        if (message.iframeID && message.height) {\n" +
                "            let ifr = document.querySelector(`span[data-mce-p-id=\"${message.iframeID}\"] > iframe`);\n" +
                "            if (ifr) ifr.style.height = message.height + 'px';\n" +
                "        }\n" +
                "\t} , false);"
            editor_frame.contentDocument.body.appendChild(gistHeightScript);
        }
    }
}

window.onload = function () {
    addStylesToEditorFrame();
}


function toggle(elementId, displayMode, minWidth ) {
    const x = document.getElementById(elementId);

    if (x.style.display === displayMode) x.style.display = "none";
    else x.style.display = displayMode;

    if (minWidth) {
        if (window[`${elementId}_listener`] !== 'true'){
            window.addEventListener('resize', function(event){
                const el = x;
                window[`${elementId}_listener`] = 'true';
                    if (window.innerWidth > minWidth && el.style.display === 'none') {
                        el.style.display = displayMode
                    }
            });
        }
    }
}


