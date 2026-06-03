// ✅ This code handles saving Facebook login credentials
// These are NOT Django user logins — they are used by the automation bot to log into Facebook Marketplace.

document.addEventListener("DOMContentLoaded", () => {
  const phoneEl = document.getElementById("userEmail"); // phone/email input
  const passwordEl = document.getElementById("userPassword"); // password input
  const saveForm = document.getElementById("credentialsForm"); // form
  const statusEl = document.getElementById("credentialStatus"); // status message element
  const startBotBtn = document.getElementById("startBot"); // Start bot button
  const tabsCountInput = document.getElementById("tabsCount"); // Number of tabs input

  // ------------------------------------------
  // 🔹 Helper: Get CSRF cookie (for Django POST)
  // ------------------------------------------
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + "=")) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  // ------------------------------------------
  // 💾 Save Facebook credentials (phone + pass)
  // ------------------------------------------
  saveForm?.addEventListener("submit", async (e) => {
    e.preventDefault();

    const phone = phoneEl?.value.trim();
    const password = passwordEl?.value.trim();

    // Validation before sending
    if (!phone || !password) {
      showStatus("⚠️ Facebook phone/email and password are required!", "red");
      return;
    }

    try {
      const response = await fetch("/listings/save-credentials/", {  // ✅ FIXED URL
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ phone, password }),
      });

      const data = await response.json();

      if (data.success) {
        showStatus(data.message, "lime");
      } else {
        showStatus(`❌ Error: ${data.message}`, "red");
      }
    } catch (err) {
      console.error("Network error:", err);
      showStatus("⚠️ Network Error: " + err.message, "red");
    }
  });

  // ------------------------------------------
// 🤖 START AUTOMATION BOT
// ------------------------------------------
startBotBtn?.addEventListener("click", async () => {
    const tabsCount = tabsCountInput?.value || 1;
    
    // ✅ VALIDATION: Check if tabs count is between 1-100
    if (!tabsCount || tabsCount < 1 || tabsCount > 100) {
        showStatus("⚠️ Please enter a valid number between 1 and 100", "red");
        return;
    }

    showStatus("🚀 Starting automation... Please wait...", "blue");

    try {
        const response = await fetch("/listings/start/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: JSON.stringify({
                tabs: parseInt(tabsCount),  // ✅ SEND NUMBER OF TABS (1-100)
                automation_type: automationType
            }),
        });

        const data = await response.json();

        if (data.success) {
            showStatus(`✅ ${data.message}`, "lime");
        } else {
            showStatus(`❌ Error: ${data.message}`, "red");
        }
    } catch (err) {
        console.error("Bot start error:", err);
        showStatus("⚠️ Network Error starting bot: " + err.message, "red");
    }
});

  // ------------------------------------------
  // 🔄 Auto-load saved credentials on page open
  // ------------------------------------------
  (async function loadCredentials() {
    try {
      const response = await fetch("/listings/get-credentials/");  // ✅ FIXED URL
      const data = await response.json();

      if (data.success) {
        phoneEl.value = data.phone_or_email || "";
        passwordEl.value = data.password || "";
        showStatus("✅ Loaded saved credentials.", "lime");
      }
    } catch (error) {
      console.error("⚠️ Network Error while loading credentials:", error);
      showStatus("⚠️ Network Error while loading credentials", "red");
    }
  })();

  // ------------------------------------------
  // 💬 Helper: Show status message on screen
  // ------------------------------------------
  function showStatus(msg, color) {
    if (!statusEl) {
      alert(msg);
      return;
    }
    statusEl.textContent = msg;
    statusEl.style.color = color;
    statusEl.style.display = "block";
    
    // Auto-hide success messages after 5 seconds
    if (color === "lime") {
      setTimeout(() => {
        statusEl.style.display = "none";
      }, 5000);
    }
  }
});
