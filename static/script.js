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
    
    // Loop through all modals
    const modals = document.getElementsByClassName("modal");
    for (let i = 0; i < modals.length; i++) {
        const renameModal = modals[i];
        // When modal is shown, focus on the input
        renameModal.addEventListener("shown.bs.modal", function () {
            const input = renameModal.querySelector(".rename-input");
            if (input) {
                input.focus();
            }
        });
    }
    
    // Calendar - WORKS
    // Add this later only to the calender page
    // !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    const monthNames = [
        "January", "February", "March",
        "April", "May", "June", "July",
        "August", "September", "October",
        "November", "December"
      ];
      
    const prevMonthBtn = document.querySelector('.cal-btn:first-of-type');
    const nextMonthBtn = document.querySelector('.cal-btn:last-of-type');
    const monthNameSpan = document.querySelector('.cal-month-name');
    const weekdaysDiv = document.querySelector('.cal-weekdays');
    const daysDiv = document.querySelector('.cal-days');
    
    let currentDate = new Date();
    let currentMonth = currentDate.getMonth();
    let currentYear = currentDate.getFullYear();
    
    function daysInMonth(month, year) {
    return new Date(year, month + 1, 0).getDate();
    }
    
    function getFirstDayOfMonth(month, year) {
    return new Date(year, month, 1).getDay();
    }
      
    function updateCalendar() {
        monthNameSpan.textContent = monthNames[currentMonth] + " " + currentYear;
        weekdaysDiv.innerHTML = '';
        daysDiv.innerHTML = '';
        for (let i = 0; i < 7; i++) {
            const weekdayDiv = document.createElement('div');
            weekdayDiv.classList.add('cal-weekday');
            weekdayDiv.textContent = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][i];
            weekdaysDiv.appendChild(weekdayDiv);
        }
        const firstDayOfMonth = getFirstDayOfMonth(currentMonth, currentYear);
        for (let i = 0; i < firstDayOfMonth; i++) {
            const emptyDayBtn = document.createElement('button');
            emptyDayBtn.classList.add('btn', 'cal-btn', 'invisible');
            daysDiv.appendChild(emptyDayBtn);
        }
        const daysInCurrentMonth = daysInMonth(currentMonth, currentYear);
        for (let i = 1; i <= daysInCurrentMonth; i++) {
            const dayBtn = document.createElement('button');
            dayBtn.classList.add('btn', 'cal-btn');
            dayBtn.textContent = i;
            daysDiv.appendChild(dayBtn);
        }
    }
      
    prevMonthBtn.addEventListener('click', () => {
        currentMonth--;
        if (currentMonth < 0) {
            currentMonth = 11;
            currentYear--;
        }
        updateCalendar();
    });
    
    nextMonthBtn.addEventListener('click', () => {
        currentMonth++;
        if (currentMonth > 11) {
            currentMonth = 0;
            currentYear++;
        }
        updateCalendar();
    });
    
    updateCalendar();






    // TODO
    // Save the selected date to a variable
    // Get the calendar element
    const calendar = document.querySelector(".cal");

    // Function to format the date as YYYY-MM-DD
    function formatDate(date) {
        const year = date.getFullYear();
        const month = (date.getMonth() + 1).toString().padStart(2, "0");
        const day = date.getDate().toString().padStart(2, "0");
        return `${year}-${month}-${day}`;
    }

    // Function to handle click events on calendar buttons
    function handleClick(event) {
        // get the clicked element
        const element = event.target;
        // check if the clicked element is a calendar button
        if (element.classList.contains("cal-btn")) {
            // get the date from the data-date attribute
            const date = new Date(element.dataset.date);
            console.log(date);
            // format the date
            const formattedDate = formatDate(date);
            console.log(formattedDate);
        }


        // send the formatted date to the Flask backend using AJAX
        const xhr = new XMLHttpRequest();
        xhr.open("POST", "/save_date", true);
        xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
            console.log(xhr.responseText); // for testing
            }
        };
        xhr.send(JSON.stringify({ date: formattedDate }));
    }
    

    function save_date() {
        var date = document.getElementById("date").value;
        console.log(date);
        var xhr = new XMLHttpRequest();
        xhr.open("POST", "/save_date", true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.send(JSON.stringify({"date": "{{ formatted_date }}"}));
      }
    
    // Add click event listener to calendar element
    calendar.addEventListener("click", handleClick);
    
});