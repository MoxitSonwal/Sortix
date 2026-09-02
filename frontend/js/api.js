const request = async (path, options = {}) => {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
    body: options.body && typeof options.body !== "string" ? JSON.stringify(options.body) : options.body,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || "Sortix could not complete that request.");
  return data;
};

export const scanFolder = (path, includeHidden) => request("/api/scan", { method: "POST", body: { path, include_hidden: includeHidden } });
export const makePreview = (root, records, rules) => request("/api/preview", { method: "POST", body: { root, records, rules } });
export const sortPlan = (plan) => request("/api/sort", { method: "POST", body: plan });
export const undoOperation = (operationId) => request("/api/undo", { method: "POST", body: { operation_id: operationId } });
export const findDuplicates = (path, includeHidden) => request("/api/duplicates", { method: "POST", body: { path, include_hidden: includeHidden } });
export const getHistory = () => request("/api/history");