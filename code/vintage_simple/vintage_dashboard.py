"""
VVD Vintage Dashboard Generator
===============================

Takes vintage analysis output and generates an interactive HTML dashboard.

For YARN/Spark Jupyter (can't save files locally):
    results = run_all_campaigns(spark)
    display_dashboard(results)  # Renders directly in notebook

For local environments:
    generate_dashboard(results, "vvd_vintage_dashboard.html")
"""

import pandas as pd
import json
from IPython.display import display, HTML

def generate_dashboard(results, output_path="vvd_vintage_dashboard.html", title="VVD Vintage Curves"):
    """
    Generate interactive HTML dashboard from vintage analysis results.

    Args:
        results: Dictionary from run_all_campaigns() or dict of {mne: {"vintage_df": df, "summary_df": df}}
        output_path: Where to save the HTML file
        title: Dashboard title
    """

    # Collect all vintage data
    all_data = []
    campaigns = []

    for mne, result in results.items():
        if mne.startswith("_"):  # Skip combined summary
            continue
        if result is None:
            continue

        df = result["vintage_df"].copy()
        df["MNE"] = mne
        all_data.append(df)
        campaigns.append(mne)

    if not all_data:
        print("No data to generate dashboard")
        return

    combined_df = pd.concat(all_data, ignore_index=True)

    # Convert to JSON for embedding
    data_json = combined_df.to_json(orient="records")
    campaigns_json = json.dumps(sorted(campaigns))

    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            color: #333;
        }}
        .header {{
            background: linear-gradient(135deg, #003366 0%, #004d99 100%);
            color: white;
            padding: 20px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .header h1 {{ font-size: 1.5em; }}
        .header .subtitle {{ opacity: 0.8; font-size: 0.9em; }}
        .controls {{
            background: white;
            padding: 20px 40px;
            border-bottom: 1px solid #ddd;
            display: flex;
            gap: 30px;
            flex-wrap: wrap;
            align-items: center;
        }}
        .control-group {{
            display: flex;
            flex-direction: column;
            gap: 5px;
        }}
        .control-group label {{
            font-size: 0.85em;
            color: #666;
            font-weight: 600;
        }}
        .control-group select {{
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 1em;
            min-width: 150px;
        }}
        .main {{
            padding: 20px 40px;
        }}
        .chart-container {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 20px;
            margin-bottom: 20px;
        }}
        .summary-table {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 20px;
            overflow-x: auto;
        }}
        .summary-table h3 {{
            margin-bottom: 15px;
            color: #003366;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9em;
        }}
        th, td {{
            padding: 10px 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        th {{
            background: #003366;
            color: white;
        }}
        tr:hover {{ background: #f9f9f9; }}
        .positive {{ color: #28a745; font-weight: bold; }}
        .negative {{ color: #dc3545; }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 0.85em;
        }}
    </style>
</head>
<body>

<div class="header">
    <div>
        <h1>{title}</h1>
        <div class="subtitle">Test vs Control Comparison | Interactive Dashboard</div>
    </div>
    <div class="subtitle">Generated: <span id="genDate"></span></div>
</div>

<div class="controls">
    <div class="control-group">
        <label>Campaign</label>
        <select id="campaignSelect" onchange="updateChart()">
            <!-- Populated by JS -->
        </select>
    </div>
    <div class="control-group">
        <label>Cohort View</label>
        <select id="cohortSelect" onchange="updateChart()">
            <option value="all">All Cohorts</option>
            <!-- Populated by JS -->
        </select>
    </div>
    <div class="control-group">
        <label>Aggregation</label>
        <select id="aggSelect" onchange="updateChart()">
            <option value="none">By Deployment</option>
            <option value="monthly">Monthly</option>
        </select>
    </div>
</div>

<div class="main">
    <div class="chart-container">
        <div id="vintageChart" style="height: 500px;"></div>
    </div>

    <div class="summary-table">
        <h3>Summary - Final Day Metrics</h3>
        <table id="summaryTable">
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
                    <th>Significant</th>
                </tr>
            </thead>
            <tbody id="summaryBody">
            </tbody>
        </table>
    </div>
</div>

<div class="footer">
    VVD Vintage Dashboard | Marketing Analytics
</div>

<script>
// Embedded data
const rawData = {data_json};
const campaigns = {campaigns_json};

// Set generated date
document.getElementById('genDate').textContent = new Date().toLocaleDateString();

// Populate campaign dropdown
const campaignSelect = document.getElementById('campaignSelect');
campaigns.forEach(c => {{
    const opt = document.createElement('option');
    opt.value = c;
    opt.textContent = c;
    campaignSelect.appendChild(opt);
}});

// Get unique cohorts for selected campaign
function getCohorts(mne) {{
    const cohorts = [...new Set(rawData.filter(d => d.MNE === mne).map(d => d.COHORT))];
    return cohorts.sort();
}}

// Update cohort dropdown when campaign changes
function updateCohortDropdown() {{
    const mne = document.getElementById('campaignSelect').value;
    const cohortSelect = document.getElementById('cohortSelect');
    const cohorts = getCohorts(mne);

    // Clear existing options except "All"
    cohortSelect.innerHTML = '<option value="all">All Cohorts</option>';

    cohorts.forEach(c => {{
        const opt = document.createElement('option');
        opt.value = c;
        opt.textContent = c;
        cohortSelect.appendChild(opt);
    }});
}}

// Aggregate data monthly if needed
function aggregateMonthly(data) {{
    // Group by month and calculate weighted averages
    const grouped = {{}};

    data.forEach(row => {{
        const month = row.COHORT.substring(0, 7); // yyyy-MM
        const day = row.DAY;
        const key = month + '_' + day;

        if (!grouped[key]) {{
            grouped[key] = {{
                COHORT: month,
                DAY: day,
                TEST_CLIENTS: 0,
                TEST_SUCCESSES: 0,
                CTRL_CLIENTS: 0,
                CTRL_SUCCESSES: 0
            }};
        }}

        grouped[key].TEST_CLIENTS += row.TEST_CLIENTS || 0;
        grouped[key].TEST_SUCCESSES += row.TEST_SUCCESSES || 0;
        grouped[key].CTRL_CLIENTS += row.CTRL_CLIENTS || 0;
        grouped[key].CTRL_SUCCESSES += row.CTRL_SUCCESSES || 0;
    }});

    // Calculate rates
    return Object.values(grouped).map(row => ({{
        ...row,
        TEST_RATE: row.TEST_CLIENTS > 0 ? (row.TEST_SUCCESSES / row.TEST_CLIENTS) * 100 : 0,
        CTRL_RATE: row.CTRL_CLIENTS > 0 ? (row.CTRL_SUCCESSES / row.CTRL_CLIENTS) * 100 : 0,
        ABS_LIFT: row.TEST_CLIENTS > 0 && row.CTRL_CLIENTS > 0
            ? ((row.TEST_SUCCESSES / row.TEST_CLIENTS) - (row.CTRL_SUCCESSES / row.CTRL_CLIENTS)) * 100
            : 0
    }}));
}}

// Main chart update function
function updateChart() {{
    updateCohortDropdown();

    const mne = document.getElementById('campaignSelect').value;
    const cohortFilter = document.getElementById('cohortSelect').value;
    const agg = document.getElementById('aggSelect').value;

    // Filter data
    let data = rawData.filter(d => d.MNE === mne);

    if (cohortFilter !== 'all') {{
        data = data.filter(d => d.COHORT === cohortFilter);
    }}

    // Aggregate if needed
    if (agg === 'monthly') {{
        data = aggregateMonthly(data);
    }}

    // Get unique cohorts
    const cohorts = [...new Set(data.map(d => d.COHORT))].sort();

    // Create traces
    const traces = [];
    const colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#3B1F2B', '#95190C', '#610345', '#044B7F', '#107E7D', '#FFD700'];

    cohorts.forEach((cohort, i) => {{
        const cohortData = data.filter(d => d.COHORT === cohort).sort((a, b) => a.DAY - b.DAY);
        const color = colors[i % colors.length];

        // Test line
        traces.push({{
            x: cohortData.map(d => d.DAY),
            y: cohortData.map(d => d.TEST_RATE),
            name: cohort + ' Test',
            mode: 'lines+markers',
            line: {{ color: color, width: 2 }},
            marker: {{ size: 4 }},
            legendgroup: cohort
        }});

        // Control line (dashed)
        traces.push({{
            x: cohortData.map(d => d.DAY),
            y: cohortData.map(d => d.CTRL_RATE),
            name: cohort + ' Control',
            mode: 'lines+markers',
            line: {{ color: color, width: 2, dash: 'dash' }},
            marker: {{ size: 4, symbol: 'square' }},
            legendgroup: cohort
        }});
    }});

    const layout = {{
        title: mne + ' - Vintage Curves (Test: solid, Control: dashed)',
        xaxis: {{ title: 'Days from Treatment', rangemode: 'tozero' }},
        yaxis: {{ title: 'Cumulative Conversion Rate (%)', rangemode: 'tozero' }},
        legend: {{ orientation: 'v', x: 1.02, y: 1 }},
        hovermode: 'closest',
        margin: {{ r: 150 }}
    }};

    Plotly.newPlot('vintageChart', traces, layout, {{ responsive: true }});

    // Update summary table
    updateSummaryTable(data, cohorts);
}}

// Update summary table
function updateSummaryTable(data, cohorts) {{
    const tbody = document.getElementById('summaryBody');
    tbody.innerHTML = '';

    cohorts.forEach(cohort => {{
        const cohortData = data.filter(d => d.COHORT === cohort);
        if (cohortData.length === 0) return;

        // Get final day
        const maxDay = Math.max(...cohortData.map(d => d.DAY));
        const final = cohortData.find(d => d.DAY === maxDay);
        if (!final) return;

        const lift = final.ABS_LIFT || 0;
        const ciLower = final.CI_LOWER || (lift - 1);
        const ciUpper = final.CI_UPPER || (lift + 1);
        const significant = (ciLower > 0) || (ciUpper < 0);

        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${{cohort}}</td>
            <td>${{final.WINDOW_DAYS || maxDay}} days</td>
            <td>${{(final.TEST_CLIENTS || 0).toLocaleString()}}</td>
            <td>${{(final.TEST_RATE || 0).toFixed(2)}}%</td>
            <td>${{(final.CTRL_CLIENTS || 0).toLocaleString()}}</td>
            <td>${{(final.CTRL_RATE || 0).toFixed(2)}}%</td>
            <td class="${{lift > 0 ? 'positive' : 'negative'}}">${{lift.toFixed(2)}}pp</td>
            <td>[$${{ciLower.toFixed(2)}}, ${{ciUpper.toFixed(2)}}]</td>
            <td>${{significant ? '✓ Yes' : 'No'}}</td>
        `;
        tbody.appendChild(row);
    }});
}}

// Initial load
updateChart();
</script>

</body>
</html>
'''

    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Dashboard generated: {output_path}")
    print(f"Campaigns included: {', '.join(campaigns)}")
    print(f"Total data points: {len(combined_df)}")


def display_dashboard(results, title="VVD Vintage Curves"):
    """
    Display dashboard directly in Jupyter notebook - NO FILE SAVING.

    This is the function to use on YARN/Spark Jupyter environments
    where you cannot save files locally.

    Args:
        results: Dictionary from run_all_campaigns()
        title: Dashboard title

    Usage:
        results = run_all_campaigns(spark)
        display_dashboard(results)
    """
    # Collect all vintage data
    all_data = []
    campaigns = []

    for mne, result in results.items():
        if mne.startswith("_"):
            continue
        if result is None:
            continue

        df = result["vintage_df"].copy()
        df["MNE"] = mne
        all_data.append(df)
        campaigns.append(mne)

    if not all_data:
        print("No data to display")
        return

    combined_df = pd.concat(all_data, ignore_index=True)

    # Convert to JSON for embedding
    data_json = combined_df.to_json(orient="records")
    campaigns_json = json.dumps(sorted(campaigns))

    html_content = f'''
<div style="border: 1px solid #ddd; border-radius: 8px; overflow: hidden; margin: 10px 0;">
    <div style="background: linear-gradient(135deg, #003366 0%, #004d99 100%); color: white; padding: 15px 20px;">
        <h2 style="margin: 0; font-size: 1.3em;">{title}</h2>
        <div style="opacity: 0.8; font-size: 0.85em;">Test vs Control Comparison</div>
    </div>

    <div style="background: white; padding: 15px 20px; border-bottom: 1px solid #ddd; display: flex; gap: 20px; flex-wrap: wrap;">
        <div>
            <label style="font-size: 0.8em; color: #666; display: block;">Campaign</label>
            <select id="campaignSelect" onchange="updateDashboard()" style="padding: 6px 10px; border: 1px solid #ddd; border-radius: 4px;">
            </select>
        </div>
        <div>
            <label style="font-size: 0.8em; color: #666; display: block;">Cohort</label>
            <select id="cohortSelect" onchange="updateDashboard()" style="padding: 6px 10px; border: 1px solid #ddd; border-radius: 4px;">
                <option value="all">All Cohorts</option>
            </select>
        </div>
    </div>

    <div id="chartArea" style="padding: 20px; background: white;"></div>

    <div style="padding: 20px; background: white;">
        <h4 style="color: #003366; margin-bottom: 10px;">Summary - Final Day Metrics</h4>
        <div style="overflow-x: auto;">
            <table id="summaryTbl" style="width: 100%; border-collapse: collapse; font-size: 0.85em;">
                <thead>
                    <tr style="background: #003366; color: white;">
                        <th style="padding: 8px; text-align: left;">Cohort</th>
                        <th style="padding: 8px; text-align: left;">Window</th>
                        <th style="padding: 8px; text-align: right;">Test N</th>
                        <th style="padding: 8px; text-align: right;">Test Rate</th>
                        <th style="padding: 8px; text-align: right;">Control N</th>
                        <th style="padding: 8px; text-align: right;">Control Rate</th>
                        <th style="padding: 8px; text-align: right;">Lift</th>
                        <th style="padding: 8px; text-align: left;">95% CI</th>
                    </tr>
                </thead>
                <tbody id="summaryBody"></tbody>
            </table>
        </div>
    </div>
</div>

<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<script>
(function() {{
    const data = {data_json};
    const campaigns = {campaigns_json};

    // Populate campaign dropdown
    const campSel = document.getElementById('campaignSelect');
    campaigns.forEach(c => {{
        const opt = document.createElement('option');
        opt.value = c; opt.textContent = c;
        campSel.appendChild(opt);
    }});

    window.updateDashboard = function() {{
        const mne = document.getElementById('campaignSelect').value;
        const cohortFilter = document.getElementById('cohortSelect').value;

        // Update cohort dropdown
        const cohortSel = document.getElementById('cohortSelect');
        const cohorts = [...new Set(data.filter(d => d.MNE === mne).map(d => d.COHORT))].sort();
        cohortSel.innerHTML = '<option value="all">All Cohorts</option>';
        cohorts.forEach(c => {{
            const opt = document.createElement('option');
            opt.value = c; opt.textContent = c;
            cohortSel.appendChild(opt);
        }});
        if (cohortFilter !== 'all' && cohorts.includes(cohortFilter)) {{
            cohortSel.value = cohortFilter;
        }}

        // Filter data
        let filtered = data.filter(d => d.MNE === mne);
        if (cohortFilter !== 'all') {{
            filtered = filtered.filter(d => d.COHORT === cohortFilter);
        }}

        const uniqueCohorts = [...new Set(filtered.map(d => d.COHORT))].sort();
        const colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#3B1F2B', '#95190C'];

        // Build traces
        const traces = [];
        uniqueCohorts.forEach((cohort, i) => {{
            const cData = filtered.filter(d => d.COHORT === cohort).sort((a,b) => a.DAY - b.DAY);
            const color = colors[i % colors.length];

            traces.push({{
                x: cData.map(d => d.DAY),
                y: cData.map(d => d.TEST_RATE),
                name: cohort + ' Test',
                mode: 'lines+markers',
                line: {{ color: color, width: 2 }},
                marker: {{ size: 4 }}
            }});
            traces.push({{
                x: cData.map(d => d.DAY),
                y: cData.map(d => d.CTRL_RATE),
                name: cohort + ' Ctrl',
                mode: 'lines+markers',
                line: {{ color: color, width: 2, dash: 'dash' }},
                marker: {{ size: 4, symbol: 'square' }}
            }});
        }});

        Plotly.newPlot('chartArea', traces, {{
            title: mne + ' Vintage Curves (solid=Test, dashed=Control)',
            xaxis: {{ title: 'Days from Treatment' }},
            yaxis: {{ title: 'Cumulative Rate (%)' }},
            height: 450,
            margin: {{ r: 120 }}
        }});

        // Update summary table
        const tbody = document.getElementById('summaryBody');
        tbody.innerHTML = '';
        uniqueCohorts.forEach(cohort => {{
            const cData = filtered.filter(d => d.COHORT === cohort);
            const maxDay = Math.max(...cData.map(d => d.DAY));
            const final = cData.find(d => d.DAY === maxDay);
            if (!final) return;

            const lift = final.ABS_LIFT || 0;
            const ciLo = final.CI_LOWER || 0;
            const ciHi = final.CI_UPPER || 0;

            const row = document.createElement('tr');
            row.style.borderBottom = '1px solid #eee';
            row.innerHTML = `
                <td style="padding:8px">${{cohort}}</td>
                <td style="padding:8px">${{final.WINDOW_DAYS || maxDay}}d</td>
                <td style="padding:8px;text-align:right">${{(final.TEST_CLIENTS||0).toLocaleString()}}</td>
                <td style="padding:8px;text-align:right">${{(final.TEST_RATE||0).toFixed(2)}}%</td>
                <td style="padding:8px;text-align:right">${{(final.CTRL_CLIENTS||0).toLocaleString()}}</td>
                <td style="padding:8px;text-align:right">${{(final.CTRL_RATE||0).toFixed(2)}}%</td>
                <td style="padding:8px;text-align:right;color:${{lift>0?'#28a745':'#dc3545'}};font-weight:bold">${{lift.toFixed(2)}}pp</td>
                <td style="padding:8px">[${{ciLo.toFixed(2)}}, ${{ciHi.toFixed(2)}}]</td>
            `;
            tbody.appendChild(row);
        }});
    }};

    updateDashboard();
}})();
</script>
'''

    display(HTML(html_content))
    print(f"Dashboard displayed. Campaigns: {', '.join(campaigns)}")


def generate_dashboard_from_csv(csv_path, output_path="vvd_vintage_dashboard.html", title="VVD Vintage Curves"):
    """
    Generate dashboard from a saved CSV file.

    Args:
        csv_path: Path to CSV with vintage data (must have MNE column)
        output_path: Where to save the HTML
        title: Dashboard title
    """
    df = pd.read_csv(csv_path)

    # Convert to results format
    results = {}
    for mne in df["MNE"].unique():
        results[mne] = {
            "vintage_df": df[df["MNE"] == mne].copy(),
            "summary_df": None
        }

    generate_dashboard(results, output_path, title)


# For testing with sample data
def generate_sample_dashboard(output_path="sample_dashboard.html"):
    """Generate a sample dashboard with fake data for testing."""
    import numpy as np

    # Create sample data
    data = []
    for mne in ["VCN", "VDA", "VDT"]:
        for cohort in ["2025-01", "2025-02", "2025-03"]:
            for day in range(0, 31):
                test_rate = min(5, 0.1 * day + np.random.random() * 0.5)
                ctrl_rate = min(4, 0.08 * day + np.random.random() * 0.4)
                data.append({
                    "MNE": mne,
                    "COHORT": cohort,
                    "DAY": day,
                    "WINDOW_DAYS": 30,
                    "TEST_CLIENTS": 10000,
                    "TEST_SUCCESSES": int(test_rate * 100),
                    "TEST_RATE": test_rate,
                    "CTRL_CLIENTS": 5000,
                    "CTRL_SUCCESSES": int(ctrl_rate * 50),
                    "CTRL_RATE": ctrl_rate,
                    "ABS_LIFT": test_rate - ctrl_rate,
                    "CI_LOWER": (test_rate - ctrl_rate) - 0.3,
                    "CI_UPPER": (test_rate - ctrl_rate) + 0.3,
                    "SIGNIFICANT": True if day > 15 else False
                })

    df = pd.DataFrame(data)
    results = {}
    for mne in df["MNE"].unique():
        results[mne] = {
            "vintage_df": df[df["MNE"] == mne].copy(),
            "summary_df": None
        }

    generate_dashboard(results, output_path, "Sample VVD Dashboard")
    print(f"\nOpen {output_path} in your browser to preview.")


if __name__ == "__main__":
    # Generate sample for testing
    generate_sample_dashboard()
