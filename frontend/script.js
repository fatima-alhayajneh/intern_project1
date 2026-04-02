let allProducts = [];

document.addEventListener('DOMContentLoaded', () => {
    const role = localStorage.getItem("userRole");
    const token = localStorage.getItem("adminToken");

    if (role === "admin" && token) {
        showAdminView();
    }

    const searchInput = document.getElementById("searchInput");
    if (searchInput) searchInput.addEventListener("input", handleSearch);
});

function showToast(message, type = 'success') {
    const toast = document.createElement("div");
    toast.innerText = message;
    toast.style.cssText = `
        position: fixed; bottom: 20px; right: 20px;
        padding: 12px 25px; border-radius: 8px; color: white;
        z-index: 10000; font-weight: bold; transition: all 0.5s;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        background-color: ${type === 'success' ? '#4CAF50' : '#f44336'};
    `;
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 500);
    }, 3000);
}

function showAdminView() {
    document.getElementById("loginSection").style.display = "none";
    document.getElementById("dashboardSection").style.display = "block";
    loadDashboardData();
}

window.handleLogin = async function() {
    const user = document.getElementById("username").value;
    const pass = document.getElementById("password").value;
    const status = document.getElementById("loginStatus");

    if (status) status.innerText = "Attempting login...";
    const success = await loginApi(user, pass);
    
    if (success) {
        const role = localStorage.getItem("userRole");
        if (role === "admin") {
            showToast("Logged in successfully!");
            showAdminView();
        } else {
            localStorage.clear();
            showToast("Access Denied: Admin Only", "error");
        }
    } else {
        if (status) status.innerText = "Login failed!";
        showToast("Check your credentials", "error");
    }
};

window.handleLogout = function() {
    localStorage.clear();
    window.location.reload();
};

async function loadDashboardData() {
    const tableBody = document.getElementById("productTableBody");
    const refreshBtn = document.getElementById("refreshBtn");

    if (refreshBtn) refreshBtn.innerText = "Connecting...";
    tableBody.innerHTML = `<tr><td colspan='6' style="padding: 40px; text-align: center;">Fetching latest data...</td></tr>`;

    try {
        allProducts = await fetchProductsApi();
        renderTable(allProducts);
    } catch (error) {
        tableBody.innerHTML = "<tr><td colspan='6' style='color:red; text-align: center;'>Server Connection Error!</td></tr>";
        showToast("Could not reach server", "error");
    } finally {
        if (refreshBtn) refreshBtn.innerText = "Refresh Data";
    }
}

function renderTable(products) {
    const tableBody = document.getElementById("productTableBody");
    tableBody.innerHTML = "";
    
    if (!products || products.length === 0) {
        tableBody.innerHTML = "<tr><td colspan='6' style='text-align: center;'>No products found.</td></tr>";
        return;
    }

    products.forEach(product => {
        const row = document.createElement("tr");
        const stockValue = product.stock_quantity ?? 0;
        const stockClass = stockValue < 10 ? "low-stock" : "";

        row.innerHTML = `
            <td><input type="checkbox" class="product-checkbox" value="${product.id}" onclick="updateBulkDeleteButton()"></td>
            <td>${product.id}</td>
            <td>${product.name}</td>
            <td>$${product.price}</td>
            <td class="${stockClass}">${stockValue}</td>
            <td>
                <button class="btn-restock" onclick="handleRestock(${product.id})">Restock</button>
                <button onclick="handleDelete(${product.id})" style="background-color:#ff4d4d;color:white;border:none;padding:5px 10px;border-radius:4px;cursor:pointer;margin-left:5px;">Delete</button>
            </td>
        `;
        tableBody.appendChild(row);
    });
    updateBulkDeleteButton();
}

window.toggleSelectAll = function() {
    const master = document.getElementById("selectAll");
    const checkboxes = document.querySelectorAll(".product-checkbox");
    checkboxes.forEach(cb => cb.checked = master.checked);
    updateBulkDeleteButton();
}

window.updateBulkDeleteButton = function() {
    const selected = document.querySelectorAll(".product-checkbox:checked");
    const bulkBtn = document.getElementById("bulkDeleteBtn");
    if (bulkBtn) {
        if (selected.length > 0) {
            bulkBtn.style.display = "inline-block";
            bulkBtn.innerText = `Delete Selected (${selected.length})`;
        } else {
            bulkBtn.style.display = "none";
        }
    }
}

window.handleBulkDelete = async function() {
    const selected = document.querySelectorAll(".product-checkbox:checked");
    const ids = Array.from(selected).map(cb => cb.value);

    if (confirm(`Delete ${ids.length} selected items?`)) {
        for (let id of ids) {
            await deleteProductApi(id);
        }
        showToast(`Batch delete completed`);
        document.getElementById("selectAll").checked = false;
        loadDashboardData();
    }
}

function handleSearch(e) {
    const term = e.target.value.toLowerCase();
    renderTable(allProducts.filter(p => p.name.toLowerCase().includes(term)));
}

window.handleCategoryFilter = function(e) {
    const catId = e.target.value;
    const filtered = (catId === "all") ? allProducts : allProducts.filter(p => p.category_id == catId);
    renderTable(filtered);
};

window.handleRestock = async function(id) {
    if (await restockProductApi(id)) {
        showToast("Stock updated!");
        loadDashboardData();
    }
};

window.handleDelete = async function(id) {
    if (confirm("Permanently delete this item?")) {
        if (await deleteProductApi(id)) {
            showToast("Item deleted");
            loadDashboardData();
        }
    }
};

window.openModal = () => document.getElementById("productModal").style.display = "block";
window.closeModal = () => document.getElementById("productModal").style.display = "none";

const priceInputEl = document.getElementById("productPrice");
if(priceInputEl) {
    priceInputEl.oninput = () => {
        const priceError = document.getElementById("priceError");
        const saveBtn = document.getElementById("saveProductBtn");
        if (parseFloat(priceInputEl.value) < 0) {
            saveBtn.disabled = true;
            if(priceError) priceError.style.display = "block";
        } else {
            saveBtn.disabled = false;
            if(priceError) priceError.style.display = "none";
        }
    };
}

const pForm = document.getElementById("productForm");
if(pForm) {
    pForm.onsubmit = async (e) => {
        e.preventDefault();
        const data = {
            name: document.getElementById("productName").value,
            description: "Admin added product",
            price: parseFloat(document.getElementById("productPrice").value),
            stock_quantity: parseInt(document.getElementById("productStock").value),
            category_id: parseInt(document.getElementById("productCategory").value),
            vendor_id: 1
        };
        const res = await addProductApi(data);
        if (res && res.ok) {
            showToast("Product saved! ✅");
            closeModal();
            pForm.reset();
            loadDashboardData();
        } else {
            const error = await res.json();
            console.error("Save Error:", error);
            showToast("Save failed! Check fields", "error");
        }
    };
}
