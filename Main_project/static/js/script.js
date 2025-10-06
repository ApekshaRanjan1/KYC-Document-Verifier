// Upload & Preview logic
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const previewImage = document.getElementById('previewImage');
const progressBar = document.getElementById('progressBar');
const form = document.getElementById('uploadForm');

// Drag over styling
dropZone.addEventListener('dragover', e => {
  e.preventDefault();
  dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
  dropZone.classList.remove('dragover');
});

// Drop handling
dropZone.addEventListener('drop', e => {
  e.preventDefault();
  dropZone.classList.remove('dragover');
  const file = e.dataTransfer.files[0];
  if (file) {
    fileInput.files = e.dataTransfer.files;
    showPreview(file);
  }
});

// Click to browse
dropZone.addEventListener('click', () => fileInput.click());

// File selection
fileInput.addEventListener('change', () => {
  if (fileInput.files[0]) showPreview(fileInput.files[0]);
});

// Preview image
function showPreview(file) {
  const reader = new FileReader();
  reader.onload = e => {
    previewImage.src = e.target.result;
    previewImage.style.display = 'block';
  };
  reader.readAsDataURL(file);
}

// Simulated progress bar on submit
form.addEventListener('submit', () => {
  progressBar.style.display = 'block';
  let width = 0;
  const interval = setInterval(() => {
    if (width >= 100) clearInterval(interval);
    else {
      width += 3;
      progressBar.style.width = width + '%';
    }
  }, 80);
});
