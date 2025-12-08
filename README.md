# Criminal Network Detection

Wright State University
CEG7560 - Visualization and Image Processing for Cyber Security

## What is this?

Analyzes a social network (Flitter) to find a criminal organization. Looking for an insider employee who communicates with handlers, who connect through middlemen to a leader.

Two possible structures:

- **Scenario A:** Employee → 3 Handlers → Boris (middleman) → Leader
- **Scenario B:** Employee → 3 Handlers → 3 Middlemen (Boris/Morris/Horace) → Leader

## Files

```
dataset/               - social network data
src/                   - python code
  data_loader.py       - loads the data
  network_analysis.py  - graph stuff and metrics
  criminal_detector.py - finds the criminal network
  geospatial_analysis.py - city/location analysis
  visualization.py     - makes plots
config/                - settings
outputs/               - generated visualizations and reports
main.py               - run this
explore_network.py    - interactive exploration tool
```

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

This will analyze the network, find the criminal structure, and save visualizations + report.

Takes about 2-3 minutes to run.

## Interactive Exploration

```bash
python explore_network.py
```

Then try commands like:

- `node 38` - explore a specific person
- `top betweenness_centrality 10` - see top 10 influential nodes
- `degree 35 45` - find nodes with 35-45 connections

## How it works

1. Load 6000 people and their connections
2. Build a network graph
3. Calculate metrics (centrality, clustering, etc)
4. Look for patterns:
   - Employee: ~40 connections
   - Handlers: 3 people with 30-40 connections each
   - Middlemen: high betweenness (bridge nodes)
   - Leader: 100+ connections
5. Score different configurations
6. Pick the best match

## Output

**Visualizations** (outputs/visualizations/):

- network_overview.png
- degree_distribution.png
- centrality_comparison.png
- criminal_network_scenario_A.png
- criminal_network_scenario_B.png

**Report** (outputs/reports/):

- criminal_network_analysis_report.txt

## Settings

Edit `config/analysis_config.yaml` to change thresholds, colors, etc.
