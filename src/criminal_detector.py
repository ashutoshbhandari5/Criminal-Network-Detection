from itertools import combinations
import yaml


class CriminalNetworkDetector:
    def __init__(self, analyzer, geospatial_analyzer, config_path="config/analysis_config.yaml"):
        self.analyzer = analyzer
        self.geo_analyzer = geospatial_analyzer

        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.employee_candidates = []
        self.handler_candidates = {}
        self.middleman_candidates = {}
        self.leader_candidates = []

    def detect_all_patterns(self):
        print("\nCRIMINAL NETWORK DETECTION\n")

        self.employee_candidates = self.identify_employee_candidates()

        results = {
            'scenario_a': {},
            'scenario_b': {},
            'employee_candidates': self.employee_candidates
        }

        print(f"\nAnalyzing {len(self.employee_candidates)} employee candidates\n")

        for emp_id, emp_score in self.employee_candidates[:5]:
            print(f"\nCandidate: {self.analyzer.graph.nodes[emp_id]['name']} (ID: {emp_id})")

            scenario_a_results = self.detect_scenario_a(emp_id)
            if scenario_a_results:
                results['scenario_a'][emp_id] = scenario_a_results

            scenario_b_result = self.detect_scenario_b(emp_id)
            if scenario_b_result:
                results['scenario_b'][emp_id] = scenario_b_result

        return results

    def identify_employee_candidates(self):
        print("Identifying Employee Candidates\n")

        expected_contacts = self.config['network_characteristics']['employee']['expected_contacts']
        tolerance = self.config['network_characteristics']['employee']['tolerance']

        min_contacts = expected_contacts - tolerance
        max_contacts = expected_contacts + tolerance

        candidates = []

        for node in self.analyzer.graph.nodes():
            degree = self.analyzer.graph.degree(node)

            if min_contacts <= degree <= max_contacts:
                score = self._calculate_employee_score(node, degree, expected_contacts)
                candidates.append((node, score))

        candidates.sort(key=lambda x: x[1], reverse=True)

        print(f"Found {len(candidates)} employee candidates with approx 40 contacts\n")

        print("Top 10 Employee Candidates:")
        for i, (node_id, score) in enumerate(candidates[:10], 1):
            info = self.analyzer.get_node_info(node_id)
            print(f"  {i}. {info['name']:20s} | Degree: {info['degree']:3d} | "
                  f"City: {info['city']:15s} | Score: {score:.4f}")

        return candidates

    def _calculate_employee_score(self, node_id, degree, expected_degree):
        score = 0.0

        degree_diff = abs(degree - expected_degree)
        degree_score = 1.0 / (1.0 + degree_diff)
        score += degree_score * 0.4

        city = self.analyzer.graph.nodes[node_id].get('city', '')
        large_cities = self.config['geospatial']['large_cities']
        if city in large_cities:
            score += 0.3

        betweenness = self.analyzer.metrics['betweenness_centrality'].get(node_id, 0)
        if 0.001 < betweenness < 0.05:
            score += 0.2

        clustering = self.analyzer.metrics['clustering_coefficient'].get(node_id, 0)
        if 0.2 < clustering < 0.6:
            score += 0.1

        return score

    def detect_scenario_a(self, employee_id, verbose=True):
        print("Analyzing Scenario A (Single Middleman)")

        employee_neighbors = self.analyzer.get_neighbors(employee_id)
        handler_candidates = self._find_handler_candidates(employee_neighbors)

        if len(handler_candidates) < 3:
            print(f"Not enough handlers ({len(handler_candidates)} < 3)")
            return []

        all_valid_results = []
        handler_combos = list(combinations(handler_candidates[:10], 3))

        configs_checked = 0
        rejected_self_referential = 0

        for handler_combo in handler_combos:
            handler_ids = [h[0] for h in handler_combo]

            potential_boris = []
            for neighbor in employee_neighbors:
                if neighbor not in handler_ids:
                    betweenness = self.analyzer.metrics['betweenness_centrality'].get(neighbor, 0)
                    if betweenness > 0.001:
                        potential_boris.append((neighbor, betweenness))

            potential_boris.sort(key=lambda x: x[1], reverse=True)

            if not potential_boris:
                continue

            for boris_candidate, boris_betw in potential_boris[:5]:
                configs_checked += 1

                if boris_candidate == employee_id:
                    rejected_self_referential += 1
                    continue

                boris_degree = self.analyzer.graph.degree(boris_candidate)
                boris_betweenness = self.analyzer.metrics['betweenness_centrality'].get(boris_candidate, 0)

                if boris_degree > 80 or boris_betweenness < 0.001:
                    continue

                boris_neighbors = self.analyzer.get_neighbors(boris_candidate)
                leader_candidate = self._find_fearless_leader(boris_neighbors, exclude_ids=handler_ids + [employee_id])

                if leader_candidate:
                    config_score = self._score_scenario_a_configuration(
                        employee_id, handler_ids, boris_candidate, leader_candidate
                    )

                    all_valid_results.append({
                        'employee': employee_id,
                        'handlers': handler_ids,
                        'boris': boris_candidate,
                        'fearless_leader': leader_candidate,
                        'score': config_score,
                        'scenario': 'A'
                    })

        all_valid_results.sort(key=lambda x: x['score'], reverse=True)
        top_results = all_valid_results[:3]

        if top_results:
            print(f"\nFound {len(top_results)} pattern(s) for Scenario A")
            self._print_scenario_result(top_results[0], 'A')
        elif verbose:
            print("No valid configuration for Scenario A")

        return top_results

    def detect_scenario_b(self, employee_id, verbose=True):
        print("Analyzing Scenario B (Three Middlemen)")

        employee_neighbors = self.analyzer.get_neighbors(employee_id)
        handler_candidates = self._find_handler_candidates(employee_neighbors)

        if len(handler_candidates) < 3:
            print(f"Not enough handlers ({len(handler_candidates)} < 3)")
            return None

        best_result = None
        best_score = 0

        for handler_combo in combinations(handler_candidates[:10], 3):
            handler_ids = [h[0] for h in handler_combo]

            middlemen = []

            for handler_id in handler_ids:
                handler_neighbors = self.analyzer.get_neighbors(handler_id)

                potential_middlemen = [n for n in handler_neighbors
                                       if n != employee_id and n not in handler_ids]

                middleman = self._find_best_middleman_for_handler(potential_middlemen)

                if middleman:
                    middlemen.append(middleman)

            if len(middlemen) != 3 or len(set(middlemen)) != 3:
                continue

            common_leader_neighbors = set(self.analyzer.get_neighbors(middlemen[0]))
            for m in middlemen[1:]:
                common_leader_neighbors &= set(self.analyzer.get_neighbors(m))

            exclude_set = set(handler_ids + [employee_id] + middlemen)
            common_leader_neighbors -= exclude_set

            leader_candidate = self._find_fearless_leader(list(common_leader_neighbors), exclude_ids=list(exclude_set))

            if leader_candidate:
                config_score = self._score_scenario_b_configuration(
                    employee_id, handler_ids, middlemen, leader_candidate
                )

                if config_score > best_score:
                    best_score = config_score
                    best_result = {
                        'employee': employee_id,
                        'handlers': handler_ids,
                        'boris': middlemen[0],
                        'morris': middlemen[1],
                        'horace': middlemen[2],
                        'fearless_leader': leader_candidate,
                        'score': config_score,
                        'scenario': 'B'
                    }

        if best_result:
            self._print_scenario_result(best_result, 'B')

        return best_result

    def _find_handler_candidates(self, potential_handlers):
        min_contacts = self.config['network_characteristics']['handlers']['expected_contacts_min']
        max_contacts = self.config['network_characteristics']['handlers']['expected_contacts_max']

        candidates = []

        for node_id in potential_handlers:
            degree = self.analyzer.graph.degree(node_id)

            if (min_contacts - 5) <= degree <= (max_contacts + 5):
                score = self._calculate_handler_score(node_id, degree)
                if min_contacts <= degree <= max_contacts:
                    score *= 1.5
                candidates.append((node_id, score))

        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates

    def _calculate_handler_score(self, node_id, degree):
        score = 0.5

        if 25 <= degree <= 45:
            score += 0.4

        city = self.analyzer.graph.nodes[node_id].get('city', '')
        if city in self.config['geospatial']['large_cities']:
            score += 0.2

        betweenness = self.analyzer.metrics['betweenness_centrality'].get(node_id, 0)
        if betweenness > 0.005:
            score += 0.3
        elif betweenness > 0.001:
            score += 0.15

        return score

    def _find_common_middleman(self, handler_ids):
        if not handler_ids:
            return []

        common = set(self.analyzer.get_neighbors(handler_ids[0]))

        for handler_id in handler_ids[1:]:
            common &= set(self.analyzer.get_neighbors(handler_id))

        common_list = [(node, self.analyzer.metrics['betweenness_centrality'].get(node, 0))
                       for node in common]
        common_list.sort(key=lambda x: x[1], reverse=True)

        return [node for node, _ in common_list]

    def _find_best_middleman_for_handler(self, potential_middlemen):
        best_candidate = None
        best_score = 0

        for node_id in potential_middlemen:
            degree = self.analyzer.graph.degree(node_id)
            betweenness = self.analyzer.metrics['betweenness_centrality'].get(node_id, 0)

            if 15 <= degree <= 70 and betweenness > 0.005:
                city = self.analyzer.graph.nodes[node_id].get('city', '')
                score = betweenness * degree

                if city in self.config['geospatial']['small_cities']:
                    score *= 1.3

                if score > best_score:
                    best_score = score
                    best_candidate = node_id

        return best_candidate

    def _find_fearless_leader(self, potential_leaders, exclude_ids=None):
        if exclude_ids is None:
            exclude_ids = []

        min_contacts = self.config['network_characteristics']['fearless_leader']['min_contacts']

        total_nodes = self.analyzer.graph.number_of_nodes()
        top_2_percent_count = max(1, int(total_nodes * 0.02))

        all_degrees = sorted([self.analyzer.graph.degree(n) for n in self.analyzer.graph.nodes()], reverse=True)
        degree_threshold_top2 = all_degrees[min(top_2_percent_count, len(all_degrees) - 1)]

        all_betweenness = sorted(self.analyzer.metrics['betweenness_centrality'].values(), reverse=True)
        betweenness_threshold_top2 = all_betweenness[min(top_2_percent_count, len(all_betweenness) - 1)]

        best_candidate = None
        best_score = 0

        for node_id in potential_leaders:
            if node_id in exclude_ids:
                continue

            degree = self.analyzer.graph.degree(node_id)
            betweenness = self.analyzer.metrics['betweenness_centrality'].get(node_id, 0)

            in_top_2_percent = (degree >= degree_threshold_top2) or (betweenness >= betweenness_threshold_top2)

            if degree >= min_contacts and in_top_2_percent:
                city = self.analyzer.graph.nodes[node_id].get('city', '')

                score = degree + betweenness * 1000

                if city in self.config['geospatial']['large_cities']:
                    score *= 1.2

                if score > best_score:
                    best_score = score
                    best_candidate = node_id

        return best_candidate

    def _score_scenario_a_configuration(self, employee_id, handler_ids, boris_id, leader_id):
        score = 0.0

        emp_degree = self.analyzer.graph.degree(employee_id)
        if 35 <= emp_degree <= 45:
            score += 20

        for handler_id in handler_ids:
            handler_degree = self.analyzer.graph.degree(handler_id)
            if 30 <= handler_degree <= 40:
                score += 10

        boris_degree = self.analyzer.graph.degree(boris_id)
        boris_betweenness = self.analyzer.metrics['betweenness_centrality'].get(boris_id, 0)
        if 20 <= boris_degree <= 50:
            score += 15
        if boris_betweenness > 0.01:
            score += 15

        leader_degree = self.analyzer.graph.degree(leader_id)
        if leader_degree >= 100:
            score += 20

        score += self._score_geographic_pattern(employee_id, handler_ids, [boris_id], leader_id)

        return score

    def _score_scenario_b_configuration(self, employee_id, handler_ids, middlemen_ids, leader_id):
        score = 0.0

        emp_degree = self.analyzer.graph.degree(employee_id)
        if 35 <= emp_degree <= 45:
            score += 20

        for handler_id in handler_ids:
            handler_degree = self.analyzer.graph.degree(handler_id)
            if 30 <= handler_degree <= 40:
                score += 10

        for middleman_id in middlemen_ids:
            m_degree = self.analyzer.graph.degree(middleman_id)
            m_betweenness = self.analyzer.metrics['betweenness_centrality'].get(middleman_id, 0)
            if 20 <= m_degree <= 60:
                score += 5
            if m_betweenness > 0.01:
                score += 5

        leader_degree = self.analyzer.graph.degree(leader_id)
        if leader_degree >= 100:
            score += 20

        score += self._score_geographic_pattern(employee_id, handler_ids, middlemen_ids, leader_id)

        return score

    def _score_geographic_pattern(self, employee_id, handler_ids, middlemen_ids, leader_id):
        score = 0.0

        large_cities = self.config['geospatial']['large_cities']

        emp_city = self.analyzer.graph.nodes[employee_id].get('city', '')
        if emp_city in large_cities:
            score += 5

        for handler_id in handler_ids:
            h_city = self.analyzer.graph.nodes[handler_id].get('city', '')
            if h_city in large_cities:
                score += 3

        leader_city = self.analyzer.graph.nodes[leader_id].get('city', '')
        if leader_city in large_cities:
            score += 5

        return score

    def _print_scenario_result(self, result, scenario):
        print(f"\nScenario {scenario} found (score: {result['score']:.2f})")
        print(f"Employee: {self._format_node_info(result['employee'])}")
        print("Handlers:")
        for i, h_id in enumerate(result['handlers'], 1):
            print(f"  {i}. {self._format_node_info(h_id)}")

        if scenario == 'A':
            print(f"Boris: {self._format_node_info(result['boris'])}")
        else:
            print(f"Boris: {self._format_node_info(result['boris'])}")
            print(f"Morris: {self._format_node_info(result['morris'])}")
            print(f"Horace: {self._format_node_info(result['horace'])}")

        print(f"Leader: {self._format_node_info(result['fearless_leader'])}")

    def _format_node_info(self, node_id):
        info = self.analyzer.get_node_info(node_id)
        return f"{info['name']} (degree={info['degree']}, city={info['city']})"
