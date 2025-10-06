// static/js/script.js

document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.querySelector('input[type="file"]');
    const uploadButton = document.querySelector('button');

    if (fileInput) {
        fileInput.addEventListener('change', () => {
            const fileName = fileInput.files[0]?.name || 'No file selected';
            uploadButton.textContent = `Upload & Verify (${fileName})`;
        });
    }
});
