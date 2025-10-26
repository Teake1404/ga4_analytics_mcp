#!/usr/bin/env python3
"""
Demo script to run AI insights with Bags of Love mock data
"""

import json
import sys
import os
from datetime import datetime, timedelta
import random

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import mock_ga4_data
import ai_insights
import funnel_analysis

def generate_bagsoflove_funnel_data():
    """Generate funnel data specifically for Bags of Love"""
    
    # Load the realistic mock data
    with open('bagsoflove_realistic_mock_data.json', 'r') as f:
        bagsoflove_data = json.load(f)
    
    # Generate realistic funnel data based on Bags of Love business
    funnel_data = mock_ga4_data.generate_mock_funnel_data(
        funnel_steps=["view_item", "add_to_cart", "purchase"],
        dimensions=[
            "sessionDefaultChannelGroup",  # channel
            "deviceCategory",              # device  
            "browser",                     # browser
            "screenResolution",            # resolution
            "itemName",                    # product
            "itemCategory"                 # category
        ]
    )
    
    # Customize the data for Bags of Love products
    customize_for_bagsoflove(funnel_data, bagsoflove_data)
    
    return funnel_data

def customize_for_bagsoflove(funnel_data, bagsoflove_data):
    """Customize funnel data with Bags of Love specific products and categories"""
    
    # Update product names with real Bags of Love products
    if "itemName" in funnel_data["dimension_breakdowns"]:
        products = {}
        for product in bagsoflove_data["featured_products"]:
            products[product["name"]] = {
                "view_item": random.randint(200, 800),
                "add_to_cart": random.randint(30, 120),
                "purchase": random.randint(3, 15)
            }
        
        # Add some trending products
        for product in bagsoflove_data["trending_products"][:5]:
            products[product["name"]] = {
                "view_item": random.randint(150, 600),
                "add_to_cart": random.randint(25, 100),
                "purchase": random.randint(2, 12)
            }
        
        funnel_data["dimension_breakdowns"]["itemName"] = products
    
    # Update categories with Bags of Love categories
    if "itemCategory" in funnel_data["dimension_breakdowns"]:
        categories = {}
        for category in bagsoflove_data["product_categories"]:
            categories[category["name"]] = {
                "view_item": random.randint(300, 1200),
                "add_to_cart": random.randint(45, 180),
                "purchase": random.randint(4, 20)
            }
        
        funnel_data["dimension_breakdowns"]["itemCategory"] = categories

def run_demo():
    """Run the complete demo with AI insights"""
    
    print("🎯 Bags of Love AI Insights Demo")
    print("=" * 50)
    
    # Generate funnel data
    print("📊 Generating funnel data...")
    funnel_data = generate_bagsoflove_funnel_data()
    
    # Run funnel analysis
    print("🔍 Running funnel analysis...")
    analysis_result = funnel_analysis.analyze_funnel_performance(funnel_data)
    
    # Generate AI insights
    print("🤖 Generating AI insights with Claude...")
    insights = ai_insights.generate_funnel_insights(
        outliers=analysis_result["outliers"],
        baseline_rates=analysis_result["baseline_rates"],
        funnel_metrics=analysis_result["dimension_breakdowns"]
    )
    
    # Display results
    print("\n" + "=" * 50)
    print("📈 FUNNEL ANALYSIS RESULTS")
    print("=" * 50)
    
    print(f"\n🎯 BASELINE PERFORMANCE:")
    print(f"   View Item → Add to Cart: {analysis_result['baseline_rates']['view_item_to_add_to_cart']:.1%}")
    print(f"   Add to Cart → Purchase: {analysis_result['baseline_rates']['add_to_cart_to_purchase']:.1%}")
    print(f"   Overall Conversion: {analysis_result['baseline_rates']['overall_conversion']:.1%}")
    
    print(f"\n🔍 OUTLIERS DETECTED:")
    if analysis_result["outliers"]:
        for dimension, outliers in analysis_result["outliers"].items():
            print(f"\n   {dimension.upper()}:")
            for outlier in outliers:
                direction = "↑" if outlier['overall_deviation'] > 0 else "↓"
                print(f"     {outlier['dimension_value']} {direction} {abs(outlier['overall_deviation']):.0%} from baseline")
    else:
        print("   No significant outliers detected")
    
    print("\n" + "=" * 50)
    print("🤖 AI INSIGHTS (Claude Sonnet 4)")
    print("=" * 50)
    
    print(f"\n🔴 CRITICAL ISSUES ({len(insights['critical_issues'])}):")
    for i, issue in enumerate(insights['critical_issues'], 1):
        print(f"   {i}. {issue['dimension'].upper()}: {issue['value']}")
        print(f"      Issue: {issue['issue']}")
        print(f"      Impact: {issue['impact']}")
        print(f"      Root Cause: {issue['root_cause']}")
        print()
    
    print(f"\n🟢 OPPORTUNITIES ({len(insights['opportunities'])}):")
    for i, opp in enumerate(insights['opportunities'], 1):
        print(f"   {i}. {opp['dimension'].upper()}: {opp['value']}")
        print(f"      Opportunity: {opp['opportunity']}")
        print(f"      Potential Lift: {opp['potential_lift']}")
        print(f"      Why: {opp['why']}")
        print()
    
    print(f"\n💡 RECOMMENDATIONS ({len(insights['recommendations'])}):")
    for i, rec in enumerate(insights['recommendations'], 1):
        print(f"   {i}. Priority {rec['priority']}: {rec['action']}")
        print(f"      Expected Impact: {rec['expected_impact']}")
        print(f"      Implementation: {rec['implementation']}")
        print(f"      Focus: {rec['dimension_focus']}")
        print()
    
    print(f"\n🧪 SUGGESTED TESTS ({len(insights['suggested_tests'])}):")
    for i, test in enumerate(insights['suggested_tests'], 1):
        print(f"   {i}. {test['test_name']}")
        print(f"      Hypothesis: {test['hypothesis']}")
        print(f"      Metric: {test['metric']}")
        print(f"      Dimension: {test['dimension']}")
        print()
    
    # Save results to file
    results = {
        "timestamp": datetime.now().isoformat(),
        "funnel_analysis": analysis_result,
        "ai_insights": insights,
        "company": "Bags of Love",
        "website": "www.bagsoflove.co.uk"
    }
    
    with open('bagsoflove_ai_insights_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("=" * 50)
    print("✅ Demo completed! Results saved to 'bagsoflove_ai_insights_results.json'")
    print("=" * 50)

if __name__ == "__main__":
    run_demo()
