document.addEventListener("click", function (event) {
    const btn = event.target.closest(".copy-lead-btn");
    if (!btn) return;

    const lines = [
        "Business: " + (btn.dataset.name || ""),
        "Region: " + (btn.dataset.region || ""),
        "Website: " + (btn.dataset.website || "None listed"),
        "Site assessment: " + (btn.dataset.flag || ""),
    ];
    const text = lines.join("\n");

    navigator.clipboard.writeText(text).then(function () {
        const original = btn.textContent;
        btn.textContent = "Copied!";
        setTimeout(function () {
            btn.textContent = original;
        }, 1500);
    });
});
