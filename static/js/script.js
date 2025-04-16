// Log to confirm script is loaded
console.log("Monument Explorer JavaScript loaded!");

// Add click handler for View Details buttons
document.querySelectorAll('.monument-card .btn').forEach(button => {
    button.addEventListener('click', (e) => {
        e.preventDefault(); // Prevent default link behavior
        alert('Details page coming soon! This will show more information about the monument.');
    });
});