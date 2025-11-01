"""
Funnel Analysis Engine - Core calculations and outlier detection
Following SEO MCP pattern: stateless, dynamic configuration
"""

import config
from typing import Dict, List, Any


def calculate_funnel_metrics(funnel_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate completion rates for each funnel step across all dimensions
    
    Args:
        funnel_data: Raw funnel data from GA4 or mock data
        
    Returns:
        dict: Calculated metrics for each dimension and value
    """
    
    results = {}
    dimension_breakdowns = funnel_data.get("dimension_breakdowns", {})
    
    for dimension, values in dimension_breakdowns.items():
        dimension_results = {}
        
        for value, steps in values.items():
            # Calculate step completion rates
            view_item = steps.get("view_item", 0)
            add_to_cart = steps.get("add_to_cart", 0)
            purchase = steps.get("purchase", 0)
            
            # Avoid division by zero
            view_to_cart = (add_to_cart / view_item) if view_item > 0 else 0
            cart_to_purchase = (purchase / add_to_cart) if add_to_cart > 0 else 0
            overall = (purchase / view_item) if view_item > 0 else 0
            
            dimension_results[value] = {
                "view_to_cart_rate": round(view_to_cart, 4),
                "cart_to_purchase_rate": round(cart_to_purchase, 4),
                "overall_conversion_rate": round(overall, 4),
                "absolute_numbers": {
                    "view_item": view_item,
                    "add_to_cart": add_to_cart,
                    "purchase": purchase
                },
                # Calculate drop-offs
                "view_to_cart_dropoff": view_item - add_to_cart,
                "cart_to_purchase_dropoff": add_to_cart - purchase
            }
        
        results[dimension] = dimension_results
    
    return results


def detect_funnel_outliers(
    funnel_metrics: Dict[str, Any],
    baseline_rates: Dict[str, float],
    threshold: float = None
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Detect dimension values performing significantly above/below baseline
    
    Args:
        funnel_metrics: Calculated funnel metrics from calculate_funnel_metrics()
        baseline_rates: Overall baseline conversion rates
        threshold: Deviation threshold (default: 0.20 = ±20%)
        
    Returns:
        dict: Outliers grouped by dimension
    """
    
    if threshold is None:
        threshold = config.OUTLIER_THRESHOLD
    
    outliers = {}
    
    for dimension, values in funnel_metrics.items():
        dimension_outliers = []
        
        for value, metrics in values.items():
            # Calculate deviations from baseline
            baseline_view_to_cart = baseline_rates.get("view_item_to_add_to_cart", 0)
            baseline_cart_to_purchase = baseline_rates.get("add_to_cart_to_purchase", 0)
            
            # Avoid division by zero
            if baseline_view_to_cart == 0 or baseline_cart_to_purchase == 0:
                continue
            
            view_to_cart_deviation = (
                (metrics["view_to_cart_rate"] - baseline_view_to_cart) / baseline_view_to_cart
            )
            
            cart_to_purchase_deviation = (
                (metrics["cart_to_purchase_rate"] - baseline_cart_to_purchase) / baseline_cart_to_purchase
            )
            
            overall_deviation = (
                (metrics["overall_conversion_rate"] - baseline_rates.get("overall_conversion", 0)) 
                / baseline_rates.get("overall_conversion", 1)
            )
            
            # Check if any metric exceeds threshold
            is_outlier = (
                abs(view_to_cart_deviation) > threshold or
                abs(cart_to_purchase_deviation) > threshold or
                abs(overall_deviation) > threshold
            )
            
            if is_outlier:
                dimension_outliers.append({
                    "dimension": dimension,
                    "dimension_value": value,
                    "view_to_cart_rate": metrics["view_to_cart_rate"],
                    "cart_to_purchase_rate": metrics["cart_to_purchase_rate"],
                    "overall_conversion_rate": metrics["overall_conversion_rate"],
                    "view_to_cart_deviation": round(view_to_cart_deviation, 4),
                    "cart_to_purchase_deviation": round(cart_to_purchase_deviation, 4),
                    "overall_deviation": round(overall_deviation, 4),
                    "absolute_numbers": metrics["absolute_numbers"],
                    "performance": "above" if overall_deviation > 0 else "below",
                    "severity": calculate_severity(overall_deviation, threshold)
                })
        
        if dimension_outliers:
            # Sort by absolute overall deviation (most significant first)
            dimension_outliers.sort(
                key=lambda x: abs(x["overall_deviation"]), 
                reverse=True
            )
            outliers[dimension] = dimension_outliers
    
    return outliers


def calculate_severity(deviation: float, threshold: float) -> str:
    """
    Calculate severity level of deviation
    
    Args:
        deviation: Deviation percentage (e.g., 0.47 = 47%)
        threshold: Base threshold (e.g., 0.20 = 20%)
        
    Returns:
        str: "critical", "high", "medium", or "low"
    """
    abs_deviation = abs(deviation)
    
    if abs_deviation >= threshold * 2:  # ≥40%
        return "critical"
    elif abs_deviation >= threshold * 1.5:  # ≥30%
        return "high"
    elif abs_deviation >= threshold:  # ≥20%
        return "medium"
    else:
        return "low"


def calculate_baseline_from_data(funnel_data: Dict[str, Any]) -> Dict[str, float]:
    """
    Calculate overall baseline rates from dimension breakdowns
    (Used when baseline is not provided)
    
    Args:
        funnel_data: Raw funnel data
        
    Returns:
        dict: Calculated baseline rates
    """
    
    dimension_breakdowns = funnel_data.get("dimension_breakdowns", {})
    
    # Aggregate all events across dimensions
    total_view_item = 0
    total_add_to_cart = 0
    total_purchase = 0
    
    for dimension, values in dimension_breakdowns.items():
        for value, steps in values.items():
            total_view_item += steps.get("view_item", 0)
            total_add_to_cart += steps.get("add_to_cart", 0)
            total_purchase += steps.get("purchase", 0)
    
    # Calculate rates
    view_to_cart = (total_add_to_cart / total_view_item) if total_view_item > 0 else 0
    cart_to_purchase = (total_purchase / total_add_to_cart) if total_add_to_cart > 0 else 0
    overall = (total_purchase / total_view_item) if total_view_item > 0 else 0
    
    return {
        "view_item_to_add_to_cart": round(view_to_cart, 4),
        "add_to_cart_to_purchase": round(cart_to_purchase, 4),
        "overall_conversion": round(overall, 4),
        "total_events": {
            "view_item": total_view_item,
            "add_to_cart": total_add_to_cart,
            "purchase": total_purchase
        }
    }


def get_top_opportunities(outliers: Dict[str, List[Dict[str, Any]]], limit: int = 5) -> List[Dict[str, Any]]:
    """
    Get top opportunities (positive outliers) sorted by potential impact
    
    Args:
        outliers: Outliers from detect_funnel_outliers()
        limit: Maximum number of opportunities to return
        
    Returns:
        list: Top opportunities to capitalize on
    """
    
    opportunities = []
    
    for dimension, outlier_list in outliers.items():
        for outlier in outlier_list:
            if outlier["performance"] == "above":
                opportunities.append(outlier)
    
    # Sort by overall deviation (highest first)
    opportunities.sort(key=lambda x: x["overall_deviation"], reverse=True)
    
    return opportunities[:limit]


def get_critical_issues(outliers: Dict[str, List[Dict[str, Any]]], limit: int = 5) -> List[Dict[str, Any]]:
    """
    Get critical issues (negative outliers) sorted by severity
    
    Args:
        outliers: Outliers from detect_funnel_outliers()
        limit: Maximum number of issues to return
        
    Returns:
        list: Critical issues to address
    """
    
    issues = []
    
    for dimension, outlier_list in outliers.items():
        for outlier in outlier_list:
            if outlier["performance"] == "below":
                issues.append(outlier)
    
    # Sort by severity and absolute deviation
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    issues.sort(
        key=lambda x: (severity_order.get(x["severity"], 4), -abs(x["overall_deviation"]))
    )
    
    return issues[:limit]


