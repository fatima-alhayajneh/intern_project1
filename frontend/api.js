const API_URL = "http://127.0.0.1:8000";

async function loginApi(username, password) {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    try {
        const response = await fetch(`${API_URL}/token`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('adminToken', data.access_token);
            return true;
        }
        return false;
    } catch (error) {
        console.error("Login error:", error);
        return false;
    }
}

async function fetchProductsApi() {
    const response = await fetch(`${API_URL}/products/`);
    return await response.json();
}

async function addProductApi(productData) {
    const token = localStorage.getItem('adminToken');

    return await fetch(`${API_URL}/products/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(productData)
    });
}

async function deleteProductApi(id) {
    const token = localStorage.getItem("adminToken");

    const response = await fetch(`${API_URL}/products/${id}`, {
        method: "DELETE",
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    return response.ok;
}

async function restockProductApi(id) {
    const response = await fetch(`${API_URL}/products/${id}/restock`, {
        method: 'PATCH'
    });

    return response.ok;
}
