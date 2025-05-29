let token = '';

function signup() {
  const username = document.getElementById('signup-username').value;
  const password = document.getElementById('signup-password').value;

  fetch('https://ai-creators-studio-viral.onrender.com/signup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  })
  .then(res => res.json())
  .then(data => alert(data.message || 'Signup successful!'))
  .catch(err => alert('Signup failed'));
}

function login() {
  const username = document.getElementById('login-username').value;
  const password = document.getElementById('login-password').value;

  fetch('https://ai-creators-studio-viral.onrender.com/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  })
  .then(res => res.json())
  .then(data => {
    if (data.access_token) {
      token = data.access_token;
      alert('Login successful!');
    } else {
      alert('Login failed');
    }
  });
}

function generate() {
  const prompt = document.getElementById('prompt').value;

  fetch('https://ai-creators-studio-viral.onrender.com/generate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + token
    },
    body: JSON.stringify({ prompt })
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById('result').textContent = data.result || 'No output received.';
  });
}
