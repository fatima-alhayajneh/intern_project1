let allProducts = [];

document.addEventListener('DOMContentLoaded', () => {
    loadDashboardData();

    const refreshBtn = document.getElementById("refreshBtn");
    if (refreshBtn) {
        refreshBtn.onclick = loadDashboardData;
    }

    const searchInput = document.getElementById("searchInput");
    if (searchInput) {
        searchInput.addEventListener("input", handleSearch);
    }
});

async function handleLogin() {
    const user = document.getElementById("username").value;
    const pass = document.getElementById("password").value;
    const status = document.getElementById("loginStatus");

    status.innerText = "Attempting login...";
    
    const success = await loginApi(user, pass);
    
    if (success) {
        status.innerText = "Logged in successfully!";
        status.style.color = "green";
        setTimeout(() => {
            document.getElementById("loginSection").style.display = "none";
        }, 1000);
    } else {
        status.innerText = "Login failed!";
        status.style.color = "red";
    }
}

async function loadDashboardData() {
    const tableBody = document.getElementById("productTableBody");
    const refreshBtn = document.getElementById("refreshBtn");

    if (refreshBtn) refreshBtn.innerText = "Loading...";
    tableBody.innerHTML = "<tr><td colspan='6'>Loading products...</td></tr>";

    try {
        allProducts = await fetchProductsApi();
        renderTable(allProducts);
    } catch (error) {
        tableBody.innerHTML = "<tr><td colspan='6' style='color:red'>Error loading data!</td></tr>";
    } finally {
        if (refreshBtn) refreshBtn.innerText = "Refresh Data";
    }
}

function handleSearch(e) {
    const term = e.target.value.toLowerCase();
    
    let filtered = allProducts.filter(product => 
        product.name.toLowerCase().includes(term)
    );

    filtered.sort((a, b) => {
        const nameA = a.name.toLowerCase();
        const nameB = b.name.toLowerCase();

        const startsWithA = nameA.startsWith(term);
        const startsWithB = nameB.startsWith(term);

        if (startsWithA && !startsWithB) return -1;
        if (!startsWithA && startsWithB) return 1;

        return nameA.localeCompare(nameB);
    });

    renderTable(filtered);
}

function renderTable(products) {
    const tableBody = document.getElementById("productTableBody");
    tableBody.innerHTML = "";

    if (products.length === 0) {
        tableBody.innerHTML = "<tr><td colspan='6'>No products found.</td></tr>";
        return;
    }

    products.forEach(product => {
        const row = document.createElement("tr");
        const stockValue = product.stock_quantity ?? (product.stock || 0);
        const stockClass = stockValue < 10 ? "low-stock" : "";

        row.innerHTML = `
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
}

async function handleRestock(id) {
    const success = await restockProductApi(id);
    if (success) {
        loadDashboardData();
    } else {
        alert("Failed to update stock.");
    }
}

window.handleDelete = async function(id) {
    console.log("DELETE CLICKED", id);

    if (confirm("Are you sure?")) {
        const success = await deleteProductApi(id);

        if (success) {
            loadDashboardData();
        } else {
            alert("Delete failed");
        }
    }
};

// Modal
const modal = document.getElementById("productModal");
const openModalBtn = document.getElementById("openModalBtn");
const closeModalBtn = document.getElementById("closeModal");
const productForm = document.getElementById("productForm");
const nameInput = document.getElementById("productName");
const priceInput = document.getElementById("productPrice");
const saveBtn = document.getElementById("saveProductBtn");

openModalBtn.onclick = () => modal.style.display = "block";
closeModalBtn.onclick = () => modal.style.display = "none";

window.onclick = (event) => {
    if (event.target == modal) modal.style.display = "none";
};

priceInput.oninput = () => {
    if (parseFloat(priceInput.value) < 0) {
        saveBtn.disabled = true;
        document.getElementById("priceError").style.display = "block";
    } else {
        saveBtn.disabled = false;
        document.getElementById("priceError").style.display = "none";
    }
};

productForm.onsubmit = async (e) => {
    e.preventDefault();

    const newProduct = {
        name: nameInput.value,
        description: "Standard Admin Product",
        price: parseFloat(priceInput.value),
        stock_quantity: parseInt(document.getElementById("productStock").value),
        category_id: 1,
        vendor_id: 1
    };

    const response = await addProductApi(newProduct);

    if (response.ok) {
        alert("Product Added Successfully!");
        modal.style.display = "none";
        productForm.reset();
        loadDashboardData();
    } else if (response.status === 401) {
        alert("Unauthorized! Please login.");
    } else {
        alert("Error adding product.");
    }
};
