export const DEFAULT_RULES = [
  { id: "images", name: "Images", enabled: true, conditions: [{ field: "category", operator: "is", value: "Images" }], destination: "Images" },
  { id: "videos", name: "Videos", enabled: true, conditions: [{ field: "category", operator: "is", value: "Videos" }], destination: "Videos" },
  { id: "pdfs", name: "PDFs", enabled: true, conditions: [{ field: "extension", operator: "is", value: "pdf" }], destination: "Documents/PDFs" },
  { id: "documents", name: "Documents", enabled: true, conditions: [{ field: "category", operator: "is", value: "Documents" }], destination: "Documents" },
  { id: "spreadsheets", name: "Spreadsheets", enabled: true, conditions: [{ field: "category", operator: "is", value: "Spreadsheets" }], destination: "Documents/Spreadsheets" },
  { id: "archives", name: "Archives", enabled: true, conditions: [{ field: "category", operator: "is", value: "Archives" }], destination: "Archives" },
  { id: "code", name: "Code", enabled: true, conditions: [{ field: "category", operator: "is", value: "Code" }], destination: "Code" },
];

export const loadRules = () => {
  try { return JSON.parse(localStorage.getItem("sortix-rules")) || DEFAULT_RULES; }
  catch { return DEFAULT_RULES; }
};

export const saveRules = rules => localStorage.setItem("sortix-rules", JSON.stringify(rules));

const fieldLabel = { category: "category", extension: "extension", filename: "filename", mime_type: "MIME type" };
export const describeRule = rule => {
  const conditions = (rule.conditions || []).map(condition => `${fieldLabel[condition.field] || condition.field} ${condition.operator.replace("_", " ")} “${condition.value}”`).join(" AND ");
  return `When ${conditions || "a file matches"} → move to ${rule.destination}`;
};