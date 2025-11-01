"""
Mock GA4 Data Generator for Funnel Analysis Prototype
Generates realistic ecommerce funnel data for demo purposes
"""

from datetime import datetime, timedelta
import random


def generate_mock_funnel_data(
    funnel_steps=None,
    dimensions=None,
    date_range="last_30_days",
    property_id="123456789"
):
    """
    Generate realistic GA4 funnel mock data
    
    Args:
        funnel_steps: List of funnel steps (default: view_item, add_to_cart, purchase)
        dimensions: List of dimensions to break down (ALL 6: channel, device, browser, resolution, product, category)
        date_range: Date range for data
        property_id: GA4 property ID
        
    Returns:
        dict: Complete funnel data structure
    """
    
    if funnel_steps is None:
        funnel_steps = ["view_item", "add_to_cart", "purchase"]
    
    if dimensions is None:
        # ALL 6 dimensions as requested by client
        dimensions = [
            "sessionDefaultChannelGroup",  # channel
            "deviceCategory",              # device
            "browser",                     # browser
            "screenResolution",            # resolution
            "itemName",                    # product
            "itemCategory"                 # category
        ]
    
    # ============================================================================
    # OVERALL BASELINE RATES (Industry-realistic ecommerce metrics)
    # ============================================================================
    
    overall_baseline = {
        "view_item_to_add_to_cart": 0.152,  # 15.2% add-to-cart rate
        "add_to_cart_to_purchase": 0.087,   # 8.7% checkout completion
        "overall_conversion": 0.0132        # 1.32% overall conversion
    }
    
    # ============================================================================
    # DIMENSION BREAKDOWNS (Realistic patterns with outliers)
    # ============================================================================
    
    dimension_breakdowns = {}
    
    # Channel breakdown (with intentional outliers)
    if "sessionDefaultChannelGroup" in dimensions:
        dimension_breakdowns["sessionDefaultChannelGroup"] = {
            "Organic Search": {
                "view_item": 1000,
                "add_to_cart": 183,  # 18.3% (above baseline +20%)
                "purchase": 16       # 8.7% checkout completion
            },
            "Social": {
                "view_item": 800,
                "add_to_cart": 65,   # 8.1% (below baseline -47% ⚠️ OUTLIER)
                "purchase": 5        # 7.7% checkout completion
            },
            "Email": {
                "view_item": 500,
                "add_to_cart": 107,  # 21.4% (above baseline +41% ⚠️ OPPORTUNITY)
                "purchase": 12       # 11.2% checkout completion
            },
            "Direct": {
                "view_item": 1200,
                "add_to_cart": 178,  # 14.8% (near baseline)
                "purchase": 15       # 8.4% checkout completion
            },
            "Paid Search": {
                "view_item": 600,
                "add_to_cart": 96,   # 16.0% (above baseline)
                "purchase": 10       # 10.4% checkout completion
            }
        }
    
    # Device breakdown (mobile underperforming)
    if "deviceCategory" in dimensions:
        dimension_breakdowns["deviceCategory"] = {
            "desktop": {
                "view_item": 2000,
                "add_to_cart": 378,  # 18.9% (above baseline +24%)
                "purchase": 42       # 11.1% checkout completion (above baseline +28% ⚠️ OPPORTUNITY)
            },
            "mobile": {
                "view_item": 1800,
                "add_to_cart": 203,  # 11.3% (below baseline -26% ⚠️ OUTLIER)
                "purchase": 16       # 7.9% checkout completion (below baseline -9%)
            },
            "tablet": {
                "view_item": 300,
                "add_to_cart": 52,   # 17.3% (above baseline)
                "purchase": 2        # 3.8% checkout completion (below baseline -56% ⚠️ OUTLIER)
            }
        }
    
    # Browser breakdown
    if "browser" in dimensions:
        dimension_breakdowns["browser"] = {
            "Chrome": {
                "view_item": 2500,
                "add_to_cart": 403,  # 16.1% (above baseline)
                "purchase": 38       # 9.4% checkout completion
            },
            "Safari": {
                "view_item": 1200,
                "add_to_cart": 170,  # 14.2% (near baseline)
                "purchase": 15       # 8.8% checkout completion
            },
            "Firefox": {
                "view_item": 400,
                "add_to_cart": 57,   # 14.3% (near baseline)
                "purchase": 5        # 8.8% checkout completion
            },
            "Edge": {
                "view_item": 200,
                "add_to_cart": 26,   # 13.0% (below baseline -14%)
                "purchase": 2        # 7.7% checkout completion
            }
        }
    
    # Screen resolution breakdown
    if "screenResolution" in dimensions:
        dimension_breakdowns["screenResolution"] = {
            "1920x1080": {
                "view_item": 1500,
                "add_to_cart": 285,  # 19.0% (above baseline +25% ⚠️ OPPORTUNITY)
                "purchase": 28       # 9.8% checkout completion
            },
            "1366x768": {
                "view_item": 800,
                "add_to_cart": 120,  # 15.0% (near baseline)
                "purchase": 11       # 9.2% checkout completion
            },
            "375x667": {
                "view_item": 900,
                "add_to_cart": 99,   # 11.0% (below baseline -28% ⚠️ OUTLIER - mobile resolution)
                "purchase": 8        # 8.1% checkout completion
            },
            "414x896": {
                "view_item": 600,
                "add_to_cart": 72,   # 12.0% (below baseline -21% ⚠️ OUTLIER)
                "purchase": 6        # 8.3% checkout completion
            },
            "1536x864": {
                "view_item": 400,
                "add_to_cart": 64,   # 16.0% (above baseline)
                "purchase": 6        # 9.4% checkout completion
            }
        }
    
    # Product breakdown - Bags of Love products
    if "itemName" in dimensions:
        dimension_breakdowns["itemName"] = {
            "China Mugs": {
                "view_item": 1200,
                "add_to_cart": 252,  # 21.0% (above baseline +38% ⚠️ OPPORTUNITY - best seller)
                "purchase": 25       # 9.9% checkout completion
            },
            "Photo Canvas": {
                "view_item": 800,
                "add_to_cart": 128,  # 16.0% (above baseline)
                "purchase": 12       # 9.4% checkout completion
            },
            "Personalised Socks": {
                "view_item": 600,
                "add_to_cart": 72,   # 12.0% (below baseline -21% ⚠️ OUTLIER)
                "purchase": 6        # 8.3% checkout completion
            },
            "Tea Towels": {
                "view_item": 900,
                "add_to_cart": 81,   # 9.0% (below baseline -41% ⚠️ OUTLIER - poor product-market fit)
                "purchase": 7        # 8.6% checkout completion
            },
            "Photo Blankets": {
                "view_item": 700,
                "add_to_cart": 112,  # 16.0% (above baseline)
                "purchase": 10       # 8.9% checkout completion
            }
        }
    
    # Product category breakdown - Bags of Love categories
    if "itemCategory" in dimensions:
        dimension_breakdowns["itemCategory"] = {
            "Canvas & Wall Art": {
                "view_item": 1800,
                "add_to_cart": 306,  # 17.0% (above baseline +12%)
                "purchase": 30       # 9.8% checkout completion
            },
            "Photo Blankets": {
                "view_item": 1200,
                "add_to_cart": 156,  # 13.0% (below baseline -14% ⚠️ OUTLIER - high returns?)
                "purchase": 13       # 8.3% checkout completion
            },
            "Kitchen & Dining": {
                "view_item": 800,
                "add_to_cart": 136,  # 17.0% (above baseline +12%)
                "purchase": 13       # 9.6% checkout completion
            },
            "Clothing & Accessories": {
                "view_item": 500,
                "add_to_cart": 40,   # 8.0% (below baseline -47% ⚠️ CRITICAL - poor targeting?)
                "purchase": 3        # 7.5% checkout completion
            }
        }
    
    # ============================================================================
    # METADATA
    # ============================================================================
    
    metadata = {
        "property_id": property_id,
        "date_range": date_range,
        "generated_at": datetime.now().isoformat(),
        "data_source": "mock",
        "funnel_steps": funnel_steps,
        "dimensions_analyzed": list(dimension_breakdowns.keys()),
        "total_view_item": sum(
            sum(v.get("view_item", 0) for v in breakdown.values())
            for breakdown in dimension_breakdowns.values()
        ) // len(dimension_breakdowns) if dimension_breakdowns else 0
    }
    
    # ============================================================================
    # RETURN COMPLETE DATA STRUCTURE
    # ============================================================================
    
    return {
        "overall_baseline": overall_baseline,
        "dimension_breakdowns": dimension_breakdowns,
        "metadata": metadata
    }


def generate_historical_mock_data(days=7, property_id="123456789"):
    """
    Generate historical funnel data for trend analysis
    
    Args:
        days: Number of days of historical data
        property_id: GA4 property ID
        
    Returns:
        list: Historical data points
    """
    
    historical_data = []
    
    for i in range(days):
        date = (datetime.now() - timedelta(days=days-i)).strftime("%Y-%m-%d")
        
        # Add slight variation to baseline rates
        variation = 1 + random.uniform(-0.05, 0.05)  # ±5% daily variation
        
        historical_data.append({
            "date": date,
            "view_item_to_add_to_cart": round(0.152 * variation, 4),
            "add_to_cart_to_purchase": round(0.087 * variation, 4),
            "overall_conversion": round(0.0132 * variation, 4),
            "total_view_item": random.randint(3800, 4200)
        })
    
    return historical_data



