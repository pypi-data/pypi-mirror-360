document.addEventListener("DOMContentLoaded", function() {
    const sidebarButton = document.getElementById("toggle-sidebar");
    const sidebar = document.getElementById("sidebar");

    sidebarButton.addEventListener("click", function() {
        sidebar.classList.toggle("open");
    });
});