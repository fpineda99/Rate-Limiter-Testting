#!/usr/bin/env python3
import csv
import matplotlib.pyplot as plt

CSV_FILE = "rate_limit_results.csv"
OUTPUT_FILE = "rate_limit_graph.png"

def create_graph():
    data = {'float': [], 'int': [], 'error': []}

    with open(CSV_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rps = float(row['RPS'])
            resp_type = row['ResponseType']
            data[resp_type].append(rps)

    type_map = {'float': 0, 'int': 1, 'error': 2}
    colors = {'float': 'blue', 'int': 'orange', 'error': 'red'}

    plt.figure(figsize=(10, 6))

    for resp_type in data:
        if data[resp_type]:
            y_values = [type_map[resp_type]] * len(data[resp_type])
            plt.scatter(data[resp_type], y_values,
                        c=colors[resp_type], label=resp_type, s=100, alpha=0.7)

    if data['int'] and data['float']:
        first_int = min(data['int'])
        last_float = max(data['float'])
        threshold_1 = (first_int + last_float) / 2
        plt.axvline(threshold_1, color='green', linestyle='--',
                    linewidth=2, label=f'Threshold 1: {threshold_1:.2f} RPS')

    plt.xlabel('Request Rate (RPS)', fontsize=12, fontweight='bold')
    plt.ylabel('Response Type', fontsize=12, fontweight='bold')
    plt.yticks([0, 1, 2], ['float', 'int', 'error'])
    plt.title('Rate Limit Discovery: Request Rate vs Response Type',
              fontsize=14, fontweight='bold')
    plt.legend(loc='best', fontsize=10)
    plt.grid(alpha=0.3, linestyle=':', linewidth=0.5)

    plt.tight_layout()
    plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches='tight')
    print(f"Graph saved to: {OUTPUT_FILE}")
    print(f"Resolution: 300 DPI (high quality for report)")

if __name__ == "__main__":
    try:
        create_graph()
    except FileNotFoundError:
        print(f"Error: {CSV_FILE} not found.")
        print("Run Template-2.py first to generate data.")
    except Exception as e:
        print(f"Error creating graph: {e}")
