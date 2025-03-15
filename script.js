// ✅ Fetch Kits
async function fetchKits() {
    let response = await fetch("/get-kits");
    let kits = await response.json();
    let container = document.getElementById("kits-container");
    container.innerHTML = "";

    kits.forEach(kit => {
        let kitElement = document.createElement("div");
        kitElement.innerHTML = `
            <img src="${kit.image}" alt="${kit.name}" width="200">
            <h2>${kit.name}</h2>
            <button onclick="customizeKit('${kit.id}')">Customize</button>
        `;
        container.appendChild(kitElement);
    });
}

// ✅ Upload a Kit
async function uploadKit() {
    let kitName = document.getElementById('kitName').value;
    let kitImage = document.getElementById('kitImage').files[0];

    let formData = new FormData();
    formData.append("name", kitName);
    formData.append("image", kitImage);

    let response = await fetch("/upload-kit", { method: "POST", body: formData });
    let result = await response.json();
    alert(result.message);
    fetchKits();
}

// ✅ Customize a Kit
async function customizeKit(kitId) {
    let newColor = prompt("Enter customization details:");
    if (!newColor) return;

    let response = await fetch("/customize-kit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ kit_id: kitId, color: newColor })
    });

    let result = await response.json();
    alert(result.message);
}

// ✅ Load Kits on Page Load
window.onload = fetchKits;
