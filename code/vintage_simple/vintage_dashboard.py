"""
VVD Vintage Dashboard Generator
===============================

Takes vintage analysis output and generates an interactive HTML dashboard.
Now includes engagement funnel visualization (email sent/opened/clicked, fulfillment).

For YARN/Spark Jupyter (can't save files locally):
    results = run_all_campaigns(spark)
    display_dashboard(results)  # Renders directly in notebook

For local environments:
    generate_dashboard(results, "vvd_vintage_dashboard.html")
"""

import pandas as pd
import json
from IPython.display import display, HTML

def generate_dashboard(results, output_path="vvd_vintage_dashboard.html", title="Vintage Automation Dashboard"):
    """
    Generate interactive HTML dashboard from vintage analysis results.

    Args:
        results: Dictionary from run_all_campaigns() containing:
            - vintage_df: Primary success vintage curves
            - channel_breakdown_df: Client counts by channel
            - engagement_vintage_df: Open/click rate curves by cohort
            - engagement_summary_df: Overall engagement summary
        output_path: Where to save the HTML file
        title: Dashboard title
    """

    # Collect all data types
    all_vintage = []
    all_channel = []
    all_engagement_vintage = []
    all_engagement_summary = []
    campaigns = []

    for mne, result in results.items():
        if mne.startswith("_"):  # Skip combined summary
            continue
        if result is None:
            continue

        campaigns.append(mne)

        # Primary success vintage
        df = result["vintage_df"].copy()
        df["MNE"] = mne
        df["METRIC"] = "PRIMARY_SUCCESS"
        all_vintage.append(df)

        # Channel breakdown
        if result.get("channel_breakdown_df") is not None and not result["channel_breakdown_df"].empty:
            all_channel.append(result["channel_breakdown_df"])

        # Engagement vintage (open rate, click rate curves)
        if result.get("engagement_vintage_df") is not None and not result["engagement_vintage_df"].empty:
            all_engagement_vintage.append(result["engagement_vintage_df"])

        # Engagement summary
        if result.get("engagement_summary_df") is not None and not result["engagement_summary_df"].empty:
            all_engagement_summary.append(result["engagement_summary_df"])

    if not all_vintage:
        print("No data to generate dashboard")
        return

    combined_vintage = pd.concat(all_vintage, ignore_index=True)

    # Combine channel breakdown
    channel_json = "[]"
    if all_channel:
        combined_channel = pd.concat(all_channel, ignore_index=True)
        channel_json = combined_channel.to_json(orient="records")

    # Combine engagement vintage (for metric dropdown)
    engagement_vintage_json = "[]"
    if all_engagement_vintage:
        combined_eng_vintage = pd.concat(all_engagement_vintage, ignore_index=True)
        engagement_vintage_json = combined_eng_vintage.to_json(orient="records")

    # Combine engagement summary
    engagement_json = "[]"
    if all_engagement_summary:
        combined_eng = pd.concat(all_engagement_summary, ignore_index=True)
        engagement_json = combined_eng.to_json(orient="records")

    # Convert to JSON for embedding
    data_json = combined_vintage.to_json(orient="records")
    campaigns_json = json.dumps(sorted(campaigns))

    # Log what we're including
    print(f"Dashboard data:")
    print(f"  - Vintage curves: {len(combined_vintage)} rows")
    print(f"  - Channel breakdown: {len(all_channel)} campaigns")
    print(f"  - Engagement vintage: {len(all_engagement_vintage)} campaigns")
    print(f"  - Engagement summary: {len(all_engagement_summary)} campaigns")

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
        .tabs {{
            display: flex;
            gap: 0;
            margin-left: auto;
        }}
        .tab {{
            padding: 10px 20px;
            background: #e9ecef;
            border: 1px solid #ddd;
            cursor: pointer;
            font-size: 0.9em;
            transition: all 0.2s;
        }}
        .tab:first-child {{ border-radius: 4px 0 0 4px; }}
        .tab:last-child {{ border-radius: 0 4px 4px 0; }}
        .tab.active {{
            background: #003366;
            color: white;
            border-color: #003366;
        }}
        .tab:hover:not(.active) {{ background: #dee2e6; }}
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
        .hidden {{ display: none !important; }}
        .summary-table {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 20px;
            overflow-x: auto;
            margin-bottom: 20px;
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
        .funnel-container {{
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }}
        .funnel-chart {{
            flex: 1;
            min-width: 300px;
        }}
        .funnel-table {{
            flex: 1;
            min-width: 300px;
        }}
        .metric-card {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .metric-card .label {{ font-size: 0.9em; color: #666; }}
        .metric-card .value {{ font-size: 1.5em; font-weight: bold; color: #003366; }}
        .metric-card .rate {{ font-size: 0.85em; color: #28a745; }}
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
        <label>Metric</label>
        <select id="metricSelect" onchange="updateChart()">
            <option value="PRIMARY_SUCCESS">Primary Success</option>
            <option value="OPEN_RATE">Open Rate</option>
            <option value="CLICK_RATE">Click Rate</option>
        </select>
    </div>
    <div class="control-group">
        <label>Channel</label>
        <select id="channelSelect" onchange="updateChart()">
            <option value="all">All Channels</option>
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
    <div class="tabs">
        <div class="tab active" onclick="switchTab('vintage')">Vintage Curves</div>
        <div class="tab" onclick="switchTab('channel')">Channel Breakdown</div>
        <div class="tab" onclick="switchTab('engagement')">Engagement Funnel</div>
    </div>
</div>

<div class="main">
    <!-- Vintage View -->
    <div id="vintageView">
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

    <!-- Channel Breakdown View -->
    <div id="channelView" class="hidden">
        <div class="chart-container">
            <h3 style="margin-bottom: 15px; color: #003366;">Channel Distribution by Cohort</h3>
            <div id="channelChart" style="height: 400px;"></div>
        </div>
        <div class="summary-table">
            <h3>Channel Breakdown - Client Counts</h3>
            <table id="channelTable">
                <thead>
                    <tr>
                        <th>Cohort</th>
                        <th>Group</th>
                        <th>Channel</th>
                        <th>Clients</th>
                        <th>Successes</th>
                        <th>Success Rate</th>
                    </tr>
                </thead>
                <tbody id="channelBody"></tbody>
            </table>
        </div>
    </div>

    <!-- Engagement View -->
    <div id="engagementView" class="hidden">
        <div class="chart-container">
            <h3 style="margin-bottom: 15px; color: #003366;">Email Engagement Funnel</h3>
            <div class="funnel-container">
                <div class="funnel-chart">
                    <div id="funnelChart" style="height: 350px;"></div>
                </div>
                <div class="funnel-table">
                    <div id="engagementCards"></div>
                </div>
            </div>
        </div>

        <div class="summary-table">
            <h3>Engagement Summary - All Campaigns</h3>
            <table id="engagementTable">
                <thead>
                    <tr>
                        <th>Campaign</th>
                        <th>Total Clients</th>
                        <th>Emails Sent</th>
                        <th>Send Rate</th>
                        <th>Opened</th>
                        <th>Open Rate</th>
                        <th>Clicked</th>
                        <th>Click Rate</th>
                        <th>Unsubscribed</th>
                        <th>Unsub Rate</th>
                    </tr>
                </thead>
                <tbody id="engagementBody">
                </tbody>
            </table>
        </div>
    </div>
</div>

<div class="footer">
    Vintage Automation Dashboard | Marketing Analytics | SuperFact 4-Layer Framework
</div>

<script>
// Embedded data
const rawData = {data_json};
const engagementVintageData = {engagement_vintage_json};
const channelData = {channel_json};
const engagementData = {engagement_json};
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

// Tab switching
function switchTab(tab) {{
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    const tabs = document.querySelectorAll('.tab');
    if (tab === 'vintage') tabs[0].classList.add('active');
    else if (tab === 'channel') tabs[1].classList.add('active');
    else tabs[2].classList.add('active');

    document.getElementById('vintageView').classList.toggle('hidden', tab !== 'vintage');
    document.getElementById('channelView').classList.toggle('hidden', tab !== 'channel');
    document.getElementById('engagementView').classList.toggle('hidden', tab !== 'engagement');

    if (tab === 'engagement') {{
        updateEngagement();
    }}
    if (tab === 'channel') {{
        updateChannelBreakdown();
    }}
}}

// Update channel breakdown view
function updateChannelBreakdown() {{
    const mne = document.getElementById('campaignSelect').value;
    const cohortFilter = document.getElementById('cohortSelect').value;

    let data = channelData.filter(d => d.MNE === mne);
    if (cohortFilter !== 'all') {{
        data = data.filter(d => d.COHORT === cohortFilter);
    }}

    if (data.length === 0) {{
        document.getElementById('channelChart').innerHTML = '<p style="text-align:center;color:#666;padding:50px;">No channel data available</p>';
        document.getElementById('channelBody').innerHTML = '<tr><td colspan="6" style="text-align:center;color:#666;">No data</td></tr>';
        return;
    }}

    // Group by channel for chart
    const channelGroups = {{}};
    data.forEach(row => {{
        const ch = row.CHANNEL || 'UNKNOWN';
        if (!channelGroups[ch]) channelGroups[ch] = {{ TEST: 0, CONTROL: 0 }};
        channelGroups[ch][row.GROUP] = (channelGroups[ch][row.GROUP] || 0) + row.CLIENT_COUNT;
    }});

    const channels = Object.keys(channelGroups).sort();
    const testCounts = channels.map(c => channelGroups[c].TEST || 0);
    const ctrlCounts = channels.map(c => channelGroups[c].CONTROL || 0);

    const traces = [
        {{
            x: channels,
            y: testCounts,
            name: 'TEST',
            type: 'bar',
            marker: {{ color: '#2E86AB' }}
        }},
        {{
            x: channels,
            y: ctrlCounts,
            name: 'CONTROL',
            type: 'bar',
            marker: {{ color: '#A23B72' }}
        }}
    ];

    Plotly.newPlot('channelChart', traces, {{
        title: mne + ' - Client Distribution by Channel',
        barmode: 'group',
        xaxis: {{ title: 'Channel' }},
        yaxis: {{ title: 'Client Count' }}
    }}, {{ responsive: true }});

    // Update table
    const tbody = document.getElementById('channelBody');
    tbody.innerHTML = '';
    data.sort((a, b) => a.COHORT.localeCompare(b.COHORT) || a.GROUP.localeCompare(b.GROUP)).forEach(row => {{
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${{row.COHORT}}</td>
            <td>${{row.GROUP}}</td>
            <td>${{row.CHANNEL || 'UNKNOWN'}}</td>
            <td>${{(row.CLIENT_COUNT || 0).toLocaleString()}}</td>
            <td>${{(row.SUCCESS_COUNT || 0).toLocaleString()}}</td>
            <td>${{(row.SUCCESS_RATE || 0).toFixed(2)}}%</td>
        `;
        tbody.appendChild(tr);
    }});
}}

// Get unique channels for selected campaign
function getChannels(mne) {{
    const channels = [...new Set(rawData.filter(d => d.MNE === mne).map(d => d.CHANNEL || 'ALL'))];
    return channels.sort();
}}

// Get unique cohorts for selected campaign and channel
function getCohorts(mne, channel) {{
    let filtered = rawData.filter(d => d.MNE === mne);
    if (channel && channel !== 'all') {{
        filtered = filtered.filter(d => (d.CHANNEL || 'ALL') === channel);
    }}
    const cohorts = [...new Set(filtered.map(d => d.COHORT))];
    return cohorts.sort();
}}

// Update channel dropdown when campaign changes
function updateChannelDropdown() {{
    const mne = document.getElementById('campaignSelect').value;
    const channelSelect = document.getElementById('channelSelect');
    const channels = getChannels(mne);

    // Clear existing options except "All"
    channelSelect.innerHTML = '<option value="all">All Channels</option>';

    channels.forEach(c => {{
        if (c && c !== 'ALL') {{  // Skip null/ALL since we have "All Channels" option
            const opt = document.createElement('option');
            opt.value = c;
            opt.textContent = c === 'EM' ? 'Email' : c === 'IM' ? 'In-Market' : c;
            channelSelect.appendChild(opt);
        }}
    }});
}}

// Update cohort dropdown when campaign or channel changes
function updateCohortDropdown() {{
    const mne = document.getElementById('campaignSelect').value;
    const channel = document.getElementById('channelSelect').value;
    const cohortSelect = document.getElementById('cohortSelect');
    const cohorts = getCohorts(mne, channel);

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
    const grouped = {{}};

    data.forEach(row => {{
        const month = row.COHORT.substring(0, 7);
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
    updateChannelDropdown();
    updateCohortDropdown();

    const mne = document.getElementById('campaignSelect').value;
    const metric = document.getElementById('metricSelect').value;
    const channelFilter = document.getElementById('channelSelect').value;
    const cohortFilter = document.getElementById('cohortSelect').value;

    // Select data source based on metric
    let data;
    let yAxisLabel;
    let chartTitle;

    if (metric === 'PRIMARY_SUCCESS') {{
        // Use primary vintage data
        data = rawData.filter(d => d.MNE === mne);
        yAxisLabel = 'Cumulative Conversion Rate (%)';
        chartTitle = mne + ' - Primary Success (Test: solid, Control: dashed)';
    }} else {{
        // Use engagement vintage data (OPEN_RATE, CLICK_RATE)
        data = engagementVintageData.filter(d => d.MNE === mne && d.METRIC === metric);
        yAxisLabel = metric === 'OPEN_RATE' ? 'Cumulative Open Rate (%)' : 'Cumulative Click Rate (%)';
        chartTitle = mne + ' - ' + (metric === 'OPEN_RATE' ? 'Email Open Rate' : 'Email Click Rate') + ' by Cohort';
    }}

    if (cohortFilter !== 'all') {{
        data = data.filter(d => d.COHORT === cohortFilter);
    }}

    // Get unique cohorts
    const cohorts = [...new Set(data.map(d => d.COHORT))].sort();

    // Create traces
    const traces = [];
    const colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#3B1F2B', '#95190C', '#610345', '#044B7F', '#107E7D', '#FFD700'];

    if (metric === 'PRIMARY_SUCCESS') {{
        // Primary success: Test vs Control
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
    }} else {{
        // Engagement metrics: By group (TEST only for email metrics)
        cohorts.forEach((cohort, i) => {{
            const cohortData = data.filter(d => d.COHORT === cohort && d.GROUP === 'TEST').sort((a, b) => a.DAY - b.DAY);
            const color = colors[i % colors.length];

            if (cohortData.length > 0) {{
                traces.push({{
                    x: cohortData.map(d => d.DAY),
                    y: cohortData.map(d => d.CUMULATIVE_RATE),
                    name: cohort,
                    mode: 'lines+markers',
                    line: {{ color: color, width: 2 }},
                    marker: {{ size: 4 }}
                }});
            }}
        }});
    }}

    const layout = {{
        title: chartTitle,
        xaxis: {{ title: 'Days from Treatment', rangemode: 'tozero' }},
        yaxis: {{ title: yAxisLabel, rangemode: 'tozero' }},
        legend: {{ orientation: 'v', x: 1.02, y: 1 }},
        hovermode: 'closest',
        margin: {{ r: 150 }}
    }};

    Plotly.newPlot('vintageChart', traces, layout, {{ responsive: true }});

    // Update summary table (only for primary success)
    if (metric === 'PRIMARY_SUCCESS') {{
        updateSummaryTable(data, cohorts);
    }} else {{
        // Clear summary for engagement metrics
        document.getElementById('summaryBody').innerHTML = '<tr><td colspan="9" style="text-align:center;color:#666;">Summary available for Primary Success metric only</td></tr>';
    }}

    // Also update engagement if on that tab
    if (!document.getElementById('engagementView').classList.contains('hidden')) {{
        updateEngagement();
    }}

    // Update channel breakdown if on that tab
    if (!document.getElementById('channelView') || !document.getElementById('channelView').classList.contains('hidden')) {{
        updateChannelBreakdown();
    }}
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
            <td>[${{ciLower.toFixed(2)}}, ${{ciUpper.toFixed(2)}}]</td>
            <td>${{significant ? '&#10003; Yes' : 'No'}}</td>
        `;
        tbody.appendChild(row);
    }});
}}

// Update engagement view
function updateEngagement() {{
    const mne = document.getElementById('campaignSelect').value;

    // Find engagement data for this campaign
    const engData = engagementData.find(d => d.MNE === mne);

    // Update funnel chart
    updateFunnelChart(engData);

    // Update engagement cards
    updateEngagementCards(engData);

    // Update engagement table (all campaigns)
    updateEngagementTable();
}}

// Update funnel chart
function updateFunnelChart(engData) {{
    if (!engData) {{
        Plotly.newPlot('funnelChart', [], {{
            title: 'No engagement data available',
            height: 350
        }});
        return;
    }}

    const total = engData.TOTAL_CLIENTS || 0;
    const sent = engData.EMAIL_SENT || 0;
    const opened = engData.EMAIL_OPENED || 0;
    const clicked = engData.EMAIL_CLICKED || 0;

    const trace = {{
        type: 'funnel',
        y: ['Total Clients', 'Email Sent', 'Email Opened', 'Email Clicked'],
        x: [total, sent, opened, clicked],
        textinfo: 'value+percent previous',
        marker: {{
            color: ['#003366', '#2E86AB', '#28a745', '#F18F01']
        }},
        connector: {{ line: {{ color: '#ccc' }} }}
    }};

    const layout = {{
        title: engData.MNE + ' - Email Funnel',
        height: 350,
        margin: {{ l: 100, r: 20 }}
    }};

    Plotly.newPlot('funnelChart', [trace], layout, {{ responsive: true }});
}}

// Update engagement cards
function updateEngagementCards(engData) {{
    const container = document.getElementById('engagementCards');

    if (!engData) {{
        container.innerHTML = '<div class="metric-card"><span class="label">No engagement data available for this campaign</span></div>';
        return;
    }}

    const metrics = [
        {{ label: 'Total Clients', value: engData.TOTAL_CLIENTS, rate: null }},
        {{ label: 'Emails Sent', value: engData.EMAIL_SENT, rate: engData.SEND_RATE || engData.EMAIL_SENT_RATE }},
        {{ label: 'Emails Opened', value: engData.EMAIL_OPENED, rate: engData.OPEN_RATE || engData.EMAIL_OPEN_RATE }},
        {{ label: 'Emails Clicked', value: engData.EMAIL_CLICKED, rate: engData.CLICK_RATE || engData.EMAIL_CLICK_RATE }},
        {{ label: 'Unsubscribed', value: engData.EMAIL_UNSUBSCRIBED, rate: engData.UNSUB_RATE }}
    ];

    container.innerHTML = metrics
        .filter(m => m.value !== undefined && m.value !== null)
        .map(m => `
            <div class="metric-card">
                <span class="label">${{m.label}}</span>
                <div>
                    <span class="value">${{(m.value || 0).toLocaleString()}}</span>
                    ${{m.rate !== null && m.rate !== undefined ? `<span class="rate">${{m.rate.toFixed(1)}}%</span>` : ''}}
                </div>
            </div>
        `).join('');
}}

// Update engagement table
function updateEngagementTable() {{
    const tbody = document.getElementById('engagementBody');
    tbody.innerHTML = '';

    if (!engagementData || engagementData.length === 0) {{
        tbody.innerHTML = '<tr><td colspan="10" style="text-align:center;color:#666;">No engagement data available</td></tr>';
        return;
    }}

    engagementData.forEach(eng => {{
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${{eng.MNE || '-'}}</td>
            <td>${{(eng.TOTAL_CLIENTS || 0).toLocaleString()}}</td>
            <td>${{(eng.EMAIL_SENT || 0).toLocaleString()}}</td>
            <td>${{(eng.SEND_RATE || eng.EMAIL_SENT_RATE || 0).toFixed(1)}}%</td>
            <td>${{(eng.EMAIL_OPENED || 0).toLocaleString()}}</td>
            <td>${{(eng.OPEN_RATE || eng.EMAIL_OPEN_RATE || 0).toFixed(1)}}%</td>
            <td>${{(eng.EMAIL_CLICKED || 0).toLocaleString()}}</td>
            <td>${{(eng.CLICK_RATE || eng.EMAIL_CLICK_RATE || 0).toFixed(1)}}%</td>
            <td>${{(eng.EMAIL_UNSUBSCRIBED || 0).toLocaleString()}}</td>
            <td>${{(eng.UNSUB_RATE || 0).toFixed(1)}}%</td>
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

    print(f"\nDashboard generated: {output_path}")
    print(f"Campaigns included: {', '.join(campaigns)}")
    print(f"Features:")
    print(f"  - Metric dropdown: Primary Success, Open Rate, Click Rate")
    print(f"  - Channel breakdown tab: {len(all_channel)} campaigns with data")
    print(f"  - Engagement funnel tab: {len(all_engagement_summary)} campaigns with data")


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
    all_engagement = []
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

        # Collect engagement data if available
        if result.get("engagement_summary_df") is not None and not result["engagement_summary_df"].empty:
            eng_df = result["engagement_summary_df"].copy()
            all_engagement.append(eng_df)

    if not all_data:
        print("No data to display")
        return

    combined_df = pd.concat(all_data, ignore_index=True)

    # Combine engagement data if available
    engagement_json = "[]"
    if all_engagement:
        combined_eng = pd.concat(all_engagement, ignore_index=True)
        engagement_json = combined_eng.to_json(orient="records")

    # Convert to JSON for embedding
    data_json = combined_df.to_json(orient="records")
    campaigns_json = json.dumps(sorted(campaigns))

    html_content = f'''
<div style="border: 1px solid #ddd; border-radius: 8px; overflow: hidden; margin: 10px 0;">
    <div style="background: linear-gradient(135deg, #003366 0%, #004d99 100%); color: white; padding: 15px 20px;">
        <h2 style="margin: 0; font-size: 1.3em;">{title}</h2>
        <div style="opacity: 0.8; font-size: 0.85em;">Test vs Control Comparison</div>
    </div>

    <div style="background: white; padding: 15px 20px; border-bottom: 1px solid #ddd; display: flex; gap: 20px; flex-wrap: wrap; align-items: center;">
        <div>
            <label style="font-size: 0.8em; color: #666; display: block;">Campaign</label>
            <select id="campaignSelectNb" onchange="updateDashboardNb()" style="padding: 6px 10px; border: 1px solid #ddd; border-radius: 4px;">
            </select>
        </div>
        <div>
            <label style="font-size: 0.8em; color: #666; display: block;">Channel</label>
            <select id="channelSelectNb" onchange="updateDashboardNb()" style="padding: 6px 10px; border: 1px solid #ddd; border-radius: 4px;">
                <option value="all">All Channels</option>
            </select>
        </div>
        <div>
            <label style="font-size: 0.8em; color: #666; display: block;">Cohort</label>
            <select id="cohortSelectNb" onchange="updateDashboardNb()" style="padding: 6px 10px; border: 1px solid #ddd; border-radius: 4px;">
                <option value="all">All Cohorts</option>
            </select>
        </div>
        <div style="margin-left: auto;">
            <button onclick="toggleViewNb('vintage')" id="vintageTabNb" style="padding: 8px 16px; background: #003366; color: white; border: none; cursor: pointer;">Vintage</button>
            <button onclick="toggleViewNb('engagement')" id="engagementTabNb" style="padding: 8px 16px; background: #e9ecef; border: 1px solid #ddd; cursor: pointer;">Engagement</button>
        </div>
    </div>

    <div id="vintageViewNb" style="padding: 20px; background: white;">
        <div id="chartAreaNb"></div>
        <h4 style="color: #003366; margin: 20px 0 10px;">Summary - Final Day Metrics</h4>
        <div style="overflow-x: auto;">
            <table id="summaryTblNb" style="width: 100%; border-collapse: collapse; font-size: 0.85em;">
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
                <tbody id="summaryBodyNb"></tbody>
            </table>
        </div>
    </div>

    <div id="engagementViewNb" style="padding: 20px; background: white; display: none;">
        <div id="funnelChartNb" style="height: 300px;"></div>
        <h4 style="color: #003366; margin: 20px 0 10px;">Engagement Summary</h4>
        <div id="engagementCardsNb" style="display: flex; flex-wrap: wrap; gap: 10px;"></div>
    </div>
</div>

<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<script>
(function() {{
    const data = {data_json};
    const engagementData = {engagement_json};
    const campaigns = {campaigns_json};

    // Populate campaign dropdown
    const campSel = document.getElementById('campaignSelectNb');
    campaigns.forEach(c => {{
        const opt = document.createElement('option');
        opt.value = c; opt.textContent = c;
        campSel.appendChild(opt);
    }});

    window.toggleViewNb = function(view) {{
        const vintageBtn = document.getElementById('vintageTabNb');
        const engBtn = document.getElementById('engagementTabNb');
        const vintageView = document.getElementById('vintageViewNb');
        const engView = document.getElementById('engagementViewNb');

        if (view === 'vintage') {{
            vintageBtn.style.background = '#003366';
            vintageBtn.style.color = 'white';
            engBtn.style.background = '#e9ecef';
            engBtn.style.color = 'black';
            vintageView.style.display = 'block';
            engView.style.display = 'none';
        }} else {{
            engBtn.style.background = '#003366';
            engBtn.style.color = 'white';
            vintageBtn.style.background = '#e9ecef';
            vintageBtn.style.color = 'black';
            vintageView.style.display = 'none';
            engView.style.display = 'block';
            updateEngagementNb();
        }}
    }};

    window.updateEngagementNb = function() {{
        const mne = document.getElementById('campaignSelectNb').value;
        const engData = engagementData.find(d => d.MNE === mne);

        if (!engData) {{
            document.getElementById('funnelChartNb').innerHTML = '<p style="color:#666;text-align:center;padding:50px;">No engagement data available</p>';
            document.getElementById('engagementCardsNb').innerHTML = '';
            return;
        }}

        // Funnel chart
        const trace = {{
            type: 'funnel',
            y: ['Total', 'Sent', 'Opened', 'Clicked'],
            x: [engData.TOTAL_CLIENTS || 0, engData.EMAIL_SENT || 0, engData.EMAIL_OPENED || 0, engData.EMAIL_CLICKED || 0],
            textinfo: 'value+percent previous',
            marker: {{ color: ['#003366', '#2E86AB', '#28a745', '#F18F01'] }}
        }};

        Plotly.newPlot('funnelChartNb', [trace], {{
            title: mne + ' Email Funnel',
            height: 300,
            margin: {{ l: 80 }}
        }});

        // Cards
        const cards = document.getElementById('engagementCardsNb');
        const metrics = [
            ['Total', engData.TOTAL_CLIENTS, null],
            ['Sent', engData.EMAIL_SENT, engData.SEND_RATE || engData.EMAIL_SENT_RATE],
            ['Opened', engData.EMAIL_OPENED, engData.OPEN_RATE || engData.EMAIL_OPEN_RATE],
            ['Clicked', engData.EMAIL_CLICKED, engData.CLICK_RATE || engData.EMAIL_CLICK_RATE],
            ['Unsubscribed', engData.EMAIL_UNSUBSCRIBED, engData.UNSUB_RATE]
        ].filter(m => m[1] !== undefined);

        cards.innerHTML = metrics.map(m => `
            <div style="background:#f8f9fa;padding:12px 20px;border-radius:6px;min-width:120px;">
                <div style="font-size:0.8em;color:#666;">${{m[0]}}</div>
                <div style="font-size:1.4em;font-weight:bold;color:#003366;">${{(m[1]||0).toLocaleString()}}</div>
                ${{m[2] !== null && m[2] !== undefined ? `<div style="font-size:0.75em;color:#28a745;">${{m[2].toFixed(1)}}%</div>` : ''}}
            </div>
        `).join('');
    }};

    window.updateDashboardNb = function() {{
        const mne = document.getElementById('campaignSelectNb').value;
        const channelFilter = document.getElementById('channelSelectNb').value;
        const cohortFilter = document.getElementById('cohortSelectNb').value;

        // Update channel dropdown
        const channelSel = document.getElementById('channelSelectNb');
        const channels = [...new Set(data.filter(d => d.MNE === mne).map(d => d.CHANNEL || 'ALL'))].sort();
        channelSel.innerHTML = '<option value="all">All Channels</option>';
        channels.forEach(c => {{
            if (c && c !== 'ALL') {{
                const opt = document.createElement('option');
                opt.value = c;
                opt.textContent = c === 'EM' ? 'Email' : c === 'IM' ? 'In-Market' : c;
                channelSel.appendChild(opt);
            }}
        }});

        // Update cohort dropdown
        let forCohorts = data.filter(d => d.MNE === mne);
        if (channelFilter !== 'all') {{
            forCohorts = forCohorts.filter(d => (d.CHANNEL || 'ALL') === channelFilter);
        }}
        const cohortSel = document.getElementById('cohortSelectNb');
        const cohorts = [...new Set(forCohorts.map(d => d.COHORT))].sort();
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
        if (channelFilter !== 'all') {{
            filtered = filtered.filter(d => (d.CHANNEL || 'ALL') === channelFilter);
        }}
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

        Plotly.newPlot('chartAreaNb', traces, {{
            title: mne + ' Vintage Curves (solid=Test, dashed=Control)',
            xaxis: {{ title: 'Days from Treatment' }},
            yaxis: {{ title: 'Cumulative Rate (%)' }},
            height: 450,
            margin: {{ r: 120 }}
        }});

        // Update summary table
        const tbody = document.getElementById('summaryBodyNb');
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

        // Update engagement if visible
        if (document.getElementById('engagementViewNb').style.display !== 'none') {{
            updateEngagementNb();
        }}
    }};

    updateDashboardNb();
}})();
</script>
'''

    display(HTML(html_content))
    print(f"Dashboard displayed. Campaigns: {', '.join(campaigns)}")
    if all_engagement:
        print(f"Engagement data: {len(all_engagement)} campaigns")


def generate_dashboard_from_csv(csv_path, output_path="vvd_vintage_dashboard.html", title="VVD Vintage Curves", engagement_csv_path=None):
    """
    Generate dashboard from saved CSV files.

    Args:
        csv_path: Path to CSV with vintage data (must have MNE column)
        output_path: Where to save the HTML
        title: Dashboard title
        engagement_csv_path: Optional path to engagement CSV
    """
    df = pd.read_csv(csv_path)

    # Convert to results format
    results = {}
    for mne in df["MNE"].unique():
        results[mne] = {
            "vintage_df": df[df["MNE"] == mne].copy(),
            "summary_df": None,
            "engagement_summary_df": None
        }

    # Load engagement data if provided
    if engagement_csv_path:
        eng_df = pd.read_csv(engagement_csv_path)
        for mne in eng_df["MNE"].unique():
            if mne in results:
                results[mne]["engagement_summary_df"] = eng_df[eng_df["MNE"] == mne].copy()

    generate_dashboard(results, output_path, title)


# For testing with sample data
def generate_sample_dashboard(output_path="sample_dashboard.html"):
    """Generate a sample dashboard with fake data for testing."""
    import numpy as np

    # Create sample vintage data
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

    # Create sample engagement data
    engagement_data = []
    for mne in ["VCN", "VDA", "VDT"]:
        total = np.random.randint(8000, 12000)
        sent = int(total * np.random.uniform(0.85, 0.95))
        opened = int(sent * np.random.uniform(0.15, 0.30))
        clicked = int(opened * np.random.uniform(0.10, 0.25))
        fulfilled = int(total * np.random.uniform(0.80, 0.90))

        engagement_data.append({
            "MNE": mne,
            "TOTAL_CLIENTS": total,
            "EMAIL_SENT": sent,
            "EMAIL_SENT_RATE": round(sent / total * 100, 2),
            "EMAIL_OPENED": opened,
            "EMAIL_OPEN_RATE": round(opened / total * 100, 2),
            "EMAIL_CLICKED": clicked,
            "EMAIL_CLICK_RATE": round(clicked / total * 100, 2),
            "FULFILLED": fulfilled,
            "FULFILLMENT_RATE": round(fulfilled / total * 100, 2)
        })

    eng_df = pd.DataFrame(engagement_data)

    # Build results
    results = {}
    for mne in df["MNE"].unique():
        results[mne] = {
            "vintage_df": df[df["MNE"] == mne].copy(),
            "summary_df": None,
            "engagement_summary_df": eng_df[eng_df["MNE"] == mne].copy()
        }

    generate_dashboard(results, output_path, "Sample VVD Dashboard")
    print(f"\nOpen {output_path} in your browser to preview.")


if __name__ == "__main__":
    import os

    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Look for CSV in current folder first, then source folder
    csv_files = [f for f in os.listdir(script_dir) if f.endswith('.csv') and 'engagement' not in f.lower()]

    if not csv_files:
        # Try source folder at different levels
        for source_path in [
            os.path.join(script_dir, "..", "..", "source"),
            os.path.join(script_dir, "..", "source"),
            os.path.join(script_dir, "source"),
        ]:
            if os.path.exists(source_path):
                csv_files = [os.path.join(source_path, f) for f in os.listdir(source_path) if f.endswith('.csv') and 'engagement' not in f.lower()]
                if csv_files:
                    break

    if not csv_files:
        print("ERROR: No CSV file found!")
        print("Put your CSV file in the same folder as this script.")
        print("\nGenerating sample dashboard instead...")
        generate_sample_dashboard(os.path.join(script_dir, "sample_dashboard.html"))
        exit(0)

    # Get full path
    if os.path.dirname(csv_files[0]):
        csv_path = csv_files[0]
    else:
        csv_path = os.path.join(script_dir, csv_files[0])

    print(f"Found CSV: {csv_path}")

    # Check for engagement CSV
    engagement_csv = None
    eng_files = [f for f in os.listdir(os.path.dirname(csv_path) or script_dir) if 'engagement' in f.lower() and f.endswith('.csv')]
    if eng_files:
        engagement_csv = os.path.join(os.path.dirname(csv_path) or script_dir, eng_files[0])
        print(f"Found engagement CSV: {engagement_csv}")

    output_path = os.path.join(script_dir, "vvd_vintage_dashboard.html")
    generate_dashboard_from_csv(csv_path, output_path, engagement_csv_path=engagement_csv)

    print(f"\nDONE! Open this file in your browser:")
    print(f"  {output_path}")
