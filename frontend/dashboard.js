"use strict";

const API = "/api/v1";
const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
const COLORS = ["#4f46e5", "#16a34a", "#f59e0b", "#ef4444", "#06b6d4", "#8b5cf6", "#ec4899", "#14b8a6", "#f97316", "#64748b"];
const inr = new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR" });
const money = (n) => inr.format(Number(n) || 0);
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

const state = {
  categories: [], comparison: [], transactions: [],
  prediction: null, categoryTouched: false,
  editingTx: null, editingBudgetId: null, charts: {},
};

/* ---------- helpers ---------- */
async function api(path, options = {}) {
  let res;
  try {
    res = await fetch(API + path, { headers: { "Content-Type": "application/json" }, ...options });
  } catch (err) {
    throw new Error("Unable to connect to the server. Please make sure the backend is running.");
  }
  let data = null;
  try { data = await res.json(); } catch (_) { /* empty body */ }
  if (!res.ok) throw new Error((data && typeof data.detail === "string" && data.detail) || `Request failed (${res.status}).`);
  return data;
}

function toast(message, type = "info") {
  const el = document.createElement("div");
  el.className = `toast ${type}`;
  el.textContent = message;
  $("toasts").appendChild(el);
  setTimeout(() => el.remove(), 4500);
}

const reportError = (err) => toast(err.message || "Something went wrong.", "error");
const todayISO = () => { const d = new Date(); return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`; };
const period = () => { const [year, month] = $("monthPicker").value.split("-").map(Number); return { month, year }; };
const periodQuery = () => { const p = period(); return `month=${p.month}&year=${p.year}`; };
const debounce = (fn, ms) => { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; };

/* ---------- categories ---------- */
async function loadCategories() {
  state.categories = await api("/categories");
  const options = state.categories.map((c) => `<option value="${c.id}">${esc(c.name)}</option>`).join("");
  $("category").innerHTML = `<option value="">AI will automatically detect category</option>${options}`;
  $("budgetCategory").innerHTML = options;
  $("filterCategory").innerHTML = `<option value="">All categories</option>${options}`;
}

/* ---------- summary ---------- */
async function loadSummary() {
  const s = await api(`/dashboard/summary?${periodQuery()}`);
  $("totalSpending").textContent = money(s.total_spending);
  $("monthlyBudget").textContent = money(s.monthly_budget);
  $("remainingBudget").textContent = money(s.remaining_budget);
  $("remainingBudget").style.color = s.remaining_budget < 0 ? "var(--danger)" : "";
  $("remainingNote").textContent = s.monthly_budget ? (s.remaining_budget < 0 ? "Over total budget" : "Left to spend") : "No budgets set";
  $("txCount").textContent = s.transaction_count;
  $("topCategory").textContent = s.highest_category ? `Top: ${s.highest_category} (${money(s.highest_category_amount)})` : "No spending yet";
}

/* ---------- transactions ---------- */
async function loadTransactions() {
  const params = new URLSearchParams(periodQuery());
  const filters = { search: $("filterSearch").value.trim(), category_id: $("filterCategory").value, date: $("filterDate").value, min_amount: $("filterMin").value, max_amount: $("filterMax").value };
  Object.entries(filters).forEach(([k, v]) => { if (v !== "") params.set(k, v); });
  state.transactions = await api(`/transactions?${params}`);
  renderTransactions();
}

function renderTransactions() {
  const body = $("txBody");
  if (!state.transactions.length) {
    body.innerHTML = `<tr><td colspan="7" style="text-align:center;color:var(--muted);padding:1.5rem">No transactions found.</td></tr>`;
    return;
  }
  body.innerHTML = state.transactions.map((t) => {
    const conf = t.prediction_confidence == null ? "—" : `${Math.round(t.prediction_confidence * 100)}%`;
    return `<tr>
      <td>${esc(t.transaction_date)}</td>
      <td title="${esc(t.notes || "")}">${esc(t.description)}</td>
      <td><span class="badge">${esc(t.category)}</span></td>
      <td class="num">${money(t.amount)}</td>
      <td>${esc(t.payment_method)}</td>
      <td>${conf}</td>
      <td><button class="btn small" data-edit="${t.id}">Edit</button> <button class="btn small danger" data-del="${t.id}">Delete</button></td>
    </tr>`;
  }).join("");
}

/* ---------- AI prediction ---------- */
function clearPrediction() {
  state.prediction = null;
  $("aiBox").className = "ai-box muted";
  $("aiBox").textContent = "🤖 AI will suggest a category as you type.";
}

function renderPrediction() {
  const p = state.prediction;
  const pct = Math.round(p.confidence * 100);
  $("aiBox").className = `ai-box${p.low_confidence ? " low" : ""}`;
  $("aiBox").innerHTML = `<span>🤖 AI Category: <strong>${esc(p.category)}</strong></span><span>Confidence: ${pct}%</span>` +
    (p.low_confidence ? `<span>⚠ Low confidence — please check.</span>` : "") +
    `<button type="button" class="btn small" id="acceptBtn">Accept Prediction</button>`;
  $("acceptBtn").addEventListener("click", () => { selectCategoryByName(p.category); state.categoryTouched = true; toast(`Category set to ${p.category}.`, "success"); });
}

function selectCategoryByName(name) {
  const cat = state.categories.find((c) => c.name === name);
  if (cat) $("category").value = String(cat.id);
}

async function runPrediction() {
  const description = $("description").value.trim();
  if (!description) { clearPrediction(); return; }
  try {
    const r = await api("/transactions/categorize", { method: "POST", body: JSON.stringify({ description }) });
    if (description !== $("description").value.trim()) return; // user kept typing
    state.prediction = { category: r.predicted_category, confidence: r.confidence, low_confidence: r.low_confidence };
    renderPrediction();
    if (!state.categoryTouched) selectCategoryByName(r.predicted_category);
  } catch (err) {
    $("aiBox").className = "ai-box muted";
    $("aiBox").textContent = "AI prediction unavailable — please choose a category manually.";
  }
}

/* ---------- transaction form ---------- */
function resetTxForm() {
  $("txForm").reset();
  $("txDate").value = todayISO();
  state.editingTx = null; state.categoryTouched = false;
  $("formTitle").textContent = "Add Expense";
  $("saveBtn").textContent = "Save Transaction";
  $("cancelEditBtn").hidden = true;
  clearPrediction();
}

async function submitTransaction(e) {
  e.preventDefault();
  const description = $("description").value.trim();
  const amount = parseFloat($("amount").value);
  const date = $("txDate").value;
  if (!description) return toast("Please enter a description.", "error");
  if (!(amount > 0)) return toast("Amount must be greater than zero.", "error");
  if (!date) return toast("Please choose a valid date.", "error");

  let categoryId = Number($("category").value);
  if (!categoryId && state.prediction) {
    const cat = state.categories.find((c) => c.name === state.prediction.category);
    if (cat) categoryId = cat.id;
  }
  if (!categoryId) return toast("Please choose a category.", "error");

  const old = state.editingTx;
  const payload = {
    description, amount, transaction_date: date,
    payment_method: $("paymentMethod").value, category_id: categoryId,
    notes: $("notes").value.trim() || null,
    predicted_category: state.prediction ? state.prediction.category : (old ? old.predicted_category : null),
    prediction_confidence: state.prediction ? state.prediction.confidence : (old ? old.prediction_confidence : null),
  };
  try {
    const editing = Boolean(old);
    await api(editing ? `/transactions/${old.id}` : "/transactions", { method: editing ? "PUT" : "POST", body: JSON.stringify(payload) });
    toast(editing ? "Transaction updated." : "Transaction saved.", "success");
    resetTxForm();
    await refreshAll();
    const row = state.comparison.find((r) => r.category_id === categoryId);
    if (row && row.status !== "safe") toast(alertText(row), row.status === "exceeded" ? "error" : "warning");
  } catch (err) { reportError(err); }
}

function startEdit(id) {
  const t = state.transactions.find((x) => x.id === id);
  if (!t) return;
  state.editingTx = t; state.categoryTouched = true; state.prediction = null;
  $("description").value = t.description;
  $("amount").value = t.amount;
  $("txDate").value = t.transaction_date;
  $("paymentMethod").value = t.payment_method;
  $("category").value = String(t.category_id);
  $("notes").value = t.notes || "";
  $("formTitle").textContent = `Edit Expense #${t.id}`;
  $("saveBtn").textContent = "Update Transaction";
  $("cancelEditBtn").hidden = false;
  $("aiBox").className = "ai-box muted";
  $("aiBox").textContent = t.predicted_category ? `🤖 Original AI prediction: ${t.predicted_category}` : "Editing transaction.";
  $("txForm").scrollIntoView({ behavior: "smooth", block: "center" });
}

async function deleteTransaction(id) {
  if (!confirm("Delete this transaction?")) return;
  try {
    await api(`/transactions/${id}`, { method: "DELETE" });
    toast("Transaction deleted.", "success");
    if (state.editingTx && state.editingTx.id === id) resetTxForm();
    await refreshAll();
  } catch (err) { reportError(err); }
}

/* ---------- budgets, alerts, charts ---------- */
function alertText(r) {
  if (r.status === "exceeded") {
    return r.remaining < 0 ? `🚨 ${r.category} budget exceeded by ${money(-r.remaining)}.` : `🚨 ${r.category} budget fully used (100%).`;
  }
  return `⚠ ${r.category} budget is ${Math.floor(r.percentage_used)}% used.`;
}

function renderAlerts() {
  const items = state.comparison.filter((r) => r.status !== "safe");
  $("alerts").innerHTML = items.map((r) => `<div class="alert ${r.status}">${esc(alertText(r))}</div>`).join("");
}

function renderBudgets() {
  const list = $("budgetList");
  if (!state.comparison.length) {
    list.innerHTML = `<p style="color:var(--muted)">No budgets for ${MONTHS[period().month - 1]} ${period().year}. Add one above.</p>`;
    return;
  }
  list.innerHTML = state.comparison.map((r) => `
    <div class="budget-item">
      <div class="head"><strong>${esc(r.category)}</strong>
        <span><button class="btn small" data-bedit="${r.budget_id}">Edit</button> <button class="btn small danger" data-bdel="${r.budget_id}">Delete</button></span></div>
      <div class="meta">${money(r.actual)} / ${money(r.budget)} &nbsp;•&nbsp; ${r.percentage_used.toFixed(1)}%</div>
      <div class="progress"><div class="${r.status}" style="width:${Math.min(r.percentage_used, 100)}%"></div></div>
    </div>`).join("");
}

function drawChart(key, canvasId, emptyId, hasData, config) {
  if (state.charts[key]) { state.charts[key].destroy(); state.charts[key] = null; }
  $(emptyId).hidden = hasData;
  $(canvasId).style.display = hasData ? "block" : "none";
  if (hasData && window.Chart) state.charts[key] = new Chart($(canvasId), config);
}

async function loadCharts() {
  const [spending, comparison] = await Promise.all([
    api(`/dashboard/category-spending?${periodQuery()}`),
    api(`/dashboard/budget-comparison?${periodQuery()}`),
  ]);
  state.comparison = comparison;
  renderAlerts();
  renderBudgets();

  drawChart("pie", "pieChart", "pieEmpty", spending.length > 0, {
    type: "doughnut",
    data: { labels: spending.map((s) => s.category), datasets: [{ data: spending.map((s) => s.amount), backgroundColor: COLORS }] },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: "right" },
      tooltip: { callbacks: { label: (c) => ` ${c.label}: ${money(c.parsed)}` } } } },
  });
  drawChart("bar", "barChart", "barEmpty", comparison.length > 0, {
    type: "bar",
    data: { labels: comparison.map((c) => c.category), datasets: [
      { label: "Budget", data: comparison.map((c) => c.budget), backgroundColor: "#a5b4fc" },
      { label: "Actual", data: comparison.map((c) => c.actual), backgroundColor: comparison.map((c) => ({ safe: "#16a34a", warning: "#f59e0b", exceeded: "#ef4444" }[c.status])) },
    ] },
    options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true, ticks: { callback: (v) => money(v) } } },
      plugins: { tooltip: { callbacks: { label: (c) => ` ${c.dataset.label}: ${money(c.parsed.y)}` } } } },
  });
}

function resetBudgetForm() {
  const p = period();
  state.editingBudgetId = null;
  $("budgetMonth").value = String(p.month);
  $("budgetYear").value = p.year;
  $("budgetAmount").value = "";
  $("budgetSaveBtn").textContent = "Save Budget";
  $("budgetCancelBtn").hidden = true;
}

async function submitBudget(e) {
  e.preventDefault();
  const amount = parseFloat($("budgetAmount").value);
  const month = Number($("budgetMonth").value), year = Number($("budgetYear").value);
  if (!(amount > 0)) return toast("Budget amount must be greater than zero.", "error");
  if (!year) return toast("Please enter a valid year.", "error");
  const payload = { category_id: Number($("budgetCategory").value), month, year, budget_amount: amount };
  try {
    const id = state.editingBudgetId;
    await api(id ? `/budgets/${id}` : "/budgets", { method: id ? "PUT" : "POST", body: JSON.stringify(payload) });
    toast(id ? "Budget updated." : "Budget saved.", "success");
    $("monthPicker").value = `${year}-${String(month).padStart(2, "0")}`; // show the month just edited
    resetBudgetForm();
    await refreshAll();
  } catch (err) { reportError(err); }
}

function startBudgetEdit(id) {
  const r = state.comparison.find((x) => x.budget_id === id);
  if (!r) return;
  state.editingBudgetId = id;
  $("budgetCategory").value = String(r.category_id);
  $("budgetMonth").value = String(r.month);
  $("budgetYear").value = r.year;
  $("budgetAmount").value = r.budget;
  $("budgetSaveBtn").textContent = "Update Budget";
  $("budgetCancelBtn").hidden = false;
  $("budgetForm").scrollIntoView({ behavior: "smooth", block: "center" });
}

async function deleteBudget(id) {
  if (!confirm("Delete this budget?")) return;
  try {
    await api(`/budgets/${id}`, { method: "DELETE" });
    toast("Budget deleted.", "success");
    await refreshAll();
  } catch (err) { reportError(err); }
}

/* ---------- refresh & init ---------- */
async function refreshAll() {
  try { await Promise.all([loadSummary(), loadTransactions(), loadCharts()]); }
  catch (err) { reportError(err); }
}

async function init() {
  const now = new Date();
  $("monthPicker").value = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
  $("budgetMonth").innerHTML = MONTHS.map((m, i) => `<option value="${i + 1}">${m}</option>`).join("");
  resetBudgetForm();
  $("txDate").value = todayISO();
  try { await loadCategories(); } catch (err) { reportError(err); }

  $("monthPicker").addEventListener("change", () => { if ($("monthPicker").value) { resetBudgetForm(); refreshAll(); } });
  $("txForm").addEventListener("submit", submitTransaction);
  $("cancelEditBtn").addEventListener("click", resetTxForm);
  $("description").addEventListener("input", debounce(runPrediction, 600));
  $("description").addEventListener("blur", runPrediction);
  $("category").addEventListener("change", () => { state.categoryTouched = $("category").value !== ""; });
  $("budgetForm").addEventListener("submit", submitBudget);
  $("budgetCancelBtn").addEventListener("click", resetBudgetForm);

  const reload = debounce(() => loadTransactions().catch(reportError), 300);
  ["filterSearch", "filterCategory", "filterDate", "filterMin", "filterMax"].forEach((id) => $(id).addEventListener("input", reload));
  $("clearFilters").addEventListener("click", () => {
    ["filterSearch", "filterCategory", "filterDate", "filterMin", "filterMax"].forEach((id) => { $(id).value = ""; });
    reload();
  });

  $("txBody").addEventListener("click", (e) => {
    const edit = e.target.closest("[data-edit]"), del = e.target.closest("[data-del]");
    if (edit) startEdit(Number(edit.dataset.edit));
    if (del) deleteTransaction(Number(del.dataset.del));
  });
  $("budgetList").addEventListener("click", (e) => {
    const edit = e.target.closest("[data-bedit]"), del = e.target.closest("[data-bdel]");
    if (edit) startBudgetEdit(Number(edit.dataset.bedit));
    if (del) deleteBudget(Number(del.dataset.bdel));
  });

  await refreshAll();
}

document.addEventListener("DOMContentLoaded", init);
