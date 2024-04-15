function setUserPreferredTheme(userPreferTheme) {
    document.documentElement.setAttribute('data-theme', userPreferTheme);
    // Save theme selection in local storage
    localStorage.setItem('theme', userPreferTheme); 
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