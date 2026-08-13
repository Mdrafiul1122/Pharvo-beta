(function () {
  "use strict";

  var form = document.getElementById("login-form");
  var usernameInput = document.getElementById("username");
  var passwordInput = document.getElementById("password");
  var submitBtn = document.getElementById("sign-in-btn");
  var alertBox = document.getElementById("form-alert");
  var alertMessage = document.getElementById("form-alert-message");
  var submitLabel = submitBtn ? submitBtn.querySelector("[data-btn-label]") : null;

  var MIN_PASSWORD_LENGTH = 6;

  if (!form || !usernameInput || !passwordInput || !submitBtn) {
    return;
  }

  function fieldOf(input) {
    return input.closest(".field");
  }

  function errorEl(input) {
    return fieldOf(input).querySelector(".field__error");
  }

  function setFieldState(input, valid, message) {
    var field = fieldOf(input);
    var error = errorEl(input);

    if (valid) {
      field.classList.remove("field--invalid");
      input.removeAttribute("aria-invalid");
      error.textContent = "";
    } else {
      field.classList.add("field--invalid");
      input.setAttribute("aria-invalid", "true");
      error.textContent = message;
    }
  }

  function validateUsername() {
    var value = usernameInput.value.trim();
    if (!value) {
      setFieldState(usernameInput, false, "Email or username is required.");
      return false;
    }
    setFieldState(usernameInput, true);
    return true;
  }

  function validatePassword() {
    var value = passwordInput.value;
    if (!value) {
      setFieldState(passwordInput, false, "Password is required.");
      return false;
    }
    if (value.length < MIN_PASSWORD_LENGTH) {
      setFieldState(
        passwordInput,
        false,
        "Password must be at least " + MIN_PASSWORD_LENGTH + " characters."
      );
      return false;
    }
    setFieldState(passwordInput, true);
    return true;
  }

  function showAlert(message) {
    alertMessage.textContent = message || "Invalid username or password.";
    alertBox.hidden = false;
  }

  function hideAlert() {
    alertBox.hidden = true;
  }

  function setLoading(loading) {
    submitBtn.disabled = loading;
    submitBtn.classList.toggle("btn--loading", loading);
    if (submitLabel) {
      submitLabel.textContent = loading ? "Signing in..." : "Sign In";
    }
  }

  function clearFieldState(input) {
    if (fieldOf(input).classList.contains("field--invalid")) {
      setFieldState(input, true);
    }
    hideAlert();
  }

  usernameInput.addEventListener("input", function () {
    clearFieldState(usernameInput);
  });

  passwordInput.addEventListener("input", function () {
    clearFieldState(passwordInput);
  });

  var toggles = document.querySelectorAll("[data-toggle-password]");
  Array.prototype.forEach.call(toggles, function (btn) {
    btn.addEventListener("click", function () {
      var target = document.getElementById(btn.getAttribute("data-toggle-password"));
      if (!target) {
        return;
      }
      var showing = btn.getAttribute("aria-pressed") === "true";
      target.type = showing ? "password" : "text";
      btn.setAttribute("aria-pressed", showing ? "false" : "true");
      btn.setAttribute("aria-label", showing ? "Show password" : "Hide password");
    });
  });

  // Simulated authentication. No backend auth endpoint exists yet, so all
  // attempts resolve as failed. To connect a real API, replace performLogin
  // with a POST to the authentication endpoint and route on its response.
  function performLogin(credentials) {
    return new Promise(function (resolve) {
      window.setTimeout(function () {
        resolve({ ok: false, error: "Invalid username or password." });
      }, 900);
    });
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();

    if (submitBtn.disabled) {
      return;
    }

    var usernameOk = validateUsername();
    var passwordOk = validatePassword();

    if (!usernameOk || !passwordOk) {
      hideAlert();
      return;
    }

    hideAlert();
    setLoading(true);

    performLogin({
      username: usernameInput.value.trim(),
      password: passwordInput.value,
      remember: document.getElementById("remember").checked
    }).then(function (result) {
      setLoading(false);
      if (result && result.ok) {
        // Successful authentication — navigate to the dashboard when a
        // backend endpoint is available.
        return;
      }
      showAlert((result && result.error) || "Invalid username or password.");
      passwordInput.select();
      passwordInput.focus();
    });
  });
})();