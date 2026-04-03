const nodes = [
  { id: "node-a", name: "Node Alpha", address: "127.0.0.1:8001" },
  { id: "node-b", name: "Node Beta", address: "127.0.0.1:8002" },
  { id: "node-c", name: "Node Gamma", address: "127.0.0.1:8003" },
];

const state = {
  file: null,
  content: "",
};

const fileInput = document.querySelector("#file-input");
const fileName = document.querySelector("#file-name");
const fileSize = document.querySelector("#file-size");
const uploadForm = document.querySelector("#upload-form");
const nodesGrid = document.querySelector("#nodes-grid");
const activityList = document.querySelector("#activity-list");
const networkStatus = document.querySelector("#network-status");
const nodeTemplate = document.querySelector("#node-template");
const themeToggle = document.querySelector("#theme-toggle");

function applyTheme(mode) {
  const isDark = mode === "dark";
  document.body.classList.toggle("dark-mode", isDark);
  themeToggle.textContent = isDark ? "Light mode" : "Dark mode";
}

function loadTheme() {
  const savedTheme = window.localStorage.getItem("theme");
  if (savedTheme === "dark" || savedTheme === "light") {
    applyTheme(savedTheme);
    return;
  }

  applyTheme("light");
}

function formatBytes(size) {
  if (!size) return "0 B";
  if (size < 1024) return `${size} B`;
  return `${(size / 1024).toFixed(1)} KB`;
}

function addActivity(message) {
  const item = document.createElement("li");
  item.textContent = message;
  activityList.prepend(item);

  while (activityList.children.length > 5) {
    activityList.removeChild(activityList.lastChild);
  }
}

function renderNodes() {
  nodesGrid.innerHTML = "";

  nodes.forEach((node) => {
    const fragment = nodeTemplate.content.cloneNode(true);
    fragment.querySelector(".node-name").textContent = node.name;
    fragment.querySelector(".node-address").textContent = node.address;
    fragment.querySelector(".node-file").textContent = state.file
      ? state.file.name
      : "No file replicated yet";
    fragment.querySelector(".node-preview").textContent = state.content
      ? state.content.slice(0, 240)
      : "Waiting for client upload...";
    nodesGrid.appendChild(fragment);
  });

  networkStatus.textContent = `${nodes.length} nodes online`;
}

fileInput.addEventListener("change", async (event) => {
  const [selectedFile] = event.target.files;

  if (!selectedFile) {
    return;
  }

  if (!selectedFile.name.toLowerCase().endsWith(".txt")) {
    addActivity("Upload blocked: only .txt files are allowed.");
    fileInput.value = "";
    return;
  }

  state.file = selectedFile;
  state.content = await selectedFile.text();

  fileName.textContent = selectedFile.name;
  fileSize.textContent = formatBytes(selectedFile.size);
  addActivity(`Client selected ${selectedFile.name}. Ready to replicate.`);
});

uploadForm.addEventListener("submit", (event) => {
  event.preventDefault();

  if (!state.file) {
    addActivity("Select a .txt file before uploading.");
    return;
  }

  renderNodes();
  addActivity(
    `Replicated ${state.file.name} to ${nodes.length} connected nodes.`
  );
});

themeToggle.addEventListener("click", () => {
  const nextTheme = document.body.classList.contains("dark-mode")
    ? "light"
    : "dark";

  applyTheme(nextTheme);
  window.localStorage.setItem("theme", nextTheme);
});

loadTheme();
renderNodes();
addActivity("Network initialized. Nodes are waiting for client uploads.");
