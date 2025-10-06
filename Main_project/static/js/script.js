const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("fileInput");
const previewImage = document.getElementById("previewImage");
const scanBtn = document.getElementById("scanBtn");
const resultContainer = document.getElementById("resultContainer");
const predictionText = document.getElementById("predictionText");
const detailsBtn = document.getElementById("detailsBtn");

// --- Dropzone logic ---
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

function showPreview(file) {
  const reader = new FileReader();
  reader.onload = (e) => {
    dropZone.style.display = "none"; // hide box
    previewImage.src = e.target.result;
    previewImage.style.display = "block";
    scanBtn.style.display = "inline-block";
  };
  reader.readAsDataURL(file);
}

// --- Scan document ---
scanBtn.addEventListener("click", async () => {
  if (!fileInput.files.length) {
    alert("Please upload an image first.");
    return;
  }

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  resultContainer.classList.remove("hidden");
  predictionText.textContent = "Scanning document...";

  const response = await fetch("/scan", { method: "POST", body: formData });
  const data = await response.json();

  if (data.error) {
    predictionText.textContent = `Error: ${data.error}`;
  } else {
    predictionText.innerHTML = `Detected: <strong>${data.prediction}</strong>`;
    detailsBtn.href = `/result/${data.filename}`;
    detailsBtn.classList.remove("hidden");
  }
});
