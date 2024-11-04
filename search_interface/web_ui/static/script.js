document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('searchForm');
    const searchInput = document.getElementById('searchInput');
    const resultsContainer = document.getElementById('resultsContainer');
    const paginationContainer = document.getElementById('paginationContainer');
    const suggestionsContainer = document.getElementById('suggestionsContainer');
    
    let currentPage = 1;
    let totalPages = 0;
    
    // Debounce for reducing query frequency on user input
    let debounceTimer;
    searchInput.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(handleInput, 300);
    });
    
    function handleInput() {
        const query = searchInput.value.trim();
        if (query.length > 0) {
            fetchSuggestions(query);
        } else {
            suggestionsContainer.innerHTML = '';
        }
    }
    
    // Submit the search query
    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const query = searchInput.value.trim();
        if (query.length > 0) {
            fetchSearchResults(query, 1);
        }
    });

    // Fetch search results from the server
    function fetchSearchResults(query, page) {
        currentPage = page;
        const url = `/search?query=${encodeURIComponent(query)}&page=${page}`;
        
        fetch(url)
            .then(response => response.json())
            .then(data => {
                totalPages = data.totalPages;
                displayResults(data.results);
                displayPagination();
            })
            .catch(error => console.error('Error fetching search results:', error));
    }

    // Fetch query suggestions based on user input
    function fetchSuggestions(query) {
        const url = `/suggestions?query=${encodeURIComponent(query)}`;
        
        fetch(url)
            .then(response => response.json())
            .then(suggestions => {
                displaySuggestions(suggestions);
            })
            .catch(error => console.error('Error fetching suggestions:', error));
    }

    // Display the search results
    function displayResults(results) {
        resultsContainer.innerHTML = '';
        
        if (results.length === 0) {
            resultsContainer.innerHTML = '<p>No results found.</p>';
            return;
        }
        
        results.forEach(result => {
            const resultItem = document.createElement('div');
            resultItem.classList.add('result-item');
            
            const title = document.createElement('h3');
            const link = document.createElement('a');
            link.href = result.url;
            link.textContent = result.title;
            title.appendChild(link);
            
            const snippet = document.createElement('p');
            snippet.textContent = result.snippet;
            
            resultItem.appendChild(title);
            resultItem.appendChild(snippet);
            resultsContainer.appendChild(resultItem);
        });
    }

    // Display pagination controls
    function displayPagination() {
        paginationContainer.innerHTML = '';
        
        if (totalPages <= 1) return;
        
        const paginationList = document.createElement('ul');
        paginationList.classList.add('pagination-list');
        
        for (let i = 1; i <= totalPages; i++) {
            const paginationItem = document.createElement('li');
            paginationItem.textContent = i;
            paginationItem.classList.add('pagination-item');
            
            if (i === currentPage) {
                paginationItem.classList.add('active');
            }
            
            paginationItem.addEventListener('click', function() {
                fetchSearchResults(searchInput.value.trim(), i);
            });
            
            paginationList.appendChild(paginationItem);
        }
        
        paginationContainer.appendChild(paginationList);
    }

    // Display query suggestions
    function displaySuggestions(suggestions) {
        suggestionsContainer.innerHTML = '';
        
        suggestions.forEach(suggestion => {
            const suggestionItem = document.createElement('div');
            suggestionItem.classList.add('suggestion-item');
            suggestionItem.textContent = suggestion;
            
            suggestionItem.addEventListener('click', function() {
                searchInput.value = suggestion;
                suggestionsContainer.innerHTML = '';
                fetchSearchResults(suggestion, 1);
            });
            
            suggestionsContainer.appendChild(suggestionItem);
        });
    }
    
    // Infinite scroll for loading more results
    let loading = false;
    window.addEventListener('scroll', function() {
        if (window.innerHeight + window.scrollY >= document.body.offsetHeight && !loading && currentPage < totalPages) {
            loading = true;
            fetchSearchResults(searchInput.value.trim(), currentPage + 1);
            loading = false;
        }
    });

    // Auto-focus on search input
    searchInput.focus();
    
    // Theme toggle functionality
    const themeToggle = document.getElementById('themeToggle');
    themeToggle.addEventListener('click', function() {
        document.body.classList.toggle('dark-theme');
        const currentTheme = document.body.classList.contains('dark-theme') ? 'dark' : 'light';
        localStorage.setItem('theme', currentTheme);
    });
    
    // Load theme from localStorage
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.body.classList.toggle('dark-theme', savedTheme === 'dark');
    }
    
    // Back to top button functionality
    const backToTopButton = document.getElementById('backToTopButton');
    window.addEventListener('scroll', function() {
        if (window.scrollY > 300) {
            backToTopButton.classList.add('visible');
        } else {
            backToTopButton.classList.remove('visible');
        }
    });

    backToTopButton.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
});