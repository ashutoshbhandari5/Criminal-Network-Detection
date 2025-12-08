import matplotlib.pyplot as plt
import networkx as nx
import yaml
import os


class NetworkVisualizer:
    def __init__(self, graph: nx.Graph, config_path="config/analysis_config.yaml"):
        self.graph = graph

        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.colors = self.config['visualization']['colors']
        self.node_size_multiplier = self.config['visualization']['node_size_multiplier']
        self.figure_size = tuple(self.config['visualization']['figure_size'])
        self.dpi = self.config['visualization']['dpi']

    def visualize_criminal_network(self, network_structure, scenario, output_path="outputs/visualizations"):
        print(f"\nGenerating Scenario {scenario} visualization")

        all_network_members = self._extract_all_members(network_structure)

        subgraph_nodes = set(all_network_members)

        for member in all_network_members[:5]:
            neighbors = list(self.graph.neighbors(member))[:3]
            subgraph_nodes.update(neighbors)

        subgraph = self.graph.subgraph(subgraph_nodes)

        plt.figure(figsize=self.figure_size)

        if self.config['visualization']['layout_algorithm'] == 'spring':
            pos = nx.spring_layout(subgraph, k=2, iterations=50, seed=42)
        elif self.config['visualization']['layout_algorithm'] == 'kamada_kawai':
            pos = nx.kamada_kawai_layout(subgraph)
        else:
            pos = nx.circular_layout(subgraph)

        node_colors = []
        node_sizes = []

        for node in subgraph.nodes():
            color, size = self._get_node_style(node, network_structure)
            node_colors.append(color)
            node_sizes.append(size)

        nx.draw_networkx_edges(subgraph, pos, alpha=0.3, width=0.5, edge_color='gray')

        nx.draw_networkx_nodes(subgraph, pos, node_color=node_colors,
                              node_size=node_sizes, alpha=0.9)

        key_labels = {}
        for node in all_network_members:
            if node in subgraph.nodes():
                name = self.graph.nodes[node].get('name', f'@node{node}')
                key_labels[node] = name

        nx.draw_networkx_labels(subgraph, pos, labels=key_labels,
                               font_size=8, font_weight='bold')

        title = self._create_visualization_title(network_structure, scenario)
        plt.title(title, fontsize=14, fontweight='bold', pad=20)

        self._add_legend(scenario)

        plt.axis('off')
        plt.tight_layout()

        os.makedirs(output_path, exist_ok=True)
        filename = f"criminal_network_scenario_{scenario}.png"
        filepath = os.path.join(output_path, filename)
        plt.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        print(f"  Saved visualization to {filepath}")

        return filepath

    def visualize_full_network_overview(self, output_path="outputs/visualizations"):
        print("\nGenerating network overview")

        plt.figure(figsize=(16, 12))

        pos = nx.spring_layout(self.graph, k=0.5, iterations=30, seed=42)

        node_sizes = [self.graph.degree(node) * 2 for node in self.graph.nodes()]

        nx.draw_networkx_edges(self.graph, pos, alpha=0.1, width=0.3, edge_color='lightgray')
        nx.draw_networkx_nodes(self.graph, pos, node_size=node_sizes,
                              node_color='skyblue', alpha=0.6)

        plt.title("Complete Flitter Social Network Overview", fontsize=16, fontweight='bold')
        plt.axis('off')
        plt.tight_layout()

        os.makedirs(output_path, exist_ok=True)
        filepath = os.path.join(output_path, "network_overview.png")
        plt.savefig(filepath, dpi=200, bbox_inches='tight')
        plt.close()

        print(f"Saved overview to {filepath}")

        return filepath

    def visualize_degree_distribution(self, output_path="outputs/visualizations"):
        print("\nGenerating degree distribution")

        degrees = [self.graph.degree(node) for node in self.graph.nodes()]

        plt.figure(figsize=(12, 6))

        plt.subplot(1, 2, 1)
        plt.hist(degrees, bins=50, color='skyblue', edgecolor='black', alpha=0.7)
        plt.xlabel('Degree (Number of Connections)', fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.title('Degree Distribution', fontsize=14, fontweight='bold')
        plt.axvline(x=40, color='red', linestyle='--', linewidth=2, label='Expected Employee (~40)')
        plt.axvline(x=100, color='darkred', linestyle='--', linewidth=2, label='Expected Leader (100+)')
        plt.legend()
        plt.grid(True, alpha=0.3)

        plt.subplot(1, 2, 2)
        sorted_degrees = sorted(degrees, reverse=True)
        plt.plot(range(len(sorted_degrees)), sorted_degrees, color='navy', linewidth=2)
        plt.xlabel('Node Rank', fontsize=12)
        plt.ylabel('Degree', fontsize=12)
        plt.title('Cumulative Degree Distribution', fontsize=14, fontweight='bold')
        plt.axhline(y=40, color='red', linestyle='--', linewidth=2, label='Employee threshold')
        plt.axhline(y=100, color='darkred', linestyle='--', linewidth=2, label='Leader threshold')
        plt.legend()
        plt.grid(True, alpha=0.3)

        plt.tight_layout()

        os.makedirs(output_path, exist_ok=True)
        filepath = os.path.join(output_path, "degree_distribution.png")
        plt.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        print(f" Saved degree distribution to {filepath}")

        return filepath

    def visualize_centrality_comparison(self, metrics, top_n=20, output_path="outputs/visualizations"):
        print("\nGenerating centrality comparison")

        fig, axes = plt.subplots(2, 2, figsize=(16, 12))

        self._plot_centrality(axes[0, 0], metrics['degree_centrality'],
                             'Degree Centrality', top_n)

        self._plot_centrality(axes[0, 1], metrics['betweenness_centrality'],
                             'Betweenness Centrality', top_n)

        self._plot_centrality(axes[1, 0], metrics['closeness_centrality'],
                             'Closeness Centrality', top_n)

        self._plot_centrality(axes[1, 1], metrics['clustering_coefficient'],
                             'Clustering Coefficient', top_n)

        plt.suptitle('Network Centrality Metrics Comparison', fontsize=16, fontweight='bold')
        plt.tight_layout()

        os.makedirs(output_path, exist_ok=True)
        filepath = os.path.join(output_path, "centrality_comparison.png")
        plt.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        print(f"  Saved centrality comparison to {filepath}")

        return filepath

    def _plot_centrality(self, ax, centrality_dict, title, top_n):
        sorted_nodes = sorted(centrality_dict.items(), key=lambda x: x[1], reverse=True)[:top_n]

        node_ids = [node for node, _ in sorted_nodes]
        values = [val for _, val in sorted_nodes]
        names = [self.graph.nodes[node].get('name', f'@{node}') for node in node_ids]

        ax.barh(range(len(names)), values, color='steelblue', alpha=0.8)
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names, fontsize=8)
        ax.set_xlabel('Centrality Value', fontsize=10)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        ax.invert_yaxis()

    def _extract_all_members(self, network_structure):
        members = []

        if 'employee' in network_structure:
            members.append(network_structure['employee'])

        if 'handlers' in network_structure:
            members.extend(network_structure['handlers'])

        if 'boris' in network_structure:
            members.append(network_structure['boris'])

        if 'morris' in network_structure:
            members.append(network_structure['morris'])

        if 'horace' in network_structure:
            members.append(network_structure['horace'])

        if 'fearless_leader' in network_structure:
            members.append(network_structure['fearless_leader'])

        return members

    def _get_node_style(self, node_id, network_structure):
        base_size = self.node_size_multiplier

        if 'employee' in network_structure and node_id == network_structure['employee']:
            return self.colors['employee'], base_size * 15

        if 'handlers' in network_structure and node_id in network_structure['handlers']:
            return self.colors['handler'], base_size * 12

        if 'boris' in network_structure and node_id == network_structure['boris']:
            return self.colors['middleman'], base_size * 10

        if 'morris' in network_structure and node_id == network_structure['morris']:
            return self.colors['middleman'], base_size * 10

        if 'horace' in network_structure and node_id == network_structure['horace']:
            return self.colors['middleman'], base_size * 10

        if 'fearless_leader' in network_structure and node_id == network_structure['fearless_leader']:
            return self.colors['leader'], base_size * 20

        all_members = self._extract_all_members(network_structure)
        if any(node_id in self.graph.neighbors(member) for member in all_members):
            return self.colors['network_member'], base_size * 5

        return self.colors['normal'], base_size * 3

    def _create_visualization_title(self, network_structure, scenario):
        title = f"Criminal Network Detection - Scenario {scenario}\n"

        if 'employee' in network_structure:
            emp_name = self.graph.nodes[network_structure['employee']].get('name', '')
            title += f"Employee: {emp_name} | "

        if scenario == 'A':
            if 'boris' in network_structure:
                boris_name = self.graph.nodes[network_structure['boris']].get('name', '')
                title += f"Middleman (Boris): {boris_name} | "
        else:
            title += "Three Middlemen Structure | "

        if 'fearless_leader' in network_structure:
            leader_name = self.graph.nodes[network_structure['fearless_leader']].get('name', '')
            title += f"Leader: {leader_name}"

        return title

    def _add_legend(self, scenario):
        from matplotlib.patches import Patch

        legend_elements = [
            Patch(facecolor=self.colors['employee'], label='Employee (Insider)'),
            Patch(facecolor=self.colors['handler'], label='Handlers'),
            Patch(facecolor=self.colors['middleman'],
                  label='Middleman (Boris)' if scenario == 'A' else 'Middlemen (Boris/Morris/Horace)'),
            Patch(facecolor=self.colors['leader'], label='Fearless Leader'),
            Patch(facecolor=self.colors['network_member'], label='Network Associates'),
            Patch(facecolor=self.colors['normal'], label='Other Contacts')
        ]

        plt.legend(handles=legend_elements, loc='upper left',
                  bbox_to_anchor=(0.02, 0.98), fontsize=10)
