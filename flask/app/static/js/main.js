// Members
function MemberRegister() {
    const formData = new FormData(document.querySelector("form.register"));

    fetch("/member/register", { method: 'POST', body: new URLSearchParams(formData) })
    .then(response => response.json())
    .then(data => {
        alert(data.message);

        if (data.status === 'S') {
            location.href = "/";
        }
    })
    .catch(error => { console.log('ERROR: ', error) });

    return false;
}

function MemberLogin() {
    const formData = new FormData(document.querySelector("form.login"));

    fetch("/member/login", { method: "POST", body: new URLSearchParams(formData) })
    .then(response => response.json())
    .then(data => {
        alert(data.message);

        if (data.status === "S") {
            location.href = "/";
        }
    })
    .catch(error => { console.log("ERROR: ", error) })

    return false;
}

function MemberLogout() {
    fetch("/member/logout", { method: "GET" })
    .then(response => response.json())
    .then(data => {
        alert(data.message);

        if (data.status === "S") {
            location.href = "/";
        }
    })
    .catch(error => { console.log("ERROR: ", error) })

    return false;
}

function MemberUnregister() {
    if (confirm("정말 회원 탈퇴를 진행하시겠습니까?")) {
        fetch("/member/unregister", { method: "GET" })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
    
            if (data.status === 'S') {
                location.href = "/";
            }
        })
        .catch(error => { console.log('ERROR: ', error) });
    }

    return false;
}

function MemberModify() {
    const formData = new FormData(document.querySelector("#mypage"));

    fetch("/member/mypage", { method: "POST", body: new URLSearchParams(formData) })
    .then(response => response.json())
    .then(data => {
        alert(data.message);

        if (data.status === 'S') {
            location.href = "/member/mypage";
        }
    })
    .catch(error => { console.log("ERROR: ", error) });

    return false;
}

function ShowLoginForm() {
    const loginForm = document.querySelector("form.login").parentNode;
    const registerForm = document.querySelector("form.register").parentNode;

    InitFormValues();

    loginForm.style.display = "";
    registerForm.style.display = "none";
}

function ShowRegisterForm() {
    const loginForm = document.querySelector("form.login").parentNode;
    const registerForm = document.querySelector("form.register").parentNode;

    InitFormValues();

    loginForm.style.display = "none";
    registerForm.style.display = "";
}

function HideModalForm() {
    const modalBackground = document.querySelectorAll(".bg-modal")
    for (const e of modalBackground) { e.style.display = "none"; }
}

function InitFormValues() {
    const loginFormInputs = document.querySelectorAll("form.login input");
    const registerFormInputs = document.querySelectorAll("form.register input");

    for (const e of loginFormInputs) { e.value = ""; }
    for (const e of registerFormInputs) { e.value = ""; }
}


// Quiz
function OpenQuizParser() {
    document.querySelector(".quiz-parser").style.display = "";
}

function CloseQuizParser() {
    document.querySelector(".quiz-parser").style.display = "none";
}

function ParseQuiz() {
    const target = document.querySelector(".quiz-parser textarea");
    let rows = target.value.split("\n").filter(Boolean);

    let q = "";
    for (const row of rows.slice(0, -4)) {
        q += `${row}\n`;
    }

    q = q.slice(0, -1); // 개행문자 제거
    options = rows.slice(-4); // 선택지 4개

    let inputs = document.querySelectorAll('#quiz-cvm input, #quiz-cvm textarea');
    inputs[0].value = q;
    for (let i = 0; i < 4; ++i) {
        inputs[i+1].value = options[i].replace(/^(\d|\W)[\S]*[\s]/g, '');
    }

    CloseQuizParser();
}

function QuizCreate() {
    const formData = new FormData(document.querySelector("#quiz-cvm"));

    fetch("/quiz/create", { method: "POST", body: new URLSearchParams(formData) })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        if (data.status === "S") {
            location.href = "/quiz/create";
        }
    })
    .catch(error => { console.log("ERROR: ", error)});

    return false;
}

function QuizModify() {
    const formData = new FormData(document.querySelector("#quiz-cvm"));

    fetch(window.location.href, { method: "POST", body: new URLSearchParams(formData) })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        if (data.status === "S") {
            location.href = window.location.href;
        }
    })
    .catch(error => { console.log("ERROR: ", error)});

    return false;
}

function QuizDelete() {
    if (confirm("게시글된 문제를 정말 삭제하시겠습니까?")) {
        console.log("/quiz/delete/" + window.location.pathname.slice(11));
        fetch("/quiz/delete/" + window.location.pathname.slice(11), {method: "GET"})
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            if (data.status == "S") {
                location.href = "/quiz/lists";
            }
        })
        .catch(error => { console.log("ERROR: ", error)});
    }
}


// Board
function PostWrite() {
    const title = document.querySelector("#board-cvm input[name=title]").value;
    const content = window.editor.getData();
    const file = document.querySelector("#board-cvm input[name=file]").files[0];

    const formData = new FormData();
    formData.append("title", title);
    formData.append("content", content);
    formData.append("file", file);

    fetch("/board/write", { method: "POST", body: formData })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        if (data.status === "S") {
            location.href = "/board/lists";
        }
    })
    .catch(error => { console.log("ERROR: ", error) });

    return false;
}

function PostModify() {
    const title = document.querySelector("#board-cvm input[name=title]").value;
    const content = window.editor.getData();
    const file = document.querySelector("#board-cvm input[name=file]").files[0];

    const formData = new FormData();
    formData.append("title", title);
    formData.append("content", content);
    formData.append("file", file);

    fetch(window.location.href, { method: "POST", body: formData })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        if (data.status === "S") {
            location.href = "/board/lists";
        }
    })
    .catch(error => { console.log("ERROR: ", error) });

    return false;
}

function PostDelete() {
    if (confirm("게시글을 정말 삭제하시겠습니까?")) {
        fetch("/board/delete/" + window.location.pathname.slice(12), {method: "GET"})
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            if (data.status == "S") {
                location.href = "/board/lists";
            }
        })
        .catch(error => { console.log("ERROR: ", error)});
    }

    return false;
}

function ShowChatbot() {
    const chatbotPopup = document.getElementById("chatbotPopup");
    chatbotPopup.classList.toggle("hidden");
}


// Lecture
function LectureCreate() {
    const subject = document.querySelector("select[name=subject]").value;
    const title = document.querySelector("input[name=title]").value;
    const description = document.querySelector("textarea[name=description]").value;
    const file = document.querySelector("input[name=file]").files[0];

    const formData = new FormData();
    formData.append("subject", subject);
    formData.append("title", title);
    formData.append("description", description);
    formData.append("file", file);

    fetch("/lecture/create", { method: "POST", body: formData })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        if (data.status === "S") {
            location.href = "/lecture/lists";
        }
    })
    .catch(error => { console.log("ERROR: ", error); });

    return false;
}

// Subscribe
function SubscribeRevoke() {
    fetch("/subscribe/api/revoke_request")
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        if (data.status === "S") {
            location.href = "/member/mypage";
        }
    })
    .catch(error => { console.log("ERROR: ", error); });
}