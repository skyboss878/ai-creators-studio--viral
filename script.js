document.getElementById('signup-form').addEventListener('submit', async (e) => {
  e.preventDefault();

  const name = e.target.name.value;
  const email = e.target.email.value;
  const password = e.target.password.value;

  const response = await fetch('http://127.0.0.1:5000/api/signup', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ name, email, password })
  });

  const result = await response.json();
  document.getElementById('message').textContent = result.message || result.error;
})
