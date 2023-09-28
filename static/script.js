document.addEventListener('DOMContentLoaded', function() {
    // Assign variables to buttons
    const today_button = document.getElementById('today');
    const five_day_button = document.getElementById('five_day');
    const ten_day_button = document.getElementById('ten_day');
    const celsius_button = document.getElementById('celsius');
    const fahrenheit_button = document.getElementById('fahrenheit');

    // Assign variables to cards, temps & other elements
    let today_card = document.getElementById('today_card');
    let five_cards = document.getElementsByClassName('five_day_forecast');
    let ten_cards = document.getElementsByClassName('ten_cards');
    let all_cards = document.getElementsByClassName('ten_day_forecast');
    let temps = document.getElementsByClassName('temp');
    let temp_units = document.getElementsByClassName('temp_unit');
    let is_day = document.getElementById('is_day');
    let nav = document.getElementById('navbar');

    if (is_day.hasAttribute('0') == true) {
        document.body.style.backgroundImage = "url('/static/background_night.jpg')";
        nav.style.backgroundColor = '#4e6cc2';
    }

    // functions for temperature conversions
    function convertToF(value) {
        return Math.round(value * 9 / 5 + 32);
    }

    function convertToC(value) {
        return Math.round((value - 32) * 5 / 9);
    }

    // Listen for 'today' button click
    today_button.addEventListener('click', function() {
        for (let i = 0; i < all_cards.length; i++) {

            // assign and remove attributes to trigger CSS animations
            if (all_cards[i].hasAttribute('open') == true) {
                all_cards[i].removeAttribute('open');
                all_cards[i].setAttribute('closing', '');
                all_cards[i].setAttribute('closed', '');
                all_cards[i].addEventListener('animationend', function() {
                    all_cards[i].style.display = 'none';
                    all_cards[i].removeAttribute('closing');
                }, {

                    // remove event listener once the animation ends
                    once: true
                });
            }
        }
    });

    // Listen for 5-day forecast button click
    five_day_button.addEventListener('click', function() {
        for (let i = 0; i < five_cards.length; i++) {

            // assign and remove attributes to trigger CSS animations
            if (five_cards[i].hasAttribute('closed') == true) {
                five_cards[i].removeAttribute('closed');
                five_cards[i].setAttribute('opening', '');
                five_cards[i].setAttribute('open', '');
                five_cards[i].style.display = 'flex';
                five_cards[i].addEventListener('animationend', function() {
                    five_cards[i].removeAttribute('opening');
                }, {

                    // remove event listener once the animation ends
                    once: true
                });
            }
        }

        for (let i = 0; i < ten_cards.length; i++) {

            // assign and remove attributes to trigger CSS animations
            if (ten_cards[i].hasAttribute('open') == true) {
                ten_cards[i].removeAttribute('open');
                ten_cards[i].setAttribute('closing', '');
                ten_cards[i].setAttribute('closed', '');
                ten_cards[i].addEventListener('animationend', function() {
                    ten_cards[i].removeAttribute('closing');
                    ten_cards[i].style.display = 'none';
                }, {

                    // remove event listener once the animation ends
                    once: true
                });
            }
        }
    });

    // listen for 10-day forecast button click
    ten_day_button.addEventListener('click', function() {
        for (let i = 0; i < all_cards.length; i++) {

            // assign and remove attributes to trigger CSS animations
            if (all_cards[i].hasAttribute('closed') == true) {
                all_cards[i].removeAttribute('closed');
                all_cards[i].setAttribute('opening', '');
                all_cards[i].setAttribute('open', '');
                all_cards[i].style.display = 'flex';
                all_cards[i].addEventListener('animationend', function() {
                    all_cards[i].removeAttribute('opening');
                }, {

                    // remove event listener once the animation ends
                    once: true
                });
            }
        }
    });

    // listen for celsius button click
    celsius_button.addEventListener('click', function() {
        for (let i = 0; i < temps.length; i++) {

            // convert temperature and change temp unit if necessary
            if (temps[i].hasAttribute('fahrenheit') == true) {
                temps[i].innerHTML = convertToC(temps[i].innerHTML);
                temp_units[i].innerHTML = '°C';
                temps[i].removeAttribute('fahrenheit');
                temps[i].setAttribute('celsius', '');
            }
        }
    });

    // listen for fahrenheit button click
    fahrenheit_button.addEventListener('click', function() {
        for (let i = 0; i < temps.length; i++) {

            // convert temperature and change temp unit if necessary
            if (temps[i].hasAttribute('celsius') == true) {
                temps[i].innerHTML = convertToF(temps[i].innerHTML);
                temp_units[i].innerHTML = '°F';
                temps[i].removeAttribute('celsius');
                temps[i].setAttribute('fahrenheit', '');
            }
        }
    });
});