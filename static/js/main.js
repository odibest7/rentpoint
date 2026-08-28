/**
 * RentPoint front-end behaviour.
 * Kept dependency-free: plain DOM APIs only, no build step required.
 */
document.addEventListener("DOMContentLoaded", function () {
  initMobileNav();
  initAlertDismiss();
  initFormsetAdd();
  initConfirmDialogs();
  initModalPopups();
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

    newRow.innerHTML = newRow.innerHTML.replace(/images-(\d+)-/g, "images-" + newIndex + "-");
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
  if (window.location.hash && window.location.hash.startsWith("#receipt-modal-")) {
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
    "width=920,height=700,scrollbars=yes,resizable=yes"
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
