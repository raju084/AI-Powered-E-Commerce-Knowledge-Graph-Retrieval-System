import { useState, useEffect, useRef } from 'react';
import { Network } from 'vis-network/standalone';

export default function App() {
  const [stats, setStats] = useState({ summary: { total_nodes: 0, total_edges: 0 }, banana_audit: { total_occurrences: 5 }, active_model: 'DETECTING...' });
  const [sampleQuestions, setSampleQuestions] = useState([]);
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [pipelineData, setPipelineData] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [copied, setCopied] = useState(false);
  const [graphData, setGraphData] = useState(null);

  const networkRef = useRef(null);
  const containerRef = useRef(null);

  useEffect(() => {
    fetchStats();
    fetchSampleQuestions();
    fetchGraphData();
  }, []);

  const fetchStats = async () => {
    try {
      const res = await fetch('/api/stats');
      const data = await res.json();
      setStats(data);
    } catch (err) {
      console.error("Failed to load stats:", err);
    }
  };

  const fetchSampleQuestions = async () => {
    try {
      const res = await fetch('/api/sample-questions');
      const data = await res.json();
      setSampleQuestions(data);
    } catch (err) {
      console.error("Failed to load sample questions:", err);
    }
  };

  const fetchGraphData = async () => {
    try {
      const res = await fetch('/api/graph');
      const data = await res.json();
      setGraphData(data);
      initVisNetwork(data);
    } catch (err) {
      console.error("Failed to load graph data:", err);
    }
  };

  const initVisNetwork = (data) => {
    if (!containerRef.current) return;

    if (networkRef.current) {
      networkRef.current.destroy();
      networkRef.current = null;
    }

    const options = {
      nodes: {
        borderWidth: 2,
        shadow: { enabled: true, color: 'rgba(0,0,0,0.5)', size: 10, x: 2, y: 2 },
        font: { color: '#f8fafc', face: 'Plus Jakarta Sans', size: 13, strokeWidth: 3, strokeColor: '#090d16' }
      },
      edges: {
        width: 1.5,
        color: { color: 'rgba(148, 163, 184, 0.25)', highlight: '#38bdf8', hover: '#38bdf8' },
        smooth: { type: 'continuous', roundness: 0.2 },
        font: { color: '#94a3b8', size: 10, align: 'middle', background: 'rgba(15, 23, 42, 0.8)' }
      },
      physics: {
        stabilization: { iterations: 150 },
        barnesHut: { gravitationalConstant: -3500, springConstant: 0.04, springLength: 95 }
      },
      interaction: { hover: true, tooltipDelay: 150 }
    };

    const net = new Network(containerRef.current, data, options);
    networkRef.current = net;

    net.on("click", (params) => {
      if (params.nodes.length > 0) {
        const nodeId = params.nodes[0];
        const node = data.nodes.find(n => n.id === nodeId);
        if (node) {
          const connected = data.edges.filter(e => e.from === nodeId || e.to === nodeId);
          setSelectedNode({ ...node, connectedEdgesCount: connected.length });
        }
      } else {
        setSelectedNode(null);
      }
    });
  };

  const handleFitGraph = () => {
    if (networkRef.current) networkRef.current.fit({ animation: { duration: 600 } });
  };

  const handleResetGraph = () => {
    if (networkRef.current) {
      networkRef.current.unselectAll();
      networkRef.current.fit({ animation: { duration: 600 } });
      networkRef.current.startSimulation();
    }
    setSelectedNode(null);
  };

  const handleSubmit = async (qText) => {
    const queryQuestion = qText || question;
    if (!queryQuestion.trim()) return;

    setLoading(true);
    try {
      const res = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: queryQuestion.trim() })
      });
      const data = await res.json();
      setPipelineData(data);

      if (networkRef.current && data.retrieved_nodes && data.retrieved_nodes.length > 0) {
        const nodeIds = data.retrieved_nodes.map(n => n.id).filter(Boolean);
        if (nodeIds.length > 0) {
          networkRef.current.selectNodes(nodeIds);
          networkRef.current.fit({ nodes: nodeIds, animation: { duration: 600 } });
        }
      }
    } catch (err) {
      console.error("Query execution error:", err);
      alert("Error executing query. Check console.");
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="app-container">
      {/* Top Header Navigation */}
      <header className="top-nav">
        <div className="brand-section">
          <div className="logo-badge">KG</div>
          <div className="brand-text">
            <h1>E-Commerce Knowledge Graph <span className="accent-badge">AI Retrieval Engine</span></h1>
            <p className="subtitle">Natural Language Question &rarr; Structured Graph Spec &rarr; Grounded Factual QA</p>
          </div>
        </div>

      </header>

      {/* Main Grid Layout */}
      <main className="main-layout">
        {/* Left Column: Knowledge Graph Visualizer */}
        <section className="graph-panel">
          <div className="panel-header">
            <div className="panel-title-group">
              <h2>Interactive Knowledge Graph Canvas</h2>
              <span className="hint-text">Drag, zoom, or click nodes to inspect relationships</span>
            </div>
            <div className="graph-controls">
              <button onClick={handleFitGraph} className="control-btn">Fit Screen</button>
              <button onClick={handleResetGraph} className="control-btn">Reset</button>
            </div>
          </div>

          {/* Color Legend */}
          <div className="legend-bar">
            <span className="legend-item"><span className="legend-dot dot-product"></span> Product</span>
            <span className="legend-item"><span className="legend-dot dot-brand"></span> Brand</span>
            <span className="legend-item"><span className="legend-dot dot-category"></span> Category</span>
            <span className="legend-item"><span className="legend-dot dot-vendor"></span> Vendor</span>
            <span className="legend-item"><span className="legend-dot dot-customer"></span> Customer</span>
            <span className="legend-item"><span className="legend-dot dot-order"></span> Order</span>
          </div>

          <div className="graph-canvas-container">
            <div ref={containerRef} style={{ width: '100%', height: '100%' }}></div>
            {!graphData && (
              <div className="loading-overlay">
                <div className="spinner"></div>
                <span>Constructing Knowledge Graph...</span>
              </div>
            )}
          </div>

          {/* Node Property Inspector Drawer */}
          <div className="node-inspector">
            <span className="inspector-label">Node Inspector:</span>
            <span className="inspector-content">
              {selectedNode ? (
                <span>
                  <strong>[{selectedNode.group}] {selectedNode.label}</strong> (ID: <code>{selectedNode.id}</code>) &bull; Connected Edges: <strong>{selectedNode.connectedEdgesCount}</strong>
                  {selectedNode.customNote && <span style={{ color: '#fbbf24', marginLeft: '8px' }}>— {selectedNode.customNote}</span>}
                </span>
              ) : (
                "Click any node in the graph above to inspect properties and relational edges."
              )}
            </span>
          </div>
        </section>

        {/* Right Column: AI Retrieval Pipeline */}
        <section className="qa-panel">
          <div className="panel-header">
            <div className="panel-title-group">
              <h2>AI Graph Retrieval Pipeline</h2>
              <span className="hint-text">Zero-hallucination answers strictly grounded in NetworkX facts</span>
            </div>
          </div>

          {/* Sample Evaluation Question Cards */}
          <div className="sample-queries-section">
            <label className="section-label">Benchmark Evaluation Questions:</label>
            <div className="sample-chips-grid">
              {sampleQuestions.map((q, idx) => (
                <button
                  key={idx}
                  className="sample-card-btn"
                  onClick={() => {
                    setQuestion(q.question);
                    handleSubmit(q.question);
                  }}
                >
                  <div className="chip-header">
                    <span className="chip-badge">{q.title.split(':')[0]}</span>
                  </div>
                  <div className="chip-text">{q.question}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Search Query Input */}
          <form onSubmit={(e) => { e.preventDefault(); handleSubmit(); }} className="query-input-bar">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask anything about products, brands, vendors, orders, customers, or bananas..."
              required
            />
            <button type="submit" disabled={loading} className="send-btn">
              {loading ? (
                <span>Querying...</span>
              ) : (
                <>
                  <span>Query Graph</span>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                    <line x1="22" y1="2" x2="11" y2="13"></line>
                    <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                  </svg>
                </>
              )}
            </button>
          </form>

          {/* Pipeline Execution Output */}
          <div className="pipeline-trace">
            {!pipelineData && !loading && (
              <div className="welcome-card">
                <div className="welcome-icon">⚡</div>
                <h3>Ready for Natural Language Graph Queries</h3>
                <p>Select any benchmark question above or type your own to see the 5-step Graph Retrieval Pipeline execute with strict zero-hallucination grounding.</p>
                <div className="flow-pill-row">
                  <span className="flow-step">1. User Question</span>
                  <span className="flow-arrow">&rarr;</span>
                  <span className="flow-step">2. LLM Spec</span>
                  <span className="flow-arrow">&rarr;</span>
                  <span className="flow-step">3. NetworkX Traversal</span>
                  <span className="flow-arrow">&rarr;</span>
                  <span className="flow-step">4. Fact Extraction</span>
                  <span className="flow-arrow">&rarr;</span>
                  <span className="flow-step">5. Grounded Answer</span>
                </div>
              </div>
            )}

            {loading && (
              <div className="welcome-card">
                <div className="spinner" style={{ margin: '0 auto 16px auto' }}></div>
                <h3>Executing Pipeline...</h3>
                <p style={{ color: '#38bdf8' }}>Translating question &rarr; Traversing Graph &rarr; Verifying Grounding</p>
              </div>
            )}

            {pipelineData && !loading && (
              <div className="trace-steps-container">
                {/* Step 1 */}
                <div className="trace-step-card">
                  <div className="step-badge step-1">Step 1</div>
                  <div className="step-content">
                    <div className="step-title-row">
                      <h4>Natural Language Question</h4>
                      <span className="timestamp-badge">User Request</span>
                    </div>
                    <div className="step-box">{pipelineData.question}</div>
                  </div>
                </div>

                {/* Step 2 */}
                <div className="trace-step-card">
                  <div className="step-badge step-2">Step 2</div>
                  <div className="step-content">
                    <div className="step-title-row">
                      <h4>LLM &rarr; Generated Graph Spec (JSON)</h4>
                      <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                        <span className="sub-badge">{pipelineData.model_used.toUpperCase()}</span>
                        <button
                          className="copy-btn"
                          onClick={() => copyToClipboard(JSON.stringify(pipelineData.graph_query, null, 2))}
                        >
                          {copied ? "Copied! ✓" : "Copy Spec"}
                        </button>
                      </div>
                    </div>
                    <pre className="code-box">{JSON.stringify(pipelineData.graph_query, null, 2)}</pre>
                  </div>
                </div>

                {/* Step 3 */}
                <div className="trace-step-card">
                  <div className="step-badge step-3">Step 3</div>
                  <div className="step-content">
                    <div className="step-title-row">
                      <h4>NetworkX Graph Traversal Facts</h4>
                      <span className="count-tag">{pipelineData.retrieved_nodes_count} matched nodes</span>
                    </div>
                    <ul className="facts-list">
                      {pipelineData.facts.length === 0 ? (
                        <li>No graph facts returned matching constraints.</li>
                      ) : (
                        pipelineData.facts.map((fact, idx) => (
                          <li key={idx}><span className="fact-bullet">▪</span> {fact}</li>
                        ))
                      )}
                    </ul>
                  </div>
                </div>

                {/* Step 4 */}
                <div className="trace-step-card answer-card">
                  <div className="step-badge answer-badge">Step 4</div>
                  <div className="step-content">
                    <div className="step-title-row">
                      <h4>Final Grounded Answer</h4>
                      <span className={`grounded-badge ${pipelineData.grounded ? 'grounded-pass' : 'grounded-warn'}`}>
                        {pipelineData.grounded ? "✓ Strictly Grounded" : "⚠ Potential Gap"}
                      </span>
                    </div>
                    <div className="final-answer-box">{pipelineData.final_answer}</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}
