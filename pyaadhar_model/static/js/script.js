const fileInput = document.getElementById("file");
const previewImage = document.getElementById("previewImage");
const loader = document.getElementById("loader");
const form = document.getElementById("uploadForm");
const uploadBtn = document.getElementById("uploadBtn");

// Show preview when file selected
fileInput.addEventListener("change", (e) => {
  const file = e.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = (ev) => {
      previewImage.src = ev.target.result;
      previewImage.style.display = "block";
    };
    reader.readAsDataURL(file);
  }
});

// Show loader during upload
form.addEventListener("submit", () => {
  loader.style.display = "block";
  uploadBtn.disabled = true;
});
