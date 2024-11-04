// Main JavaScript for Search Interface

document.addEventListener("DOMContentLoaded", function () {
    // Select DOM elements
    const searchInput = document.getElementById('search-input');
    const searchButton = document.getElementById('search-button');
    const resultsContainer = document.getElementById('results-container');
    const loadingIndicator = document.getElementById('loading-indicator');
    const errorMessage = document.getElementById('error-message');
    const paginationContainer = document.getElementById('pagination-container');
    
    let currentPage = 1;
    const resultsPerPage = 10;
    
    // Event listener for search button
    searchButton.addEventListener('click', function () {
        const query = searchInput.value.trim();
        if (query.length > 0) {
            search(query, currentPage);
        }
    });
    
    // Search function to fetch results from the API
    function search(query, page) {
        showLoading();
        hideError();
        fetch(`/api/search?q=${encodeURIComponent(query)}&page=${page}&size=${resultsPerPage}`)
            .then(response => response.json())
            .then(data => {
                if (data.results && data.results.length > 0) {
                    renderResults(data.results);
                    setupPagination(data.totalResults, page);
                } else {
                    showError("No results found for the query.");
                }
                hideLoading();
            })
            .catch(error => {
                console.error('Search error:', error);
                showError("An error occurred while fetching search results.");
                hideLoading();
            });
    }
    
    // Render search results in the results container
    function renderResults(results) {
        resultsContainer.innerHTML = ''; // Clear previous results
        results.forEach(result => {
            const resultItem = document.createElement('div');
            resultItem.classList.add('result-item');
            resultItem.innerHTML = `
                <h3><a href="${result.url}" target="_blank">${result.title}</a></h3>
                <p>${result.snippet}</p>
            `;
            resultsContainer.appendChild(resultItem);
        });
    }
    
    // Setup pagination controls
    function setupPagination(totalResults, page) {
        paginationContainer.innerHTML = ''; // Clear previous pagination
        const totalPages = Math.ceil(totalResults / resultsPerPage);
        
        for (let i = 1; i <= totalPages; i++) {
            const pageButton = document.createElement('button');
            pageButton.textContent = i;
            pageButton.classList.add('pagination-button');
            if (i === page) {
                pageButton.classList.add('active');
            }
            pageButton.addEventListener('click', () => {
                currentPage = i;
                search(searchInput.value.trim(), currentPage);
            });
            paginationContainer.appendChild(pageButton);
        }
    }
    
    // Show loading indicator
    function showLoading() {
        loadingIndicator.style.display = 'block';
    }

    // Hide loading indicator
    function hideLoading() {
        loadingIndicator.style.display = 'none';
    }
    
    // Show error message
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
    }

    // Hide error message
    function hideError() {
        errorMessage.style.display = 'none';
    }

    // Handle Enter key for initiating search
    searchInput.addEventListener('keyup', function (event) {
        if (event.key === 'Enter') {
            searchButton.click();
        }
    });
    
    // Autocomplete functionality
    searchInput.addEventListener('input', function () {
        const query = searchInput.value.trim();
        if (query.length >= 3) {
            fetch(`/api/autocomplete?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(suggestions => {
                    renderAutocompleteSuggestions(suggestions);
                })
                .catch(error => console.error('Autocomplete error:', error));
        }
    });

    // Render autocomplete suggestions
    function renderAutocompleteSuggestions(suggestions) {
        const suggestionBox = document.getElementById('suggestion-box');
        suggestionBox.innerHTML = ''; // Clear previous suggestions
        suggestions.forEach(suggestion => {
            const suggestionItem = document.createElement('div');
            suggestionItem.classList.add('suggestion-item');
            suggestionItem.textContent = suggestion;
            suggestionItem.addEventListener('click', function () {
                searchInput.value = suggestion;
                suggestionBox.innerHTML = '';
                searchButton.click();
            });
            suggestionBox.appendChild(suggestionItem);
        });
    }

    // Dark mode toggle
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    darkModeToggle.addEventListener('click', function () {
        document.body.classList.toggle('dark-mode');
    });

    // Infinite scroll implementation
    window.addEventListener('scroll', function () {
        if (window.innerHeight + window.scrollY >= document.body.offsetHeight) {
            loadMoreResults();
        }
    });

    // Load more results function for infinite scrolling
    function loadMoreResults() {
        currentPage++;
        search(searchInput.value.trim(), currentPage);
    }

    // Track user interactions (search queries, result clicks)
    function trackInteraction(eventType, details) {
        fetch('/api/track', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ eventType, details })
        }).catch(error => console.error('Tracking error:', error));
    }

    // Add tracking to result clicks
    resultsContainer.addEventListener('click', function (event) {
        if (event.target.tagName === 'A') {
            const clickedResult = event.target.textContent;
            trackInteraction('result_click', { clickedResult });
        }
    });

    // Accessibility: focus on search input on page load
    searchInput.focus();
    
    // Initialize search if query param exists in URL
    const params = new URLSearchParams(window.location.search);
    const queryFromUrl = params.get('q');
    if (queryFromUrl) {
        searchInput.value = queryFromUrl;
        search(queryFromUrl, 1);
    }
});