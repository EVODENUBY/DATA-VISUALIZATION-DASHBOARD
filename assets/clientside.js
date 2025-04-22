window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        fixDropdowns: function(pathname) {
            // Fix for all dropdowns
            setTimeout(() => {
                const selects = document.querySelectorAll('.Select');
                selects.forEach(select => {
                    select.style.zIndex = '100';
                    const menu = select.querySelector('.Select-menu-outer');
                    if (menu) {
                        menu.style.zIndex = '9999';
                        menu.style.position = 'absolute';
                    }
                });
            }, 500); // Small delay to ensure DOM is ready
            return null;
        }
    }
});