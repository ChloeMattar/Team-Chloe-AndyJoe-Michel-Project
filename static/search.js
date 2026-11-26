
const tabs = document.querySelectorAll("#navbar-search .search-tabs button");
const searchForm = document.getElementById("navbar-search-form");
const searchInput = document.getElementById("navbar-search-query");
const searchLabel = document.querySelector('label[for="navbar-search-query"]');

const searchTypes = {
    movies: {
        action: "/search",
        name: "q",
        placeholder: "Search for a movie..."
    },
    actors: {
        action: "/search/actor",
        name: "name",
        placeholder: "Search for an actor..."
    },
    directors: {
        action: "/search/director",
        name: "name",
        placeholder: "Search for a director..."
    }
};

tabs.forEach(function(tab) {
    tab.addEventListener("click", function() {
        const type = tab.dataset.tab;
        const selected = searchTypes[type];

        tabs.forEach(function(button) {
            button.classList.remove("active");
            button.setAttribute("aria-pressed", "false");
        });

        tab.classList.add("active");
        tab.setAttribute("aria-pressed", "true");

        searchForm.action = selected.action;
        searchInput.name = selected.name;
        searchInput.placeholder = selected.placeholder;
        searchLabel.textContent = selected.placeholder.replace("...", "");
        searchInput.value = "";
    });
});

searchForm.addEventListener("submit", function() {
    const searchButton = searchForm.querySelector('button[type="submit"]');
    searchButton.textContent = "Searching...";
});
