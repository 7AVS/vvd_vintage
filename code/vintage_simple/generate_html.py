"""
Run this script to generate the HTML dashboard from CSV.
Just run: python generate_html.py
"""
import pandas as pd
import json
import os

# Find CSV file in current directory
csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]

if not csv_files:
    print("ERROR: No CSV file found in current folder!")
    print("Put your vintage_data.csv file in this folder and run again.")
    exit(1)

csv_file = csv_files[0]
print(f"Found CSV: {csv_file}")

# Read CSV
df = pd.read_csv(csv_file)
print(f"Loaded {len(df)} rows")

# Get campaigns
campaigns = sorted(df["MNE"].unique().tolist())
print(f"Campaigns: {campaigns}")

# Convert to JSON
data_json = df.to_json(orient="records")
campaigns_json = json.dumps(campaigns)

# Build HTML
html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VVD Vintage Curves</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #E7EEF1; }}
        .header {{ background: linear-gradient(135deg, #003168 0%, #0051A5 100%); color: white; padding: 20px 40px; }}
        .header h1 {{ font-size: 1.5em; }}
        .controls {{ background: white; padding: 20px 40px; border-bottom: 1px solid #ddd; display: flex; gap: 30px; flex-wrap: wrap; }}
        .control-group {{ display: flex; flex-direction: column; gap: 5px; }}
        .control-group label {{ font-size: 0.85em; color: #666; font-weight: 600; }}
        .control-group select {{ padding: 8px 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 1em; min-width: 150px; }}
        .main {{ padding: 20px 40px; }}
        .chart-container {{ background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); padding: 20px; margin-bottom: 20px; }}
        .summary-table {{ background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); padding: 20px; overflow-x: auto; }}
        .summary-table h3 {{ margin-bottom: 15px; color: #003168; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 0.9em; }}
        th, td {{ padding: 10px 12px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: #003168; color: white; }}
        tr:hover {{ background: #f9f9f9; }}
        .positive {{ color: #0051A5; font-weight: bold; }}
        .negative {{ color: #B58500; }}
    </style>
</head>
<body>

<div class="header">
    <h1>VVD Vintage Curves Dashboard</h1>
    <div style="opacity: 0.8; font-size: 0.9em;">Test vs Control Comparison</div>
</div>

<div class="controls">
    <div class="control-group">
        <label>Campaign</label>
        <select id="campaignSelect" onchange="updateChart()"></select>
    </div>
    <div class="control-group">
        <label>Cohort</label>
        <select id="cohortSelect" onchange="updateChart()">
            <option value="all">All Cohorts</option>
        </select>
    </div>
</div>

<div class="main">
    <div class="chart-container">
        <div id="vintageChart" style="height: 500px;"></div>
    </div>
    <div class="summary-table">
        <h3>Summary - Final Day Metrics</h3>
        <table>
            <thead>
                <tr>
                    <th>Cohort</th>
                    <th>Window</th>
                    <th>Test N</th>
                    <th>Test Rate</th>
                    <th>Control N</th>
                    <th>Control Rate</th>
                    <th>Lift (pp)</th>
                    <th>95% CI</th>
                </tr>
            </thead>
            <tbody id="summaryBody"></tbody>
        </table>
    </div>
</div>

<script>
const rawData = {data_json};
const campaigns = {campaigns_json};

const campaignSelect = document.getElementById('campaignSelect');
campaigns.forEach(c => {{
    const opt = document.createElement('option');
    opt.value = c; opt.textContent = c;
    campaignSelect.appendChild(opt);
}});

function updateChart() {{
    const mne = campaignSelect.value;
    const cohortFilter = document.getElementById('cohortSelect').value;

    const cohortSelect = document.getElementById('cohortSelect');
    const cohorts = [...new Set(rawData.filter(d => d.MNE === mne).map(d => d.COHORT))].sort();
    cohortSelect.innerHTML = '<option value="all">All Cohorts</option>';
    cohorts.forEach(c => {{
        const opt = document.createElement('option');
        opt.value = c; opt.textContent = c;
        cohortSelect.appendChild(opt);
    }});

    let data = rawData.filter(d => d.MNE === mne);
    if (cohortFilter !== 'all') data = data.filter(d => d.COHORT === cohortFilter);

    const uniqueCohorts = [...new Set(data.map(d => d.COHORT))].sort();
    // RBC Brand Colors
    const colors = ['#0051A5', '#FFC72C', '#0091DA', '#07AFBF', '#FCA311', '#C1B5E0', '#003168', '#B58500'];

    const traces = [];
    uniqueCohorts.forEach((cohort, i) => {{
        const cData = data.filter(d => d.COHORT === cohort).sort((a, b) => a.DAY - b.DAY);
        const color = colors[i % colors.length];
        traces.push({{
            x: cData.map(d => d.DAY), y: cData.map(d => d.TEST_RATE),
            name: cohort + ' Test', mode: 'lines+markers',
            line: {{ color: color, width: 2 }}, marker: {{ size: 4 }}
        }});
        traces.push({{
            x: cData.map(d => d.DAY), y: cData.map(d => d.CTRL_RATE),
            name: cohort + ' Ctrl', mode: 'lines+markers',
            line: {{ color: color, width: 2, dash: 'dash' }}, marker: {{ size: 4, symbol: 'square' }}
        }});
    }});

    Plotly.newPlot('vintageChart', traces, {{
        title: mne + ' - Vintage Curves (solid=Test, dashed=Control)',
        xaxis: {{ title: 'Days from Treatment' }},
        yaxis: {{ title: 'Cumulative Rate (%)' }},
        legend: {{ x: 1.02, y: 1 }},
        margin: {{ r: 150 }}
    }});

    const tbody = document.getElementById('summaryBody');
    tbody.innerHTML = '';
    uniqueCohorts.forEach(cohort => {{
        const cData = data.filter(d => d.COHORT === cohort);
        const maxDay = Math.max(...cData.map(d => d.DAY));
        const final = cData.find(d => d.DAY === maxDay);
        if (!final) return;
        const lift = final.ABS_LIFT || 0;
        const ciLo = final.CI_LOWER || 0;
        const ciHi = final.CI_UPPER || 0;
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${{cohort}}</td>
            <td>${{final.WINDOW_DAYS || maxDay}}d</td>
            <td>${{(final.TEST_CLIENTS||0).toLocaleString()}}</td>
            <td>${{(final.TEST_RATE||0).toFixed(2)}}%</td>
            <td>${{(final.CTRL_CLIENTS||0).toLocaleString()}}</td>
            <td>${{(final.CTRL_RATE||0).toFixed(2)}}%</td>
            <td style="color: ${{lift > 0 ? '#0051A5' : '#B58500'}}; font-weight: bold;">${{lift.toFixed(2)}}pp</td>
            <td>[${{ciLo.toFixed(2)}}, ${{ciHi.toFixed(2)}}]</td>
        `;
        tbody.appendChild(row);
    }});
}}

updateChart();
</script>
</body>
</html>
'''

# Write HTML
output_file = "vvd_vintage_dashboard.html"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\nDONE! Created: {output_file}")
print(f"Open it in your browser.")
