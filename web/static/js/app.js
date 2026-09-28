// Interactive Knowledge Graph Frontend Logic
let network = null;
let graphData = null;

document.addEventListener("DOMContentLoaded", () => {
  initGraph();
  loadStats();
  loadSampleQuestions();
  setupEventHandlers();
});

async function initGraph() {
  const container = document.getElementById("networkGraph");
  const loader = document.getElementById("graphLoading");

  try {
    const res = await fetch("/api/graph");
    graphData = await res.json();

    const options = {
      nodes: {
        borderWidth: 2,
        shadow: true
      },
      edges: {
        width: 1.5,
        smooth: {
          type: "continuous"
        }
      },
      physics: {
        stabilization: { iterations: 150 },
        barnesHut: {
          gravitationalConstant: -3500,
          springConstant: 0.04,
          springLength: 95
        }
      },
      interaction: {
        hover: true,
        tooltipDelay: 150,
        hideEdgesOnDrag: false
      }
    };

    network = new vis.Network(container, graphData, options);

    network.on("click", (params) => {
      if (params.nodes.length > 0) {
        const nodeId = params.nodes[0];
        inspectNode(nodeId);
      }
    });

    loader.style.display = "none";
  } catch (err) {
    console.error("Failed to load graph:", err);
    loader.innerHTML = `<span style="color:#ef4444;">Error loading graph. Check server logs.</span>`;
  }
}

function inspectNode(nodeId) {
  const node = graphData.nodes.find(n => n.id === nodeId);
  if (!node) return;

  const connectedEdges = graphData.edges.filter(e => e.from === nodeId || e.to === nodeId);
  const inspector = document.getElementById("nodeDetails");
  inspector.innerHTML = `
    <strong>[${node.group}] ${node.label}</strong> (ID: <code>${node.id}</code>) &bull;
    Connected Edges: <strong>${connectedEdges.length}</strong>
  `;
}

async function loadStats() {
  try {
    const res = await fetch("/api/stats");
    const data = await res.json();

    document.getElementById("totalNodes").textContent = data.summary.total_nodes;
    document.getElementById("totalEdges").textContent = data.summary.total_edges;
    document.getElementById("bananaCount").textContent = `${data.banana_audit.total_occurrences} / 5 Verified`;
    document.getElementById("activeModel").textContent = data.active_model.toUpperCase();
  } catch (err) {
    console.error("Failed to fetch stats:", err);
  }
}

async function loadSampleQuestions() {
  const container = document.getElementById("sampleChipsContainer");
  try {
    const res = await fetch("/api/sample-questions");
    const questions = await res.json();

    container.innerHTML = "";
    questions.forEach(q => {
      const chip = document.createElement("button");
      chip.className = "sample-chip";
      chip.textContent = `${q.title}: "${q.question}"`;
      chip.title = q.question;
      chip.onclick = () => {
        document.getElementById("questionInput").value = q.question;
        submitQuery(q.question);
      };
      container.appendChild(chip);
    });
  } catch (err) {
    console.error("Failed to fetch sample questions:", err);
  }
}

function setupEventHandlers() {
  const form = document.getElementById("queryForm");
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const q = document.getElementById("questionInput").value.trim();
    if (q) submitQuery(q);
  });

  document.getElementById("btnFitGraph").addEventListener("click", () => {
    if (network) network.fit({ animation: { duration: 600 } });
  });

  document.getElementById("btnResetView").addEventListener("click", () => {
    if (network) network.startSimulation();
  });

  document.getElementById("btnHighlightBanana").addEventListener("click", () => {
    highlightBananaNodes();
  });
}

function highlightBananaNodes() {
  if (!network || !graphData) return;
  const bananaNodeIds = graphData.nodes
    .filter(n => n.label.toLowerCase() === "banana")
    .map(n => n.id);

  if (bananaNodeIds.length > 0) {
    network.selectNodes(bananaNodeIds);
    network.fit({ nodes: bananaNodeIds, animation: { duration: 800 } });
    const inspector = document.getElementById("nodeDetails");
    inspector.innerHTML = `<span style="color:#fbbf24;">🍌 Selected all 5 Banana nodes (${bananaNodeIds.join(", ")}) across Brand, Category, Vendor, Product, and Customer!</span>`;
  }
}

async function submitQuery(question) {
  const submitBtn = document.getElementById("submitBtn");
  const welcomeCard = document.getElementById("welcomeCard");
  const traceContainer = document.getElementById("traceContainer");

  submitBtn.disabled = true;
  submitBtn.querySelector("span").textContent = "Querying...";

  try {
    const res = await fetch("/api/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question })
    });

    const data = await res.json();
    welcomeCard.style.display = "none";
    traceContainer.style.display = "flex";

    // Step 1: Question
    document.getElementById("traceQuestion").textContent = data.question;

    // Step 2: Query Spec
    document.getElementById("traceModelBadge").textContent = data.model_used.toUpperCase();
    document.getElementById("traceGraphQuery").textContent = JSON.stringify(data.graph_query, null, 2);

    // Step 3: Retrieved Facts
    document.getElementById("traceMatchCount").textContent = `${data.retrieved_nodes_count} matched nodes`;
    const factsList = document.getElementById("traceFactsList");
    factsList.innerHTML = "";
    if (data.facts.length === 0) {
      factsList.innerHTML = "<li>No facts found matching this query in the graph.</li>";
    } else {
      data.facts.forEach(fact => {
        const li = document.createElement("li");
        li.textContent = fact;
        factsList.appendChild(li);
      });
    }

    // Step 4: Final Answer & Grounding
    document.getElementById("traceFinalAnswer").textContent = data.final_answer;
    const badge = document.getElementById("groundingBadge");
    if (data.grounded) {
      badge.innerHTML = `<span class="check-icon">&#10003;</span> Strictly Grounded`;
      badge.style.color = "#34d399";
    } else {
      badge.innerHTML = `<span>&#9888;</span> Potential Gap`;
      badge.style.color = "#f43f5e";
    }

    // Focus / select matched nodes on graph
    if (network && data.retrieved_nodes && data.retrieved_nodes.length > 0) {
      const nodeIdsToSelect = data.retrieved_nodes.map(n => n.id).filter(id => id);
      if (nodeIdsToSelect.length > 0) {
        network.selectNodes(nodeIdsToSelect);
        network.fit({ nodes: nodeIdsToSelect, animation: { duration: 600 } });
      }
    }
  } catch (err) {
    console.error("Query failed:", err);
    alert("Error executing query. See console for details.");
  } finally {
    submitBtn.disabled = false;
    submitBtn.querySelector("span").textContent = "Query Graph";
  }
}
