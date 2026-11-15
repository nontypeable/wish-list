(() => {
    const uploader = document.querySelector('[data-image-upload]');
    if (!uploader) return;

    const input = uploader.querySelector('input[type="file"]');
    const preview = uploader.querySelector('[data-image-preview]');
    const remove = uploader.querySelector('[data-image-remove]');
    const status = uploader.querySelector('[data-image-status]');
    const filename = uploader.querySelector('[data-image-filename]');
    let previewUrl;
    let dragDepth = 0;

    function clearPreview() {
        filename.textContent = 'Файл не выбран';
        filename.removeAttribute('title');
        if (previewUrl) URL.revokeObjectURL(previewUrl);
        previewUrl = undefined;
        preview.removeAttribute('src');
        preview.hidden = true;
        remove.hidden = true;
    }

    function updatePreview() {
        clearPreview();
        status.textContent = '';
        const file = input.files[0];
        if (!file) return;
        if (!file.type.startsWith('image/')) {
            input.value = '';
            status.textContent = 'Выберите файл изображения.';
            return;
        }
        previewUrl = URL.createObjectURL(file);
        filename.textContent = file.name;
        filename.title = file.name;
        preview.src = previewUrl;
        preview.hidden = false;
        remove.hidden = false;
    }

    function attachFile(file) {
        if (!file.type.startsWith('image/')) {
            status.textContent = 'Выберите файл изображения.';
            return;
        }
        const transfer = new DataTransfer();
        transfer.items.add(file);
        input.files = transfer.files;
        input.dispatchEvent(new Event('change', { bubbles: true }));
    }

    input.addEventListener('change', updatePreview);

    remove.addEventListener('click', () => {
        input.value = '';
        clearPreview();
        status.textContent = 'Картинка убрана.';
        input.focus();
    });

    uploader.addEventListener('dragenter', (event) => {
        event.preventDefault();
        dragDepth += 1;
        uploader.classList.add('image-upload--dragging');
    });

    uploader.addEventListener('dragover', (event) => {
        event.preventDefault();
        event.dataTransfer.dropEffect = 'copy';
    });

    uploader.addEventListener('dragleave', () => {
        dragDepth = Math.max(0, dragDepth - 1);
        if (!dragDepth) uploader.classList.remove('image-upload--dragging');
    });

    uploader.addEventListener('drop', (event) => {
        event.preventDefault();
        dragDepth = 0;
        uploader.classList.remove('image-upload--dragging');
        const files = event.dataTransfer.files;
        if (files.length !== 1) {
            status.textContent = 'Перетащите одну картинку.';
            return;
        }
        attachFile(files[0]);
    });

    document.addEventListener('paste', (event) => {
        const item = Array.from(event.clipboardData?.items || [])
            .find((item) => item.kind === 'file' && item.type.startsWith('image/'));
        const file = item?.getAsFile();
        if (!file) return;
        event.preventDefault();
        attachFile(file);
    });

    input.form.addEventListener('reset', () => {
        clearPreview();
        status.textContent = '';
    });

    window.addEventListener('pagehide', (event) => {
        if (!event.persisted && previewUrl) URL.revokeObjectURL(previewUrl);
    });
})();
