import networkx as nx
import pandas as pd
import community as community_louvain


class SocialNetworkAnalyzer:
    def __init__(self, links_df: pd.DataFrame, entities_df: pd.DataFrame, locations_df: pd.DataFrame):
        self.links_df = links_df
        self.entities_df = entities_df
        self.locations_df = locations_df
        self.graph = None
        self.metrics = {}

    def build_graph(self):
        print("Now I'm building social network graph...")

        self.graph = nx.Graph()

        for _, row in self.entities_df.iterrows():
            node_id = row['ID']
            self.graph.add_node(
                node_id,
                name=row['Name'],
                type=row['Type']
            )

        for _, row in self.locations_df.iterrows():
            node_id = row['ID']
            if node_id in self.graph.nodes:
                self.graph.nodes[node_id]['city'] = row['City']

        for _, row in self.links_df.iterrows():
            self.graph.add_edge(row['ID1'], row['ID2'])

        print(f" Graph created with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges\n")

        return self.graph

    def calculate_all_metrics(self):
        print("Calculating network metrics...")

        print(" Computing degree centrality...")
        degree_centrality = nx.degree_centrality(self.graph)

        print(" Computing betweenness centrality (using approximation for speed)...")
        k_sample = min(500, self.graph.number_of_nodes())
        betweenness_centrality = nx.betweenness_centrality(self.graph, k=k_sample)

        print(" Computing closeness centrality...")
        closeness_centrality = nx.closeness_centrality(self.graph)

        print(" Computing eigenvector centrality...")
        try:
            eigenvector_centrality = nx.eigenvector_centrality(self.graph, max_iter=1000)
        except:
            eigenvector_centrality = {}
            print(" (Eigenvector centrality calculation did not converge)")

        print(" Computing clustering coefficients...")
        clustering_coef = nx.clustering(self.graph)

        print(" Detecting communities...")
        communities = community_louvain.best_partition(self.graph)

        self.metrics = {
            'degree_centrality': degree_centrality,
            'betweenness_centrality': betweenness_centrality,
            'closeness_centrality': closeness_centrality,
            'eigenvector_centrality': eigenvector_centrality,
            'clustering_coefficient': clustering_coef,
            'communities': communities
        }

        print("Calculation done for all the metrices\n")

        return self.metrics

    def get_node_degree(self, node_id):
        return self.graph.degree(node_id)

    def get_neighbors(self, node_id):
        return list(self.graph.neighbors(node_id))

    def get_nodes_by_degree_range(self, min_degree, max_degree):
        nodes = []
        for node in self.graph.nodes():
            degree = self.graph.degree(node)
            if min_degree <= degree <= max_degree:
                nodes.append((node, degree))

        return sorted(nodes, key=lambda x: x[1], reverse=True)

    def get_common_neighbors(self, node1, node2):
        neighbors1 = set(self.graph.neighbors(node1))
        neighbors2 = set(self.graph.neighbors(node2))
        return list(neighbors1.intersection(neighbors2))

    def find_paths_between_nodes(self, source, target, max_length=5):
        try:
            paths = list(nx.all_simple_paths(self.graph, source, target, cutoff=max_length))
            return paths
        except:
            return []

    def get_node_info(self, node_id):
        if node_id not in self.graph.nodes:
            return {}

        info = {
            'id': node_id,
            'name': self.graph.nodes[node_id].get('name', 'Unknown'),
            'city': self.graph.nodes[node_id].get('city', 'Unknown'),
            'degree': self.graph.degree(node_id),
            'neighbors': list(self.graph.neighbors(node_id))
        }

        if self.metrics:
            info['degree_centrality'] = self.metrics['degree_centrality'].get(node_id, 0)
            info['betweenness_centrality'] = self.metrics['betweenness_centrality'].get(node_id, 0)
            info['closeness_centrality'] = self.metrics['closeness_centrality'].get(node_id, 0)
            info['clustering_coefficient'] = self.metrics['clustering_coefficient'].get(node_id, 0)
            info['community'] = self.metrics['communities'].get(node_id, -1)

        return info

    def get_top_nodes_by_metric(self, metric_name, top_n=10):
        if metric_name not in self.metrics:
            return []

        metric_data = self.metrics[metric_name]
        sorted_nodes = sorted(metric_data.items(), key=lambda x: x[1], reverse=True)

        return sorted_nodes[:top_n]

    def analyze_subgraph(self, node_ids):
        subgraph = self.graph.subgraph(node_ids)

        analysis = {
            'num_nodes': subgraph.number_of_nodes(),
            'num_edges': subgraph.number_of_edges(),
            'density': nx.density(subgraph),
            'is_connected': nx.is_connected(subgraph)
        }

        if nx.is_connected(subgraph):
            analysis['diameter'] = nx.diameter(subgraph)
            analysis['avg_shortest_path_length'] = nx.average_shortest_path_length(subgraph)

        return analysis

    def find_bridges(self):
        return list(nx.bridges(self.graph))

    def find_articulation_points(self):
        return list(nx.articulation_points(self.graph))

    def get_network_summary(self):
        summary = {
            'num_nodes': self.graph.number_of_nodes(),
            'num_edges': self.graph.number_of_edges(),
            'density': nx.density(self.graph),
            'is_connected': nx.is_connected(self.graph),
            'num_connected_components': nx.number_connected_components(self.graph),
            'avg_degree': sum(dict(self.graph.degree()).values()) / self.graph.number_of_nodes(),
            'avg_clustering': nx.average_clustering(self.graph)
        }

        if nx.is_connected(self.graph):
            summary['diameter'] = nx.diameter(self.graph)
            summary['avg_shortest_path_length'] = nx.average_shortest_path_length(self.graph)

        return summary
