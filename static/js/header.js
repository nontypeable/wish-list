(() => {
    const header = document.querySelector('.site-header');
    if (!header) return;

    const mobile = window.matchMedia('(max-width: 40rem)');
    let previousY = window.scrollY;
    let direction = 0;
    let distance = 0;
    let scheduled = false;

    function reset() {
        header.classList.remove('site-header--hidden');
        previousY = window.scrollY;
        direction = 0;
        distance = 0;
    }

    function update() {
        scheduled = false;
        if (!mobile.matches) {
            reset();
            return;
        }

        // Ignore elastic overscroll at the top and bottom of the page.
        const maximumY = Math.max(0, document.documentElement.scrollHeight - window.innerHeight);
        const y = Math.max(0, Math.min(window.scrollY, maximumY));
        const delta = y - previousY;
        previousY = y;

        if (y <= header.offsetHeight || header.contains(document.activeElement)) {
            header.classList.remove('site-header--hidden');
            distance = 0;
            return;
        }
        if (document.querySelector('dialog[open]') || Math.abs(delta) < 1) return;

        const nextDirection = delta > 0 ? 1 : -1;
        if (nextDirection !== direction) distance = 0;
        direction = nextDirection;
        distance += Math.abs(delta);

        // Small finger movements should not make navigation flicker.
        if (distance >= 12) {
            header.classList.toggle('site-header--hidden', direction > 0);
            distance = 0;
        }
    }

    window.addEventListener('scroll', () => {
        if (scheduled) return;
        scheduled = true;
        window.requestAnimationFrame(update);
    }, { passive: true });

    mobile.addEventListener('change', reset);
    window.addEventListener('pageshow', reset);
    header.addEventListener('focusin', reset);
})();
