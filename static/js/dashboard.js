document.getElementById("generateBtn")?.addEventListener("click", async () => {
    const res = await fetch("/generate", { method: "POST" });
    const data = await res.json();
    document.getElementById("output").innerText = "Nova API Key: " + data.api_key;
});