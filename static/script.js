// Switch to dark more by modyfiying data-bs-theme class of the html element from auto to either dark or light using input checkbox with id lightSwitch

document.addEventListener("DOMContentLoaded", function () {
    const lightSwitch = document.getElementById("lightSwitch");
    lightSwitch.addEventListener("change", function () {
        if (this.checked) {
            document.documentElement.setAttribute("data-bs-theme", "dark");
            // Remember user's preference when reloading the page
            localStorage.setItem("lightSwitch", "dark");
        } else {
            document.documentElement.setAttribute("data-bs-theme", "light");
            // Remember user's preference when reloading the page
            localStorage.setItem("lightSwitch", "light");
        }
    })

    // Remember user's preference when reloading the page
    if (localStorage.getItem("lightSwitch") === "dark") {
        document.documentElement.setAttribute("data-bs-theme", "dark");
        document.getElementById("lightSwitch").checked = true;
    } else {
        document.documentElement.setAttribute("data-bs-theme", "light");
    }

    
});




