# 🧠 Knowledge Graph Library & Examples Reference

## Table of Contents
- [Core Libraries](#core-libraries)  
- [Documentation Resources](#documentation-resources)
- [Example Implementations](#example-implementations)
- [API References](#api-references)
- [Layout Algorithms](#layout-algorithms)
- [Visualization Features](#visualization-features)
- [Data Formats & Import/Export](#data-formats--importexport)
- [Event Systems](#event-systems)
- [Performance & Rendering](#performance--rendering)
- [Integration Patterns](#integration-patterns)

## Core Libraries

### Graphology
- **Purpose**: JavaScript library for graph manipulation and analysis
- **URL**: https://graphology.github.io/
- **Key Features**:
  - Data-level graph operations
  - Support for both directed and undirected graphs
  - Node and edge management (add, remove, update)
  - Various graph algorithms (centrality, clustering, pathfinding)
  - Layout algorithms (ForceAtlas2, circular, random)

### Sigma.js
- **Purpose**: JavaScript library for graph rendering using WebGL
- **URL**: https://www.sigmajs.org/docs/
- **Key Features**:
  - High-performance WebGL rendering
  - Interactive graph visualization
  - Customizable node and edge rendering
  - Camera controls (pan, zoom, rotate)
  - Event handling system

### @react-sigma/core
- **Purpose**: React bindings for Sigma.js
- **URL**: https://sim51.github.io/react-sigma/
- **Key Features**:
  - React component wrappers for Sigma.js
  - Hooks for accessing Sigma instance
  - Layout integration with React state
  - Event handling in React context

## Documentation Resources

### Official Documentation
- **Graphology**: https://graphology.github.io/
  - Core graph operations
  - Layout algorithms
  - Import/export utilities
- **Sigma.js**: https://www.sigmajs.org/docs/
  - Renderer settings
  - Camera controls
  - Event system
- **React-Sigma**: https://sim51.github.io/react-sigma/
  - React integration
  - Component API
  - Hook references

### Project Resources
- **Project Documentation**: `/sigma-examples/docs`
- **Example Code**: `/sigma-examples/examples`

## Example Implementations

### Layout Examples
- **File**: `sigma-examples/examples/layouts.tsx`
- **Concepts Demonstrated**: Multi-layout control (FA2, Circular, Random)
- **Key Features**:
  - ForceAtlas2 worker layout
  - Circular layout
  - Animated transitions between layouts
- **Hooks Used**: `useWorkerLayoutForceAtlas2`, `animateNodes`

### Camera Settings
- **File**: `sigma-examples/examples/camera-settings.tsx`
- **Concepts Demonstrated**: Camera boundaries, rotation
- **Key Features**:
  - Camera constraints (min/max ratios)
  - Rotation controls
  - Boundary settings
- **Settings Used**: `minCameraRatio`, `maxCameraRatio`

### CSV Bipartite Network
- **File**: `sigma-examples/examples/csv-bipartite-network.tsx`
- **Concepts Demonstrated**: CSV import, degree-based sizing
- **Key Features**:
  - CSV parsing with papaparse
  - Bipartite graph construction
  - Degree-based node sizing
  - Largest connected component filtering
- **Libraries Used**: `papaparse`, `cropToLargestConnectedComponent`

### Cluster Labeling
- **File**: `sigma-examples/examples/cluster-label.tsx`
- **Concepts Demonstrated**: Leaflet map, cluster barycenters
- **Key Features**:
  - Integration with Leaflet maps
  - Community detection visualization
  - Cluster centroid calculation
- **Libraries Used**: `@sigma/layer-leaflet`, `iwanthue`

### Custom Rendering
- **File**: `sigma-examples/examples/custom-rendering.tsx`
- **Concepts Demonstrated**: Custom node rendering
- **Key Features**:
  - Custom node visualization
  - Node images and borders
  - Custom rendering programs

### Event Handling
- **File**: `sigma-examples/examples/events.tsx`
- **Concepts Demonstrated**: Full event logging
- **Key Features**:
  - Node events (click, hover, double-click)
  - Edge events (click, hover)
  - Event logging and handling
- **Events**: `enterNode`, `clickNode`, `doubleClickNode`

### Node Dragging
- **File**: `sigma-examples/examples/drag-nodes.tsx`
- **Concepts Demonstrated**: Node dragging interaction
- **Key Features**:
  - Interactive node positioning
  - Pointer event handling
  - Node attribute updates
- **Events**: `onPointerDown`, `setNodeAttribute`

### JSON-LD RDF Graph
- **File**: `sigma-examples/examples/jsonld-rdf-graph.tsx`
- **Concepts Demonstrated**: RDF/JSON-LD parsing
- **Key Features**:
  - Semantic graph parsing
  - JSON-LD expansion
  - RDF triple handling
- **Libraries Used**: `jsonld.expand()`

## API References

### Essential React-Sigma Hooks

#### `useSigma()`
- **Purpose**: Access the live Sigma instance (camera, renderer, settings)
- **Usage**: `const sigma = useSigma();`
- **Returns**: Sigma instance with access to camera, renderer, and settings

#### `useLoadGraph()`
- **Purpose**: Load/replace a Graphology graph into the current Sigma instance
- **Usage**: `const loadGraph = useLoadGraph(); loadGraph(graph);`
- **Returns**: Function to load graphs into Sigma

#### `useRegisterEvents()`
- **Purpose**: Attach event handlers (node/edge hover, click, double-click)
- **Usage**: `registerEvents({ clickNode, enterNode, leaveEdge })`
- **Parameters**: Event handler functions

#### `useSetSettings()`
- **Purpose**: Dynamically tweak renderer settings (label threshold, edge program, etc.)
- **Usage**: `const setSettings = useSetSettings(); setSettings({ labelThreshold: 0 });`

#### `useCamera()`
- **Purpose**: Programmatically pan/zoom/animate the camera
- **Usage**: `const camera = useCamera(); camera.animate({ x, y, ratio })`
- **Returns**: Camera instance with animation controls

#### `useWorkerLayoutForceAtlas2()`
- **Purpose**: Run ForceAtlas2 in a Web Worker; start/stop; stream positions
- **Usage**: `{ start, stop, isRunning } = useWorkerLayoutForceAtlas2()`
- **Returns**: Control functions for the layout worker

#### `useLayoutCircular()`
- **Purpose**: Assign circular coordinates; quick baseline layout
- **Usage**: `const { positions } = useLayoutCircular({ scale: 100 })`
- **Returns**: Position mapping for circular layout

### Essential Components

#### `SigmaContainer`
- **Purpose**: React wrapper around a Sigma instance
- **Usage**: `<SigmaContainer settings={{ renderLabels: true }}>...</SigmaContainer>`
- **Props**: Settings object, children

#### `ControlsContainer`
- **Purpose**: Container for UI controls
- **Usage**: `<ControlsContainer>...</ControlsContainer>`

## Layout Algorithms

### ForceAtlas2
- **Description**: Force-directed layout optimized for clarity
- **Implementation**: `useWorkerLayoutForceAtlas2()` or `forceAtlas2.assign(graph, { iterations: 100 })`
- **Features**:
  - Runs in Web Worker to prevent UI blocking
  - Physics-based clustering
  - Configurable parameters (iterations, gravity, barnesHutOptimize)
- **Parameters**:
  - `iterations`: Number of simulation steps
  - `gravity`: Attraction to center
  - `barnesHutOptimize`: Performance optimization for large graphs

### Circular Layout
- **Description**: Simple deterministic layout with nodes evenly placed on a circle
- **Implementation**: `useLayoutCircular()` or `circular.assign(graph)`
- **Features**:
  - Quick baseline positioning
  - Deterministic results
  - Good for initial graph visualization

### Random Layout
- **Description**: Random initial positions for nodes
- **Implementation**: `random.assign(graph)`
- **Features**:
  - Useful for stress-testing
  - Good starting point for force-directed algorithms

### Animated Transitions
- **Implementation**: `animateNodes(graph, positions, { duration: 2000 })`
- **Purpose**: Smooth transition between different layouts
- **Parameters**:
  - `graph`: The Graphology graph instance
  - `positions`: New positions object
  - `options`: Animation options (duration, easing)

## Visualization Features

### Node Attributes
- **Visual Properties**: `{ x, y, size, color, label, type }`
- **Size Control**: Often based on node degree or custom properties
- **Color Coding**: By type, community, or other categorical attributes
- **Labeling**: Visible labels based on threshold settings

### Edge Attributes
- **Visual Properties**: `{ weight, color, label, type, directed }`
- **Weight Representation**: Visualized through thickness or other properties
- **Directionality**: Arrows for directed relationships
- **Type Differentiation**: Different rendering programs for different relationship types

### Edge Programs (WebGL Shaders)
- **`EdgeArrowProgram`**: Directed single arrow edges
- **`EdgeDoubleArrowProgram`**: Bidirectional arrows
- **`EdgeCurvedArrowProgram`**: Curved directed edges
- **`EdgeCurvedDoubleArrowProgram`**: Curved bidirectional
- **`EdgeCurveProgram`**: Smooth undirected curves
- **`EdgeRectangleProgram`**: Rectangular edge styling

### Camera Controls
- **Pan**: Drag to move the view
- **Zoom**: Scroll or pinch to zoom in/out
- **Rotation**: Rotate the entire graph view
- **Boundaries**: Constrain camera movement to specific areas
- **Animation**: Smooth transitions to specific positions

### Interaction Events
- **Node Hover**: Highlight the node and its neighbors
- **Node Click**: Select or focus on a node
- **Edge Hover**: Highlight the edge and connected nodes
- **Edge Click**: Select or inspect the relationship
- **Drag Nodes**: Interactive positioning of nodes

## Data Formats & Import/Export

### Supported Formats
- **JSON**: Direct graph import/export
  - Standard format: `{ nodes: [...], edges: [...] }`
  - Node format: `{ id, label, type, ...attributes }`
  - Edge format: `{ source, target, type, ...attributes }`

- **GEXF**: Gephi XML format
  - Import library: `graphology-gexf/browser`
  - Compatible with Gephi projects
  - Supports attributes and visualization properties

- **CSV**: Tabular data import
  - Parsing library: `papaparse`
  - Often converted to bipartite graphs
  - Useful for relational data

- **JSON-LD**: RDF-based linked data
  - Processing library: `jsonld`
  - Semantic web compatibility
  - Type and relationship mapping

### Import Patterns
- **Static JSON**: Load predefined graph datasets
- **Dynamic CSV**: Parse tabular data and convert to graph
- **RDF/JSON-LD**: Semantic data conversion to graph format

### Export Options
- **Image**: PNG/SVG export of current view
- **Graph Data**: JSON export of current graph structure
- **Library**: `@sigma/export-image` for image exports

## Event Systems

### Node Events
- `clickNode`: Node clicked
- `doubleClickNode`: Node double-clicked
- `enterNode`: Mouse enters node area
- `leaveNode`: Mouse leaves node area
- `downNode`: Mouse button pressed on node

### Edge Events
- `clickEdge`: Edge clicked
- `doubleClickEdge`: Edge double-clicked
- `enterEdge`: Mouse enters edge area
- `leaveEdge`: Mouse leaves edge area
- `downEdge`: Mouse button pressed on edge

### Camera Events
- `cameraUpdated`: Camera position/zoom changed
- `kill`: Sigma instance destroyed

### Global Events
- `beforeRender`: Before each render frame
- `afterRender`: After each render frame
- `rescale`: When graph is rescaled

## Performance & Rendering

### WebGL Rendering
- **Advantages**: Hardware-accelerated rendering
- **Performance**: Handles thousands of nodes/edges efficiently
- **Customization**: Custom shaders for specific visual effects

### Layout Optimization
- **Barnes-Hut Optimization**: For large force-directed graphs
- **Web Workers**: Keep UI responsive during layout computation
- **Batch Processing**: Efficient updates to large graphs

### Camera Efficiency
- **Frustum Culling**: Only render visible nodes/edges
- **Label Thresholds**: Control label visibility based on zoom level
- **Edge Programs**: Optimized rendering for different edge types

## Integration Patterns

### Data Pipeline
1. **Data Source**: CSV, JSON, GEXF, or JSON-LD
2. **Parsing**: Convert to Graphology format
3. **Processing**: Apply transformations, filtering, or analysis
4. **Loading**: Load into Sigma.js via React-Sigma
5. **Visualization**: Render with appropriate layouts and styling

### State Management
- **React State**: Control layout, selection, and filters
- **Sigma State**: Camera position, selected nodes, rendering settings
- **Graph State**: Node/edge attributes, clustering results

### Component Architecture
```
SigmaContainer
├── ControlsContainer
├── Graphology Graph
├── Layout (ForceAtlas2, Circular, etc.)
├── Event Handlers
└── Custom Rendering
```

### Common Patterns
- **Layout Switching**: Allow users to toggle between different layouts
- **Interactive Filtering**: Enable users to highlight/focus on specific node types
- **Search Functionality**: Find and center on specific nodes
- **Community Detection**: Identify and colorize node clusters
- **Responsive Design**: Adapt visualization to different screen sizes

## Best Practices

### Performance
1. Use Web Workers for heavy computations (like ForceAtlas2)
2. Implement proper data filtering (like LCC cropping)
3. Optimize rendering with appropriate thresholds
4. Use efficient data structures (Graphology)

### User Experience
1. Provide clear interaction feedback
2. Offer multiple layout options
3. Implement smooth transitions between states
4. Include appropriate visual cues (colors, sizes, labels)

### Data Handling
1. Validate graph structure before loading
2. Normalize node/edge attributes
3. Handle missing or incomplete data gracefully
4. Provide import/export capabilities for persistence