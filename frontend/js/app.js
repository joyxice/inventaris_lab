const API = "/api";
const $ = (selector) => document.querySelector(selector);
let editingId = null;
let toastTimer;

document.addEventListener("DOMContentLoaded", () => {
  $("#today").textContent = new Intl.DateTimeFormat("id-ID", {
    weekday: "long", day: "numeric", month: "long", year: "numeric"
  }).format(new Date());

  loadDashboard();
  loadItems();

  $("#addItemBtn").addEventListener("click", () => openModal());
  $("#closeModal").addEventListener("click", closeModal);
  $("#cancelModal").addEventListener("click", closeModal);
  $("#itemModal").addEventListener("click", (event) => {
    if (event.target === $("#itemModal")) closeModal();
  });
  $("#itemForm").addEventListener("submit", saveItem);
  $("#searchInput").addEventListener("input", debounce(loadItems, 250));
  $("#conditionFilter").addEventListener("change", loadItems);
  $("#refreshBtn").addEventListener("click", () => {
    loadDashboard();
    loadItems();
  });
});

async function api(url, options = {}) {
  const response = await fetch(`${API}${url}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || "Terjadi kesalahan pada server");
  return data;
}

async function loadDashboard() {
  try {
    const data = await api("/dashboard");
    $("#totalItems").textContent = data.total_items;
    $("#totalQuantity").textContent = data.total_quantity.toLocaleString("id-ID");
    $("#totalCategories").textContent = data.total_categories;
    $("#goodCount").textContent = data.good;
    $("#repairCount").textContent = data.repair;
    $("#needsRepair").textContent = data.repair;
  } catch (error) {
    showToast(error.message);
  }
}

async function loadItems() {
  const params = new URLSearchParams({
    search: $("#searchInput").value.trim(),
    condition: $("#conditionFilter").value
  });
  try {
    const items = await api(`/items?${params}`);
    renderItems(items);
  } catch (error) {
    $("#inventoryBody").innerHTML = `<tr><td colspan="7" class="empty-state">${escapeHtml(error.message)}</td></tr>`;
  }
}

function renderItems(items) {
  $("#itemCount").textContent = `Menampilkan ${items.length} barang`;
  if (!items.length) {
    $("#inventoryBody").innerHTML = '<tr><td colspan="7" class="empty-state">Belum ada data barang. Klik “Tambah Barang” untuk memulai.</td></tr>';
    return;
  }
  $("#inventoryBody").innerHTML = items.map(item => {
    const statusClass = item.condition.toLowerCase().replaceAll(" ", "-");
    return `<tr>
      <td>${escapeHtml(item.code)}</td>
      <td>${escapeHtml(item.name)}</td>
      <td>${escapeHtml(item.category)}</td>
      <td><span class="stock">${item.quantity} ${escapeHtml(item.unit)}</span></td>
      <td>${escapeHtml(item.location)}</td>
      <td><span class="status status-${statusClass}">${escapeHtml(item.condition)}</span></td>
      <td><div class="actions">
        <button class="action-btn" data-edit="${item.id}">Edit</button>
        <button class="action-btn" data-delete="${item.id}">Hapus</button>
      </div></td>
    </tr>`;
  }).join("");

  document.querySelectorAll("[data-edit]").forEach(button => {
    button.addEventListener("click", () => editItem(Number(button.dataset.edit)));
  });
  document.querySelectorAll("[data-delete]").forEach(button => {
    button.addEventListener("click", () => removeItem(Number(button.dataset.delete)));
  });
}

function openModal(item = null) {
  editingId = item ? item.id : null;
  const form = $("#itemForm");
  form.reset();
  if (item) {
    Object.entries(item).forEach(([key, value]) => {
      if (form.elements[key]) form.elements[key].value = value ?? "";
    });
  } else {
    form.elements.quantity.value = 1;
    form.elements.condition.value = "Baik";
  }
  $("#modalTitle").textContent = item ? "Edit Barang" : "Tambah Barang";
  $("#saveBtn").textContent = item ? "Simpan Perubahan" : "Simpan Barang";
  $("#itemModal").classList.remove("hidden");
  form.elements.code.focus();
}

function closeModal() {
  $("#itemModal").classList.add("hidden");
  editingId = null;
}

async function editItem(id) {
  try {
    const item = await api(`/items/${id}`);
    openModal(item);
  } catch (error) {
    showToast(error.message);
  }
}

async function saveItem(event) {
  event.preventDefault();
  const formData = new FormData(event.currentTarget);
  const payload = Object.fromEntries(formData.entries());
  payload.quantity = Number(payload.quantity);

  const isEditing = editingId !== null;
  try {
    await api(isEditing ? `/items/${editingId}` : "/items", {
      method: isEditing ? "PUT" : "POST",
      body: JSON.stringify(payload)
    });
    closeModal();
    await Promise.all([loadItems(), loadDashboard()]);
    showToast(isEditing ? "Data barang diperbarui" : "Barang berhasil ditambahkan");
  } catch (error) {
    showToast(error.message);
  }
}

async function removeItem(id) {
  if (!confirm("Yakin ingin menghapus barang ini? Tindakan ini tidak dapat dibatalkan.")) return;
  try {
    await api(`/items/${id}`, { method: "DELETE" });
    await Promise.all([loadItems(), loadDashboard()]);
    showToast("Barang berhasil dihapus");
  } catch (error) {
    showToast(error.message);
  }
}

function showToast(message) {
  const toast = $("#toast");
  toast.textContent = message;
  toast.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("show"), 2800);
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, char => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[char]);
}

function debounce(callback, delay) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => callback(...args), delay);
  };
}
