import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_loader import FlitterDataLoader
from network_analysis import SocialNetworkAnalyzer
from geospatial_analysis import GeospatialAnalyzer
from criminal_detector import CriminalNetworkDetector
from visualization import NetworkVisualizer


def print_header():
    print("\nIEEE VAST 2009 MINI CHALLENGE")
    print("CRIMINAL NETWORK DETECTION")
    print(f"\nAnalysis started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


def save_final_report(results, analyzer, geo_analyzer, output_path="outputs/reports"):
    os.makedirs(output_path, exist_ok=True)
    report_file = os.path.join(output_path, "criminal_network_analysis_report.txt")

    with open(report_file, 'w') as f:
        f.write("IEEE VAST 2009 MINI CHALLENGE - CRIMINAL NETWORK DETECTION\n")
        f.write("COMPREHENSIVE ANALYSIS REPORT\n\n")
        f.write(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("\nEXECUTIVE SUMMARY\n\n")
        f.write("Objective: Identify criminal espionage network within Flitter social network\n")
        f.write("Method: Graph-based network analysis with geospatial correlation\n\n")
        f.write("Two scenarios investigated:\n")
        f.write("  A. Single middleman (Boris) connecting handlers to leader\n")
        f.write("  B. Three middlemen (Boris, Morris, Horace) each connecting handlers to leader\n\n")

        f.write("\nNETWORK STATISTICS\n\n")
        network_summary = analyzer.get_network_summary()
        f.write(f"Total Nodes (People): {network_summary['num_nodes']}\n")
        f.write(f"Total Edges (Connections): {network_summary['num_edges']}\n")
        f.write(f"Network Density: {network_summary['density']:.6f}\n")
        f.write(f"Average Degree: {network_summary['avg_degree']:.2f}\n")
        f.write(f"Average Clustering Coefficient: {network_summary['avg_clustering']:.4f}\n")
        f.write(f"Connected: {network_summary['is_connected']}\n\n")

        geo_stats = geo_analyzer.get_city_statistics()
        f.write(f"Total Cities: {geo_stats['total_cities']}\n")
        f.write(f"Large Cities: {', '.join(geo_stats['large_cities'].keys())}\n")
        f.write(f"Small Cities: {', '.join(geo_stats['small_cities'].keys())}\n\n")

        f.write("\nSCENARIO A: SINGLE MIDDLEMAN (BORIS)\n\n")

        if results['scenario_a']:
            all_scenario_a_results = []
            for result_list in results['scenario_a'].values():
                all_scenario_a_results.extend(result_list)

            result_a = max(all_scenario_a_results, key=lambda x: x['score'])

            f.write(f"Detection Score: {result_a['score']:.2f}\n\n")
            f.write("IDENTIFIED NETWORK MEMBERS:\n\n")

            emp_info = analyzer.get_node_info(result_a['employee'])
            f.write("Employee (Insider):\n")
            f.write(f"Name: {emp_info['name']}\n")
            f.write(f"City: {emp_info['city']}\n")
            f.write(f"Connections: {emp_info['degree']}\n\n")

            f.write("Handlers:\n")
            for i, handler_id in enumerate(result_a['handlers'], 1):
                h_info = analyzer.get_node_info(handler_id)
                f.write(f"{i}. {h_info['name']} (city: {h_info['city']}, degree: {h_info['degree']})\n")

            boris_info = analyzer.get_node_info(result_a['boris'])
            f.write(f"\nBoris (Middleman):\n")
            f.write(f"Name: {boris_info['name']}\n")
            f.write(f"City: {boris_info['city']}\n")
            f.write(f"Connections: {boris_info['degree']}\n\n")

            leader_info = analyzer.get_node_info(result_a['fearless_leader'])
            f.write("Fearless Leader:\n")
            f.write(f"Name: {leader_info['name']}\n")
            f.write(f"City: {leader_info['city']}\n")
            f.write(f"Connections: {leader_info['degree']}\n")
            f.write(f"International reach: {geo_analyzer.find_international_connections(analyzer.graph, leader_info['id'])} cities\n\n")

            geo_report = geo_analyzer.generate_geographic_report(result_a)
            f.write(geo_report + "\n")

        else:
            f.write("No valid Scenario A pattern detected.\n\n")

        f.write("\nSCENARIO B: THREE MIDDLEMEN (BORIS, MORRIS, HORACE)\n\n")

        if results['scenario_b']:
            best_b = max(results['scenario_b'].items(), key=lambda x: x[1]['score'])
            result_b = best_b[1]

            f.write(f"Detection Score: {result_b['score']:.2f}\n\n")
            f.write("IDENTIFIED NETWORK MEMBERS:\n\n")

            emp_info = analyzer.get_node_info(result_b['employee'])
            f.write("Employee (Insider):\n")
            f.write(f"Name: {emp_info['name']}\n")
            f.write(f"City: {emp_info['city']}\n")
            f.write(f"Connections: {emp_info['degree']}\n\n")

            f.write("Handlers:\n")
            for i, handler_id in enumerate(result_b['handlers'], 1):
                h_info = analyzer.get_node_info(handler_id)
                f.write(f"{i}. {h_info['name']} (city: {h_info['city']}, degree: {h_info['degree']})\n")

            f.write("\nMiddlemen:\n")
            middleman_names = ['Boris', 'Morris', 'Horace']
            middleman_keys = ['boris', 'morris', 'horace']

            for name, key in zip(middleman_names, middleman_keys):
                if key in result_b:
                    m_info = analyzer.get_node_info(result_b[key])
                    f.write(f"{name}: {m_info['name']} (city: {m_info['city']}, degree: {m_info['degree']})\n")

            leader_info = analyzer.get_node_info(result_b['fearless_leader'])
            f.write("\nFearless Leader:\n")
            f.write(f"Name: {leader_info['name']}\n")
            f.write(f"City: {leader_info['city']}\n")
            f.write(f"Connections: {leader_info['degree']}\n")
            f.write(f"International reach: {geo_analyzer.find_international_connections(analyzer.graph, leader_info['id'])} cities\n\n")

            geo_report = geo_analyzer.generate_geographic_report(result_b)
            f.write(geo_report + "\n")

        else:
            f.write("No valid Scenario B pattern detected.\n\n")

        f.write("\nCONCLUSION\n\n")

        if results['scenario_a'] or results['scenario_b']:
            f.write("Criminal network structure successfully identified.\n\n")

            all_a_scores = []
            if results['scenario_a']:
                for result_list in results['scenario_a'].values():
                    all_a_scores.extend([r['score'] for r in result_list])
            best_score_a = max(all_a_scores) if all_a_scores else 0
            best_score_b = max([r['score'] for r in results['scenario_b'].values()]) if results['scenario_b'] else 0

            if best_score_a > best_score_b:
                f.write(f"Most Likely Scenario: A (Single Middleman)\n")
                f.write(f"Confidence Score: {best_score_a:.2f}\n\n")
            else:
                f.write(f"Most Likely Scenario: B (Three Middlemen)\n")
                f.write(f"Confidence Score: {best_score_b:.2f}\n\n")

            f.write("Recommendations:\n")
            f.write("  1. Conduct surveillance on identified handlers and middlemen\n")
            f.write("  2. Monitor communications of Fearless Leader\n")
            f.write("  3. Investigate financial transactions between identified parties\n")
            f.write("  4. Cross-reference with other intelligence sources\n\n")
        else:
            f.write("No clear criminal network pattern detected in the data.\n")
            f.write("Further investigation required.\n\n")

        f.write("END OF REPORT\n")

    print(f"\nComprehensive report saved to {report_file}")
    return report_file


def main():
    print_header()

    print("\nSTEP 1: DATA LOADING\n")

    loader = FlitterDataLoader()
    data = loader.load_all_data()

    summary = loader.get_data_summary()
    print("\nDataset Summary:")
    print(f"  Total People: {summary['total_people']}")
    print(f"  Total Connections: {summary['total_connections']}")
    print(f"  Total Cities: {summary['total_cities']}")
    print(f"  Cities: {', '.join(summary['cities'])}")

    print("\n\nSTEP 2: NETWORK ANALYSIS\n")

    analyzer = SocialNetworkAnalyzer(
        data['links'],
        data['entities'],
        data['locations']
    )

    graph = analyzer.build_graph()
    metrics = analyzer.calculate_all_metrics()

    network_stats = analyzer.get_network_summary()
    print("\nNetwork Statistics:")
    print(f"  Nodes: {network_stats['num_nodes']}")
    print(f"  Edges: {network_stats['num_edges']}")
    print(f"  Density: {network_stats['density']:.6f}")
    print(f"  Average Degree: {network_stats['avg_degree']:.2f}")

    print("\n\nSTEP 3: GEOSPATIAL ANALYSIS\n")

    geo_analyzer = GeospatialAnalyzer(data['locations'])
    print(geo_analyzer.get_all_cities_summary())

    print("\n\nSTEP 4: CRIMINAL NETWORK DETECTION\n")

    detector = CriminalNetworkDetector(analyzer, geo_analyzer)
    results = detector.detect_all_patterns()

    print("\n\nSTEP 5: VISUALIZATION\n")

    visualizer = NetworkVisualizer(graph)

    visualizer.visualize_full_network_overview()

    visualizer.visualize_degree_distribution()

    visualizer.visualize_centrality_comparison(metrics)

    if results['scenario_a']:
        all_scenario_a = []
        for result_list in results['scenario_a'].values():
            all_scenario_a.extend(result_list)
        best_a = max(all_scenario_a, key=lambda x: x['score'])
        visualizer.visualize_criminal_network(best_a, 'A')

    if results['scenario_b']:
        best_b = max(results['scenario_b'].items(), key=lambda x: x[1]['score'])[1]
        visualizer.visualize_criminal_network(best_b, 'B')

    print("\n\nSTEP 6: GENERATING FINAL REPORT\n")

    report_path = save_final_report(results, analyzer, geo_analyzer)

    print("\n\nANALYSIS COMPLETE\n")

    print("\nResults:")
    if results['scenario_a']:
        all_a_scores = []
        for result_list in results['scenario_a'].values():
            all_a_scores.extend([r['score'] for r in result_list])
        best_score_a = max(all_a_scores)
        print(f"  Scenario A detected (Score: {best_score_a:.2f})")

    if results['scenario_b']:
        best_score_b = max([r['score'] for r in results['scenario_b'].values()])
        print(f"  Scenario B detected (Score: {best_score_b:.2f})")

    print("\nOutput files saved to:")
    print(f"  - Visualizations: outputs/visualizations/")
    print(f"  - Report: {report_path}")

    print(f"\nAnalysis completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


if __name__ == "__main__":
    main()
