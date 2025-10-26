#!/usr/bin/env python3
"""
Bagsoflove Website Crawler for GA4 Demo
Crawls bagsoflove.co.uk to generate realistic GA4 mock data
"""

import os
import json
import logging
from firecrawl import FirecrawlApp
from datetime import datetime, timedelta
import random

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Firecrawl
api_key = "fc-42c7a87023d2465c84070620ece90bcf"
app = FirecrawlApp(api_key=api_key)

def crawl_bagsoflove():
    """Crawl Bagsoflove website to understand their products and structure"""
    logger.info("🔍 Crawling Bagsoflove website...")
    
    try:
        # First, map the website to understand structure
        logger.info("📋 Mapping website structure...")
        map_result = app.map("https://bagsoflove.co.uk", limit=50)
        
        urls = map_result.get('links', [])
        logger.info(f"Found {len(urls)} URLs on the site")
        
        # Key pages to scrape for product information
        key_pages = [
            "https://bagsoflove.co.uk",
            "https://bagsoflove.co.uk/shop",
            "https://bagsoflove.co.uk/about",
            "https://bagsoflove.co.uk/blog"
        ]
        
        # Add product pages if found
        product_urls = [url for url in urls if '/product/' in url or '/shop/' in url]
        key_pages.extend(product_urls[:5])  # Limit to first 5 product pages
        
        scraped_data = {}
        
        for url in key_pages:
            try:
                logger.info(f"📄 Scraping: {url}")
                scrape_result = app.scrape(url, params={
                    'formats': ['markdown'],
                    'onlyMainContent': True
                })
                
                scraped_data[url] = {
                    'content': scrape_result.get('markdown', ''),
                    'metadata': scrape_result.get('metadata', {})
                }
                
            except Exception as e:
                logger.warning(f"Failed to scrape {url}: {e}")
                continue
        
        return scraped_data
        
    except Exception as e:
        logger.error(f"Error crawling website: {e}")
        return {}

def extract_product_info(scraped_data):
    """Extract product categories and information from scraped data"""
    logger.info("📦 Extracting product information...")
    
    products = []
    categories = set()
    
    # Analyze scraped content for products and categories
    for url, data in scraped_data.items():
        content = data.get('content', '').lower()
        
        # Look for product-related keywords
        if any(keyword in content for keyword in ['t-shirt', 'tshirt', 'custom', 'personalized', 'gift']):
            # Extract potential products and categories
            if 't-shirt' in content or 'tshirt' in content:
                categories.add('T-Shirts')
                products.append('Custom T-Shirts')
            
            if 'mug' in content:
                categories.add('Mugs')
                products.append('Personalized Mugs')
            
            if 'bag' in content:
                categories.add('Bags')
                products.append('Custom Bags')
            
            if 'poster' in content or 'print' in content:
                categories.add('Posters')
                products.append('Custom Posters')
    
    # Default products if none found
    if not products:
        products = [
            'Custom T-Shirts',
            'Personalized Mugs', 
            'Custom Bags',
            'Custom Posters',
            'Personalized Gifts'
        ]
        categories = ['T-Shirts', 'Mugs', 'Bags', 'Posters', 'Gifts']
    
    return list(set(products)), list(categories)

def generate_realistic_ga4_data(products, categories):
    """Generate realistic GA4 mock data based on Bagsoflove's actual products"""
    logger.info("📊 Generating realistic GA4 data...")
    
    # Base metrics (similar to SEO demo numbers)
    total_users = 1096  # From SEO demo
    total_revenue = 837.24  # From SEO demo
    
    # Generate funnel data
    funnel_data = {
        "overall_metrics": {
            "total_users": total_users,
            "total_sessions": int(total_users * 1.2),  # Some users have multiple sessions
            "total_revenue": total_revenue,
            "total_conversions": int(total_revenue / 25),  # Assume £25 average order value
            "conversion_rate": round((int(total_revenue / 25) / total_users) * 100, 2)
        },
        "funnel_steps": {
            "view_item": {
                "users": total_users,
                "rate": 100.0
            },
            "add_to_cart": {
                "users": int(total_users * 0.15),  # 15% cart rate
                "rate": 15.0
            },
            "purchase": {
                "users": int(total_users * 0.08),  # 8% conversion rate
                "rate": 8.0
            }
        },
        "dimensions": {
            "channel": {
                "Organic Search": {"users": int(total_users * 0.45), "conversion_rate": 8.5},
                "Social": {"users": int(total_users * 0.25), "conversion_rate": 6.2},
                "Direct": {"users": int(total_users * 0.15), "conversion_rate": 12.1},
                "Email": {"users": int(total_users * 0.10), "conversion_rate": 15.8},
                "Paid Search": {"users": int(total_users * 0.05), "conversion_rate": 9.3}
            },
            "device": {
                "desktop": {"users": int(total_users * 0.55), "conversion_rate": 10.2},
                "mobile": {"users": int(total_users * 0.40), "conversion_rate": 6.8},
                "tablet": {"users": int(total_users * 0.05), "conversion_rate": 8.1}
            },
            "product": {}
        }
    }
    
    # Add realistic product data
    for i, product in enumerate(products[:5]):
        # Vary performance based on product type
        if 't-shirt' in product.lower():
            conversion_rate = 7.2  # Lower for clothing (size concerns)
            users = int(total_users * 0.35)
        elif 'mug' in product.lower():
            conversion_rate = 9.8  # Higher for simple gifts
            users = int(total_users * 0.25)
        elif 'bag' in product.lower():
            conversion_rate = 6.5  # Lower for bags
            users = int(total_users * 0.20)
        else:
            conversion_rate = 8.5  # Average
            users = int(total_users * 0.20)
        
        funnel_data["dimensions"]["product"][product] = {
            "users": users,
            "conversion_rate": conversion_rate
        }
    
    return funnel_data

def save_mock_data(funnel_data):
    """Save the generated mock data to a JSON file"""
    logger.info("💾 Saving mock data...")
    
    # Add timestamp
    funnel_data["generated_at"] = datetime.now().isoformat()
    funnel_data["source"] = "bagsoflove.co.uk"
    
    with open("bagsoflove_mock_data.json", "w") as f:
        json.dump(funnel_data, f, indent=2)
    
    logger.info("✅ Mock data saved to bagsoflove_mock_data.json")

def main():
    """Main function to crawl and generate data"""
    logger.info("🚀 Starting Bagsoflove GA4 Demo Data Generation")
    
    # Crawl the website
    scraped_data = crawl_bagsoflove()
    
    if not scraped_data:
        logger.warning("⚠️ No data scraped, using default products")
        products = ['Custom T-Shirts', 'Personalized Mugs', 'Custom Bags', 'Custom Posters', 'Personalized Gifts']
        categories = ['T-Shirts', 'Mugs', 'Bags', 'Posters', 'Gifts']
    else:
        # Extract product information
        products, categories = extract_product_info(scraped_data)
    
    logger.info(f"📦 Found products: {products}")
    logger.info(f"🏷️ Found categories: {categories}")
    
    # Generate realistic GA4 data
    funnel_data = generate_realistic_ga4_data(products, categories)
    
    # Save the data
    save_mock_data(funnel_data)
    
    logger.info("🎉 Bagsoflove GA4 demo data generation complete!")
    logger.info("📊 Next: Update demo.html to use this realistic data")

if __name__ == "__main__":
    main()
