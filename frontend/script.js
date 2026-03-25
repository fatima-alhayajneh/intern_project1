const API_URL = "http://127.0.0.1:8000";

async function fetchProducts() {
    try {
        const response = await fetch(`${API_URL}/products/`);
        const products = await response.json();
        
        const tableBody = document.getElementById("productTableBody");
        tableBody.innerHTML = "";

        products.forEach(product => {
            const row = document.createElement("tr");
            const stockClass = product.stock_quantity < 10 ? "low-stock" : "";

            row.innerHTML = `
                <td>${product.id}</td>
                <td>${product.name}</td>
                <td>$${product.price}</td>
                <td class="${stockClass}">${product.stock_quantity}</td>
                <td>
                    <button class="btn-restock" onclick="restockProduct(${product.id})">Restock</button>
                </td>
            `;
            tableBody.appendChild(row);
        });
    } catch (error) {
        console.error("Error fetching products:", error);
    }
}

async function restockProduct(id) {
    if (!confirm("Are you sure you want to add 10 units to this product?")) {
        return; 
    }

    try {
        const response = await fetch(`${API_URL}/products/${id}/restock`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            fetchProducts();
        } else {
            alert("Failed to update stock");
        }
    } catch (error) {
        console.error("Error updating stock:", error);
    }
}

window.onload = fetchProducts;
document.getElementById("refreshBtn").onclick = fetchProducts;
