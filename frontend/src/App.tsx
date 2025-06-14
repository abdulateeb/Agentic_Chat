import React, { useState, useCallback, useEffect, useMemo, useRef } from 'react';
import { motion } from 'framer-motion';
import { v4 as uuidv4 } from 'uuid';
import { CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import './App.css';

// A simple type definition for the nodes we expect from the backend
interface AgentNode {
  id: string;
  label: string;
  status: 'waiting' | 'processing' | 'completed' | 'failed';
  parentId?: string;
  depth: number;
  data?: {
    description?: string;
    error?: string;
  };
}

// --- 2. UTILITY FUNCTIONS ---

const NODE_WIDTH = 320;
const Y_SPACING = 160;
const X_SPACING = 350;

const calculateNodePosition = (depth: number, index: number, totalSiblings: number): { x: number; y: number } => {
  const levelWidth = totalSiblings * NODE_WIDTH + (totalSiblings - 1) * (X_SPACING - NODE_WIDTH);
  const currentX = -levelWidth / 2 + (index * (NODE_WIDTH + (X_SPACING - NODE_WIDTH)));
  return {
    x: currentX,
    y: depth * Y_SPACING
  };
};

const calculateNodeIndex = (nodes: AgentNode[], depth: number): Record<string, number> => {
  const indices: Record<string, number> = {};
  const nodesAtDepth = nodes.filter(node => node.depth === depth);
  nodesAtDepth.forEach((node, index) => {
    indices[node.id] = index;
  });
  return indices;
};

// --- 2. UI COMPONENTS ---

const Node = ({ node, style }: { node: AgentNode; style: React.CSSProperties }) => {
  const statusClasses = {
    waiting: 'border-gray-600 bg-gray-800/50',
    processing: 'border-blue-500 bg-blue-900/50 ring-2 ring-blue-500/50 ring-offset-2 ring-offset-gray-900',
    completed: 'border-green-500 bg-green-900/50',
    failed: 'border-red-500 bg-red-900/50',
  };
  const statusIcons = {
    waiting: <Loader2 size={16} className="text-gray-500" />,
    processing: <Loader2 size={16} className="animate-spin text-blue-400" />,
    completed: <CheckCircle2 size={16} className="text-green-400" />,
    failed: <AlertCircle size={16} className="text-red-400" />,
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.5 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ type: 'spring', damping: 15, stiffness: 200 }}
      className={`node-card ${statusClasses[node.status]}`}
      style={style}
    >
      <div className="flex justify-between items-center">
        <p className="font-bold">{node.label}</p>
        {statusIcons[node.status]}
      </div>
      <p className="text-sm text-gray-400 mt-1">{node.data?.description}</p>
      {node.data?.error && <p className="text-xs text-red-400 mt-2">Error: {node.data.error}</p>}
    </motion.div>
  );
};

const AgentTree = ({ nodes }: { nodes: AgentNode[] }) => {
  const nodePositions = useMemo(() => {
    const positions: Record<string, { x: number; y: number }> = {};
    const maxDepth = Math.max(...nodes.map(n => n.depth));

    for (let depth = 0; depth <= maxDepth; depth++) {
      const indices = calculateNodeIndex(nodes, depth);
      const nodesAtDepth = nodes.filter(n => n.depth === depth);
      
      nodesAtDepth.forEach(node => {
        const index = indices[node.id];
        const pos = calculateNodePosition(depth, index, nodesAtDepth.length);
        positions[node.id] = pos;
      });
    }
    return positions;
  }, [nodes]);

  const edges = useMemo(() => {
    return nodes
      .filter(node => node.parentId && nodePositions[node.id] && nodePositions[node.parentId])
      .map(node => ({
        id: `${node.parentId}-${node.id}`,
        source: nodePositions[node.parentId],
        target: nodePositions[node.id],
      }));
  }, [nodes, nodePositions]);

  return (
    <div className="agent-tree-container">
      <div className="agent-tree" style={{ transform: `translate(50%, 50px)` }}>
        <svg className="edges-svg">
          {edges.map(edge => (
            <motion.path
              key={edge.id}
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 0.5, ease: "easeInOut" }}
              d={`M ${edge.source.x + NODE_WIDTH / 2} ${edge.source.y + 70} C ${edge.source.x + NODE_WIDTH / 2} ${edge.source.y + 70 + Y_SPACING / 2}, ${edge.target.x + NODE_WIDTH / 2} ${edge.target.y - Y_SPACING / 2}, ${edge.target.x + NODE_WIDTH / 2} ${edge.target.y}`}
              stroke="#4a5568"
              strokeWidth="2"
              fill="none"
            />
          ))}
        </svg>
        {nodes.map(node => {
          const pos = nodePositions[node.id];
          if (!pos) return null;
          return <Node key={node.id} node={node} style={{ left: `${pos.x}px`, top: `${pos.y}px` }} />;
        })}
      </div>
    </div>
  );
};

function App() {
  const [query, setQuery] = useState<string>('');
  const [nodes, setNodes] = useState<AgentNode[]>([]);
  const [isConnecting, setIsConnecting] = useState<boolean>(false);
  const [currentQuery, setCurrentQuery] = useState<string>('');

  const startWorkflow = useCallback(async (q: string) => {
    if (isConnecting) return;
    setIsConnecting(true);
    setCurrentQuery(q);
    setNodes([]);
    const sessionId = uuidv4();

    try {
      const response = await fetch('http://localhost:8001/api/v1/chat/initiate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: q, session_id: sessionId }),
      });

      if (!response.ok) throw new Error(`API Error: ${await response.text()}`);

      const { workflow_id } = await response.json();
      const ws = new WebSocket(`ws://localhost:8001/ws/${sessionId}/${workflow_id}`);

      ws.onopen = () => setIsConnecting(false);
      ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        if (message.type === 'node' && message.payload) {
          setNodes(prevNodes => {
            const newNodes = [...prevNodes];
            const index = newNodes.findIndex(n => n.id === message.payload.id);
            if (index > -1) newNodes[index] = message.payload;
            else newNodes.push(message.payload);
            return newNodes;
          });
        }
      };
      ws.onclose = () => setIsConnecting(false);
      ws.onerror = () => setIsConnecting(false);
    } catch (err) {
      setIsConnecting(false);
    }
  }, [isConnecting]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) startWorkflow(query);
  };

  return (
    <div className="App">
      {!currentQuery ? (
        <div className="initial-view">
          <h1>Agentic SRE Chat</h1>
          <form onSubmit={handleSubmit}>
            <input type="text" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Ask a question..." disabled={isConnecting} />
            <button type="submit" disabled={isConnecting}>{isConnecting ? 'Connecting...' : 'Send'}</button>
          </form>
        </div>
      ) : (
        <div className="main-view">
          <h2 className="query-header">Query: {currentQuery}</h2>
          <AgentTree nodes={nodes} />
        </div>
      )}
                        </div>
                    ))}
                </div>
            </div>
          </div>
        )}
        {error && <div className="error-banner">{error}</div>}
      </header>
    </div>
  );
}

export default App;
