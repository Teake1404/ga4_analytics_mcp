"""
Simple Report Generator - Fast HTML generation without server-side Plotly rendering
Charts render client-side for speed
"""

import json
from datetime import datetime
from typing import Dict, Any


def generate_simple_report(analysis_data: Dict[str, Any]) -> str:
    """
    Generate HTML report with client-side chart rendering (FAST!)
    
    Args:
        analysis_data: JSON response from AI Insights API
        
    Returns:
        str: Complete HTML report
    """
    
    baseline = analysis_data['data']['baseline_rates']
    insights = analysis_data['insights']
    summary = analysis_data['summary']
    
    # Prepare chart data for client-side rendering
    chart_data = json.dumps(analysis_data)
    
    # Generate HTML with embedded data
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GA4 Funnel Analysis Report - {datetime.now().strftime('%Y-%m-%d')}</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f7fa;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            border-left: 4px solid #667eea;
        }}
        .metric-card h3 {{
            color: #667eea;
            font-size: 0.9em;
            text-transform: uppercase;
            margin-bottom: 10px;
        }}
        .metric-card .value {{
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }}
        .section {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}
        .section h2 {{
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }}
        .chart-container {{ margin: 20px 0; min-height: 300px; }}
        
        /* Compact grid layout for visualizations */
        .charts-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }}
        .chart-item {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}
        .chart-item h3 {{
            color: #333;
            margin-bottom: 15px;
            font-size: 1.1em;
            text-align: center;
        }}
        .chart-item .chart-container {{ 
            margin: 0; 
            min-height: 250px; 
        }}
        .heatmap-container {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            margin: 20px 0;
        }}
        .issue {{
            background: #fee;
            border-left: 4px solid #e74c3c;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
        }}
        .opportunity {{
            background: #efe;
            border-left: 4px solid #27ae60;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
        }}
        .recommendation {{
            background: #f0f8ff;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
        }}
        .priority {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 3px 10px;
            border-radius: 3px;
            font-size: 0.9em;
            font-weight: bold;
            margin-right: 10px;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        .badge-high {{ background: #e74c3c; color: white; }}
        .badge-medium {{ background: #f39c12; color: white; }}
        .badge-quick {{ background: #27ae60; color: white; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 GA4 Funnel Analysis Report</h1>
            <p>Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            <p>AI-Powered Insights by Claude Sonnet 4.5</p>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>View → Cart Rate</h3>
                <div class="value">{baseline['view_item_to_add_to_cart']*100:.1f}%</div>
            </div>
            <div class="metric-card">
                <h3>Cart → Purchase Rate</h3>
                <div class="value">{baseline['add_to_cart_to_purchase']*100:.1f}%</div>
            </div>
            <div class="metric-card">
                <h3>Overall Conversion</h3>
                <div class="value">{baseline['overall_conversion']*100:.2f}%</div>
            </div>
            <div class="metric-card">
                <h3>Outliers Detected</h3>
                <div class="value">{summary['total_outliers']}</div>
            </div>
        </div>
        
    <!-- Compact Grid Layout for All Visualizations -->
    <div class="section">
        <h2>📊 Performance Across All Dimensions</h2>
        <div class="charts-grid">
            <div class="chart-item">
                <h3>📈 Baseline Performance</h3>
                <div id="chart_baseline" class="chart-container"></div>
            </div>
            <div class="chart-item">
                <h3>📊 Best vs Worst</h3>
                <div id="chart_comparison" class="chart-container"></div>
            </div>
            <div class="chart-item">
                <h3>📺 Channel Performance</h3>
                <div id="chart_channel" class="chart-container"></div>
            </div>
            <div class="chart-item">
                <h3>📱 Device Performance</h3>
                <div id="chart_device" class="chart-container"></div>
            </div>
            <div class="chart-item">
                <h3>🛍️ Product Performance</h3>
                <div id="chart_product" class="chart-container"></div>
            </div>
            <div class="chart-item">
                <h3>🏷️ Category Performance</h3>
                <div id="chart_category" class="chart-container"></div>
            </div>
        </div>
    </div>
    
    <!-- Additional Charts in Second Row -->
    <div class="section">
        <h2>🔍 Technical Performance Details</h2>
        <div class="charts-grid">
            <div class="chart-item">
                <h3>🌐 Browser Performance</h3>
                <div id="chart_browser" class="chart-container"></div>
            </div>
            <div class="chart-item">
                <h3>📐 Resolution Performance</h3>
                <div id="chart_resolution" class="chart-container"></div>
            </div>
            <div class="chart-item">
                <!-- Empty space for future expansion -->
            </div>
        </div>
    </div>
    
    <!-- Heatmap removed for debugging -->
    
    <!-- Additional charts removed for debugging -->
        
        <div class="section">
            <h2>🔴 Critical Issues (AI-Identified)</h2>
"""
    
    # Add critical issues
    for issue in insights.get('critical_issues', [])[:5]:
        impact_class = issue.get('impact', 'medium')
        html += f"""
            <div class="issue">
                <h3><span class="badge badge-{impact_class}">{issue.get('impact', '').upper()}</span> {issue.get('value', '')} ({issue.get('dimension', '')})</h3>
                <p><strong>Issue:</strong> {issue.get('issue', '')}</p>
                <p><strong>Root Cause:</strong> {issue.get('root_cause', '')}</p>
            </div>
"""
    
    html += """
        </div>
        
        <div class="section">
            <h2>🟢 Growth Opportunities (AI-Identified)</h2>
"""
    
    # Add opportunities
    for opp in insights.get('opportunities', [])[:5]:
        html += f"""
            <div class="opportunity">
                <h3>{opp.get('value', '')} ({opp.get('dimension', '')})</h3>
                <p><strong>Opportunity:</strong> {opp.get('opportunity', '')}</p>
                <p><strong>Potential Lift:</strong> {opp.get('potential_lift', '')}</p>
                <p><strong>Why:</strong> {opp.get('why', '')}</p>
            </div>
"""
    
    html += """
        </div>
        
        <div class="section">
            <h2>💡 Actionable Recommendations (Prioritized by AI)</h2>
"""
    
    # Add recommendations
    for rec in insights.get('recommendations', [])[:8]:
        impl = rec.get('implementation', '').lower()
        html += f"""
            <div class="recommendation">
                <span class="priority">Priority {rec.get('priority', 0)}</span>
                <span class="badge badge-quick">{rec.get('implementation', '').title()}</span>
                <h3>{rec.get('action', '')}</h3>
                <p><strong>Expected Impact:</strong> {rec.get('expected_impact', '')}</p>
                <p><strong>Focus:</strong> {rec.get('dimension_focus', '')}</p>
            </div>
"""
    
    html += f"""
        </div>
        
        <div class="footer">
            <p>Generated by GA4 Funnel Analysis MCP | Powered by Claude Sonnet 4.5</p>
            <p>Cache Used: {'Yes (saved API call!)' if summary.get('cache_used') else 'No (fresh analysis)'} | 
               Storage Optimized: {analysis_data.get('storage_optimization', {}).get('savings_percent', 0)}%</p>
            <p>This report analyzes funnel performance across {summary.get('dimensions_analyzed', 0)} dimensions</p>
        </div>
    </div>
    
    <script>
    // Chart data embedded - all rendered client-side for speed
    const data = {chart_data};
    const baseline = data.data.baseline_rates;
    const baselineVal = baseline.overall_conversion * 100;
    const metrics = data.data.funnel_metrics;
    
    // ========================================================================
    // 1. BASELINE PERFORMANCE
    // ========================================================================
    const baselineTrace = {{
        x: ['View→Cart', 'Cart→Purchase', 'Overall'],
        y: [
            baseline.view_item_to_add_to_cart * 100,
            baseline.add_to_cart_to_purchase * 100,
            baseline.overall_conversion * 100
        ],
        type: 'bar',
        marker: {{color: ['#3498db', '#2ecc71', '#9b59b6']}},
        text: [
            (baseline.view_item_to_add_to_cart * 100).toFixed(1) + '%',
            (baseline.add_to_cart_to_purchase * 100).toFixed(1) + '%',
            (baseline.overall_conversion * 100).toFixed(2) + '%'
        ],
        textposition: 'outside'
    }};
    Plotly.newPlot('chart_baseline', [baselineTrace], {{
        title: 'Baseline Funnel Rates',
        height: 350,
        yaxis: {{title: 'Rate (%)'}}
    }}, {{responsive: true}});
    
    // ========================================================================
    // 2. CHANNEL PERFORMANCE
    // ========================================================================
    if (metrics.sessionDefaultChannelGroup) {{
        const channelData = metrics.sessionDefaultChannelGroup;
        const channelNames = Object.keys(channelData);
        const channelValues = channelNames.map(name => channelData[name].overall_conversion_rate * 100);
        
        Plotly.newPlot('chart_channel', [{{
            x: channelNames,
            y: channelValues,
            type: 'bar',
            marker: {{
                color: channelValues.map(v => v > baselineVal ? '#27ae60' : '#e74c3c')
            }},
            text: channelValues.map(v => v.toFixed(2) + '%'),
            textposition: 'outside'
        }}], {{
            title: 'Conversion Rate by Channel',
            height: 400,
            yaxis: {{title: 'Conversion Rate (%)'}},
            shapes: [{{
                type: 'line',
                x0: -0.5,
                x1: channelNames.length - 0.5,
                y0: baselineVal,
                y1: baselineVal,
                line: {{color: '#3498db', width: 2, dash: 'dash'}}
            }}],
            annotations: [{{
                x: channelNames.length / 2,
                y: baselineVal,
                text: 'Baseline: ' + baselineVal.toFixed(2) + '%',
                showarrow: false,
                yshift: 10
            }}]
        }}, {{responsive: true}});
    }}
    
    // ========================================================================
    // 3. DEVICE PERFORMANCE
    // ========================================================================
    if (metrics.deviceCategory) {{
        const deviceData = metrics.deviceCategory;
        const deviceNames = Object.keys(deviceData);
        const deviceValues = deviceNames.map(name => deviceData[name].overall_conversion_rate * 100);
        
        Plotly.newPlot('chart_device', [{{
            x: deviceNames,
            y: deviceValues,
            type: 'bar',
            marker: {{
                color: deviceValues.map(v => v > baselineVal ? '#27ae60' : '#e74c3c')
            }},
            text: deviceValues.map(v => v.toFixed(2) + '%'),
            textposition: 'outside'
        }}], {{
            title: 'Conversion Rate by Device',
            height: 400,
            yaxis: {{title: 'Conversion Rate (%)'}},
            shapes: [{{
                type: 'line',
                x0: -0.5,
                x1: deviceNames.length - 0.5,
                y0: baselineVal,
                y1: baselineVal,
                line: {{color: '#3498db', width: 2, dash: 'dash'}}
            }}],
            annotations: [{{
                x: deviceNames.length / 2,
                y: baselineVal,
                text: 'Baseline',
                showarrow: false,
                yshift: 10
            }}]
        }}, {{responsive: true}});
    }}
    
    // ========================================================================
    // 4. BROWSER PERFORMANCE
    // ========================================================================
    if (metrics.browser) {{
        const browserData = metrics.browser;
        const browserNames = Object.keys(browserData);
        const browserValues = browserNames.map(name => browserData[name].overall_conversion_rate * 100);
        
        Plotly.newPlot('chart_browser', [{{
            x: browserNames,
            y: browserValues,
            type: 'bar',
            marker: {{
                color: browserValues.map(v => v > baselineVal ? '#27ae60' : '#e74c3c')
            }},
            text: browserValues.map(v => v.toFixed(2) + '%'),
            textposition: 'outside'
        }}], {{
            title: 'Conversion Rate by Browser',
            height: 400,
            yaxis: {{title: 'Conversion Rate (%)'}},
            shapes: [{{
                type: 'line',
                x0: -0.5,
                x1: browserNames.length - 0.5,
                y0: baselineVal,
                y1: baselineVal,
                line: {{color: '#3498db', width: 2, dash: 'dash'}}
            }}]
        }}, {{responsive: true}});
    }}
    
    // ========================================================================
    // 5. RESOLUTION PERFORMANCE
    // ========================================================================
    if (metrics.screenResolution) {{
        const resData = metrics.screenResolution;
        const resNames = Object.keys(resData);
        const resValues = resNames.map(name => resData[name].overall_conversion_rate * 100);
        
        Plotly.newPlot('chart_resolution', [{{
            x: resNames,
            y: resValues,
            type: 'bar',
            marker: {{
                color: resValues.map(v => v > baselineVal ? '#27ae60' : '#e74c3c')
            }},
            text: resValues.map(v => v.toFixed(2) + '%'),
            textposition: 'outside'
        }}], {{
            title: 'Conversion Rate by Resolution',
            height: 400,
            yaxis: {{title: 'Conversion Rate (%)'}},
            xaxis: {{tickangle: -45}},
            shapes: [{{
                type: 'line',
                x0: -0.5,
                x1: resNames.length - 0.5,
                y0: baselineVal,
                y1: baselineVal,
                line: {{color: '#3498db', width: 2, dash: 'dash'}}
            }}]
        }}, {{responsive: true}});
    }}
    
    // ========================================================================
    // 6. PRODUCT PERFORMANCE
    // ========================================================================
    if (metrics.itemName) {{
        const prodData = metrics.itemName;
        const prodNames = Object.keys(prodData);
        const prodValues = prodNames.map(name => prodData[name].overall_conversion_rate * 100);
        
        Plotly.newPlot('chart_product', [{{
            x: prodNames,
            y: prodValues,
            type: 'bar',
            marker: {{
                color: prodValues.map(v => v > baselineVal ? '#27ae60' : '#e74c3c')
            }},
            text: prodValues.map(v => v.toFixed(2) + '%'),
            textposition: 'outside'
        }}], {{
            title: 'Conversion Rate by Product',
            height: 400,
            yaxis: {{title: 'Conversion Rate (%)'}},
            shapes: [{{
                type: 'line',
                x0: -0.5,
                x1: prodNames.length - 0.5,
                y0: baselineVal,
                y1: baselineVal,
                line: {{color: '#3498db', width: 2, dash: 'dash'}}
            }}]
        }}, {{responsive: true}});
    }}
    
    // ========================================================================
    // 7. CATEGORY PERFORMANCE
    // ========================================================================
    if (metrics.itemCategory) {{
        const catData = metrics.itemCategory;
        const catNames = Object.keys(catData);
        const catValues = catNames.map(name => catData[name].overall_conversion_rate * 100);
        
        Plotly.newPlot('chart_category', [{{
            x: catNames,
            y: catValues,
            type: 'bar',
            marker: {{
                color: catValues.map(v => v > baselineVal ? '#27ae60' : '#e74c3c')
            }},
            text: catValues.map(v => v.toFixed(2) + '%'),
            textposition: 'outside'
        }}], {{
            title: 'Conversion Rate by Category',
            height: 400,
            yaxis: {{title: 'Conversion Rate (%)'}},
            shapes: [{{
                type: 'line',
                x0: -0.5,
                x1: catNames.length - 0.5,
                y0: baselineVal,
                y1: baselineVal,
                line: {{color: '#3498db', width: 2, dash: 'dash'}}
            }}]
        }}, {{responsive: true}});
    }}
    
    // ========================================================================
    // 8. BEST VS WORST COMPARISON
    // ========================================================================
    const critical = data.data.critical_issues.slice(0, 3);
    const opportunities = data.data.top_opportunities.slice(0, 3);
    
    const trace_worst = {{
        y: critical.map((_, i) => '#' + (i+1)),
        x: critical.map(i => i.overall_conversion_rate * 100),
        type: 'bar',
        orientation: 'h',
        name: 'Worst Performers',
        marker: {{color: '#e74c3c'}},
        text: critical.map(i => i.dimension_value + ': ' + (i.overall_conversion_rate * 100).toFixed(2) + '%'),
        textposition: 'outside',
        hovertemplate: '<b>%{{text}}</b><br>%{{x:.2f}}%<extra></extra>'
    }};
    
    const trace_best = {{
        y: opportunities.map((_, i) => '#' + (i+1)),
        x: opportunities.map(o => o.overall_conversion_rate * 100),
        type: 'bar',
        orientation: 'h',
        name: 'Best Performers',
        marker: {{color: '#27ae60'}},
        text: opportunities.map(o => o.dimension_value + ': ' + (o.overall_conversion_rate * 100).toFixed(2) + '%'),
        textposition: 'outside',
        hovertemplate: '<b>%{{text}}</b><br>%{{x:.2f}}%<extra></extra>'
    }};
    
    Plotly.newPlot('chart_comparison', [trace_worst, trace_best], {{
        title: 'Top 3 Best vs Worst Performers',
        height: 400,
        barmode: 'group',
        xaxis: {{title: 'Conversion Rate (%)'}},
        showlegend: true
    }}, {{responsive: true}});
    
    // Heatmap removed for debugging - focusing on basic charts first
    
    // Additional charts removed for debugging - focusing on basic 6-grid charts
    
    </script>
</body>
</html>"""
    
    return html

