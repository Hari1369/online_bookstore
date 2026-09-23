/* auth.js — client-side validation + localStorage-backed auth flows.
   In production, signup/login/forgot-password should call the DRF endpoints
   and store a JWT instead of a plain session object. */

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const PHONE_RE = /^[0-9+\-() ]{7,20}$/;

function showFieldError(fieldId, show) {
  const field = document.getElementById(fieldId);
  if (field) field.classList.toggle('invalid', show);
}

function showAlert(message, isError) {
  const alertBox = document.getElementById('formAlert');
  if (!alertBox) return;
  alertBox.textContent = message;
  alertBox.classList.toggle('error', !!isError);
  alertBox.classList.add('show');
}

/* ---------- Signup ---------- */
const signupForm = document.getElementById('signupForm');
if (signupForm) {
  signupForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const name = document.getElementById('name').value.trim();
    const email = document.getElementById('email').value.trim();
    const phone = document.getElementById('phone').value.trim();
    const password = document.getElementById('password').value;
    const confirm = document.getElementById('confirm').value;
    let valid = true;

    showFieldError('f-name', !name); if (!name) valid = false;
    const emailOk = EMAIL_RE.test(email);
    showFieldError('f-email', !emailOk); if (!emailOk) valid = false;
    const phoneOk = !phone || PHONE_RE.test(phone);
    showFieldError('f-phone', !phoneOk); if (!phoneOk) valid = false;
    const passOk = password.length >= 8;
    showFieldError('f-password', !passOk); if (!passOk) valid = false;
    const confirmOk = password === confirm && confirm.length > 0;
    showFieldError('f-confirm', !confirmOk); if (!confirmOk) valid = false;

    if (!valid) { showAlert('Please fix the highlighted fields.', true); return; }

    if (Users.findByEmail(email)) {
      showFieldError('f-email', true);
      showAlert('An account with that email already exists. Try logging in instead.', true);
      return;
    }

    Users.create({ name, email, phone, password, role: 'customer' });
    Session.set({ name, email, role: 'customer' });
    showAlert('Account created. Redirecting…', false);
    setTimeout(() => location.href = 'index.html', 600);
  });
}

/* ---------- Login ---------- */
const loginForm = document.getElementById('loginForm');
if (loginForm) {
  loginForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    let valid = true;

    const emailOk = EMAIL_RE.test(email);
    showFieldError('f-email', !emailOk); if (!emailOk) valid = false;
    showFieldError('f-password', !password); if (!password) valid = false;
    if (!valid) { showAlert('Please fix the highlighted fields.', true); return; }

    const user = Users.findByEmail(email);
    if (!user || user.password !== password) {
      showAlert('Email or password is incorrect.', true);
      showFieldError('f-password', true);
      return;
    }
    Session.set(user);
    showAlert('Logged in. Redirecting…', false);
    setTimeout(() => location.href = 'index.html', 500);
  });
}

/* ---------- Forgot password ---------- */
const requestForm = document.getElementById('requestForm');
const resetForm = document.getElementById('resetForm');
if (requestForm) {
  let pendingEmail = '';
  requestForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const email = document.getElementById('email').value.trim();
    const emailOk = EMAIL_RE.test(email);
    showFieldError('f-email', !emailOk);
    if (!emailOk) { showAlert('Enter a valid email address.', true); return; }

    if (!Users.findByEmail(email)) {
      showAlert("We don't have an account with that email.", true);
      showFieldError('f-email', true);
      return;
    }

    const token = ResetTokens.issue(email);
    pendingEmail = email;
    showAlert(`Reset token for demo purposes: ${token} (normally emailed to you)`, false);
    resetForm.style.display = 'block';
    requestForm.querySelector('button').disabled = true;
  });

  resetForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const token = document.getElementById('token').value.trim();
    const newpassword = document.getElementById('newpassword').value;
    let valid = true;

    const tokenOk = ResetTokens.verify(pendingEmail, token);
    showFieldError('f-token', !tokenOk); if (!tokenOk) valid = false;
    const passOk = newpassword.length >= 8;
    showFieldError('f-newpassword', !passOk); if (!passOk) valid = false;
    if (!valid) { showAlert('Please fix the highlighted fields.', true); return; }

    Users.update(pendingEmail, { password: newpassword });
    ResetTokens.clear(pendingEmail);
    showAlert('Password updated. Redirecting to log in…', false);
    setTimeout(() => location.href = 'login.html', 800);
  });
}
