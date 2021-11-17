
function applyTheme(el) {
    if (localStorage.getItem('mode') === 'light') {
        el.classList.add("light");
        el.classList.remove("dark");
    } else {
        el.classList.add("dark");
        el.classList.remove("light");
    }
}

function SwitchTheme() {
    localStorage.setItem('mode', (localStorage.getItem('mode') || 'light') === 'dark' ? 'light' : 'dark');
    applyTheme(document.body);

    let editor = frames['id_content_ifr'].contentDocument.body;
    if (!editor) {
        setTimeout(()=>{
            editor = frames['id_content_ifr'].contentDocument.body;
            applyTheme(editor)
        }, 1000)
    }
    applyTheme(editor)
}