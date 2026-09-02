import { findDuplicates, getHistory, makePreview, scanFolder, sortPlan, undoOperation } from "./api.js";
import { escapeHtml, formatBytes, formatDate, formatTime } from "./format.js";
import { DEFAULT_RULES, describeRule, loadRules, saveRules } from "./rules.js";

const $ = selector => document.querySelector(selector);
const $$ = selector => [...document.querySelectorAll(selector)];
let state = { root: "", records: [], scan: null, duplicates: null, rules: loadRules(), plan: null, history: [] };

const toast = message => {
  const node = $("#toast"); node.textContent = message; node.classList.add("show");
  clearTimeout(toast.timer); toast.timer = setTimeout(() => node.classList.remove("show"), 3200);
};

const setBusy = (button, busy, label) => {
  if (!button) return;
  button.disabled = busy;
  if (busy) { button.dataset.original = button.innerHTML; button.innerHTML = `<span class="spinner">◌</span> ${label}`; }
  else if (button.dataset.original) button.innerHTML = button.dataset.original;
};

const showPage = page => {
  $$(".page").forEach(node => { node.hidden = node.id !== `page-${page}`; });
  $$(".nav-item").forEach(node => node.classList.toggle("active", node.dataset.page === page));
  $("#breadcrumb-page").textContent = page[0].toUpperCase() + page.slice(1);
  if (page === "files") renderFiles();
  if (page === "rules") renderRules();
  if (page === "history") renderHistory();
  if (page === "duplicates" && state.duplicates) renderDuplicates(state.duplicates);
};

const requireRoot = () => {
  if (!state.root) { toast("Enter a folder path first, then scan it."); showPage("dashboard"); $("#root-path").focus(); return false; }
  return true;
};

const scan = async (sourceButton) => {
  const path = $("#root-path").value.trim();
  if (!path) { toast("Enter the path to a folder on this device."); $("#root-path").focus(); return; }
  setBusy(sourceButton, true, "Scanning locally…");
  try {
    const result = await scanFolder(path, $("#include-hidden").checked);
    state.root = result.root; state.scan = result; state.records = result.files;
    $("#root-path").value = result.root;
    $("#welcome-card").hidden = true; $("#stats-grid").hidden = false; $("#dashboard-details").hidden = false; $("#recent-panel").hidden = false;
    renderDashboard(); renderFiles(); await refreshHistory();
    toast(`Scan complete · ${result.file_count.toLocaleString()} files found`);
  } catch (error) { toast(error.message); }
  finally { setBusy(sourceButton, false); }
};

const renderDashboard = () => {
  const result = state.scan; if (!result) return;
  $("#file-count").textContent = result.file_count.toLocaleString();
  $("#total-size").textContent = formatBytes(result.total_size);
  $("#folder-count").textContent = result.folder_count.toLocaleString();
  $("#scan-time").textContent = `Scanned ${new Date(result.last_scanned).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}`;
  $("#duplicate-count").textContent = state.duplicates ? state.duplicates.duplicate_count.toLocaleString() : "—";
  $("#duplicate-space").textContent = state.duplicates ? `${formatBytes(state.duplicates.reclaimable_bytes)} reclaimable` : "Run duplicate scan to check";
  const categories = Object.entries(result.category_counts).sort((a, b) => b[1] - a[1]);
  const max = Math.max(categories[0]?.[1] || 1, 1);
  $("#category-chart").innerHTML = categories.length ? categories.slice(0, 7).map(([category, count]) => `<div class="category-row"><span>${escapeHtml(category)}</span><div class="category-track"><div class="category-fill" style="width:${Math.max(4, count / max * 100)}%"></div></div><em>${count}</em></div>`).join("") : `<div class="empty-block"><p>No files found in this folder.</p></div>`;
  const suggestions = [];
  const unsorted = state.records.filter(record => record.category === "Other").length;
  if (result.file_count) suggestions.push({ mark: "✦", title: `${result.file_count.toLocaleString()} files ready for review`, copy: "Generate a safe sorting preview from your current rules." });
  if (unsorted) suggestions.push({ mark: "?", title: `${unsorted.toLocaleString()} files need a custom rule`, copy: "These files are currently classified as Other." });
  if (state.duplicates?.group_count) suggestions.push({ mark: "◈", title: `${state.duplicates.group_count} duplicate groups found`, copy: `${formatBytes(state.duplicates.reclaimable_bytes)} may be recoverable after your review.` });
  $("#suggestions-list").innerHTML = suggestions.length ? suggestions.map(item => `<div class="suggestion"><span class="suggestion-mark">${item.mark}</span><div><strong>${item.title}</strong><p>${item.copy}</p></div></div>`).join("") : `<div class="empty-block"><p>Scan a folder to see suggestions.</p></div>`;
  $("#duplicate-nav-count").textContent = state.duplicates ? state.duplicates.group_count : "—";
};

const renderFiles = () => {
  const search = ($("#file-search")?.value || "").toLowerCase().trim();
  const category = $("#category-filter")?.value || "";
  const sort = $("#sort-files")?.value || "name";
  let records = state.records.filter(record => (!category || record.category === category) && (!search || `${record.name} ${record.relative_path} ${record.category} ${record.extension}`.toLowerCase().includes(search)));
  records = [...records].sort((a, b) => sort === "size" ? b.size - a.size : sort === "modified" ? new Date(b.modified) - new Date(a.modified) : a.name.localeCompare(b.name));
  if ($("#file-result-count")) $("#file-result-count").textContent = `${records.length.toLocaleString()} file${records.length === 1 ? "" : "s"}`;
  if ($("#files-subtitle")) $("#files-subtitle").textContent = state.root ? `${state.root} · ${state.records.length.toLocaleString()} scanned` : "Scan a folder to inspect its metadata.";
  const categories = [...new Set(state.records.map(record => record.category))].sort();
  if ($("#category-filter")) {
    const selected = $("#category-filter").value;
    $("#category-filter").innerHTML = `<option value="">All categories</option>${categories.map(item => `<option ${item === selected ? "selected" : ""}>${escapeHtml(item)}</option>`).join("")}`;
  }
  $("#file-table").innerHTML = records.length ? records.slice(0, 250).map(record => `<div class="file-row"><div class="file-name" title="${escapeHtml(record.path)}"><span class="file-type">${escapeHtml(record.extension || "—").slice(0, 4)}</span><span>${escapeHtml(record.name)}</span></div><span class="file-category">${escapeHtml(record.category)}</span><span class="file-size">${formatBytes(record.size)}</span><span class="file-date">${formatDate(record.modified)}</span></div>`).join("") : `<div class="empty-block"><div class="empty-icon">▤</div><h3>${state.records.length ? "No files match" : "Nothing to show yet"}</h3><p>${state.records.length ? "Try a different search or category." : "Scan a folder to populate your library."}</p></div>`;
};

const scanDuplicates = async () => {
  if (!requireRoot()) return;
  const button = $("#duplicate-scan"); setBusy(button, true, "Hashing locally…");
  try { state.duplicates = await findDuplicates(state.root, $("#include-hidden").checked); renderDuplicates(state.duplicates); renderDashboard(); toast(`Duplicate scan complete · ${state.duplicates.group_count} groups`); }
  catch (error) { toast(error.message); } finally { setBusy(button, false); }
};

const renderDuplicates = result => {
  const numbers = $("#duplicate-summary").querySelectorAll(".big-number");
  numbers[0].textContent = result.group_count.toLocaleString(); numbers[1].textContent = formatBytes(result.reclaimable_bytes);
  $("#duplicate-groups").className = result.groups.length ? "duplicate-groups" : "duplicate-groups empty-block";
  $("#duplicate-groups").innerHTML = result.groups.length ? result.groups.map((group, index) => `<div class="duplicate-group"><div class="duplicate-group-heading"><strong>Group ${index + 1} · ${formatBytes(group.size)} each</strong><span>${group.files.length} matching files</span></div>${group.files.map(file => `<div class="duplicate-file"><span>▤ &nbsp; ${escapeHtml(file.name)} <small>${escapeHtml(file.relative_path)}</small></span><em>${formatBytes(file.size)}</em></div>`).join("")}</div>`).join("") : `<div class="empty-icon">✓</div><h3>No exact duplicates found</h3><p>Every scanned file has a unique content hash.</p>`;
};

const openPreview = async () => {
  if (!requireRoot()) return;
  if (!state.records.length) { toast("There are no files to organize in this folder."); return; }
  const button = $("#scan-button"); setBusy(button, true, "Preparing preview…");
  try {
    state.plan = await makePreview(state.root, state.records, state.rules);
    $("#preview-subtitle").textContent = `${state.plan.count} file${state.plan.count === 1 ? "" : "s"} would move · nothing has changed yet`;
    $("#preview-skipped").textContent = state.plan.skipped.length ? `${state.plan.skipped.length} skipped safely` : "All matching files shown";
    $("#preview-list").innerHTML = state.plan.moves.length ? state.plan.moves.slice(0, 100).map(item => `<div class="preview-row"><span class="preview-path" title="${escapeHtml(item.source)}">${escapeHtml(item.relative_source)}<small>${escapeHtml(item.rule)}</small></span><span class="preview-arrow">→</span><span class="preview-path" title="${escapeHtml(item.destination)}">${escapeHtml(item.relative_destination)}<small>collision-safe destination</small></span></div>`).join("") : `<div class="empty-block"><h3>No files matched your enabled rules</h3><p>Add a rule or choose another folder.</p></div>`;
    $("#approve-sort").disabled = !state.plan.moves.length; $("#preview-modal").hidden = false;
  } catch (error) { toast(error.message); } finally { setBusy(button, false); }
};

const approveSort = async () => {
  if (!state.plan?.moves.length) return;
  const button = $("#approve-sort"); setBusy(button, true, "Sorting safely…");
  try {
    const result = await sortPlan(state.plan);
    $("#preview-modal").hidden = true;
    toast(result.count ? `${result.count} files organized · undo is available in Activity` : "No files were moved.");
    await scan($("#scan-button"));
    if (result.errors?.length) toast(`${result.count} moved · ${result.errors.length} could not be moved`);
  } catch (error) { toast(error.message); } finally { setBusy(button, false); }
};

const renderRules = () => {
  $("#rules-list").innerHTML = state.rules.map((rule, index) => `<div class="rule-card"><span class="rule-priority">${String(index + 1).padStart(2, "0")}</span><div class="rule-detail"><strong>${escapeHtml(rule.name)}</strong><p>${escapeHtml(describeRule(rule))}</p></div><span class="rule-destination">→ ${escapeHtml(rule.destination)}</span><span class="rule-status ${rule.enabled ? "" : "off"}">${rule.enabled ? "Enabled" : "Paused"}</span><button class="rule-switch ${rule.enabled ? "" : "off"}" data-rule-toggle="${escapeHtml(rule.id)}" aria-label="Toggle ${escapeHtml(rule.name)}"></button></div>`).join("");
};

const refreshHistory = async () => { try { state.history = (await getHistory()).history || []; renderHistory(); } catch { /* history is optional if the local store is unavailable */ } };
const renderHistory = () => {
  $("#history-list").innerHTML = state.history.length ? state.history.map(item => `<div class="history-item"><span class="history-mark">${item.status === "failed" ? "!" : "✓"}</span><div class="history-copy"><strong>${item.status === "undone" ? "Sort undone" : "Sorted folder"}</strong><p>${item.count || 0} files · ${item.errors?.length ? `${item.errors.length} errors · ` : ""}${escapeHtml(item.root || "local folder")}</p></div><time class="history-time">${formatTime(item.timestamp)}</time>${item.status !== "undone" && item.moved?.length ? `<button class="undo-button" data-undo="${escapeHtml(item.operation_id)}">Undo</button>` : ""}</div>`).join("") : `<div class="empty-block"><div class="empty-icon">◷</div><h3>No activity yet</h3><p>Approved sorting operations will appear here.</p></div>`;
};

const initTheme = () => {
  const saved = localStorage.getItem("sortix-theme") || "system";
  $("#settings-theme").value = saved; applyTheme(saved);
  $("#settings-theme").addEventListener("change", event => { localStorage.setItem("sortix-theme", event.target.value); applyTheme(event.target.value); });
  $("#settings-hidden").checked = $("#include-hidden").checked;
  $("#settings-hidden").addEventListener("change", event => { $("#include-hidden").checked = event.target.checked; });
};
const applyTheme = mode => document.documentElement.dataset.theme = mode === "system" ? (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light") : mode;

document.addEventListener("click", async event => {
  const pageButton = event.target.closest("[data-page], [data-page-link]");
  if (pageButton) { showPage(pageButton.dataset.page || pageButton.dataset.pageLink); return; }
  if (event.target.closest("[data-close-modal]")) { event.target.closest(".modal-backdrop").hidden = true; return; }
  const toggle = event.target.closest("[data-rule-toggle]");
  if (toggle) { const rule = state.rules.find(item => item.id === toggle.dataset.ruleToggle); if (rule) { rule.enabled = !rule.enabled; saveRules(state.rules); renderRules(); } return; }
  const undoButton = event.target.closest("[data-undo]");
  if (undoButton) { undoButton.disabled = true; try { await undoOperation(undoButton.dataset.undo); toast("Files restored to their previous locations."); await refreshHistory(); if (state.root) await scan($("#scan-button")); } catch (error) { toast(error.message); undoButton.disabled = false; } }
});

$("#scan-button").addEventListener("click", () => scan($("#scan-button")));
$("#welcome-scan").addEventListener("click", () => { $("#root-path").focus(); toast("Enter the folder path above, then scan it."); });
$("#files-scan").addEventListener("click", () => scan($("#files-scan")));
$("#duplicate-scan").addEventListener("click", scanDuplicates);
$("#approve-sort").addEventListener("click", approveSort);
$("#theme-toggle").addEventListener("click", () => { const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark"; localStorage.setItem("sortix-theme", next); applyTheme(next); $("#settings-theme").value = next; });
$("#clear-folder").addEventListener("click", () => { $("#root-path").value = ""; state = { ...state, root: "", records: [], scan: null, duplicates: null }; $("#welcome-card").hidden = false; $("#stats-grid").hidden = true; $("#dashboard-details").hidden = true; $("#recent-panel").hidden = true; renderFiles(); });
$("#file-search").addEventListener("input", renderFiles); $("#category-filter").addEventListener("change", renderFiles); $("#sort-files").addEventListener("change", renderFiles);
$("#add-rule").addEventListener("click", () => { $("#rule-form").reset(); $("#rule-modal").hidden = false; });
$("#rule-form").addEventListener("submit", event => { event.preventDefault(); const data = new FormData(event.target); const rule = { id: `custom-${Date.now()}`, name: data.get("name"), enabled: true, conditions: [{ field: data.get("field"), operator: data.get("operator"), value: data.get("value") }], destination: data.get("destination") }; state.rules.push(rule); saveRules(state.rules); renderRules(); $("#rule-modal").hidden = true; toast("Rule saved and ready for preview."); });
$("#include-hidden").addEventListener("change", event => { $("#settings-hidden").checked = event.target.checked; });

initTheme(); renderRules(); renderFiles(); refreshHistory();