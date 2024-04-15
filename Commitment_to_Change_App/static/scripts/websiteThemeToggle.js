function setUserPreferredTheme(userPreferTheme) {
    document.documentElement.setAttribute('data-theme', userPreferTheme);
    // Save theme selection in local storage
    localStorage.setItem('theme', userPreferTheme);
    setThemeIcon(userPreferTheme);
}

function setThemeIcon(userPreferTheme) {
var themeIcon = document.getElementById('theme-icon');
    if (userPreferTheme === 'dark') {
        themeIcon.className = 'bi bi-moon-stars-fill';
    } else {
        themeIcon.className = 'bi bi-sun-fill';
    }
}

function toggleTheme() {
    if (localStorage.getItem('theme') === 'dark') {
        setUserPreferredTheme('light');
    } else {
        setUserPreferredTheme('dark');
    }
}

// Immediately invoked function to set the theme on initial load
(function () {
    if (localStorage.getItem('theme') === 'dark') {
        setUserPreferredTheme('dark');
    } else {
        setUserPreferredTheme('light');
}
})();

// Call toggleTheme on theme-toggle button click
document.getElementById('theme-toggle').addEventListener('click', function () {
    toggleTheme();
});