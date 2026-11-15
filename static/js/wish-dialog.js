(() => {
    const dialog = document.querySelector('#wish-details');
    if (!dialog) return;
    const content = dialog.querySelector('[data-wish-content]');
    let opener;
    let backdropPress = false;

    document.querySelectorAll('[data-wish-open]').forEach((button) => {
        button.addEventListener('click', () => {
            const template = document.getElementById(button.dataset.wishOpen);
            if (!template) return;
            opener = button;
            content.replaceChildren(template.content.cloneNode(true));
            dialog.showModal();
            dialog.scrollTop = 0;
            document.documentElement.classList.add('wish-dialog-open');
        });
    });

    dialog.querySelector('[data-wish-close]').addEventListener('click', () => dialog.close());

    function isBackdrop(event) {
        const rect = dialog.getBoundingClientRect();
        return event.clientX < rect.left || event.clientX > rect.right
            || event.clientY < rect.top || event.clientY > rect.bottom;
    }

    dialog.addEventListener('pointerdown', (event) => {
        backdropPress = event.target === dialog && isBackdrop(event);
    });

    dialog.addEventListener('click', (event) => {
        if (backdropPress && event.target === dialog && isBackdrop(event)) dialog.close();
        backdropPress = false;
    });

    dialog.addEventListener('close', () => {
        document.documentElement.classList.remove('wish-dialog-open');
        content.replaceChildren();
        opener?.focus({ preventScroll: true });
    });
})();
