import networkx as nx
import matplotlib.pyplot as plt
import io
import base64

class KnowledgeGraph:
    def __init__(self):
        self.graph = nx.DiGraph()

    def build(self, extracted_data: dict):
        """Build knowledge graph from extracted data"""
        self.graph.clear()
        
        decisions = extracted_data.get("decisions", [])
        dependencies = extracted_data.get("dependencies", {})
        risks = extracted_data.get("risks", [])
        
        # Add decisions as nodes
        for decision in decisions:
            self.graph.add_node(decision, type="decision")
        
        # Add dependencies as nodes and edges
        for decision, deps in dependencies.items():
            for dep in deps:
                self.graph.add_node(dep, type="dependency")
                self.graph.add_edge(decision, dep, relation="depends_on")
        
        # Add risks as nodes and edges (risk affects decision)
        for risk in risks:
            self.graph.add_node(risk, type="risk")
            # Link risk to all decisions for simplicity
            for decision in decisions:
                self.graph.add_edge(risk, decision, relation="affects")
        
        return self.graph

    def get_graph_info(self):
        """Return graph statistics"""
        return {
            "nodes": list(self.graph.nodes(data=True)),
            "edges": list(self.graph.edges(data=True)),
            "num_nodes": self.graph.number_of_nodes(),
            "num_edges": self.graph.number_of_edges()
        }

    def draw_graph(self):
        """Draw graph and return as image"""
        plt.figure(figsize=(10, 6))
        pos = nx.spring_layout(self.graph, seed=42)
        
        # Color nodes by type
        node_colors = []
        for node, data in self.graph.nodes(data=True):
            if data.get("type") == "decision":
                node_colors.append("lightblue")
            elif data.get("type") == "dependency":
                node_colors.append("lightgreen")
            elif data.get("type") == "risk":
                node_colors.append("salmon")
            else:
                node_colors.append("gray")
        
        nx.draw(
            self.graph, pos, 
            with_labels=True, 
            node_color=node_colors, 
            node_size=2000, 
            font_size=8,
            arrows=True
        )
        
        # Save to bytes
        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        plt.close()
        
        return buf