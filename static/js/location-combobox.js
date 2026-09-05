/**
 * location-combobox.js
 * Searchable combobox for the RentPoint catalogue location filter.
 * Fetches zone options + live item counts from /listings/locations/?q=...
 */
(function () {
  'use strict';

  function initLocationCombobox(wrap) {
    const input   = wrap.querySelector('[data-combobox="location"]');
    const popover = wrap.querySelector('.location-combobox-popover');
    if (!input || !popover) return;

    const apiUrl       = wrap.dataset.apiUrl;
    const initialValue = wrap.dataset.initialValue || '';
    let debounceTimer  = null;
    let focusedIndex   = -1;
    let currentOptions = [];

    // Pre-fill display text from URL param
    if (initialValue) {
      input.value = initialValue;
    }

    // ── Fetch & render ─────────────────────────────────────────────────────
    function fetchOptions(q) {
      const url = apiUrl + (q ? '?q=' + encodeURIComponent(q) : '');
      fetch(url)
        .then(r => r.json())
        .then(data => renderPopover(data.results, q))
        .catch(() => renderPopover([], q));
    }

    function renderPopover(results, q) {
      currentOptions = results;
      focusedIndex   = -1;
      popover.innerHTML = '';

      if (results.length === 0) {
        const empty = document.createElement('div');
        empty.className = 'location-combobox-empty';
        empty.textContent = q
          ? 'No items available in this area yet.'
          : 'No locations found.';
        popover.appendChild(empty);
      } else {
        results.forEach(function (opt, idx) {
          const row = document.createElement('div');
          row.className   = 'location-combobox-option';
          row.dataset.value = opt.value;
          row.setAttribute('role', 'option');
          row.setAttribute('aria-selected', 'false');

          const name = document.createElement('span');
          name.className   = 'option-name';
          name.textContent = opt.label;

          const count = document.createElement('span');
          count.className   = 'option-count';
          count.textContent = opt.count + (opt.count === 1 ? ' item' : ' items');

          row.appendChild(name);
          row.appendChild(count);

          row.addEventListener('mousedown', function (e) {
            e.preventDefault(); // prevent blur before click registers
            selectOption(opt);
          });

          popover.appendChild(row);
        });
      }

      openPopover();
    }

    // ── Selection ──────────────────────────────────────────────────────────
    function selectOption(opt) {
      input.value = opt.value;
      closePopover();
      input.focus();
    }

    // ── Popover visibility ─────────────────────────────────────────────────
    function openPopover() {
      popover.classList.add('is-open');
    }

    function closePopover() {
      popover.classList.remove('is-open');
      focusedIndex = -1;
      highlightOption();
    }

    // ── Keyboard navigation ────────────────────────────────────────────────
    function highlightOption() {
      const opts = popover.querySelectorAll('.location-combobox-option');
      opts.forEach(function (el, i) {
        el.classList.toggle('is-focused', i === focusedIndex);
      });
    }

    input.addEventListener('keydown', function (e) {
      const opts = popover.querySelectorAll('.location-combobox-option');
      if (!popover.classList.contains('is-open')) return;

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        focusedIndex = Math.min(focusedIndex + 1, opts.length - 1);
        highlightOption();
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        focusedIndex = Math.max(focusedIndex - 1, 0);
        highlightOption();
      } else if (e.key === 'Enter' && focusedIndex >= 0) {
        e.preventDefault();
        const focused = opts[focusedIndex];
        if (focused && currentOptions[focusedIndex]) {
          selectOption(currentOptions[focusedIndex]);
        }
      } else if (e.key === 'Escape') {
        closePopover();
      }
    });

    // ── Input events ───────────────────────────────────────────────────────
    input.addEventListener('input', function () {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(function () {
        fetchOptions(input.value.trim());
      }, 220);
    });

    input.addEventListener('focus', function () {
      fetchOptions(input.value.trim());
    });

    input.addEventListener('blur', function () {
      // Small delay to allow mousedown on option to fire first
      setTimeout(closePopover, 150);
    });

    // ── Click outside ──────────────────────────────────────────────────────
    document.addEventListener('click', function (e) {
      if (!wrap.contains(e.target)) {
        closePopover();
      }
    });
  }

  // ── Boot ───────────────────────────────────────────────────────────────
  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.location-combobox-wrap').forEach(initLocationCombobox);
  });
})();
