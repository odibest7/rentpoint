/**
 * RentPoint front-end behaviour.
 * Kept dependency-free: plain DOM APIs only, no build step required.
 */
document.addEventListener("DOMContentLoaded", function () {
  initPasswordVisibilityToggles();
  initMobileNav();
  initAccountMenu();
  initItemGallery();
  initAlertDismiss();
  initPhotoUploader();
  initConfirmDialogs();
  initModalPopups();
  initSelfieCapture();
  initVerificationCardPreviews();
  initItemDetailCalculator();
  initStartRentalCalculator();
  initOwnerPricingSimulator();
});

function initPasswordVisibilityToggles() {
  document
    .querySelectorAll('input[type="password"].password-toggle-input')
    .forEach(function (input) {
      if (
        input.parentElement &&
        input.parentElement.classList.contains("password-toggle-wrap")
      ) {
        return;
      }

      const wrap = document.createElement("div");
      wrap.className = "password-toggle-wrap";

      const button = document.createElement("button");
      button.type = "button";
      button.className = "password-toggle-button";
      button.setAttribute("aria-label", "Show password");
      button.setAttribute("aria-pressed", "false");
      button.title = "Show password";
      button.innerHTML = `
      <svg class="password-toggle-icon password-toggle-icon-show" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
        <path d="M1.5 12S5.25 5.25 12 5.25 22.5 12 22.5 12 18.75 18.75 12 18.75 1.5 12 1.5 12Z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="12" cy="12" r="3.15" fill="none" stroke="currentColor" stroke-width="1.8"/>
      </svg>
      <svg class="password-toggle-icon password-toggle-icon-hide" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
        <path d="M3 3L21 21" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
        <path d="M10.58 10.58A2 2 0 0 1 13.42 13.42" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
        <path d="M9.88 4.22A9.54 9.54 0 0 1 12 4.5c6.75 0 10.5 7.5 10.5 7.5a17.86 17.86 0 0 1-4.2 5.23M6.2 6.2A17.75 17.75 0 0 0 1.5 12S5.25 18.75 12 18.75A9.37 9.37 0 0 0 15.48 18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    `;

      button.addEventListener("click", function (event) {
        event.preventDefault();
        event.stopPropagation();

        const start = input.selectionStart;
        const end = input.selectionEnd;
        const isHidden = input.type === "password";

        input.type = isHidden ? "text" : "password";
        button.setAttribute(
          "aria-label",
          isHidden ? "Hide password" : "Show password",
        );
        button.setAttribute("aria-pressed", String(isHidden));
        button.title = isHidden ? "Hide password" : "Show password";
        button.classList.toggle("is-visible", isHidden);

        requestAnimationFrame(function () {
          input.focus();
          if (typeof start === "number" && typeof end === "number") {
            input.setSelectionRange(start, end);
          }
        });
      });

      input.parentNode.insertBefore(wrap, input);
      wrap.appendChild(input);
      wrap.appendChild(button);
      input.setAttribute("data-password-toggle-bound", "true");
    });
}

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

function initAccountMenu() {
  const wrap = document.querySelector(".user-menu-wrap");
  if (!wrap) return;

  const trigger = wrap.querySelector(".user-menu-trigger");
  if (!trigger) return;

  function setOpen(open) {
    wrap.classList.toggle("is-open", open);
    trigger.setAttribute("aria-expanded", String(open));
  }

  trigger.addEventListener("click", function (event) {
    event.stopPropagation();
    setOpen(!wrap.classList.contains("is-open"));
  });

  document.addEventListener("click", function (event) {
    if (!wrap.contains(event.target)) {
      setOpen(false);
    }
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      setOpen(false);
    }
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
 * Comprehensive item photo uploader:
 * - Instant client-side previews before saving (ObjectURL)
 * - Drag-and-drop file upload support
 * - Dynamic addition of photo slots with Django management-form index syncing
 * - Clear cover photo vs secondary photo badges
 * - Smooth removal & replace actions
 */
function initPhotoUploader() {
  const container = document.querySelector("[data-photo-grid]");
  const totalForms = document.querySelector("#id_images-TOTAL_FORMS");
  const maxFormsInput = document.querySelector("#id_images-MAX_NUM_FORMS");
  const maxForms = maxFormsInput ? parseInt(maxFormsInput.value, 10) : 8;
  const addButton = document.querySelector("[data-add-photo-btn], [data-add-image-row]");

  if (!container) return;

  function updateCardBadges() {
    const cards = container.querySelectorAll(".photo-upload-card");
    let activeIndex = 0;

    cards.forEach(function (card) {
      const isDeleted = card.querySelector('input[type="checkbox"][name$="-DELETE"]:checked');
      if (isDeleted) return;

      const coverBadge = card.querySelector(".photo-badge-cover, .photo-badge-index");
      if (coverBadge) {
        if (activeIndex === 0) {
          coverBadge.className = "photo-badge-cover";
          coverBadge.textContent = "Cover Photo";
        } else {
          coverBadge.className = "photo-badge-index";
          coverBadge.textContent = "Photo #" + (activeIndex + 1);
        }
      }
      activeIndex++;
    });

    const limitInfo = document.querySelector("[data-photo-limit-info]");
    if (limitInfo) {
      limitInfo.textContent = `${cards.length} of ${maxForms} photos allowed`;
    }
  }

  function bindCardEvents(card) {
    const fileInput = card.querySelector('input[type="file"]');
    const dropzone = card.querySelector("[data-dropzone]");
    const previewContainer = card.querySelector(".photo-live-preview");
    const positionInput = card.querySelector('input[name$="-position"]');

    if (!fileInput) return;

    // Handle Drag and Drop
    ["dragenter", "dragover"].forEach(function (eventName) {
      card.addEventListener(eventName, function (e) {
        e.preventDefault();
        e.stopPropagation();
        card.style.borderColor = "var(--color-accent-teal)";
        card.style.backgroundColor = "var(--color-accent-teal-subtle)";
      });
    });

    ["dragleave", "drop"].forEach(function (eventName) {
      card.addEventListener(eventName, function (e) {
        e.preventDefault();
        e.stopPropagation();
        card.style.borderColor = "";
        card.style.backgroundColor = "";
      });
    });

    card.addEventListener("drop", function (e) {
      if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        fileInput.files = e.dataTransfer.files;
        handleFileSelect(e.dataTransfer.files[0]);
      }
    });

    // Handle standard file selection
    fileInput.addEventListener("change", function () {
      if (fileInput.files && fileInput.files[0]) {
        handleFileSelect(fileInput.files[0]);
      }
    });

    function handleFileSelect(file) {
      if (!file.type.startsWith("image/")) {
        alert("Please select a valid image file (JPG, PNG, WEBP).");
        return;
      }

      const imageUrl = URL.createObjectURL(file);
      card.classList.add("has-photo");
      if (dropzone) dropzone.style.display = "none";

      if (previewContainer) {
        previewContainer.style.display = "block";
        previewContainer.innerHTML = `
          <div class="photo-preview-wrap">
            <img src="${imageUrl}" class="photo-preview-img" alt="Selected photo">
            <span class="photo-badge-index">Preview</span>
          </div>
          <div class="photo-card-actions">
            <span class="photo-card-filename" title="${file.name}">${file.name}</span>
            <button type="button" class="photo-action-btn photo-btn-remove" data-action="remove-preview">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              <span>Remove</span>
            </button>
          </div>
        `;

        const removeBtn = previewContainer.querySelector('[data-action="remove-preview"]');
        if (removeBtn) {
          removeBtn.addEventListener("click", function (e) {
            e.preventDefault();
            e.stopPropagation();
            fileInput.value = "";
            card.classList.remove("has-photo");
            if (dropzone) dropzone.style.display = "";
            previewContainer.innerHTML = "";
            previewContainer.style.display = "none";
            updateCardBadges();
          });
        }
      }

      updateCardBadges();
    }
  }

  // Bind existing cards
  container.querySelectorAll(".photo-upload-card").forEach(bindCardEvents);
  updateCardBadges();

  // Add another photo button
  if (addButton && totalForms) {
    addButton.addEventListener("click", function () {
      const currentCount = container.querySelectorAll(".photo-upload-card").length;
      if (currentCount >= maxForms) {
        alert(`You can upload a maximum of ${maxForms} photos per listing.`);
        return;
      }

      const newIndex = parseInt(totalForms.value, 10);
      const newCard = document.createElement("div");
      newCard.className = "photo-upload-card";
      newCard.setAttribute("data-photo-card", "");
      newCard.setAttribute("data-form-index", String(newIndex));

      newCard.innerHTML = `
        <input type="hidden" name="images-${newIndex}-id" id="id_images-${newIndex}-id">
        <input type="hidden" name="images-${newIndex}-position" value="${newIndex}" id="id_images-${newIndex}-position" class="photo-position-input">
        <div class="photo-dropzone-content" data-dropzone>
          <div class="photo-dropzone-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
              <circle cx="12" cy="13" r="4"/>
            </svg>
          </div>
          <div class="photo-dropzone-label">Upload Photo</div>
          <div class="photo-dropzone-hint">Click or drag &amp; drop</div>
        </div>
        <input type="file" name="images-${newIndex}-image" accept="image/*" class="photo-file-input" id="id_images-${newIndex}-image">
        <div class="photo-live-preview" style="display:none; width:100%;"></div>
      `;

      container.appendChild(newCard);
      totalForms.value = String(newIndex + 1);

      bindCardEvents(newCard);
      updateCardBadges();

      // Trigger file picker on new card immediately for fluid UX
      const newFileInput = newCard.querySelector('input[type="file"]');
      if (newFileInput) newFileInput.click();
    });
  }
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

/**
 * Formats a numeric value into a clean Naira currency string with commas.
 * e.g. 150000 -> "150,000.00" or "150,000"
 */
function formatNaira(amount, includeDecimals = false) {
  const num = Number(amount) || 0;
  return num.toLocaleString("en-NG", {
    minimumFractionDigits: includeDecimals ? 2 : 0,
    maximumFractionDigits: includeDecimals ? 2 : 0,
  });
}

/**
 * Smart pluralizer for item names.
 * Accurately infers singular vs plural forms so:
 *  - "Spoon", 1 -> "Spoon"
 *  - "Spoon", 2 -> "Spoons"
 *  - "Plastic Chair", 2 -> "Plastic Chairs"
 *  - "Canopy", 5 -> "Canopies"
 *  - "Dish", 2 -> "Dishes"
 *  - "Glass", 4 -> "Glasses"
 *  - "Box", 3 -> "Boxes"
 */
function pluralizeItemName(rawName, count = 1) {
  if (!rawName || typeof rawName !== "string") {
    return count === 1 ? "item" : "items";
  }

  const trimmed = rawName.trim();
  if (!trimmed) return count === 1 ? "item" : "items";

  // Check if name has extra specs in parentheses, e.g. "White Plastic Chairs (set of 50)"
  const parenMatch = trimmed.match(/^(.*?)\s*(\([^)]+\))$/);
  let coreName = trimmed;
  let suffix = "";
  if (parenMatch) {
    coreName = parenMatch[1].trim();
    suffix = " " + parenMatch[2].trim();
  }

  const words = coreName.split(/\s+/);
  const lastWord = words[words.length - 1];
  const prefixWords = words.slice(0, words.length - 1).join(" ");

  // Normalizer: if the word is already plural, find its singular stem
  let singularStem = lastWord;
  const lowerLast = lastWord.toLowerCase();

  if (lowerLast.endsWith("ies") && lowerLast.length > 3) {
    singularStem = lastWord.slice(0, -3) + (lastWord.endsWith("IES") ? "Y" : "y");
  } else if (lowerLast.endsWith("ves") && lowerLast.length > 3) {
    singularStem = lastWord.slice(0, -3) + (lastWord.endsWith("VES") ? "FE" : "fe");
  } else if (
    lowerLast.endsWith("es") &&
    (lowerLast.endsWith("shes") ||
      lowerLast.endsWith("ches") ||
      lowerLast.endsWith("xes") ||
      lowerLast.endsWith("sses") ||
      lowerLast.endsWith("zes"))
  ) {
    singularStem = lastWord.slice(0, -2);
  } else if (
    lowerLast.endsWith("s") &&
    !lowerLast.endsWith("ss") &&
    !lowerLast.endsWith("us") &&
    !lowerLast.endsWith("is") &&
    lowerLast.length > 2
  ) {
    singularStem = lastWord.slice(0, -1);
  }

  let finalNoun = "";
  if (count === 1) {
    finalNoun = singularStem;
  } else {
    // Generate proper plural from singularStem
    const lowerStem = singularStem.toLowerCase();
    if (lowerStem.endsWith("y") && !/[aeiou]y$/i.test(lowerStem)) {
      finalNoun =
        singularStem.slice(0, -1) +
        (singularStem === singularStem.toUpperCase() ? "IES" : "ies");
    } else if (
      lowerStem.endsWith("s") ||
      lowerStem.endsWith("sh") ||
      lowerStem.endsWith("ch") ||
      lowerStem.endsWith("x") ||
      lowerStem.endsWith("z")
    ) {
      finalNoun =
        singularStem +
        (singularStem === singularStem.toUpperCase() ? "ES" : "es");
    } else if (lowerStem.endsWith("fe")) {
      finalNoun =
        singularStem.slice(0, -2) +
        (singularStem === singularStem.toUpperCase() ? "VES" : "ves");
    } else if (lowerStem.endsWith("f") && !lowerStem.endsWith("ff")) {
      finalNoun =
        singularStem.slice(0, -1) +
        (singularStem === singularStem.toUpperCase() ? "VES" : "ves");
    } else {
      finalNoun =
        singularStem +
        (singularStem === singularStem.toUpperCase() ? "S" : "s");
    }
  }

  const fullForm = prefixWords ? `${prefixWords} ${finalNoun}` : finalNoun;
  return `${fullForm}${suffix}`;
}

/**
 * Interactive Item Detail Rental Calculator
 * Computes: Unit Price × Quantity × Duration (Days) in real time.
 * Dynamically uses the exact item name (e.g. "1 Spoon", "2 Spoons", "5 Spoons").
 */
function initItemDetailCalculator() {
  const calcSidebar = document.getElementById("itemRentalCalculator");
  if (!calcSidebar) return;

  const itemName = calcSidebar.dataset.itemName || "Item";
  const unitPrice = parseFloat(calcSidebar.dataset.unitPrice) || 0;
  const maxStock = parseInt(calcSidebar.dataset.maxStock, 10) || 1;
  const baseRentUrl = calcSidebar.dataset.baseRentUrl || "";
  const loginUrl = calcSidebar.dataset.loginUrl || "";

  const qtyLabel = document.getElementById("calcQtyLabel");
  const stockHint = document.getElementById("calcStockHint");
  const qtyInput = document.getElementById("calcQtyInput");
  const qtyMinus = document.getElementById("calcQtyMinus");
  const qtyPlus = document.getElementById("calcQtyPlus");
  const qtyChips = document.querySelectorAll("#calcQtyChips .calc-chip");

  const durInput = document.getElementById("calcDurationInput");
  const durMinus = document.getElementById("calcDurationMinus");
  const durPlus = document.getElementById("calcDurationPlus");
  const durChips = document.querySelectorAll("#calcDurationChips .calc-chip");

  const formulaQty = document.getElementById("formulaQty");
  const formulaDur = document.getElementById("formulaDuration");
  const subtotalEl = document.getElementById("calcSubtotal");
  const grandTotalEl = document.getElementById("calcGrandTotal");
  const rentBtn = document.getElementById("calcRentButton");

  if (!qtyInput || !durInput) return;

  // Initialize quick chips with actual item names
  if (qtyChips) {
    qtyChips.forEach((chip) => {
      const chipVal = parseInt(chip.dataset.qty, 10);
      if (chipVal === maxStock && maxStock > 10) {
        chip.textContent = `All (${chipVal} ${pluralizeItemName(itemName, chipVal)})`;
      } else if (chipVal) {
        chip.textContent = `${chipVal} ${pluralizeItemName(itemName, chipVal)}`;
      }
    });
  }

  if (stockHint) {
    stockHint.textContent = `Max: ${maxStock} ${pluralizeItemName(itemName, maxStock)}`;
  }

  if (qtyLabel) {
    qtyLabel.textContent = `Quantity (${pluralizeItemName(itemName, 2)})`;
  }

  function recalculate() {
    let qty = parseInt(qtyInput.value, 10);
    if (isNaN(qty) || qty < 1) qty = 1;
    if (qty > maxStock) qty = maxStock;
    qtyInput.value = qty;

    let dur = parseInt(durInput.value, 10);
    if (isNaN(dur) || dur < 1) dur = 1;
    if (dur > 365) dur = 365;
    durInput.value = dur;

    const total = unitPrice * qty * dur;
    const nameWithCount = pluralizeItemName(itemName, qty);

    if (formulaQty) {
      formulaQty.textContent = `${qty} ${nameWithCount}`;
    }
    if (formulaDur) {
      formulaDur.textContent = `${dur} ${dur === 1 ? "day" : "days"}`;
    }
    if (subtotalEl) {
      subtotalEl.textContent = `₦${formatNaira(total, true)}`;
    }
    if (grandTotalEl) {
      grandTotalEl.textContent = `₦${formatNaira(total, true)}`;
      grandTotalEl.classList.remove("calc-pulse-anim");
      void grandTotalEl.offsetWidth;
      grandTotalEl.classList.add("calc-pulse-anim");
    }

    // Sync button href and label
    if (rentBtn) {
      const spanEl = rentBtn.querySelector("span");
      if (spanEl) {
        if (rentBtn.getAttribute("href")?.includes("/login/")) {
          spanEl.textContent = `Log in to Rent ${qty} ${nameWithCount} &rarr;`;
        } else {
          spanEl.textContent = `Rent ${qty} ${nameWithCount} &rarr;`;
        }
      }

      if (baseRentUrl) {
        const url = new URL(baseRentUrl, window.location.origin);
        url.searchParams.set("quantity", qty);
        url.searchParams.set("duration", dur);

        if (loginUrl && rentBtn.getAttribute("href")?.includes("/login/")) {
          const nextTarget = `${url.pathname}?${url.searchParams.toString()}`;
          const loginTarget = new URL(loginUrl, window.location.origin);
          loginTarget.searchParams.set("next", nextTarget);
          rentBtn.href = loginTarget.pathname + loginTarget.search;
        } else {
          rentBtn.href = url.pathname + url.search;
        }
      }
    }

    // Update active states for chips
    if (qtyChips) {
      qtyChips.forEach((chip) => {
        const chipVal = parseInt(chip.dataset.qty, 10);
        chip.classList.toggle("is-active", chipVal === qty);
      });
    }

    if (durChips) {
      durChips.forEach((chip) => {
        const chipVal = parseInt(chip.dataset.days, 10);
        chip.classList.toggle("is-active", chipVal === dur);
      });
    }
  }

  // Stepper handlers
  if (qtyMinus) {
    qtyMinus.addEventListener("click", () => {
      let current = parseInt(qtyInput.value, 10) || 1;
      if (current > 1) {
        qtyInput.value = current - 1;
        recalculate();
      }
    });
  }

  if (qtyPlus) {
    qtyPlus.addEventListener("click", () => {
      let current = parseInt(qtyInput.value, 10) || 1;
      if (current < maxStock) {
        qtyInput.value = current + 1;
        recalculate();
      }
    });
  }

  if (durMinus) {
    durMinus.addEventListener("click", () => {
      let current = parseInt(durInput.value, 10) || 1;
      if (current > 1) {
        durInput.value = current - 1;
        recalculate();
      }
    });
  }

  if (durPlus) {
    durPlus.addEventListener("click", () => {
      let current = parseInt(durInput.value, 10) || 1;
      if (current < 365) {
        durInput.value = current + 1;
        recalculate();
      }
    });
  }

  qtyInput.addEventListener("input", recalculate);
  durInput.addEventListener("input", recalculate);
  qtyInput.addEventListener("change", recalculate);
  durInput.addEventListener("change", recalculate);

  // Quick Chips Handlers
  if (qtyChips) {
    qtyChips.forEach((chip) => {
      chip.addEventListener("click", () => {
        const val = parseInt(chip.dataset.qty, 10);
        if (val) {
          qtyInput.value = Math.min(val, maxStock);
          recalculate();
        }
      });
    });
  }

  if (durChips) {
    durChips.forEach((chip) => {
      chip.addEventListener("click", () => {
        const val = parseInt(chip.dataset.days, 10);
        if (val) {
          durInput.value = val;
          recalculate();
        }
      });
    });
  }

  // Initial calculation run
  recalculate();
}

/**
 * Start Rental Checkout Page Live Calculation
 * Syncs form inputs (quantity, duration in days, delivery preference) with
 * the sticky live order summary card using real item name.
 */
function initStartRentalCalculator() {
  const summaryCard = document.getElementById("startRentalSummary");
  if (!summaryCard) return;

  const itemName = summaryCard.dataset.itemName || "Item";
  const unitPrice = parseFloat(summaryCard.dataset.unitPrice) || 0;
  const maxStock = parseInt(summaryCard.dataset.maxStock, 10) || 1;
  const locationName = summaryCard.dataset.location || "Owner Location";

  const startQtyLabel = document.getElementById("startQtyLabel");
  const qtyInput = document.getElementById("id_quantity");
  const durInput = document.getElementById("id_duration");
  const deliverySelect = document.getElementById("id_delivery_option");
  const deliveryGroup = document.getElementById("deliveryAddressGroup");
  const submitBtn = document.getElementById("submitRentalBtn");

  const qtyMinus = document.getElementById("startQtyMinus");
  const qtyPlus = document.getElementById("startQtyPlus");
  const durMinus = document.getElementById("startDurMinus");
  const durPlus = document.getElementById("startDurPlus");

  const sumQtyVal = document.getElementById("sumQtyVal");
  const sumDurVal = document.getElementById("sumDurVal");
  const sumQtyDisplay = document.getElementById("sumQtyDisplay");
  const sumDurDisplay = document.getElementById("sumDurDisplay");
  const sumDeliveryDisplay = document.getElementById("sumDeliveryDisplay");
  const sumSubtotal = document.getElementById("sumSubtotal");
  const sumGrandTotal = document.getElementById("sumGrandTotal");

  if (!qtyInput || !durInput) return;

  if (startQtyLabel) {
    startQtyLabel.textContent = `Quantity (${pluralizeItemName(itemName, 2)} Needed)`;
  }

  function updateSummary() {
    let qty = parseInt(qtyInput.value, 10);
    if (isNaN(qty) || qty < 1) qty = 1;
    if (qty > maxStock) qty = maxStock;

    let dur = parseInt(durInput.value, 10);
    if (isNaN(dur) || dur < 1) dur = 1;
    if (dur > 365) dur = 365;

    const total = unitPrice * qty * dur;
    const nameWithCount = pluralizeItemName(itemName, qty);

    if (sumQtyVal) {
      sumQtyVal.textContent = qty;
      const tagEl = sumQtyVal.parentElement?.querySelector(".formula-tag");
      if (tagEl) {
        tagEl.textContent = nameWithCount.toLowerCase();
      }
    }
    if (sumDurVal) sumDurVal.textContent = dur;

    if (sumQtyDisplay) {
      sumQtyDisplay.textContent = `${qty} ${nameWithCount}`;
    }
    if (sumDurDisplay) {
      sumDurDisplay.textContent = `${dur} ${dur === 1 ? "day" : "days"}`;
    }

    if (sumSubtotal) sumSubtotal.textContent = `₦${formatNaira(total, true)}`;
    if (sumGrandTotal) {
      sumGrandTotal.textContent = `₦${formatNaira(total, true)}`;
      sumGrandTotal.classList.remove("calc-pulse-anim");
      void sumGrandTotal.offsetWidth;
      sumGrandTotal.classList.add("calc-pulse-anim");
    }

    if (submitBtn) {
      const spanEl = submitBtn.querySelector("span");
      if (spanEl) {
        spanEl.textContent = `Proceed to Review & Pay for ${qty} ${nameWithCount} &rarr;`;
      }
    }

    if (deliverySelect && sumDeliveryDisplay) {
      const isDelivery = deliverySelect.value === "delivery";
      if (isDelivery) {
        sumDeliveryDisplay.textContent = "Direct Delivery";
        if (deliveryGroup) deliveryGroup.style.display = "block";
      } else {
        sumDeliveryDisplay.textContent = `Self-Pickup in ${locationName}`;
        if (deliveryGroup) deliveryGroup.style.display = "block";
      }
    }
  }

  // Stepper buttons
  if (qtyMinus) {
    qtyMinus.addEventListener("click", () => {
      let current = parseInt(qtyInput.value, 10) || 1;
      if (current > 1) {
        qtyInput.value = current - 1;
        updateSummary();
      }
    });
  }

  if (qtyPlus) {
    qtyPlus.addEventListener("click", () => {
      let current = parseInt(qtyInput.value, 10) || 1;
      if (current < maxStock) {
        qtyInput.value = current + 1;
        updateSummary();
      }
    });
  }

  if (durMinus) {
    durMinus.addEventListener("click", () => {
      let current = parseInt(durInput.value, 10) || 1;
      if (current > 1) {
        durInput.value = current - 1;
        updateSummary();
      }
    });
  }

  if (durPlus) {
    durPlus.addEventListener("click", () => {
      let current = parseInt(durInput.value, 10) || 1;
      if (current < 365) {
        durInput.value = current + 1;
        updateSummary();
      }
    });
  }

  qtyInput.addEventListener("input", updateSummary);
  durInput.addEventListener("input", updateSummary);
  qtyInput.addEventListener("change", updateSummary);
  durInput.addEventListener("change", updateSummary);

  if (deliverySelect) {
    deliverySelect.addEventListener("change", updateSummary);
  }

  // Initial update
  updateSummary();
}

/**
 * Item Owner Listing Creation & Edit Pricing Simulator
 * Dynamically reflects the actual item name typed by the owner (e.g. Spoon -> 2 Spoons).
 */
function initOwnerPricingSimulator() {
  const simulator = document.getElementById("ownerPricingSimulator");
  if (!simulator) return;

  const nameInput = document.getElementById("id_name");
  const priceInput = document.getElementById("id_rental_price");
  const qtyAvailInput = document.getElementById("id_quantity_available");

  const simQtyLabel = document.querySelector('label[for="simQtyInput"]');
  const simQtyInput = document.getElementById("simQtyInput");
  const simQtyMinus = document.getElementById("simQtyMinus");
  const simQtyPlus = document.getElementById("simQtyPlus");

  const simDurInput = document.getElementById("simDurInput");
  const simDurMinus = document.getElementById("simDurMinus");
  const simDurPlus = document.getElementById("simDurPlus");

  const formulaText = document.getElementById("simFormulaText");
  const customerTotalEl = document.getElementById("simCustomerTotal");
  const ownerPayoutEl = document.getElementById("simOwnerPayout");

  if (!priceInput || !simQtyInput || !simDurInput) return;

  function updateSimulation() {
    const rawName = (nameInput?.value || "").trim() || "Item";
    const rate = parseFloat(priceInput.value) || 0;
    let simQty = parseInt(simQtyInput.value, 10) || 1;
    let simDur = parseInt(simDurInput.value, 10) || 1;

    if (simQty < 1) simQty = 1;
    if (simDur < 1) simDur = 1;

    const customerTotal = rate * simQty * simDur;
    const ownerPayout = customerTotal * 0.95; // 5% platform commission
    const nameWithCount = pluralizeItemName(rawName, simQty);

    if (simQtyLabel) {
      simQtyLabel.textContent = `Simulate Customer Quantity (${pluralizeItemName(rawName, 2)}):`;
    }

    if (formulaText) {
      formulaText.innerHTML = `
        <span class="sim-rate">₦${formatNaira(rate, true)}</span> &times; 
        <span class="sim-qty">${simQty} ${nameWithCount}</span> &times; 
        <span class="sim-days">${simDur} ${simDur === 1 ? "day" : "days"}</span>
      `;
    }

    if (customerTotalEl) {
      customerTotalEl.textContent = `₦${formatNaira(customerTotal, true)}`;
    }
    if (ownerPayoutEl) {
      ownerPayoutEl.textContent = `₦${formatNaira(ownerPayout, true)}`;
    }
  }

  if (simQtyMinus) {
    simQtyMinus.addEventListener("click", () => {
      let current = parseInt(simQtyInput.value, 10) || 1;
      if (current > 1) {
        simQtyInput.value = current - 1;
        updateSimulation();
      }
    });
  }

  if (simQtyPlus) {
    simQtyPlus.addEventListener("click", () => {
      let current = parseInt(simQtyInput.value, 10) || 1;
      simQtyInput.value = current + 1;
      updateSimulation();
    });
  }

  if (simDurMinus) {
    simDurMinus.addEventListener("click", () => {
      let current = parseInt(simDurInput.value, 10) || 1;
      if (current > 1) {
        simDurInput.value = current - 1;
        updateSimulation();
      }
    });
  }

  if (simDurPlus) {
    simDurPlus.addEventListener("click", () => {
      let current = parseInt(simDurInput.value, 10) || 1;
      simDurInput.value = current + 1;
      updateSimulation();
    });
  }

  if (nameInput) {
    nameInput.addEventListener("input", updateSimulation);
    nameInput.addEventListener("change", updateSimulation);
  }

  priceInput.addEventListener("input", updateSimulation);
  priceInput.addEventListener("change", updateSimulation);
  simQtyInput.addEventListener("input", updateSimulation);
  simDurInput.addEventListener("input", updateSimulation);

  if (qtyAvailInput) {
    qtyAvailInput.addEventListener("change", () => {
      const maxVal = parseInt(qtyAvailInput.value, 10);
      if (maxVal && maxVal > 0 && parseInt(simQtyInput.value, 10) > maxVal) {
        simQtyInput.value = maxVal;
      }
      updateSimulation();
    });
  }

  // Initial run
  updateSimulation();
}
