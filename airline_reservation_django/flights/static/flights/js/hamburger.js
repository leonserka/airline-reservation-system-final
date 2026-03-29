(function () {
    const btn     = document.getElementById('hamburgerBtn');
    const menu    = document.getElementById('megaMenu');
    const overlay = document.getElementById('megaMenuOverlay');
    const close   = document.getElementById('megaMenuClose');

    function openMenu() {
        menu.style.display    = 'block';
        overlay.style.display = 'block';
    }
    function closeMenu() {
        menu.style.display    = 'none';
        overlay.style.display = 'none';
    }

    btn.addEventListener('click', openMenu);
    close.addEventListener('click', closeMenu);
    overlay.addEventListener('click', closeMenu);
})();
