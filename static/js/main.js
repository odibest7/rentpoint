/**
 * RentPoint front-end behaviour.
 * Kept dependency-free: plain DOM APIs only, no build step required.
 */
document.addEventListener("DOMContentLoaded", function () {
  initMobileNav();
  initAlertDismiss();
  initFormsetAdd();
  initConfirmDialogs();
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
