const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("fileInput");
const previewImage = document.getElementById("previewImage");
const uploadForm = document.getElementById("uploadForm");
const resultBox = document.getElementById("resultBox");
const resultText = document.getElementById("resultText");
const detailsBtn = document.getElementById("detailsBtn");

let currentFilename = "";

// Drag & drop + click to upload
dropZone.addEventListener("click", () => fileInput.click());
dropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropZone.classList.add("dragover");
});
dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));
dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropZone.classList.remove("dragover");
  const file = e.dataTransfer.files[0];
  if (file) showPreview(file);
  fileInput.files = e.dataTransfer.files;
});
fileInput.addEventListener("change", () => {
  if (fileInput.files.length > 0) showPreview(fileInput.files[0]);
});

// Show preview
function showPreview(file) {
  const reader = new FileReader();
  reader.onload = (e) => {
    previewImage.src = e.target.result;
    previewImage.classList.remove("hidden");
    dropZone.style.display = "none";
  };
  reader.readAsDataURL(file);
}

// Handle form submission via AJAX
uploadForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  if (fileInput.files.length === 0) return;

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  resultText.innerHTML = "Scanning...";
  resultBox.classList.remove("hidden");

  const response = await fetch("/scan", {
    method: "POST",
    body: formData
  });

  const data = await response.json();
  if (data.error) {
    resultText.innerHTML = data.error;
    detailsBtn.classList.add("hidden");
    return;
  }

  currentFilename = data.filename;
  resultText.innerHTML = `<strong>${data.prediction}</strong>`;
  detailsBtn.href = `/result/${currentFilename}`;
  detailsBtn.classList.remove("hidden");
});
