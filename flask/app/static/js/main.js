

function ShowLoginForm() {
    const loginForm = document.getElementById("login-form");
    const registerForm = document.getElementById("register-form");
    const background = document.getElementById("modal-background")

    InitInputText()

    loginForm.style.display = "";
    registerForm.style.display = "none";
    background.style.display = "";
}

function ShowRegisterForm() {
    const loginForm = document.getElementById("login-form");
    const registerForm = document.getElementById("register-form");
    const background = document.getElementById("modal-background")

    InitInputText()

    loginForm.style.display = "none";
    registerForm.style.display = "";
    background.style.display = "";
}

function HideModalForm() {
    const loginForm = document.getElementById("login-form");
    const registerForm = document.getElementById("register-form");
    const background = document.getElementById("modal-background")

    loginForm.style.display = "none";
    registerForm.style.display = "none";
    background.style.display = "none";
}

function InitInputText() {
    const loginForm = document.querySelectorAll("#login-form input");
    const registerForm = document.querySelectorAll("#register-form input");

    for (const e of loginForm) { e.value = ""; }
    for (const e of registerForm) { e.value = ""; }
}


function Register() {
    const formData = new FormData(document.getElementById("register-form"));

    fetch('/register', {
        method: 'POST',
        body: new URLSearchParams(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert(data.message);
            location.href="/"
        } else {
            alert(data.message);
        }
    })
    .catch(error => { console.error('ERROR: ', error); });

    return false;
}

function Login() {
    const formData = new FormData(document.getElementById("login-form"));

    fetch('/login', {
        method: 'POST',
        body: new URLSearchParams(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert(data.message);
            location.href="/"
        } else {
            alert(data.message);
        }
    })
    .catch(error => { console.error('ERROR: ', error); });

    return false;
}

function Logout() {
    fetch('/logout', {
        method: 'GET'
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert(data.message);
            location.href="/"
        } else {
            alert(data.message);
        }
    })
    .catch(error => { console.error('ERROR: ', error); });

    return false;
}

function OpenQuizParser() {
    const target = document.querySelector('.wrapper.parser');
    target.style.display = "";
}

function CloseQuizParser() {
    const target = document.querySelector('.wrapper.parser');
    target.style.display = "none";
}

function ParsingQuiz() {
    const target = document.querySelector('.quiz-parser > textarea');
    let rows = target.value.split("\n").filter(Boolean);

    let q = "";
    for (const row of rows.slice(0, -4)) {
        q += `${row}\n`;
    }

    q = q.slice(0, -1); // 개행문자 제거
    options = rows.slice(-4); // 선택지 4개

    let userInputs = document.querySelectorAll('.form-template.quiz-add .user-input');
    userInputs[0].value = q;

    for (let i = 0; i < 4; ++i) {
        userInputs[i+1].value = options[i].replace(/^(\d|\W)[\S]*[\s]/g, '');
    }
    
    CloseQuizParser();
}