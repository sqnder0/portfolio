document.addEventListener("submit", function (event) {
    const form = event.target.closest(".confirm-delete-form");
    if (!form) return;

    const message = form.dataset.confirmMessage || "Are you sure? This cannot be undone.";
    if (!window.confirm(message)) {
        event.preventDefault();
    }
});
