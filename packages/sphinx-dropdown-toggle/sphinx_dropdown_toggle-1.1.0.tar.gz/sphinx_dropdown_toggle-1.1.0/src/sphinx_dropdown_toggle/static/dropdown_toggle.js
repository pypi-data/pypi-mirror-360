document.addEventListener("DOMContentLoaded", () => {
    const toggleButtonId = "toggle-dropdown-button";
    const rootDropdownState = "dropdowns-opened";

    // Check for dropdowns
    const article = document.querySelector('article.bd-article');
    if (!article) return; // Exit if no article found
    
    const dropdowns = article.querySelectorAll('details.dropdown, details.sd-dropdown, details.toggle-details, div.dropdown');
    if (dropdowns.length === 0) {
        return; // Exit if no dropdowns found
    }

    // Function to check current state of all dropdowns
    function checkDropdownState() {
        const details = article.querySelectorAll('details.dropdown, details.sd-dropdown, details.toggle-details');
        const toggleableDivs = article.querySelectorAll('div.dropdown button.toggle-button');
        
        let allOpen = true;
        let allClosed = true;
        let hasToggleableDropdowns = false;
        
        // Check details elements (includes Sphinx Design dropdowns)
        details.forEach(detail => {
            hasToggleableDropdowns = true;
            if (detail.open) {
                allClosed = false;
            } else {
                allOpen = false;
            }
        });
        
        // Check div dropdowns with toggle buttons
        toggleableDivs.forEach(button => {
            hasToggleableDropdowns = true;
            const div = button.closest('div.dropdown');
            if (div.classList.contains('toggle-hidden')) {
                allOpen = false;
            } else {
                allClosed = false;
            }
        });
        
        // If no toggleable dropdowns found, default to "all closed"
        if (!hasToggleableDropdowns) {
            allOpen = false;
            allClosed = true;
        }
        
        return { allOpen, allClosed };
    }
    
    // Function to update toggle button based on dropdown state
    function updateToggleButton() {
        const { allOpen, allClosed } = checkDropdownState();
        const button = document.getElementById(toggleButtonId);
        
        if (!button) return;
        
        if (allOpen) {
            document.body.classList.add(rootDropdownState);
            button.innerHTML = '<i class="fa-solid fa-angles-up"></i>';
            button.title = "Close all dropdowns";
        } else if (allClosed) {
            document.body.classList.remove(rootDropdownState);
            button.innerHTML = '<i class="fa-solid fa-angles-down"></i>';
            button.title = "Open all dropdowns";
        }
        // If some are open and some are closed, keep current state
    }
    
    // Function to set up observers for dropdown changes
    function setupDropdownWatchers() {
        // Watch for changes to details elements (includes Sphinx Design dropdowns)
        const details = article.querySelectorAll('details.dropdown, details.sd-dropdown, details.toggle-details');
        details.forEach(detail => {
            detail.addEventListener('toggle', updateToggleButton);
        });
        
        // Watch for class changes on div dropdowns with toggle buttons (scoped to article)
        const toggleableDivs = Array.from(article.querySelectorAll('div.dropdown')).filter(div => div.querySelector('button.toggle-button'));
        
        if (toggleableDivs.length > 0) {
            const observer = new MutationObserver(() => updateToggleButton());
            toggleableDivs.forEach(div => {
                observer.observe(div, { attributes: true, attributeFilter: ['class'] });
            });
        }
        
        // Listen for clicks on interactive elements globally (not scoped to article)
        const clickTargets = [
            ...document.querySelectorAll('.admonition-title'),
            ...document.querySelectorAll('button.toggle-button'),
            ...document.querySelectorAll('details.toggle-details summary')
        ];
        
        clickTargets.forEach(target => {
            target.addEventListener('click', () => {
                setTimeout(updateToggleButton, 10);
            });
        });
    }

    const headerEnd = document.querySelector(".article-header-buttons");
    if (headerEnd) {
        const button = document.createElement("button");
        button.id = toggleButtonId;
        button.className = "btn btn-sm nav-link pst-navbar-icon pst-js-only";
        button.title = "Open all dropdowns";
        button.innerHTML = '<i class="fa-solid fa-angles-down"></i>';

        headerEnd.prepend(button);
    }
    
    // Function to initialize watchers and state
    function initializeToggleSystem() {
        setupDropdownWatchers();
        updateToggleButton();
    }
    
    // Hook into the same system that togglebutton.js uses
    const sphinxToggleRunWhenDOMLoaded = cb => {
        if (document.readyState != 'loading') {
            cb()
        } else if (document.addEventListener) {
            document.addEventListener('DOMContentLoaded', cb)
        } else {
            document.attachEvent('onreadystatechange', function() {
                if (document.readyState == 'complete') cb()
            })
        }
    }
    
    // Initialize our system after togglebutton.js has done its work
    // We use a small delay to ensure togglebutton.js has finished
    sphinxToggleRunWhenDOMLoaded(() => {
        // Give togglebutton.js a moment to finish adding buttons
        setTimeout(() => {
            initializeToggleSystem();
        }, 10);
    });

    document.getElementById(toggleButtonId)?.addEventListener("click", () => {
        if (document.body.classList.contains(rootDropdownState)) {
            closeDropdowns();
        } else {
            openDropdowns();
        }
    });

    function openDropdowns() {
        document.body.classList.add(rootDropdownState);
        const button = document.getElementById(toggleButtonId);
        if (button) {
            button.innerHTML = '<i class="fa-solid fa-angles-up"></i>';
            button.title = "Close all dropdowns";
        }
        
        // Open all details dropdowns
        article.querySelectorAll('details.dropdown, details.sd-dropdown, details.toggle-details').forEach(detail => {
            if (!detail.open) {
                detail.open = true;
            }
        });
        
        // Open all div dropdowns
        article.querySelectorAll('div.dropdown').forEach(div => {
            div.classList.remove('toggle-hidden');
        });
        article.querySelectorAll('button.toggle-button').forEach(button => {
            button.classList.remove('toggle-button-hidden');
        });
    }

    function closeDropdowns() {
        document.body.classList.remove(rootDropdownState);
        const button = document.getElementById(toggleButtonId);
        if (button) {
            button.innerHTML = '<i class="fa-solid fa-angles-down"></i>';
            button.title = "Open all dropdowns";
        }
        
        // Close all details dropdowns
        article.querySelectorAll('details.dropdown, details.sd-dropdown, details.toggle-details').forEach(detail => {
            if (detail.open) {
                detail.open = false;
            }
        });
        
        // Close all div dropdowns
        article.querySelectorAll('div.dropdown').forEach(div => {
            div.classList.add('toggle-hidden');
        });
        article.querySelectorAll('button.toggle-button').forEach(button => {
            button.classList.add('toggle-button-hidden');
        });
    }
});
