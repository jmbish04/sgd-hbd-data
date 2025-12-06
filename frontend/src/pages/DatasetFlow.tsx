import { useCallback, useEffect, useMemo, useState } from 'react';
import ReactFlow, {
  Node,
  Edge,
  addEdge,
  Connection,
  useNodesState,
  useEdgesState,
  Controls,
  MiniMap,
  Background,
  ReactFlowProvider,
  Panel,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Play, Square, RefreshCw, Zap } from 'lucide-react';

// Turbo Flow custom node styles
const turboNodeStyles = `
  .turbo-node {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: 2px solid transparent;
    border-radius: 8px;
    color: white;
    font-weight: 500;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    position: relative;
    overflow: hidden;
  }

  .turbo-node::before {
    content: '';
    position: absolute;
    top: -2px;
    left: -2px;
    right: -2px;
    bottom: -2px;
    background: linear-gradient(45deg, #667eea, #764ba2, #f093fb, #f5576c, #4facfe, #00f2fe);
    background-size: 400% 400%;
    border-radius: 10px;
    z-index: -1;
    animation: gradientShift 3s ease infinite;
    opacity: 0;
    transition: opacity 0.3s ease;
  }

  .turbo-node.processing::before {
    opacity: 1;
  }

  .turbo-node.completed {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  }

  .turbo-node.failed {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  }

  @keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }

  .turbo-edge {
    stroke: #667eea;
    stroke-width: 2;
  }

  .turbo-edge.processing {
    stroke: #f093fb;
    stroke-dasharray: 5, 5;
    animation: dash 1s linear infinite;
  }

  .turbo-edge.completed {
    stroke: #10b981;
  }

  .turbo-edge.failed {
    stroke: #ef4444;
  }

  @keyframes dash {
    to {
      stroke-dashoffset: -10;
    }
  }
`;

interface DatasetNode extends Node {
  data: {
    label: string;
    status: 'pending' | 'processing' | 'completed' | 'failed';
    progress?: number;
    records?: number;
    error?: string;
  };
}

interface ProcessingState {
  isRunning: boolean;
  currentDataset?: string;
  totalDatasets: number;
  processedDatasets: number;
  startTime?: Date;
}

function DatasetFlowContent() {
  const [datasets, setDatasets] = useState<any[]>([]);
  const [processingState, setProcessingState] = useState<ProcessingState>({
    isRunning: false,
    totalDatasets: 0,
    processedDatasets: 0,
  });
  const [selectedDatasets, setSelectedDatasets] = useState<Set<string>>(new Set());

  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  // Load datasets on mount
  useEffect(() => {
    fetch('/api/datasets')
      .then(res => res.json())
      .then(data => {
        if (data.datasets) {
          setDatasets(data.datasets);
        }
      })
      .catch(err => console.error(err));
  }, []);

  // Create nodes and edges based on datasets
  const flowElements = useMemo(() => {
    const flowNodes: DatasetNode[] = [];
    const flowEdges: Edge[] = [];

    // Start node
    flowNodes.push({
      id: 'start',
      type: 'default',
      position: { x: 100, y: 100 },
      data: {
        label: 'Start Processing',
        status: processingState.isRunning ? 'processing' : 'pending'
      },
      className: 'turbo-node',
    });

    // Dataset nodes
    datasets.forEach((dataset, index) => {
      const nodeId = `dataset-${dataset.id}`;
      const x = 300;
      const y = 100 + index * 120;

      flowNodes.push({
        id: nodeId,
        type: 'default',
        position: { x, y },
        data: {
          label: dataset.id.replace(/_/g, ' '),
          status: processingState.isRunning && processingState.currentDataset === dataset.id
            ? 'processing'
            : dataset.status === 'active' ? 'completed' : 'pending',
          records: dataset.count || 0,
        },
        className: `turbo-node ${
          processingState.isRunning && processingState.currentDataset === dataset.id ? 'processing' :
          dataset.status === 'active' ? 'completed' : ''
        }`,
      });

      // Edge from start to dataset
      flowEdges.push({
        id: `start-${nodeId}`,
        source: 'start',
        target: nodeId,
        className: `turbo-edge ${processingState.isRunning && processingState.currentDataset === dataset.id ? 'processing' : ''}`,
        animated: processingState.isRunning && processingState.currentDataset === dataset.id,
      });

      // Edge from dataset to end
      flowEdges.push({
        id: `${nodeId}-end`,
        source: nodeId,
        target: 'end',
        className: `turbo-edge ${dataset.status === 'active' ? 'completed' : ''}`,
      });
    });

    // End node
    flowNodes.push({
      id: 'end',
      type: 'default',
      position: { x: 600, y: 100 + (datasets.length * 120) / 2 },
      data: {
        label: 'Processing Complete',
        status: processingState.processedDatasets === processingState.totalDatasets && processingState.totalDatasets > 0 ? 'completed' : 'pending'
      },
      className: `turbo-node ${processingState.processedDatasets === processingState.totalDatasets && processingState.totalDatasets > 0 ? 'completed' : ''}`,
    });

    return { nodes: flowNodes, edges: flowEdges };
  }, [datasets, processingState]);

  useEffect(() => {
    setNodes(flowElements.nodes);
    setEdges(flowElements.edges);
  }, [flowElements, setNodes, setEdges]);

  const startProcessing = async () => {
    const datasetsToProcess = selectedDatasets.size > 0 ? Array.from(selectedDatasets) : datasets.map(d => d.id);

    setProcessingState({
      isRunning: true,
      totalDatasets: datasetsToProcess.length,
      processedDatasets: 0,
      startTime: new Date(),
    });

    try {
      // Start background processing via API
      const response = await fetch('/api/populate', { method: 'POST' });
      if (!response.ok) throw new Error('Failed to start processing');

      // Poll for progress updates
      const pollInterval = setInterval(async () => {
        try {
          const res = await fetch('/api/datasets');
          const data = await res.json();

          if (data.datasets) {
            setDatasets(data.datasets);

            // Update processing state based on dataset statuses
            const completedCount = data.datasets.filter((d: any) =>
              datasetsToProcess.includes(d.id) && d.status === 'active'
            ).length;

            setProcessingState(prev => ({
              ...prev,
              processedDatasets: completedCount,
              currentDataset: completedCount < datasetsToProcess.length ? datasetsToProcess[completedCount] : undefined,
              isRunning: completedCount < datasetsToProcess.length,
            }));

            // Stop polling when all datasets are processed
            if (completedCount >= datasetsToProcess.length) {
              clearInterval(pollInterval);
            }
          }
        } catch (error) {
          console.error('Failed to poll progress:', error);
        }
      }, 2000); // Poll every 2 seconds

      // Stop polling after 10 minutes as safety measure
      setTimeout(() => {
        clearInterval(pollInterval);
        setProcessingState(prev => ({
          ...prev,
          isRunning: false,
          currentDataset: undefined,
        }));
      }, 10 * 60 * 1000);

    } catch (error) {
      console.error('Processing failed:', error);
      setProcessingState(prev => ({
        ...prev,
        isRunning: false,
        currentDataset: undefined,
      }));
    }
  };

  const stopProcessing = () => {
    setProcessingState(prev => ({
      ...prev,
      isRunning: false,
      currentDataset: undefined,
    }));
  };

  const resetFlow = () => {
    setSelectedDatasets(new Set());
    setProcessingState({
      isRunning: false,
      totalDatasets: 0,
      processedDatasets: 0,
    });
  };

  const toggleDatasetSelection = (datasetId: string) => {
    const newSelected = new Set(selectedDatasets);
    if (newSelected.has(datasetId)) {
      newSelected.delete(datasetId);
    } else {
      newSelected.add(datasetId);
    }
    setSelectedDatasets(newSelected);
  };

  return (
    <div className="flex flex-col gap-6 h-full">
      {/* Header */}
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold tracking-tight">Dataset Processing Flow</h1>
        <p className="text-muted-foreground">
          Real-time visualization of dataset ingestion and processing pipeline.
        </p>
      </div>

      {/* Controls */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5" />
            Processing Controls
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-4 items-center">
            <div className="flex gap-2">
              <Button
                onClick={startProcessing}
                disabled={processingState.isRunning}
                className="flex items-center gap-2"
              >
                <Play className="h-4 w-4" />
                {selectedDatasets.size > 0 ? `Process ${selectedDatasets.size} Selected` : 'Process All Datasets'}
              </Button>

              {processingState.isRunning && (
                <Button onClick={stopProcessing} variant="destructive">
                  <Square className="h-4 w-4 mr-2" />
                  Stop
                </Button>
              )}

              <Button onClick={resetFlow} variant="outline">
                <RefreshCw className="h-4 w-4 mr-2" />
                Reset
              </Button>
            </div>

            <div className="flex items-center gap-2">
              <Badge variant={processingState.isRunning ? "default" : "secondary"}>
                {processingState.isRunning ? 'Processing' : 'Idle'}
              </Badge>
              {processingState.isRunning && (
                <span className="text-sm text-muted-foreground">
                  {processingState.processedDatasets}/{processingState.totalDatasets} datasets
                </span>
              )}
            </div>
          </div>

          {/* Dataset Selection */}
          <div className="mt-4">
            <h4 className="text-sm font-medium mb-2">Select Datasets to Process:</h4>
            <div className="flex flex-wrap gap-2">
              {datasets.map((dataset) => (
                <Button
                  key={dataset.id}
                  variant={selectedDatasets.has(dataset.id) ? "default" : "outline"}
                  size="sm"
                  onClick={() => toggleDatasetSelection(dataset.id)}
                  disabled={processingState.isRunning}
                >
                  {dataset.id}
                </Button>
              ))}
            </div>
            {selectedDatasets.size === 0 && (
              <p className="text-xs text-muted-foreground mt-1">
                No datasets selected - will process all datasets
              </p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Flow Visualization */}
      <Card className="flex-1">
        <CardContent className="p-0 h-[600px]">
          <style dangerouslySetInnerHTML={{ __html: turboNodeStyles }} />
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            fitView
            attributionPosition="bottom-left"
          >
            <Controls />
            <MiniMap />
            <Background color="#aaa" gap={16} />
            <Panel position="top-right">
              <div className="bg-background/80 backdrop-blur-sm p-3 rounded-lg border text-sm">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
                  Processing
                </div>
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  Completed
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-gray-400 rounded-full"></div>
                  Pending
                </div>
              </div>
            </Panel>
          </ReactFlow>
        </CardContent>
      </Card>
    </div>
  );
}

export default function DatasetFlow() {
  return (
    <ReactFlowProvider>
      <DatasetFlowContent />
    </ReactFlowProvider>
  );
}
