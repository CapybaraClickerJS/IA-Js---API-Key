// Criar conta
document.getElementById("registerBtn")?.addEventListener("click", async () => {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    // Verifica regra mínima de senha
    const numeros = password.replace(/[^0-9]/g,"").length;
    if(password.length < 8 || numeros < 3){
        document.getElementById("output").innerText = "Senha fraca! Precisa ter ao menos 8 caracteres e 3 números";
        return;
    }

    const res = await fetch("/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    });

    const data = await res.json();
    document.getElementById("output").innerText = data.message;
});

// Login próprio
document.getElementById("loginBtn")?.addEventListener("click", async () => {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const res = await fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    });

    const data = await res.json();
    if(data.status === "success"){
        window.location.href = "/dashboard";
    } else {
        document.getElementById("output").innerText = data.message;
    }
});

// Google login (placeholder, precisa configurar OAuth real)
document.getElementById("googleBtn")?.addEventListener("click", () => {
    alert("Login com Google ainda precisa configurar OAuth");
});