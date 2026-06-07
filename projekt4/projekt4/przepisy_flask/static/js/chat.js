/*
 * Obsługa czatu z asystentem kulinarnym AI.
 *
 * Historia rozmowy trzymana jest w przeglądarce i przesyłana przy każdym
 * żądaniu (API modelu jest bezstanowe). Token CSRF pobierany jest z meta
 * tagu i wysyłany w nagłówku, aby zachować ochronę Flask-WTF.
 */
(function () {
    const win = document.getElementById("chat-window");
    const form = document.getElementById("chat-form");
    const input = document.getElementById("chat-input");
    const sendBtn = document.getElementById("chat-send");
    if (!win || !form) return;

    const endpoint = win.dataset.endpoint;
    const recipeSlug = win.dataset.recipe || null;
    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

    // Pełna historia rozmowy wysyłana do serwera.
    const history = [];

    function addMessage(role, text, extraClass) {
        const wrapper = document.createElement("div");
        wrapper.className = "chat-message " + role + (extraClass ? " " + extraClass : "");
        const bubble = document.createElement("div");
        bubble.className = "bubble";
        bubble.textContent = text;
        wrapper.appendChild(bubble);
        win.appendChild(wrapper);
        win.scrollTop = win.scrollHeight;
        return wrapper;
    }

    async function send(message) {
        addMessage("user", message);
        history.push({ role: "user", content: message });
        input.value = "";
        sendBtn.disabled = true;

        const typing = addMessage("assistant", "Asystent pisze…", "chat-typing");

        try {
            const res = await fetch(endpoint, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken,
                },
                body: JSON.stringify({
                    message: message,
                    history: history.slice(0, -1),
                    recipe: recipeSlug,
                }),
            });
            const data = await res.json();
            typing.remove();
            const reply = data.reply || data.error || "Brak odpowiedzi.";
            addMessage("assistant", reply);
            history.push({ role: "assistant", content: reply });
        } catch (err) {
            typing.remove();
            addMessage("assistant", "Błąd połączenia. Spróbuj ponownie.");
        } finally {
            sendBtn.disabled = false;
            input.focus();
        }
    }

    form.addEventListener("submit", function (e) {
        e.preventDefault();
        const message = input.value.trim();
        if (message) send(message);
    });

    // Przyciski z gotowymi pytaniami.
    document.querySelectorAll(".chat-suggestion").forEach(function (btn) {
        btn.addEventListener("click", function () {
            send(btn.textContent.trim());
        });
    });
})();
