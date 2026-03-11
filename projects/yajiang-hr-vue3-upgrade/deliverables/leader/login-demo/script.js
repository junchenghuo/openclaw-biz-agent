const form = document.getElementById('loginForm');
const username = document.getElementById('username');
const password = document.getElementById('password');
const usernameError = document.getElementById('usernameError');
const passwordError = document.getElementById('passwordError');
const result = document.getElementById('result');

function validate() {
  let ok = true;
  usernameError.textContent = '';
  passwordError.textContent = '';
  result.textContent = '';
  result.className = 'result';

  const userVal = username.value.trim();
  const pwdVal = password.value.trim();

  if (!userVal) {
    usernameError.textContent = '请输入账号';
    ok = false;
  } else if (userVal.length < 3) {
    usernameError.textContent = '账号至少 3 位';
    ok = false;
  }

  if (!pwdVal) {
    passwordError.textContent = '请输入密码';
    ok = false;
  } else if (pwdVal.length < 6) {
    passwordError.textContent = '密码至少 6 位';
    ok = false;
  }

  return ok;
}

form.addEventListener('submit', (e) => {
  e.preventDefault();

  if (!validate()) return;

  result.textContent = '登录成功（演示模式，无后端）';
  result.classList.add('ok');
});
