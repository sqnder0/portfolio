document.addEventListener("change", function (event) {
    if (event.target.id !== "client_id") return;

    const select = event.target;
    const option = select.options[select.selectedIndex];
    const recipientName = document.getElementById("recipient_name");
    const recipientEmail = document.getElementById("recipient_email");

    if (!option || !option.value) return;
    if (recipientName) recipientName.value = option.dataset.fullName || "";
    if (recipientEmail) recipientEmail.value = option.dataset.email || "";
});
