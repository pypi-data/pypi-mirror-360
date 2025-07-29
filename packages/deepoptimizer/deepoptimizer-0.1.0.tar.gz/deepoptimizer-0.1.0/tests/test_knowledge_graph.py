"""
Tests for the knowledge graph operations.
"""

import pytest
import json
from pathlib import Path
import tempfile
from unittest.mock import Mock, patch
import networkx as nx

from deepoptimizer.core.knowledge_graph import KnowledgeGraph
from deepoptimizer.core.models import Technique, TechniqueRelationship


class TestKnowledgeGraph:
    """Test the KnowledgeGraph functionality."""
    
    @pytest.fixture
    def knowledge_graph(self):
        """Create a KnowledgeGraph instance."""
        return KnowledgeGraph()
        
    @pytest.fixture
    def sample_techniques(self):
        """Create sample techniques for testing."""
        techniques = [
            Technique(
                name="Mixed Precision Training",
                category="training",
                description="Use FP16 for faster training",
                frameworks=["pytorch", "tensorflow"],
                hardware_requirements=["gpu"],
                expected_speedup=2.0,
                memory_reduction=0.5
            ),
            Technique(
                name="Quantization",
                category="compression",
                description="Reduce model size with INT8",
                frameworks=["pytorch", "tensorflow"],
                hardware_requirements=["cpu", "gpu"],
                expected_speedup=1.5,
                memory_reduction=0.75
            ),
            Technique(
                name="Pruning",
                category="compression",
                description="Remove unnecessary weights",
                frameworks=["pytorch"],
                expected_speedup=1.3,
                memory_reduction=0.6
            ),
            Technique(
                name="Knowledge Distillation",
                category="compression",
                description="Train smaller student model",
                frameworks=["pytorch", "tensorflow"],
                expected_speedup=3.0,
                memory_reduction=0.8
            ),
            Technique(
                name="Gradient Accumulation",
                category="training",
                description="Accumulate gradients over batches",
                frameworks=["pytorch", "tensorflow"],
                expected_speedup=1.0,
                memory_reduction=-0.1  # Slightly increases memory
            )
        ]
        return techniques
        
    @pytest.fixture
    def sample_relationships(self):
        """Create sample technique relationships."""
        return [
            TechniqueRelationship(
                source="Mixed Precision Training",
                target="Gradient Accumulation",
                type="synergizes_with",
                description="Can handle larger effective batch sizes",
                strength=0.8
            ),
            TechniqueRelationship(
                source="Quantization",
                target="Pruning",
                type="synergizes_with",
                description="Combined compression techniques",
                strength=0.7
            ),
            TechniqueRelationship(
                source="Quantization",
                target="Mixed Precision Training",
                type="conflicts_with",
                description="Different numeric precision approaches",
                strength=0.6
            ),
            TechniqueRelationship(
                source="Knowledge Distillation",
                target="Pruning",
                type="improves",
                description="Distillation helps maintain accuracy after pruning",
                strength=0.9
            )
        ]
        
    def test_add_techniques(self, knowledge_graph, sample_techniques):
        """Test adding techniques to the graph."""
        for technique in sample_techniques:
            knowledge_graph.add_technique(technique)
            
        assert len(knowledge_graph.techniques) == len(sample_techniques)
        assert "Mixed Precision Training" in knowledge_graph.techniques
        
        # Check node attributes
        node_data = knowledge_graph.graph.nodes["Mixed Precision Training"]
        assert node_data["category"] == "training"
        assert node_data["expected_speedup"] == 2.0
        
    def test_add_relationships(self, knowledge_graph, sample_techniques, sample_relationships):
        """Test adding relationships between techniques."""
        # Add techniques first
        for technique in sample_techniques:
            knowledge_graph.add_technique(technique)
            
        # Add relationships
        for relationship in sample_relationships:
            knowledge_graph.add_relationship(relationship)
            
        # Check edges exist
        assert knowledge_graph.graph.has_edge(
            "Mixed Precision Training",
            "Gradient Accumulation"
        )
        
        # Check edge attributes
        edge_data = knowledge_graph.graph.edges[
            "Quantization", "Mixed Precision Training"
        ]
        assert edge_data["type"] == "conflicts_with"
        assert edge_data["strength"] == 0.6
        
    def test_find_compatible_techniques(self, knowledge_graph, sample_techniques, sample_relationships):
        """Test finding compatible techniques."""
        # Setup graph
        for technique in sample_techniques:
            knowledge_graph.add_technique(technique)
        for relationship in sample_relationships:
            knowledge_graph.add_relationship(relationship)
            
        # Find techniques compatible with Mixed Precision
        compatible = knowledge_graph.find_compatible_techniques(
            "Mixed Precision Training"
        )
        
        assert "Gradient Accumulation" in compatible
        assert "Quantization" not in compatible  # Conflicts
        
    def test_find_conflicting_techniques(self, knowledge_graph, sample_techniques, sample_relationships):
        """Test finding conflicting techniques."""
        # Setup graph
        for technique in sample_techniques:
            knowledge_graph.add_technique(technique)
        for relationship in sample_relationships:
            knowledge_graph.add_relationship(relationship)
            
        conflicts = knowledge_graph.find_conflicts("Quantization")
        
        assert "Mixed Precision Training" in conflicts
        assert len(conflicts) == 1
        
    def test_find_synergistic_techniques(self, knowledge_graph, sample_techniques, sample_relationships):
        """Test finding synergistic techniques."""
        # Setup graph
        for technique in sample_techniques:
            knowledge_graph.add_technique(technique)
        for relationship in sample_relationships:
            knowledge_graph.add_relationship(relationship)
            
        synergies = knowledge_graph.find_synergies("Mixed Precision Training")
        
        assert "Gradient Accumulation" in synergies
        assert synergies["Gradient Accumulation"]["strength"] == 0.8
        
    def test_calculate_combined_impact(self, knowledge_graph, sample_techniques, sample_relationships):
        """Test calculating combined impact of multiple techniques."""
        # Setup graph
        for technique in sample_techniques:
            knowledge_graph.add_technique(technique)
        for relationship in sample_relationships:
            knowledge_graph.add_relationship(relationship)
            
        # Calculate impact of compatible techniques
        techniques_to_apply = ["Quantization", "Pruning"]
        impact = knowledge_graph.calculate_combined_impact(techniques_to_apply)
        
        # Should account for synergy
        assert impact["speedup"] > 1.5  # More than just Quantization
        assert impact["memory_reduction"] > 0.75  # More than individual techniques
        assert impact["synergy_bonus"] > 0
        
    def test_find_implementation_order(self, knowledge_graph, sample_techniques):
        """Test finding optimal implementation order."""
        # Add techniques with dependencies
        for technique in sample_techniques:
            knowledge_graph.add_technique(technique)
            
        # Add dependency relationships
        knowledge_graph.add_relationship(
            TechniqueRelationship(
                source="Pruning",
                target="Quantization",
                type="requires",
                description="Prune before quantizing"
            )
        )
        
        order = knowledge_graph.find_implementation_order(
            ["Quantization", "Pruning", "Mixed Precision Training"]
        )
        
        # Pruning should come before Quantization
        assert order.index("Pruning") < order.index("Quantization")
        
    def test_query_by_hardware(self, knowledge_graph, sample_techniques):
        """Test querying techniques by hardware requirements."""
        for technique in sample_techniques:
            knowledge_graph.add_technique(technique)
            
        # Query GPU techniques
        gpu_techniques = knowledge_graph.query_by_hardware("gpu")
        assert "Mixed Precision Training" in gpu_techniques
        assert "Quantization" in gpu_techniques
        
        # Query CPU techniques
        cpu_techniques = knowledge_graph.query_by_hardware("cpu")
        assert "Quantization" in cpu_techniques
        assert "Mixed Precision Training" not in cpu_techniques
        
    def test_query_by_framework(self, knowledge_graph, sample_techniques):
        """Test querying techniques by framework support."""
        for technique in sample_techniques:
            knowledge_graph.add_technique(technique)
            
        # Query PyTorch techniques
        pytorch_techniques = knowledge_graph.query_by_framework("pytorch")
        assert len(pytorch_techniques) == 5  # All support PyTorch
        
        # Query TensorFlow techniques
        tf_techniques = knowledge_graph.query_by_framework("tensorflow")
        assert "Pruning" not in tf_techniques  # Only supports PyTorch
        
    def test_query_by_category(self, knowledge_graph, sample_techniques):
        """Test querying techniques by category."""
        for technique in sample_techniques:
            knowledge_graph.add_technique(technique)
            
        # Query training techniques
        training_techniques = knowledge_graph.query_by_category("training")
        assert "Mixed Precision Training" in training_techniques
        assert "Gradient Accumulation" in training_techniques
        assert len(training_techniques) == 2
        
        # Query compression techniques
        compression_techniques = knowledge_graph.query_by_category("compression")
        assert "Quantization" in compression_techniques
        assert "Pruning" in compression_techniques
        assert "Knowledge Distillation" in compression_techniques
        
    def test_shortest_path(self, knowledge_graph, sample_techniques, sample_relationships):
        """Test finding shortest path between techniques."""
        # Setup graph
        for technique in sample_techniques:
            knowledge_graph.add_technique(technique)
        for relationship in sample_relationships:
            knowledge_graph.add_relationship(relationship)
            
        path = knowledge_graph.find_path(
            "Mixed Precision Training",
            "Pruning"
        )
        
        assert path is not None
        assert len(path) > 1
        assert path[0] == "Mixed Precision Training"
        assert path[-1] == "Pruning"
        
    def test_subgraph_extraction(self, knowledge_graph, sample_techniques, sample_relationships):
        """Test extracting subgraphs around techniques."""
        # Setup graph
        for technique in sample_techniques:
            knowledge_graph.add_technique(technique)
        for relationship in sample_relationships:
            knowledge_graph.add_relationship(relationship)
            
        # Extract subgraph around Quantization
        subgraph = knowledge_graph.get_subgraph("Quantization", radius=1)
        
        assert "Quantization" in subgraph.nodes
        assert "Pruning" in subgraph.nodes  # Connected
        assert "Mixed Precision Training" in subgraph.nodes  # Connected
        assert "Knowledge Distillation" not in subgraph.nodes  # Not directly connected
        
    def test_graph_metrics(self, knowledge_graph, sample_techniques, sample_relationships):
        """Test calculating graph metrics."""
        # Setup graph
        for technique in sample_techniques:
            knowledge_graph.add_technique(technique)
        for relationship in sample_relationships:
            knowledge_graph.add_relationship(relationship)
            
        metrics = knowledge_graph.calculate_metrics()
        
        assert metrics["num_nodes"] == len(sample_techniques)
        assert metrics["num_edges"] == len(sample_relationships)
        assert "avg_degree" in metrics
        assert "density" in metrics
        assert "num_components" in metrics
        
    def test_centrality_analysis(self, knowledge_graph, sample_techniques, sample_relationships):
        """Test analyzing technique centrality."""
        # Setup graph
        for technique in sample_techniques:
            knowledge_graph.add_technique(technique)
        for relationship in sample_relationships:
            knowledge_graph.add_relationship(relationship)
            
        centrality = knowledge_graph.calculate_centrality()
        
        # Techniques with more connections should have higher centrality
        assert centrality["Quantization"] > centrality["Gradient Accumulation"]
        assert centrality["Pruning"] > centrality["Gradient Accumulation"]
        
    def test_save_and_load(self, knowledge_graph, sample_techniques, sample_relationships):
        """Test saving and loading the graph."""
        # Setup graph
        for technique in sample_techniques:
            knowledge_graph.add_technique(technique)
        for relationship in sample_relationships:
            knowledge_graph.add_relationship(relationship)
            
        with tempfile.TemporaryDirectory() as temp_dir:
            save_path = Path(temp_dir) / "test_graph.json"
            
            # Save graph
            knowledge_graph.save(save_path)
            assert save_path.exists()
            
            # Load into new graph
            new_graph = KnowledgeGraph()
            new_graph.load(save_path)
            
            # Verify contents
            assert len(new_graph.techniques) == len(sample_techniques)
            assert new_graph.graph.number_of_edges() == len(sample_relationships)
            
    def test_graph_visualization(self, knowledge_graph, sample_techniques):
        """Test graph visualization export."""
        for technique in sample_techniques:
            knowledge_graph.add_technique(technique)
            
        # Export for visualization
        vis_data = knowledge_graph.export_for_visualization()
        
        assert "nodes" in vis_data
        assert "edges" in vis_data
        assert len(vis_data["nodes"]) == len(sample_techniques)
        
        # Check node data includes visualization properties
        node = vis_data["nodes"][0]
        assert "id" in node
        assert "label" in node
        assert "category" in node
        
    def test_recommendation_engine(self, knowledge_graph, sample_techniques, sample_relationships):
        """Test technique recommendation based on context."""
        # Setup graph
        for technique in sample_techniques:
            knowledge_graph.add_technique(technique)
        for relationship in sample_relationships:
            knowledge_graph.add_relationship(relationship)
            
        # Get recommendations for a context
        context = {
            "framework": "pytorch",
            "hardware": "gpu",
            "goal": "compression",
            "applied_techniques": ["Mixed Precision Training"]
        }
        
        recommendations = knowledge_graph.recommend_techniques(context, top_k=3)
        
        assert len(recommendations) <= 3
        assert all(t["score"] > 0 for t in recommendations)
        # Should not recommend conflicting techniques
        assert not any(
            t["name"] == "Quantization" for t in recommendations
        )  # Conflicts with Mixed Precision
        
    def test_impact_propagation(self, knowledge_graph, sample_techniques, sample_relationships):
        """Test impact propagation through the graph."""
        # Setup graph
        for technique in sample_techniques:
            knowledge_graph.add_technique(technique)
        for relationship in sample_relationships:
            knowledge_graph.add_relationship(relationship)
            
        # Simulate applying a technique and propagating impact
        impact = knowledge_graph.propagate_impact(
            "Knowledge Distillation",
            initial_impact={"accuracy": 0.95, "speedup": 3.0}
        )
        
        # Should improve Pruning due to relationship
        assert "Pruning" in impact
        assert impact["Pruning"]["accuracy"] > 0  # Positive impact
        
    def test_cycle_detection(self, knowledge_graph, sample_techniques):
        """Test detecting cycles in technique dependencies."""
        for technique in sample_techniques[:3]:
            knowledge_graph.add_technique(technique)
            
        # Create a cycle
        knowledge_graph.add_relationship(
            TechniqueRelationship(
                source="Mixed Precision Training",
                target="Quantization",
                type="requires"
            )
        )
        knowledge_graph.add_relationship(
            TechniqueRelationship(
                source="Quantization",
                target="Pruning",
                type="requires"
            )
        )
        knowledge_graph.add_relationship(
            TechniqueRelationship(
                source="Pruning",
                target="Mixed Precision Training",
                type="requires"
            )
        )
        
        cycles = knowledge_graph.find_cycles()
        assert len(cycles) > 0
        assert len(cycles[0]) == 3  # Three techniques in the cycle