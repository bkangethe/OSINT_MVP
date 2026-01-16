async function login() {
  const username = document.getElementById("loginUser").value;
  const password = document.getElementById("loginPass").value;

  const res = await fetch("/api/auth/login", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({username, password})
  });

  const data = await res.json();
  if(data.token){
    localStorage.setItem("token", data.token);
    location.reload();
  } else {
    alert("Login failed");
  }
}
