// Switch to dark more by modyfiying data-bs-theme class of the html element from auto to either dark or light using input checkbox with id lightSwitch

document.addEventListener("DOMContentLoaded", function () {
    const lightSwitch = document.getElementById("lightSwitch");
    lightSwitch.addEventListener("change", function () {
        if (this.checked) {
            document.documentElement.setAttribute("data-bs-theme", "dark");
        } else {
            document.documentElement.setAttribute("data-bs-theme", "light");
        }
    })
  });


