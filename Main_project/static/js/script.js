document.addEventListener("DOMContentLoaded", () => {
  const dropZone = document.getElementById("dropZone");
  const fileInput = document.getElementById("fileInput");
  const previewImage = document.getElementById("previewImage");
  const uploadForm = document.getElementById("uploadForm");
  const resultBox = document.getElementById("resultBox");
  const resultText = document.getElementById("resultText");
  const detailsBtn = document.getElementById("detailsBtn");
  const darkModeToggle = document.getElementById("darkModeToggle");

  let currentFilename = "";

  // ---------------- Drag & drop + click to upload ----------------
  if (dropZone && fileInput) {
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
  }

  // ---------------- Show preview ----------------
  function showPreview(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      previewImage.src = e.target.result;
      previewImage.classList.remove("hidden");
      if (dropZone) dropZone.style.display = "none";
    };
    reader.readAsDataURL(file);
  }

  // ---------------- Handle form submission via AJAX ----------------
  if (uploadForm) {
    uploadForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (!fileInput.files.length) return;

      const formData = new FormData();
      formData.append("file", fileInput.files[0]);

      if (resultText) resultText.innerHTML = "Scanning...";
      if (resultBox) resultBox.classList.remove("hidden");

      try {
        const response = await fetch("/scan", {
          method: "POST",
          body: formData
        });

        const data = await response.json();
        if (data.error) {
          if (resultText) resultText.innerHTML = data.error;
          if (detailsBtn) detailsBtn.classList.add("hidden");
          return;
        }

        currentFilename = data.filename;
        if (resultText) resultText.innerHTML = `<strong>${data.prediction}</strong>`;
        if (detailsBtn) {
          detailsBtn.href = `/result/${currentFilename}`;
          detailsBtn.classList.remove("hidden");
        }
      } catch (err) {
        if (resultText) resultText.innerHTML = "Error scanning the document.";
        if (detailsBtn) detailsBtn.classList.add("hidden");
        console.error(err);
      }
    });
  }

  // ---------------- Load saved dark mode ----------------
  if (localStorage.getItem("darkMode") === "enabled") {
    document.body.classList.add("dark-mode");
    if (darkModeToggle) darkModeToggle.textContent = "☀️ Light Mode";
  }

  // ---------------- Dark Mode Toggle ----------------
  if (darkModeToggle) {
    darkModeToggle.addEventListener("click", () => {
      document.body.classList.toggle("dark-mode");

      if (document.body.classList.contains("dark-mode")) {
        darkModeToggle.textContent = "☀️ Light Mode";
        localStorage.setItem("darkMode", "enabled");
      } else {
        darkModeToggle.textContent = "🌙 Dark Mode";
        localStorage.setItem("darkMode", "disabled");
      }
    });
  }
});
