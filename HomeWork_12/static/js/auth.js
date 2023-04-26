async function RegistrationFormShow() {

  const modal_form = document.getElementById("RegistrationForm")
  const modal = new bootstrap.Modal(modal_form);

  modal_form.querySelector("#UserName").value = "";
  modal_form.querySelector("#UserEmail").value = "";
  modal_form.querySelector("#UserPass").value = "";

  const submit_btn = modal_form.querySelector(".btn-primary");
  submit_btn.onclick = async function () {
    if (await registerUser())
      modal.hide();
  };

  modal.show();
}

async function LoginFormShow() {

  const modal_form = document.getElementById("LoginForm")
  const modal = new bootstrap.Modal(modal_form);

  modal_form.querySelector("#UserEmail").value = "";
  modal_form.querySelector("#UserPass").value = "";

  const submit_btn = modal_form.querySelector(".btn-primary");
  submit_btn.onclick = async function () {
    if (await loginUser())
      modal.hide();
  };

  modal.show();
}

async function registerUser() {
  const user_name = document.getElementById("UserName").value;

  const response = await fetch("/api/auth/signup/", {
    method: "POST",
    headers: {"Accept": "application/json", "Content-Type": "application/json"},
    body: JSON.stringify({
      username: user_name ? user_name : null,
      email: document.getElementById("UserEmail").value,
      password: document.getElementById("UserPass").value
    })
  });

  if (response.ok !== true) {
    const error = await response.json();
    if (response.status === 422){
      alert("Input data is invalid");
    }
    else
      alert(error.detail);
  }

  return response.ok
}

async function loginUser() {
  const modal_form = document.getElementById("LoginForm")

  const response = await fetch("/api/auth/login/", {
    method: "POST",
    headers: {"Content-Type": "application/x-www-form-urlencoded"},
    body: new URLSearchParams({
      username: modal_form.querySelector("#UserEmail").value,
      password: modal_form.querySelector("#UserPass").value
    })
  });
  console.log(response.status, response.statusText)

  if (response.ok === true) {
    if (response.status === 200) {
      const result = await response.json()
      localStorage.setItem('accessToken', result.access_token)
      localStorage.setItem('refreshToken', result.refresh_token)
    }
  }
  else{
    const error = await response.json();
    if (response.status === 422){
      alert("Input data is invalid");
    }
    else
      alert(error.detail);
  }

  return response.ok
}

