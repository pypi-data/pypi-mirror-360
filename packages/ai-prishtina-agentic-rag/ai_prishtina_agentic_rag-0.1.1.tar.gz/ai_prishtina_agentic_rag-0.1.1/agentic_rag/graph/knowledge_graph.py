"""
Knowledge graph implementation for Graph RAG.
"""

import uuid
from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from datetime import datetime

from pydantic import BaseModel, Field
from ..utils.logging import LoggerMixin
from ..utils.exceptions import RetrievalError


@dataclass
class GraphNode:
    """Represents a node in the knowledge graph."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    label: str = ""
    node_type: str = "entity"
    properties: Dict[str, Any] = field(default_factory=dict)
    embeddings: Optional[List[float]] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        return isinstance(other, GraphNode) and self.id == other.id


@dataclass 
class GraphEdge:
    """Represents an edge (relationship) in the knowledge graph."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str = ""
    target_id: str = ""
    relationship_type: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0
    created_at: datetime = field(default_factory=datetime.now)
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        return isinstance(other, GraphEdge) and self.id == other.id


class GraphStore(ABC):
    """Abstract base class for graph storage backends."""
    
    @abstractmethod
    async def add_node(self, node: GraphNode) -> bool:
        """Add a node to the graph."""
        pass
    
    @abstractmethod
    async def add_edge(self, edge: GraphEdge) -> bool:
        """Add an edge to the graph."""
        pass
    
    @abstractmethod
    async def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Get a node by ID."""
        pass
    
    @abstractmethod
    async def get_neighbors(self, node_id: str, max_hops: int = 1) -> List[GraphNode]:
        """Get neighboring nodes."""
        pass
    
    @abstractmethod
    async def find_nodes(self, query: str, node_type: Optional[str] = None) -> List[GraphNode]:
        """Find nodes matching a query."""
        pass
    
    @abstractmethod
    async def find_path(self, source_id: str, target_id: str, max_hops: int = 3) -> List[GraphNode]:
        """Find path between two nodes."""
        pass


class InMemoryGraphStore(GraphStore, LoggerMixin):
    """In-memory implementation of graph store."""
    
    def __init__(self):
        """Initialize in-memory graph store."""
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: Dict[str, GraphEdge] = {}
        self.adjacency: Dict[str, Set[str]] = {}  # node_id -> set of connected node_ids
        self.reverse_adjacency: Dict[str, Set[str]] = {}  # reverse edges
    
    async def add_node(self, node: GraphNode) -> bool:
        """Add a node to the graph."""
        try:
            self.nodes[node.id] = node
            if node.id not in self.adjacency:
                self.adjacency[node.id] = set()
            if node.id not in self.reverse_adjacency:
                self.reverse_adjacency[node.id] = set()
            
            self.logger.debug(f"Added node: {node.id} ({node.label})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add node {node.id}: {e}")
            return False
    
    async def add_edge(self, edge: GraphEdge) -> bool:
        """Add an edge to the graph."""
        try:
            # Ensure source and target nodes exist
            if edge.source_id not in self.nodes or edge.target_id not in self.nodes:
                self.logger.warning(f"Edge references non-existent nodes: {edge.source_id} -> {edge.target_id}")
                return False
            
            self.edges[edge.id] = edge
            
            # Update adjacency lists
            self.adjacency[edge.source_id].add(edge.target_id)
            self.reverse_adjacency[edge.target_id].add(edge.source_id)
            
            self.logger.debug(f"Added edge: {edge.source_id} -> {edge.target_id} ({edge.relationship_type})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add edge {edge.id}: {e}")
            return False
    
    async def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Get a node by ID."""
        return self.nodes.get(node_id)
    
    async def get_neighbors(self, node_id: str, max_hops: int = 1) -> List[GraphNode]:
        """Get neighboring nodes within max_hops."""
        if node_id not in self.nodes:
            return []
        
        visited = set()
        current_level = {node_id}
        
        for hop in range(max_hops):
            next_level = set()
            
            for current_node_id in current_level:
                if current_node_id in visited:
                    continue
                
                visited.add(current_node_id)
                
                # Add direct neighbors
                neighbors = self.adjacency.get(current_node_id, set())
                reverse_neighbors = self.reverse_adjacency.get(current_node_id, set())
                
                next_level.update(neighbors)
                next_level.update(reverse_neighbors)
            
            current_level = next_level - visited
            
            if not current_level:
                break
        
        # Return neighbor nodes (excluding the original node)
        neighbor_nodes = []
        for neighbor_id in visited:
            if neighbor_id != node_id and neighbor_id in self.nodes:
                neighbor_nodes.append(self.nodes[neighbor_id])
        
        return neighbor_nodes
    
    async def find_nodes(self, query: str, node_type: Optional[str] = None) -> List[GraphNode]:
        """Find nodes matching a query."""
        query_lower = query.lower()
        matching_nodes = []
        
        for node in self.nodes.values():
            # Check node type filter
            if node_type and node.node_type != node_type:
                continue
            
            # Check if query matches label or properties
            if (query_lower in node.label.lower() or
                any(query_lower in str(value).lower() for value in node.properties.values())):
                matching_nodes.append(node)
        
        # Sort by relevance (simple string matching score)
        def relevance_score(node):
            score = 0
            if query_lower in node.label.lower():
                score += 10
            for value in node.properties.values():
                if query_lower in str(value).lower():
                    score += 1
            return score
        
        matching_nodes.sort(key=relevance_score, reverse=True)
        return matching_nodes
    
    async def find_path(self, source_id: str, target_id: str, max_hops: int = 3) -> List[GraphNode]:
        """Find shortest path between two nodes using BFS."""
        if source_id not in self.nodes or target_id not in self.nodes:
            return []
        
        if source_id == target_id:
            return [self.nodes[source_id]]
        
        # BFS to find shortest path
        queue = [(source_id, [source_id])]
        visited = {source_id}
        
        while queue:
            current_id, path = queue.pop(0)
            
            if len(path) > max_hops + 1:
                continue
            
            # Check all neighbors
            neighbors = self.adjacency.get(current_id, set()) | self.reverse_adjacency.get(current_id, set())
            
            for neighbor_id in neighbors:
                if neighbor_id == target_id:
                    # Found target, return path
                    final_path = path + [neighbor_id]
                    return [self.nodes[node_id] for node_id in final_path]
                
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append((neighbor_id, path + [neighbor_id]))
        
        return []  # No path found
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get graph statistics."""
        node_types = {}
        edge_types = {}
        
        for node in self.nodes.values():
            node_types[node.node_type] = node_types.get(node.node_type, 0) + 1
        
        for edge in self.edges.values():
            edge_types[edge.relationship_type] = edge_types.get(edge.relationship_type, 0) + 1
        
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "node_types": node_types,
            "edge_types": edge_types,
            "average_degree": sum(len(neighbors) for neighbors in self.adjacency.values()) / max(len(self.nodes), 1)
        }


class KnowledgeGraph(LoggerMixin):
    """Main knowledge graph interface."""
    
    def __init__(self, store: Optional[GraphStore] = None):
        """
        Initialize knowledge graph.
        
        Args:
            store: Graph storage backend (defaults to in-memory)
        """
        self.store = store or InMemoryGraphStore()
    
    async def add_entity(self, label: str, entity_type: str = "entity", properties: Optional[Dict[str, Any]] = None) -> GraphNode:
        """Add an entity node to the graph."""
        node = GraphNode(
            label=label,
            node_type=entity_type,
            properties=properties or {}
        )
        
        success = await self.store.add_node(node)
        if not success:
            raise RetrievalError(f"Failed to add entity: {label}")
        
        return node
    
    async def add_relationship(self, source_label: str, target_label: str, relationship_type: str, properties: Optional[Dict[str, Any]] = None) -> GraphEdge:
        """Add a relationship between entities."""
        # Find source and target nodes
        source_nodes = await self.store.find_nodes(source_label)
        target_nodes = await self.store.find_nodes(target_label)
        
        if not source_nodes:
            raise RetrievalError(f"Source entity not found: {source_label}")
        if not target_nodes:
            raise RetrievalError(f"Target entity not found: {target_label}")
        
        # Use first matching nodes
        source_node = source_nodes[0]
        target_node = target_nodes[0]
        
        edge = GraphEdge(
            source_id=source_node.id,
            target_id=target_node.id,
            relationship_type=relationship_type,
            properties=properties or {}
        )
        
        success = await self.store.add_edge(edge)
        if not success:
            raise RetrievalError(f"Failed to add relationship: {source_label} -> {target_label}")
        
        return edge
    
    async def query(self, query: str, max_results: int = 10) -> List[GraphNode]:
        """Query the knowledge graph."""
        return await self.store.find_nodes(query)
    
    async def get_context(self, entity_label: str, max_hops: int = 2) -> List[GraphNode]:
        """Get contextual information around an entity."""
        # Find the entity
        entities = await self.store.find_nodes(entity_label)
        if not entities:
            return []
        
        entity = entities[0]
        
        # Get neighbors
        neighbors = await self.store.get_neighbors(entity.id, max_hops)
        
        # Include the original entity
        return [entity] + neighbors
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge graph statistics."""
        if hasattr(self.store, 'get_statistics'):
            return self.store.get_statistics()
        return {"message": "Statistics not available for this store type"}
