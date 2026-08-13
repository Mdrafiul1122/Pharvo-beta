import { useState } from "react";
import Logo from "../components/Logo";
import BrandPanel from "../components/BrandPanel";
import LoginInput from "../components/LoginInput";
import PasswordInput from "../components/PasswordInput";
import LoginButton from "../components/LoginButton";
import { AlertIcon, RoleBadgeIcon, CheckIcon } from "../components/Icons";
import { loginUser } from "../services/auth";

const MIN_PASSWORD_LENGTH = 6;

function validateUsername(value) {
  if (!value.trim()) {
    return "Email or username is required.";
  }
  return "";
}

function validatePassword(value) {
  if (!value) {
    return "Password is required.";
  }
  if (value.length < MIN_PASSWORD_LENGTH) {
    return `Password must be at least ${MIN_PASSWORD_LENGTH} characters.`;
  }
  return "";
}

export default function MedicineSpecialistLogin() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(false);
  const [errors, setErrors] = useState({ username: "", password: "" });
  const [formError, setFormError] = useState("");
  const [loading, setLoading] = useState(false);

  function handleUsernameChange(event) {
    setUsername(event.target.value);
    if (errors.username) {
      setErrors((prev) => ({ ...prev, username: "" }));
    }
    if (formError) {
      setFormError("");
    }
  }

  function handlePasswordChange(event) {
    setPassword(event.target.value);
    if (errors.password) {
      setErrors((prev) => ({ ...prev, password: "" }));
    }
    if (formError) {
      setFormError("");
    }
  }

  async function handleSubmit(event) {
    event.preventDefault();

    if (loading) {
      return;
    }

    const usernameError = validateUsername(username);
    const passwordError = validatePassword(password);
    const nextErrors = { username: usernameError, password: passwordError };

    setErrors(nextErrors);
    setFormError("");

    if (usernameError || passwordError) {
      return;
    }

    setLoading(true);

    try {
      await loginUser({
        username: username.trim(),
        password,
        remember,
      });
      // Successful authentication — navigate to the app.
      // Replace with the real dashboard route once routing is in place.
      window.location.assign("/");
    } catch (err) {
      setFormError(err?.message || "Invalid username or password.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-shell">
      <BrandPanel />

      <main className="form-panel">
        <section className="login-card" aria-labelledby="login-title">
          <div className="login-card__logo">
            <Logo className="logo logo--card" compact />
          </div>

          <header className="login-card__header">
            <h2 className="login-card__title" id="login-title">
              Welcome back
            </h2>
            <p className="login-card__subtitle">Sign in to your PHARVO account</p>
            <span className="role-badge">
              <RoleBadgeIcon />
              Medicine Specialist
            </span>
          </header>

          <form className="login-form" id="login-form" onSubmit={handleSubmit} noValidate>
            {formError && (
              <div className="form-alert" id="form-alert" role="alert">
                <AlertIcon />
                <span id="form-alert-message">{formError}</span>
              </div>
            )}

            <LoginInput
              id="username"
              name="username"
              label="Email or Username"
              placeholder="Enter your email or username"
              type="text"
              autoComplete="username"
              required
              error={errors.username}
              value={username}
              onChange={handleUsernameChange}
            />

            <PasswordInput
              id="password"
              name="password"
              error={errors.password}
              value={password}
              onChange={handlePasswordChange}
            />

            <div className="login-form__row">
              <label className="checkbox">
                <input
                  className="checkbox__input"
                  type="checkbox"
                  name="remember"
                  id="remember"
                  checked={remember}
                  onChange={(event) => setRemember(event.target.checked)}
                />
                <span className="checkbox__box" aria-hidden="true">
                  <CheckIcon />
                </span>
                <span className="checkbox__label">Remember me</span>
              </label>
              <a className="login-form__link" href="#">
                Forgot password?
              </a>
            </div>

            <LoginButton loading={loading} />

            <p className="login-form__note">Authorized pharmacy personnel only</p>
          </form>
        </section>
      </main>
    </div>
  );
}
