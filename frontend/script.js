let allProducts = [];

document.addEventListener('DOMContentLoaded', () => {
    loadDashboardData();

    const refreshBtn = document.getElementById("refreshBtn");
    if (refreshBtn) refreshBtn.onclick = loadDashboardData;

    const searchInput = document.getElementById("searchInput");
    if (searchInput) searchInput.addEventListener("input", handleSearch);

    const categoryFilter = document.getElementById("categoryFilter");
    if (categoryFilter) categoryFilter.addEventListener("change", handleCategoryFilter);
});

// --- Toast Notification System (NEW) ---
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

// --- Login Logic ---
async function handleLogin() {
    const user = document.getElementById("username").value;
    const pass = document.getElementById("password").value;
    const status = document.getElementById("loginStatus");

    status.innerText = "Attempting login...";
    const success = await loginApi(user, pass);
    
    if (success) {
        showToast("Logged in successfully!");
        status.innerText = "";
        document.getElementById("loginSection").style.display = "none";
    } else {
        status.innerText = "Login failed!";
        status.style.color = "red";
        showToast("Check your credentials", "error");
    }
}

// --- Data Loading & Rendering ---
async function loadDashboardData() {
    const tableBody = document.getElementById("productTableBody");
    const refreshBtn = document.getElementById("refreshBtn");

    if (refreshBtn) refreshBtn.innerText = "Connecting...";
    
    // إظهار شكل التحميل (Spinner) داخل الجدول
    tableBody.innerHTML = `
        <tr><td colspan='6' style="padding: 40px;">
            <div class="loader-text">Fetching latest data...</div>
        </td></tr>`;

    try {
        allProducts = await fetchProductsApi();
        renderTable(allProducts);
    } catch (error) {
        tableBody.innerHTML = "<tr><td colspan='6' style='color:red'>Server Connection Error!</td></tr>";
        showToast("Could not reach server", "error");
    } finally {
        if (refreshBtn) refreshBtn.innerText = "Refresh Data";
    }
}

function renderTable(products) {
    const tableBody = document.getElementById("productTableBody");
    tableBody.innerHTML = "";

    if (products.length === 0) {
        tableBody.innerHTML = "<tr><td colspan='6'>No products found matching criteria.</td></tr>";
        return;
    }

    products.forEach(product => {
        const row = document.createElement("tr");
        const stockValue = product.stock_quantity ?? (product.stock || 0);
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

// --- Search & Filtering ---
function handleSearch(e) {
    const term = e.target.value.toLowerCase();
    
    // 1. الفلترة: بنجيب كل اللي فيهم الحرف
    let filtered = allProducts.filter(product => 
        product.name.toLowerCase().includes(term)
    );

    // 2. الترتيب الذكي (السر هون):
    filtered.sort((a, b) => {
        const nameA = a.name.toLowerCase();
        const nameB = b.name.toLowerCase();

        const startsWithA = nameA.startsWith(term);
        const startsWithB = nameB.startsWith(term);

        // إذا A بتبدأ بالحرف و B لأ -> A تطلع فوق (-1)
        if (startsWithA && !startsWithB) return -1;
        // إذا B بتبدأ بالحرف و A لأ -> B تطلع فوق (1)
        if (!startsWithA && startsWithB) return 1;

        // إذا الاثنين ببدأوا بنفس الحرف أو الاثنين ما ببدأوا فيه، رتبيهم أبجدي عادي
        return nameA.localeCompare(nameB);
    });

    renderTable(filtered);
}

function handleCategoryFilter(e) {
    const categoryId = e.target.value;
    if (categoryId === "all") {
        renderTable(allProducts);
    } else {
        // الفلترة حسب category_id
        const filtered = allProducts.filter(p => p.category_id == categoryId);
        renderTable(filtered);
    }
}

// --- Individual Actions ---
async function handleRestock(id) {
    const success = await restockProductApi(id);
    if (success) {
        showToast("Stock updated!");
        loadDashboardData();
    } else {
        showToast("Update failed", "error");
    }
}

window.handleDelete = async function(id) {
    if (confirm("Permanently delete this item?")) {
        const success = await deleteProductApi(id);
        if (success) {
            showToast("Item deleted");
            loadDashboardData();
        } else {
            showToast("Delete operation failed", "error");
        }
    }
};

// --- Bulk Actions ---
function toggleSelectAll() {
    const selectAllCb = document.getElementById("selectAll");
    const checkboxes = document.querySelectorAll(".product-checkbox");
    checkboxes.forEach(cb => cb.checked = selectAllCb.checked);
    updateBulkDeleteButton();
}

function updateBulkDeleteButton() {
    const selected = document.querySelectorAll(".product-checkbox:checked");
    const bulkBtn = document.getElementById("bulkDeleteBtn");
    if (bulkBtn) {
        bulkBtn.style.display = selected.length > 0 ? "inline-block" : "none";
        bulkBtn.innerText = `Delete Selected (${selected.length})`;
    }
}

async function handleBulkDelete() {
    const selected = document.querySelectorAll(".product-checkbox:checked");
    const ids = Array.from(selected).map(cb => cb.value);

    if (confirm(`Delete ${ids.length} selected items?`)) {
        for (let id of ids) {
            await deleteProductApi(id);
        }
        showToast(`Batch delete completed (${ids.length} items)`);
        document.getElementById("selectAll").checked = false;
        loadDashboardData();
    }
}

// --- Modal & Validation ---
const modal = document.getElementById("productModal");
const openModalBtn = document.getElementById("openModalBtn");
const closeModalBtn = document.getElementById("closeModal");
const productForm = document.getElementById("productForm");
const nameInput = document.getElementById("productName");
const priceInput = document.getElementById("productPrice");
const saveBtn = document.getElementById("saveProductBtn");

openModalBtn.onclick = () => {
    productForm.reset();
    modal.style.display = "block";
};
closeModalBtn.onclick = () => modal.style.display = "none";

window.onclick = (event) => {
    if (event.target == modal) modal.style.display = "none";
};

// Frontend Real-time Validation
priceInput.oninput = () => {
    const priceError = document.getElementById("priceError");
    if (parseFloat(priceInput.value) < 0) {
        saveBtn.disabled = true;
        priceError.style.display = "block";
    } else {
        saveBtn.disabled = false;
        priceError.style.display = "none";
    }
};

productForm.onsubmit = async (e) => {
    e.preventDefault();

    const newProduct = {
        name: nameInput.value,
        description: "Admin Entry",
        price: parseFloat(priceInput.value),
        stock_quantity: parseInt(document.getElementById("productStock").value),
        category_id: 1, vendor_id: 1
    };

    const response = await addProductApi(newProduct);
    if (response.ok) {
        showToast("Product added to catalog!");
        modal.style.display = "none";
        productForm.reset();
        loadDashboardData();
    } else {
        showToast("Failed to save product", "error");
    }
};
