import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_loader import FlitterDataLoader
from network_analysis import SocialNetworkAnalyzer
from geospatial_analysis import GeospatialAnalyzer


def print_header():
    print("\nNETWORK EXPLORATION TOOL\n")


def explore_node(node_id, analyzer, geo_analyzer):
    info = analyzer.get_node_info(node_id)

    print(f"\nNODE DETAILS: {info['name']} (ID: {node_id})\n")

    print("Basic Information:")
    print(f"  Name: {info['name']}")
    print(f"  City: {info['city']}")
    print(f"  Degree (Connections): {info['degree']}\n")

    print("Centrality Metrics:")
    print(f"  Degree Centrality: {info['degree_centrality']:.6f}")
    print(f"  Betweenness Centrality: {info['betweenness_centrality']:.6f}")
    print(f"  Closeness Centrality: {info['closeness_centrality']:.6f}")
    print(f"  Clustering Coefficient: {info['clustering_coefficient']:.4f}\n")

    print(f"Community:")
    print(f"  Community ID: {info['community']}\n")

    print(f"Connections ({info['degree']} total):")
    neighbors = info['neighbors'][:20]
    for i, neighbor_id in enumerate(neighbors, 1):
        neighbor_info = analyzer.get_node_info(neighbor_id)
        print(f"  {i:2d}. {neighbor_info['name']:20s} | Degree: {neighbor_info['degree']:3d} | City: {neighbor_info['city']}")

    if len(info['neighbors']) > 20:
        print(f"  ... and {len(info['neighbors']) - 20} more connections")

    print("\nNetwork Role Analysis:")

    if 35 <= info['degree'] <= 45:
        print("  Possible EMPLOYEE (degree approx 40)")

    if 25 <= info['degree'] <= 45 and info['betweenness_centrality'] > 0.005:
        print("  Possible HANDLER (degree 25-45, moderate betweenness)")

    if 15 <= info['degree'] <= 70 and info['betweenness_centrality'] > 0.01:
        print("  Possible MIDDLEMAN (high betweenness centrality)")

    if info['degree'] >= 80:
        int_connections = geo_analyzer.find_international_connections(analyzer.graph, node_id)
        print("  Possible FEARLESS LEADER (degree >= 80)")
        print(f"    International reach: {int_connections} different cities")


def show_top_nodes_by_metric(analyzer, metric_name, top_n=20):
    print(f"\nTOP {top_n} NODES BY {metric_name.upper().replace('_', ' ')}\n")

    top_nodes = analyzer.get_top_nodes_by_metric(metric_name, top_n)

    print(f"{'Rank':<6} {'Name':<22} {'City':<15} {'Degree':<8} {'Metric Value'}")
    print("_" * 80)

    for i, (node_id, value) in enumerate(top_nodes, 1):
        info = analyzer.get_node_info(node_id)
        print(f"{i:<6} {info['name']:<22} {info['city']:<15} {info['degree']:<8} {value:.6f}")


def show_nodes_by_degree_range(analyzer, min_deg, max_deg):
    print(f"\nNODES WITH DEGREE BETWEEN {min_deg} AND {max_deg}\n")

    nodes = analyzer.get_nodes_by_degree_range(min_deg, max_deg)

    print(f"Found {len(nodes)} nodes\n")
    print(f"{'Rank':<6} {'Name':<22} {'City':<15} {'Degree':<8} {'Betweenness'}")
    print("_" * 80)

    for i, (node_id, degree) in enumerate(nodes[:50], 1):
        info = analyzer.get_node_info(node_id)
        print(f"{i:<6} {info['name']:<22} {info['city']:<15} {degree:<8} {info['betweenness_centrality']:.6f}")

    if len(nodes) > 50:
        print(f"\n... and {len(nodes) - 50} more nodes")


def interactive_mode(analyzer, geo_analyzer):
    print("\nInteractive mode")
    print("Commands: node <id>, top <metric>, degree <min> <max>, help, quit\n")

    while True:
        try:
            cmd = input("> ").strip().lower()
            if not cmd:
                continue

            parts = cmd.split()

            if parts[0] in ['quit', 'exit']:
                break

            elif parts[0] == 'help':
                print("\nCommands:")
                print("node <id> - explore a node")
                print("top <metric> [n] - show top nodes")
                print("degree <min> <max> - filter by degree")
                print("quit - exit")

            elif parts[0] == 'node':
                if len(parts) < 2:
                    print("need node id")
                else:
                    explore_node(int(parts[1]), analyzer, geo_analyzer)

            elif parts[0] == 'top':
                if len(parts) < 2:
                    print("need metric name")
                else:
                    metric = parts[1]
                    n = int(parts[2]) if len(parts) > 2 else 20
                    show_top_nodes_by_metric(analyzer, metric, n)

            elif parts[0] == 'degree':
                if len(parts) < 3:
                    print("need min and max")
                else:
                    show_nodes_by_degree_range(analyzer, int(parts[1]), int(parts[2]))

            else:
                print(f"unknown: {parts[0]} (type 'help')")

        except ValueError:
            print("invalid input")
        except KeyboardInterrupt:
            print("\nbye")
            break
        except Exception as e:
            print(f"error: {e}")


def main():
    print_header()

    print("Loading data...")
    loader = FlitterDataLoader()
    data = loader.load_all_data()

    print("Building network...")
    analyzer = SocialNetworkAnalyzer(data['links'], data['entities'], data['locations'])
    graph = analyzer.build_graph()
    analyzer.calculate_all_metrics()

    geo_analyzer = GeospatialAnalyzer(data['locations'])

    print("\nDATA LOADED SUCCESSFULLY\n")
    print(f"Network: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges\n")

    print("\nQUICK INSIGHTS\n")

    show_top_nodes_by_metric(analyzer, 'degree_centrality', 10)

    show_top_nodes_by_metric(analyzer, 'betweenness_centrality', 10)

    show_nodes_by_degree_range(analyzer, 35, 45)

    interactive_mode(analyzer, geo_analyzer)


if __name__ == "__main__":
    main()
