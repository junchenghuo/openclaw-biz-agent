const form = document.getElementById('loginForm');
const accountInput = document.getElementById('account');
const passwordInput = document.getElementById('password');
const accountError = document.getElementById('accountError');
const passwordError = document.getElementById('passwordError');
const globalError = document.getElementById('globalError');
const submitBtn = document.getElementById('submitBtn');
const togglePasswordBtn = document.getElementById('togglePassword');

function isPhone(v) {
  return /^1\d{10}$/.test(v);
}

function isEmail(v) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);
}

function isUsername(v) {
  return /^[a-zA-Z0-9_\u4e00-\u9fa5]{3,32}$/.test(v);
}

function clearErrors() {
  [accountInput, passwordInput].forEach((el) => el.classList.remove('input-error'));
  accountError.textContent = '';
  passwordError.textContent = '';
  globalError.textContent = '';
}

function validate() {
  clearErrors();
  const account = accountInput.value.trim();
  const password = passwordInput.value;
  let valid = true;

  if (!account) {
    accountInput.classList.add('input-error');
    accountError.textContent = '请输入账号';
    valid = false;
  } else {
    const ok = isPhone(account) || isEmail(account) || isUsername(account);
    if (!ok) {
      accountInput.classList.add('input-error');
      accountError.textContent = '账号格式不正确，请检查后重试';
      valid = false;
    }
  }

  if (!password) {
    passwordInput.classList.add('input-error');
    passwordError.textContent = '请输入密码';
    valid = false;
  } else if (password.length < 8) {
    passwordInput.classList.add('input-error');
    passwordError.textContent = '密码长度至少 8 位';
    valid = false;
  }

  return valid;
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  if (!validate()) return;

  submitBtn.disabled = true;
  submitBtn.textContent = '登录中…';

  await new Promise((r) => setTimeout(r, 800));

  globalError.textContent = '账号或密码有误，请重新输入';
  submitBtn.disabled = false;
  submitBtn.textContent = '登 录';
});

togglePasswordBtn.addEventListener('click', () => {
  const isPwd = passwordInput.type === 'password';
  passwordInput.type = isPwd ? 'text' : 'password';
  togglePasswordBtn.textContent = isPwd ? '隐藏密码' : '显示密码';
});

[accountInput, passwordInput].forEach((el) => {
  el.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') form.requestSubmit();
  });
});
