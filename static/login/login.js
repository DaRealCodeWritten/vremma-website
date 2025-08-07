document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const emailError = document.getElementById('emailError');
    const passwordError = document.getElementById('passwordError');

    // Reset error messages
    emailError.style.display = 'none';
    passwordError.style.display = 'none';

    // Simple validation
    let hasError = false;

    if (!email || !email.includes('@')) {
        emailError.style.display = 'block';
        hasError = true;
    }

    if (!password) {
        passwordError.style.display = 'block';
        hasError = true;
    }

    if (hasError) {
        this.classList.add('shake');
        setTimeout(() => this.classList.remove('shake'), 500);
        return;
    }

    this.submit();
});