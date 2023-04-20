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
    
        let selectedDate;

        // Add a click event listener to each of the day buttons
        const dayButtons = daysDiv.querySelectorAll('button');
        dayButtons.forEach(button => {
            button.addEventListener('click', () => {
            const day = button.textContent;
            const monthIndex = currentMonth;
            const year = currentYear;
            const selectedDate = new Date(year, monthIndex, day);
            
            // TESTING
            const newDate = new Date(selectedDate);
            const newYear = newDate.getFullYear();
            const newMonth = String(newDate.getMonth() + 1).padStart(2, '0');
            const newDay = String(newDate.getDate()).padStart(2, '0');
            const formattedDate = `${newYear}-${newMonth}-${newDay}`;
            console.log(formattedDate);






            if (formattedDate) {
                // Send the selected date to the Flask backend using AJAX
                const xhr = new XMLHttpRequest();
                const url = '/dashboard';
                const data = formattedDate;
                xhr.open('POST', url, true);
                xhr.setRequestHeader('Content-Type', 'text/plain');
                xhr.onload = function() {
                  if (xhr.status === 200) {
                    console.log('Date processed successfully');
                  } else {
                    console.log('Error processing date');
                  }
                };
                console.log(data)
                xhr.send(data);
              }
            });
          });
        
        

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



});