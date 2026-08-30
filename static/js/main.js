/**
 * RentPoint front-end behaviour.
 * Kept dependency-free: plain DOM APIs only, no build step required.
 */
document.addEventListener("DOMContentLoaded", function () {
  initMobileNav();
  initItemGallery();
  initAlertDismiss();
  initFormsetAdd();
  initConfirmDialogs();
  initModalPopups();
  initSelfieCapture();
  initVerificationCardPreviews();
});

function initMobileNav() {
  const toggle = document.querySelector(".nav-toggle");
  const navbar = document.querySelector(".navbar");
  if (!toggle || !navbar) return;

  toggle.addEventListener("click", function () {
    navbar.classList.toggle("nav-open");
    const expanded = navbar.classList.contains("nav-open");
    toggle.setAttribute("aria-expanded", String(expanded));
  });
}

function initItemGallery() {
  const modal = document.querySelector("[data-gallery-modal]");
  const gallery = document.querySelector("[data-item-gallery]");
  if (!modal || !gallery) return;

  const images = [...gallery.querySelectorAll(".item-gallery-thumb img")].map(
    (img) => ({ src: img.src, alt: img.alt }),
  );
  const hero = gallery.querySelector(".item-gallery-hero");
  if (hero && !images.length) {
    const background = hero.style.backgroundImage.match(
      /url\\(["']?(.*?)["']?\\)/,
    );
    if (background)
      images.push({
        src: background[1],
        alt: hero.getAttribute("aria-label") || "Item photo",
      });
  }
  if (!images.length) return;

  const imageEl = modal.querySelector("[data-gallery-image]");
  const caption = modal.querySelector("[data-gallery-caption]");
  let index = 0;

  function render() {
    const current = images[index];
    imageEl.src = current.src;
    imageEl.alt = current.alt;
    caption.textContent = `Photo ${index + 1} of ${images.length}`;
  }
  function openAt(nextIndex) {
    index = (nextIndex + images.length) % images.length;
    render();
    modal.hidden = false;
    modal.classList.add("is-open");
    document.body.style.overflow = "hidden";
  }
  function close() {
    modal.classList.remove("is-open");
    modal.hidden = true;
    document.body.style.overflow = "";
  }
  gallery
    .querySelectorAll("[data-gallery-open]")
    .forEach((button) =>
      button.addEventListener("click", () =>
        openAt(Number(button.dataset.galleryOpen)),
      ),
    );
  modal.querySelector("[data-gallery-close]").addEventListener("click", close);
  modal
    .querySelector("[data-gallery-prev]")
    .addEventListener("click", () => openAt(index - 1));
  modal
    .querySelector("[data-gallery-next]")
    .addEventListener("click", () => openAt(index + 1));
  modal.addEventListener("click", (event) => {
    if (event.target === modal) close();
  });
  document.addEventListener("keydown", (event) => {
    if (!modal.classList.contains("is-open")) return;
    if (event.key === "Escape") close();
    if (event.key === "ArrowLeft") openAt(index - 1);
    if (event.key === "ArrowRight") openAt(index + 1);
  });
}

function initAlertDismiss() {
  document.querySelectorAll("[data-dismiss-alert]").forEach(function (button) {
    button.addEventListener("click", function () {
      const alert = button.closest(".alert");
      if (alert) alert.remove();
    });
  });
}

/**
 * Lets an item owner add another image row to the listing form without a
 * page reload, by cloning the last empty formset row and updating its
 * Django management-form indices.
 */
function initFormsetAdd() {
  const addButton = document.querySelector("[data-add-image-row]");
  if (!addButton) return;

  addButton.addEventListener("click", function () {
    const container = document.querySelector("[data-formset-rows]");
    const totalForms = document.querySelector("#id_images-TOTAL_FORMS");
    if (!container || !totalForms) return;

    const rows = container.querySelectorAll("[data-formset-row]");
    const lastRow = rows[rows.length - 1];
    const newIndex = parseInt(totalForms.value, 10);
    const newRow = lastRow.cloneNode(true);

    newRow.innerHTML = newRow.innerHTML.replace(
      /images-(\d+)-/g,
      "images-" + newIndex + "-",
    );
    newRow.querySelectorAll("input").forEach(function (input) {
      if (input.type === "file") input.value = "";
      if (input.type === "number") input.value = "0";
    });

    container.appendChild(newRow);
    totalForms.value = String(newIndex + 1);
  });
}

function initConfirmDialogs() {
  document.querySelectorAll("[data-confirm]").forEach(function (form) {
    form.addEventListener("submit", function (event) {
      const message = form.getAttribute("data-confirm");
      if (!window.confirm(message)) {
        event.preventDefault();
      }
    });
  });
}

/**
 * Handles smooth pop-up receipt modals across the platform.
 */
function initModalPopups() {
  function openModal(modalId) {
    var modal = document.getElementById(modalId);
    if (!modal) return;
    modal.classList.add("is-open");
    document.body.style.overflow = "hidden";
  }

  function closeModal(modal) {
    if (!modal) return;
    modal.classList.remove("is-open");
    if (!document.querySelector(".modal-backdrop.is-open")) {
      document.body.style.overflow = "";
    }
  }

  // Open modal triggers
  document.querySelectorAll("[data-open-modal]").forEach(function (trigger) {
    trigger.addEventListener("click", function (e) {
      e.preventDefault();
      openModal(trigger.getAttribute("data-open-modal"));
    });
  });

  // Close modal triggers (X button and Close button)
  document.querySelectorAll("[data-close-modal]").forEach(function (btn) {
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      closeModal(btn.closest(".modal-backdrop"));
    });
  });

  // Click backdrop (outside dialog) to close
  document.querySelectorAll(".modal-backdrop").forEach(function (modal) {
    modal.addEventListener("click", function (e) {
      if (e.target === modal) closeModal(modal);
    });
  });

  // ESC key to close
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      var activeModal = document.querySelector(".modal-backdrop.is-open");
      if (activeModal) closeModal(activeModal);
    }
  });

  // Auto-open if the URL hash points to a receipt modal
  if (
    window.location.hash &&
    window.location.hash.startsWith("#receipt-modal-")
  ) {
    openModal(window.location.hash.substring(1));
  }
}

/**
 * Opens the standalone receipt page in a small popup window and
 * auto-triggers the browser print dialog from there.
 *
 * WHY: window.print() called from inside a modal prints the background
 * page where the receipt card is inside .no-print, producing a blank PDF.
 * This function opens the dedicated receipt URL (which has no chrome to hide)
 * so print output is always clean.
 *
 * Template usage:
 *   <button onclick="printReceiptUrl(this)"
 *           data-receipt-url="{% url 'transactions:receipt' transaction.reference %}">
 *     Print Receipt
 *   </button>
 */
function printReceiptUrl(btn) {
  var url = btn.getAttribute("data-receipt-url");
  if (!url) return;

  var popup = window.open(
    url,
    "rp_receipt_print",
    "width=920,height=700,scrollbars=yes,resizable=yes",
  );

  if (!popup) {
    // Popup was blocked by the browser - open in new tab instead
    window.open(url, "_blank");
    return;
  }

  // Wait for the receipt page to fully load before triggering print
  popup.addEventListener("load", function () {
    setTimeout(function () {
      popup.focus();
      popup.print();
    }, 400);
  });
}

/**
 * Live selfie capture for owner identity verification.
 *
 * Uses only the browser's built-in getUserMedia and canvas APIs. The
 * captured frame is placed into a hidden form field; there is no manual
 * upload fallback because verification requires a live selfie.
 *
 * getUserMedia requires a secure context (HTTPS, or localhost during
 * development). Unsupported browsers, unavailable hardware, and denied
 * permissions show an explicit retry state.
 */
function initVerificationCardPreviews() {
  document.querySelectorAll("[data-card-upload]").forEach(function (card) {
    const input = card.querySelector('input[type="file"]');
    const dropzone = card.querySelector("[data-card-dropzone]");
    const selected = card.querySelector("[data-card-selected]");
    const preview = card.querySelector("[data-card-preview]");
    const action = card.querySelector("[data-card-action]");
    const remove = card.querySelector("[data-card-remove]");
    if (!input || !dropzone || !selected || !preview) return;

    function clearSelection() {
      input.value = "";
      preview.hidden = true;
      preview.removeAttribute("src");
      selected.hidden = true;
      dropzone.hidden = false;
      if (action)
        action.textContent = dropzone.htmlFor.includes("front")
          ? "Tap to upload front of NIN card"
          : "Tap to upload back of NIN card";
    }

    input.addEventListener("change", function () {
      const file = input.files && input.files[0];
      if (!file) return clearSelection();
      preview.src = URL.createObjectURL(file);
      preview.hidden = false;
      selected.hidden = false;
      dropzone.hidden = true;
    });

    dropzone.addEventListener("keydown", function (event) {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        input.click();
      }
    });
    if (remove) remove.addEventListener("click", clearSelection);
  });
}

function initSelfieCapture() {
  const widget = document.querySelector("[data-selfie-capture]");
  if (!widget) return;

  const video = widget.querySelector(".selfie-video");
  const canvas = widget.querySelector(".selfie-canvas");
  const resultImg = widget.querySelector(".selfie-result-img");
  const placeholder = widget.querySelector(".selfie-placeholder");
  const statusEl = widget.querySelector(".selfie-status");
  const startBtn = widget.querySelector("[data-selfie-start]");
  const snapBtn = widget.querySelector("[data-selfie-snap]");
  const retakeBtn = widget.querySelector("[data-selfie-retake]");
  const fileInput = document.getElementById("id_selfie_image");
  const errorEl = widget.querySelector(".selfie-error");
  const retryBtn = widget.querySelector("[data-selfie-retry]");

  if (!video || !canvas || !fileInput) return;

  let stream = null;

  function setStatus(text, ok) {
    if (!statusEl) return;
    statusEl.textContent = text;
    statusEl.classList.toggle("selfie-status-ok", Boolean(ok));
  }

  function showOnly(element) {
    [video, resultImg, placeholder].forEach(function (el) {
      if (el) el.hidden = el !== element;
    });
    widget.classList.toggle("is-live", element === video);
    widget.classList.toggle("is-captured", element === resultImg);
  }

  function setButtons(active) {
    startBtn.hidden = active !== startBtn;
    snapBtn.hidden = active !== snapBtn;
    retakeBtn.hidden = active !== retakeBtn;
    retryBtn.hidden = active !== retryBtn;
  }

  function showError(message) {
    stopCamera();
    showOnly(placeholder);
    setButtons(retryBtn);
    errorEl.hidden = false;
    setStatus(message, false);
  }

  async function startCamera() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      showError("Your browser does not support live camera capture.");
      return;
    }
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "user" },
        audio: false,
      });
      video.srcObject = stream;
      showOnly(video);
      errorEl.hidden = true;
      setButtons(snapBtn);
      setStatus("Camera on. Frame your face and capture when ready.", false);
    } catch (error) {
      showError(
        "Camera access is required. Please allow camera access and try again.",
      );
    }
  }

  function stopCamera() {
    if (stream) {
      stream.getTracks().forEach(function (track) {
        track.stop();
      });
      stream = null;
    }
  }

  function captureFrame() {
    const width = video.videoWidth || 480;
    const height = video.videoHeight || 360;
    canvas.width = width;
    canvas.height = height;

    const context = canvas.getContext("2d");
    // Mirror the capture to match the mirrored live preview, so the
    // saved photo looks the way the person actually saw themselves.
    context.translate(width, 0);
    context.scale(-1, 1);
    context.drawImage(video, 0, 0, width, height);

    canvas.toBlob(
      function (blob) {
        if (!blob) {
          setStatus("Could not capture a photo. Please try again.", false);
          return;
        }
        const file = new File([blob], "selfie.jpg", { type: "image/jpeg" });
        const transfer = new DataTransfer();
        transfer.items.add(file);
        fileInput.files = transfer.files;

        resultImg.src = URL.createObjectURL(blob);
        showOnly(resultImg);
        errorEl.hidden = true;
        setButtons(retakeBtn);
        setStatus("Selfie captured. You're ready to submit.", true);

        stopCamera();
      },
      "image/jpeg",
      0.9,
    );
  }

  function retake() {
    fileInput.value = "";
    showOnly(placeholder);
    errorEl.hidden = true;
    setButtons(startBtn);
    setStatus("Take a live selfie to continue.", false);
    startCamera();
  }

  if (startBtn) setButtons(startBtn);
  showOnly(placeholder);
  startBtn.addEventListener("click", startCamera);
  if (snapBtn) snapBtn.addEventListener("click", captureFrame);
  if (retakeBtn) retakeBtn.addEventListener("click", retake);
  retryBtn.addEventListener("click", startCamera);

  window.addEventListener("beforeunload", stopCamera);
}
