const discoveryForms = document.querySelectorAll(
    '.genre-section form, .mood-section form'
);

const loadingMessage = document.getElementById("discovery-loading");

discoveryForms.forEach(function(form) {
    form.addEventListener("submit", function() {
        loadingMessage.hidden = false;
    });
});