// Dialogs, HTML form submission, copying server-issued URLs, and confirmations.
(() => {
    const inviteDialog = document.getElementById('invite-dialog');
    if (inviteDialog) {
        let inviteOpener;
        let backdropPress = false;
        let submitting = false;
        const content = inviteDialog.querySelector('[data-invite-content]');
        const initialContent = document.createElement('template');
        initialContent.content.append(...Array.from(content.childNodes, (node) => node.cloneNode(true)));
        const error = inviteDialog.querySelector('[data-invite-error]');
        const reset = inviteDialog.querySelector('[data-invite-reset]');

        content.addEventListener('submit', async (event) => {
            const form = event.target.closest('form');
            if (!form) return;
            event.preventDefault();
            if (submitting) return;
            submitting = true;
            const submit = form.querySelector('[type="submit"]');
            const label = submit.textContent;
            submit.disabled = true;
            submit.textContent = 'Создаём приглашение…';
            inviteDialog.setAttribute('aria-busy', 'true');
            error.hidden = true;
            try {
                const response = await fetch(form.action, {
                    method: 'POST',
                    body: new FormData(form),
                    credentials: 'same-origin',
                    headers: { Accept: 'text/html' },
                });
                const html = new DOMParser().parseFromString(await response.text(), 'text/html');
                const result = html.querySelector('[data-invitation-result]');
                if (!response.ok || !result?.querySelector('#invitation-link')?.value) {
                    throw new Error(html.querySelector('.sharing-errors')?.textContent.trim()
                        || 'Не удалось получить ссылку приглашения. Проверьте данные и попробуйте ещё раз.');
                }
                content.replaceChildren(document.importNode(result, true));
                inviteDialog.querySelector('#invite-dialog-title').textContent = 'Приглашение готово';
                reset.hidden = false;
                content.querySelector('[data-copy-target]').focus();
            } catch (failure) {
                error.textContent = failure instanceof TypeError
                    ? 'Не удалось связаться с сервером. Проверьте соединение.'
                    : failure.message;
                error.hidden = false;
            } finally {
                submitting = false;
                submit.disabled = false;
                submit.textContent = label;
                inviteDialog.removeAttribute('aria-busy');
            }
        });
        reset.addEventListener('click', () => {
            content.replaceChildren(initialContent.content.cloneNode(true));
            inviteDialog.querySelector('#invite-dialog-title').textContent = 'Пригласить в вишлист';
            reset.hidden = true;
            error.hidden = true;
            content.querySelector('input[type="email"]').focus();
        });
        document.querySelectorAll('[data-invite-open]').forEach((button) => {
            button.addEventListener('click', () => {
                inviteOpener = button;
                inviteDialog.showModal();
            });
        });
        inviteDialog.querySelector('[data-invite-close]').addEventListener('click', () => inviteDialog.close());
        const isBackdrop = (event) => {
            const rect = inviteDialog.getBoundingClientRect();
            return event.clientX < rect.left || event.clientX > rect.right
                || event.clientY < rect.top || event.clientY > rect.bottom;
        };
        inviteDialog.addEventListener('pointerdown', (event) => {
            backdropPress = event.target === inviteDialog && isBackdrop(event);
        });
        inviteDialog.addEventListener('click', (event) => {
            if (backdropPress && event.target === inviteDialog && isBackdrop(event)) inviteDialog.close();
            backdropPress = false;
        });
        inviteDialog.addEventListener('close', () => inviteOpener?.focus({ preventScroll: true }));
        if (inviteDialog.hasAttribute('data-invite-errors')) inviteDialog.showModal();
    }

    document.addEventListener('click', async (event) => {
        const button = event.target.closest('[data-copy-target]');
        if (!button || button.disabled) return;
        const input = document.getElementById(button.dataset.copyTarget);
        const status = button.closest('[data-invitation-result]')?.querySelector('[data-copy-status]');
        if (!input?.value) return;
        try {
            await navigator.clipboard.writeText(input.value);
            if (status) status.textContent = 'Ссылка скопирована';
        } catch {
            input.focus();
            input.select();
            if (status) status.textContent = 'Выделили ссылку. Скопируйте её через Ctrl+C или ⌘C.';
        }
    });

    const dialog = document.getElementById('sharing-confirm');
    if (!dialog) return;
    let pendingForm;
    let confirmed = false;
    let opener;

    document.querySelectorAll('form[data-confirm-title]').forEach((form) => {
        form.addEventListener('submit', (event) => {
            if (confirmed && pendingForm === form) return;
            event.preventDefault();
            pendingForm = form;
            opener = event.submitter;
            dialog.querySelector('#sharing-confirm-title').textContent = form.dataset.confirmTitle;
            dialog.querySelector('#sharing-confirm-message').textContent = form.dataset.confirmMessage;
            dialog.querySelector('[data-confirm-submit]').textContent = form.dataset.confirmAction;
            dialog.showModal();
        });
    });
    dialog.querySelector('[data-confirm-close]').addEventListener('click', () => dialog.close());
    dialog.querySelector('[data-confirm-submit]').addEventListener('click', () => {
        if (!pendingForm) return;
        confirmed = true;
        pendingForm.requestSubmit();
    });
    dialog.addEventListener('close', () => {
        confirmed = false;
        pendingForm = undefined;
        opener?.focus();
    });
})();
