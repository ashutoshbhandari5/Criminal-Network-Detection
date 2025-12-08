import pandas as pd
from collections import Counter
import yaml


class GeospatialAnalyzer:
    def __init__(self, locations_df: pd.DataFrame, config_path="config/analysis_config.yaml"):
        self.locations_df = locations_df

        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.large_cities = set(self.config['geospatial']['large_cities'])
        self.small_cities = set(self.config['geospatial']['small_cities'])

        self.id_to_city = {}
        for _, row in locations_df.iterrows():
            self.id_to_city[row['ID']] = row['City']

    def get_city(self, person_id):
        return self.id_to_city.get(person_id, "Unknown")

    def is_large_city(self, city):
        return city in self.large_cities

    def is_small_city(self, city):
        return city in self.small_cities

    def get_city_statistics(self):
        city_counts = Counter(self.id_to_city.values())

        stats = {
            'total_cities': len(city_counts),
            'city_populations': dict(city_counts),
            'large_cities': {},
            'small_cities': {}
        }

        for city, count in city_counts.items():
            if city in self.large_cities:
                stats['large_cities'][city] = count
            elif city in self.small_cities:
                stats['small_cities'][city] = count

        return stats

    def analyze_network_geography(self, network_nodes):
        analysis = {
            'employee_city': None,
            'handlers_cities': [],
            'middlemen_cities': [],
            'leader_city': None,
            'geographic_pattern_match': 0.0
        }

        score = 0.0
        total_checks = 0

        if 'employee' in network_nodes:
            emp_city = self.get_city(network_nodes['employee'])
            analysis['employee_city'] = emp_city

            if self.is_large_city(emp_city):
                score += 1
            total_checks += 1

        if 'handlers' in network_nodes:
            for handler_id in network_nodes['handlers']:
                h_city = self.get_city(handler_id)
                analysis['handlers_cities'].append(h_city)

                if self.is_large_city(h_city):
                    score += 1
                total_checks += 1

        middlemen_keys = ['boris', 'morris', 'horace']
        for key in middlemen_keys:
            if key in network_nodes:
                m_city = self.get_city(network_nodes[key])
                analysis['middlemen_cities'].append(m_city)
                total_checks += 1

        if 'fearless_leader' in network_nodes:
            leader_city = self.get_city(network_nodes['fearless_leader'])
            analysis['leader_city'] = leader_city

            if self.is_large_city(leader_city):
                score += 1
            total_checks += 1

        if total_checks > 0:
            analysis['geographic_pattern_match'] = (score / total_checks) * 100

        return analysis

    def find_international_connections(self, graph, node_id):
        node_city = self.get_city(node_id)
        different_city_count = 0

        for neighbor in graph.neighbors(node_id):
            neighbor_city = self.get_city(neighbor)
            if neighbor_city != node_city:
                different_city_count += 1

        return different_city_count

    def get_city_diversity_score(self, node_ids):
        if not node_ids:
            return 0.0

        cities = [self.get_city(nid) for nid in node_ids]
        unique_cities = len(set(cities))
        total_cities = len(cities)

        return unique_cities / total_cities if total_cities > 0 else 0.0

    def generate_geographic_report(self, network_structure):
        report = []
        report.append("\nGEOGRAPHIC ANALYSIS\n")

        analysis = self.analyze_network_geography(network_structure)

        if analysis['employee_city']:
            city_type = "large" if self.is_large_city(analysis['employee_city']) else "small"
            report.append(f"Employee: {analysis['employee_city']} ({city_type})")

        if analysis['handlers_cities']:
            report.append("\nHandlers:")
            for i, city in enumerate(analysis['handlers_cities'], 1):
                city_type = "large" if self.is_large_city(city) else "small"
                report.append(f"{i}. {city} ({city_type})")

        if analysis['middlemen_cities']:
            report.append("\nMiddlemen:")
            middleman_names = ['Boris', 'Morris', 'Horace']
            for i, city in enumerate(analysis['middlemen_cities']):
                city_type = "large" if self.is_large_city(city) else "small"
                name = middleman_names[i] if i < len(middleman_names) else f"Middleman {i+1}"
                report.append(f"{name}: {city} ({city_type})")

        if analysis['leader_city']:
            city_type = "large" if self.is_large_city(analysis['leader_city']) else "small"
            report.append(f"\nLeader: {analysis['leader_city']} ({city_type})")

        report.append(f"\nPattern match: {analysis['geographic_pattern_match']:.1f}%")

        return "\n".join(report)

    def get_all_cities_summary(self):
        stats = self.get_city_statistics()

        summary = []
        summary.append("\nCITY DISTRIBUTION SUMMARY\n")

        summary.append(f"\nTotal Cities: {stats['total_cities']}\n")

        summary.append("Large Cities:")
        for city, count in sorted(stats['large_cities'].items(), key=lambda x: x[1], reverse=True):
            summary.append(f"  {city:15s}: {count:4d} people")

        summary.append("\nSmall Cities:")
        for city, count in sorted(stats['small_cities'].items(), key=lambda x: x[1], reverse=True):
            summary.append(f"  {city:15s}: {count:4d} people")

        return "\n".join(summary)
