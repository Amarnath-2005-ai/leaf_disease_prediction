// Plant Disease Recognition - Modern JavaScript
// Perfect browse functionality and side-by-side layout

document.addEventListener("DOMContentLoaded", function () {
  // Get DOM elements
  const uploadArea = document.getElementById("uploadArea");
  const fileInput = document.getElementById("fileInput");
  const filePreview = document.getElementById("filePreview");
  const fileName = document.getElementById("fileName");
  const previewImage = document.getElementById("previewImage");
  const removeBtn = document.getElementById("removeBtn");
  const uploadForm = document.getElementById("uploadForm");
  const loadingOverlay = document.getElementById("loadingOverlay");
  const interactiveSection = document.getElementById("interactiveSection");
  const resultsPanel = document.getElementById("resultsPanel");

  // Debug logging
  console.log("File input found:", fileInput);
  console.log("Upload area found:", uploadArea);

  // Check if results exist on page load
  if (resultsPanel && resultsPanel.innerHTML.trim() !== "") {
    showResults();
  }

  // Browse button click event - PROPER BROWSING
  const browseBtn = document.getElementById("browseBtn");
  console.log("Browse button found:", browseBtn); // Debug log

  if (browseBtn && fileInput) {
    browseBtn.addEventListener("click", function (e) {
      console.log("Browse button clicked!"); // Debug log
      e.preventDefault();
      e.stopPropagation();

      // Try multiple ways to trigger file input
      try {
        fileInput.click();
        console.log("File input clicked successfully");
      } catch (error) {
        console.error("Error clicking file input:", error);
        // Fallback method
        const event = new MouseEvent("click", {
          view: window,
          bubbles: true,
          cancelable: true,
        });
        fileInput.dispatchEvent(event);
      }
    });

    // Also add direct onclick as backup
    browseBtn.onclick = function () {
      console.log("Browse button onclick triggered");
      fileInput.click();
    };
  } else {
    console.error("Browse button or file input not found!", {
      browseBtn,
      fileInput,
    });
  }

  // Upload area click event (only for drag-drop area, not browse button)
  uploadArea.addEventListener("click", function (e) {
    // Only trigger if not clicking the browse button
    if (!e.target.closest(".browse-btn")) {
      e.preventDefault();
      e.stopPropagation();
      fileInput.click();
    }
  });

  // Prevent default drag behaviors
  ["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
    uploadArea.addEventListener(eventName, preventDefaults, false);
    document.body.addEventListener(eventName, preventDefaults, false);
  });

  // Highlight drop area when item is dragged over it
  ["dragenter", "dragover"].forEach((eventName) => {
    uploadArea.addEventListener(eventName, highlight, false);
  });

  ["dragleave", "drop"].forEach((eventName) => {
    uploadArea.addEventListener(eventName, unhighlight, false);
  });

  // Handle dropped files
  uploadArea.addEventListener("drop", handleDrop, false);

  // Handle file input change - PREVENT DOUBLE UPLOADS
  let isProcessingFile = false;
  fileInput.addEventListener("change", function (e) {
    if (isProcessingFile) return; // Prevent double processing

    const files = e.target.files;
    if (files.length > 0) {
      isProcessingFile = true;
      handleFile(files[0]);
      setTimeout(() => {
        isProcessingFile = false;
      }, 500);
    }
  });

  // Remove file button
  removeBtn.addEventListener("click", function (e) {
    e.preventDefault();
    e.stopPropagation();
    resetUpload();
  });

  // Form submission
  uploadForm.addEventListener("submit", function (e) {
    e.preventDefault();

    if (!fileInput.files.length) {
      showNotification("Please select a file first", "error");
      return;
    }

    // Show loading overlay
    loadingOverlay.classList.add("active");

    // Submit the form after a brief delay for UX
    setTimeout(() => {
      uploadForm.submit();
    }, 500);
  });

  // Utility functions
  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  function highlight(e) {
    uploadArea.classList.add("drag-over");
  }

  function unhighlight(e) {
    uploadArea.classList.remove("drag-over");
  }

  function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;

    if (files.length > 0) {
      handleFile(files[0]);
    }
  }

  function handleFile(file) {
    // Validate file
    if (!validateFile(file)) {
      return;
    }

    // Update file input
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    fileInput.files = dataTransfer.files;

    // Show preview
    showPreview(file);
  }

  function validateFile(file) {
    const validTypes = ["image/png", "image/jpeg", "image/jpg"];
    const maxSize = 16 * 1024 * 1024; // 16MB

    if (!validTypes.includes(file.type)) {
      showNotification(
        "Please select a valid image file (PNG, JPG, JPEG)",
        "error",
      );
      return false;
    }

    if (file.size > maxSize) {
      showNotification("File size must be less than 16MB", "error");
      return false;
    }

    return true;
  }

  function showPreview(file) {
    // Update filename
    fileName.textContent = file.name;

    // Create image preview
    const reader = new FileReader();
    reader.onload = function (e) {
      previewImage.src = e.target.result;

      // Hide upload area and show preview
      uploadArea.style.display = "none";
      filePreview.style.display = "block";
    };
    reader.readAsDataURL(file);
  }

  function resetUpload() {
    // Clear file input
    fileInput.value = "";

    // Reset UI
    uploadArea.style.display = "block";
    filePreview.style.display = "none";

    // Clear preview
    previewImage.src = "";
    fileName.textContent = "";
  }

  function showResults() {
    // Show results panel and enable side-by-side layout
    resultsPanel.style.display = "block";
    interactiveSection.classList.add("has-results");

    // Add animation delay for smooth transition
    setTimeout(() => {
      resultsPanel.style.opacity = "1";
    }, 100);
  }

  function showNotification(message, type = "info") {
    // Create notification element
    const notification = document.createElement("div");
    notification.className = "flash-message";
    notification.innerHTML = `
            <i class="bi bi-${type === "error" ? "exclamation-triangle" : "info-circle"}"></i>
            <span>${message}</span>
            <button class="close-btn" onclick="this.parentElement.remove()">
                <i class="bi bi-x"></i>
            </button>
        `;

    // Add to flash messages container or create one
    let flashContainer = document.querySelector(".flash-messages");
    if (!flashContainer) {
      flashContainer = document.createElement("div");
      flashContainer.className = "flash-messages";
      document.body.appendChild(flashContainer);
    }

    flashContainer.appendChild(notification);

    // Auto remove after 5 seconds
    setTimeout(() => {
      if (notification.parentElement) {
        notification.remove();
      }
    }, 5000);
  }
});

// Global functions for template use
function openImageModal(imageSrc) {
  const modalImage = document.getElementById("modalImage");
  modalImage.src = imageSrc;
  const modal = new bootstrap.Modal(document.getElementById("imageModal"));
  modal.show();
}

function resetAnalysis() {
  // Reload the page to reset everything
  window.location.reload();
}

function downloadReport() {
  // Show notification for future feature
  const notification = document.createElement("div");
  notification.className = "flash-message";
  notification.innerHTML = `
        <i class="bi bi-info-circle"></i>
        <span>Report download feature coming soon!</span>
        <button class="close-btn" onclick="this.parentElement.remove()">
            <i class="bi bi-x"></i>
        </button>
    `;

  let flashContainer = document.querySelector(".flash-messages");
  if (!flashContainer) {
    flashContainer = document.createElement("div");
    flashContainer.className = "flash-messages";
    document.body.appendChild(flashContainer);
  }

  flashContainer.appendChild(notification);

  setTimeout(() => {
    if (notification.parentElement) {
      notification.remove();
    }
  }, 3000);
}

// Enhanced error handling
window.addEventListener("error", function (e) {
  console.error("JavaScript error:", e.error);
});

// Page visibility API for cleanup
document.addEventListener("visibilitychange", function () {
  if (document.hidden) {
    // Page is hidden, cleanup any ongoing operations
    const loadingOverlay = document.getElementById("loadingOverlay");
    if (loadingOverlay && loadingOverlay.classList.contains("active")) {
      // If page is hidden during upload, keep loading state
      console.log("Page hidden during operation");
    }
  }
});
