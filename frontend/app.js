const state = {
  file: null,
  content: "",
  gatewayUrl: "http://127.0.0.1:8000",
  nodes: [],
  files: [],
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
const gatewayUrlInput = document.querySelector("#gateway-url");
const refreshNetworkButton = document.querySelector("#refresh-network");
const fileList = document.querySelector("#file-list");

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

function normalizeBaseUrl(value) {
  return value.trim().replace(/\/+$/, "");
}

async function getJson(url, options = {}) {
  const response = await fetch(url, options);

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed with status ${response.status}`);
  }

  return response.json();
}

async function fetchLatestFile(node) {
  const filesResponse = await getJson(`${node.baseUrl}/files`);
  const fileNames = Array.isArray(filesResponse.files) ? filesResponse.files : [];

  if (!fileNames.length) {
    return {
      latestFile: "No file replicated yet",
      preview: "Waiting for client upload...",
    };
  }

  const filePayloads = await Promise.all(
    fileNames.map(async (fileName) => {
      const fileResponse = await getJson(
        `${node.baseUrl}/files/${encodeURIComponent(fileName)}`
      );

      return {
        fileName,
        text: fileResponse.text,
        metadata: fileResponse.metadata,
      };
    })
  );

  filePayloads.sort(
    (left, right) => right.metadata.timestamp - left.metadata.timestamp
  );

  const latest = filePayloads[0];
  return {
    latestFile: latest.fileName,
    preview: latest.text.slice(0, 240) || "File is empty.",
  };
}

async function fetchNodeSnapshot(node) {
  try {
    const health = await getJson(`${node.baseUrl}/health`);
    const latest = await fetchLatestFile(node);

    return {
      ...node,
      online: true,
      nodeBadge: "Online",
      displayName: health.message.replace("hi from: ", ""),
      latestFile: latest.latestFile,
      preview: latest.preview,
    };
  } catch (error) {
    return {
      ...node,
      online: false,
      nodeBadge: "Offline",
      displayName: node.name,
      latestFile: "Unavailable",
      preview: "This node did not respond to the browser.",
      error,
    };
  }
}

async function refreshCluster() {
  const gatewayUrl = normalizeBaseUrl(gatewayUrlInput.value);

  if (!gatewayUrl) {
    addActivity("Enter a gateway node URL before refreshing the cluster.");
    return;
  }

  state.gatewayUrl = gatewayUrl;
  gatewayUrlInput.value = gatewayUrl;
  networkStatus.textContent = "Checking nodes...";

  try {
    const cluster = await getJson(`${gatewayUrl}/cluster`);
    const discoveredNodes = cluster.nodes.map((node) => ({
      ...node,
      baseUrl: `http://${node.address}`,
    }));
    const gatewayFilesResponse = await getJson(`${gatewayUrl}/files`);

    state.nodes = await Promise.all(discoveredNodes.map(fetchNodeSnapshot));
    state.files = Array.isArray(gatewayFilesResponse.files)
      ? gatewayFilesResponse.files.slice().sort()
      : [];
    renderNodes();
    renderFileList();

    const onlineCount = state.nodes.filter((node) => node.online).length;
    addActivity(
      `Connected to ${cluster.current_node}. ${onlineCount}/${state.nodes.length} nodes responded.`
    );
  } catch (error) {
    state.nodes = [];
    state.files = [];
    renderNodes();
    renderFileList();
    networkStatus.textContent = "Gateway unreachable";
    addActivity(`Unable to reach ${gatewayUrl}. Start a node and try again.`);
    console.error(error);
  }
}

function renderFileList() {
  fileList.innerHTML = "";

  if (!state.files?.length) {
    const item = document.createElement("li");
    item.textContent = "No files available on the gateway node yet.";
    fileList.appendChild(item);
    return;
  }

  state.files.forEach((fileName) => {
    const item = document.createElement("li");
    const label = document.createElement("span");
    const button = document.createElement("button");

    label.className = "file-entry-name";
    label.textContent = fileName;

    button.className = "danger-button";
    button.type = "button";
    button.textContent = "Delete";
    button.addEventListener("click", async () => {
      await deleteFile(fileName);
    });

    item.append(label, button);
    fileList.appendChild(item);
  });
}

async function deleteFile(fileName) {
  try {
    await getJson(`${state.gatewayUrl}/files/${encodeURIComponent(fileName)}`, {
      method: "DELETE",
    });

    addActivity(`Deleted ${fileName} from ${state.gatewayUrl}.`);

    if (state.file?.name === fileName) {
      state.file = null;
      state.content = "";
      fileInput.value = "";
      fileName.textContent = "No file selected";
      fileSize.textContent = "0 B";
    }

    await refreshCluster();
    addActivity(`Deletion sync finished for ${fileName}.`);
  } catch (error) {
    addActivity(`Delete failed for ${fileName}.`);
    console.error(error);
  }
}

function renderNodes() {
  nodesGrid.innerHTML = "";

  if (!state.nodes.length) {
    networkStatus.textContent = "No nodes discovered";
    return;
  }

  state.nodes.forEach((node) => {
    const fragment = nodeTemplate.content.cloneNode(true);
    fragment.querySelector(".node-name").textContent = node.displayName || node.name;
    fragment.querySelector(".node-address").textContent = node.address;
    fragment.querySelector(".node-file").textContent = node.latestFile;
    fragment.querySelector(".node-preview").textContent = node.preview;
    const badge = fragment.querySelector(".node-badge");
    badge.textContent = node.nodeBadge;
    badge.style.background = node.online
      ? "rgba(47, 125, 75, 0.1)"
      : "rgba(217, 108, 61, 0.12)";
    badge.style.color = node.online ? "var(--success)" : "var(--accent)";
    nodesGrid.appendChild(fragment);
  });

  const onlineCount = state.nodes.filter((node) => node.online).length;
  networkStatus.textContent = `${onlineCount}/${state.nodes.length} nodes online`;
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

uploadForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (!state.file) {
    addActivity("Select a .txt file before uploading.");
    return;
  }

  try {
    await getJson(
      `${state.gatewayUrl}/files/${encodeURIComponent(state.file.name)}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: state.content,
        }),
      }
    );

    addActivity(`Uploaded ${state.file.name} to ${state.gatewayUrl}.`);
    await refreshCluster();
    addActivity(`Replication check finished for ${state.file.name}.`);
  } catch (error) {
    addActivity(`Upload failed for ${state.file.name}. Check that the gateway node is running.`);
    console.error(error);
  }
});

themeToggle.addEventListener("click", () => {
  const nextTheme = document.body.classList.contains("dark-mode")
    ? "light"
    : "dark";

  applyTheme(nextTheme);
  window.localStorage.setItem("theme", nextTheme);
});

refreshNetworkButton.addEventListener("click", () => {
  refreshCluster();
});

loadTheme();
gatewayUrlInput.value = state.gatewayUrl;
renderNodes();
renderFileList();
refreshCluster();
addActivity("Frontend connected. Select a .txt file to write through a live node.");
