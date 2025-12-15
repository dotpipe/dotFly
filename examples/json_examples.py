"""
JSON Framework Examples
=======================
Practical examples showing how to use the JSON web framework.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from json_framework import (
    JSONWebApp, JSONToHTML, JSONPage, JSONForm, JSONTable, 
    JSONLink, OptimizedCSVDatabase
)
import json


def example_1_simple_page():
    """Example 1: Create a simple page with JSON."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Simple JSON Page")
    print("="*60)
    
    page_json = {
        "head": {
            "title": "My Website",
            "styles": """
                body { font-family: Arial; margin: 20px; }
                h1 { color: #333; }
            """
        },
        "body": [
            {
                "tag": "h1",
                "text": "Hello, JSON Web Framework!"
            },
            {
                "tag": "p",
                "text": "This entire page is defined in JSON."
            }
        ]
    }
    
    converter = JSONToHTML()
    html = JSONPage().build(page_json)
    print("\nGenerated HTML:")
    print(html[:500] + "...")
    
    return html


def example_2_navigation():
    """Example 2: Create navigation with internal and external links."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Navigation with Links")
    print("="*60)
    
    nav = {
        "tag": "nav",
        "attributes": {"class": "navbar"},
        "children": [
            {
                "tag": "div",
                "attributes": {"class": "nav-brand"},
                "text": "My Site"
            },
            {
                "tag": "div",
                "attributes": {"class": "nav-links"},
                "children": [
                    # Internal link - uses AJAX
                    JSONLink.create_internal("/home", "Home", target="content"),
                    # Another internal link
                    JSONLink.create_internal("/products", "Products", target="content"),
                    # External link - opens in new tab
                    JSONLink.create_external("https://github.com", "GitHub", "external")
                ]
            }
        ]
    }
    
    converter = JSONToHTML()
    html = converter.convert(nav)
    print("\nGenerated Navigation HTML:")
    print(html)
    
    return html


def example_3_form():
    """Example 3: Create a form with JSON."""
    print("\n" + "="*60)
    print("EXAMPLE 3: JSON Form")
    print("="*60)
    
    form = JSONForm.create_form(
        "contact-form",
        method="POST",
        name={
            "type": "text",
            "label": "Your Name",
            "attributes": {"placeholder": "Enter your name", "required": True}
        },
        email={
            "type": "email",
            "label": "Email Address",
            "attributes": {"placeholder": "your@email.com", "required": True}
        },
        message={
            "type": "textarea",
            "label": "Message",
            "attributes": {"placeholder": "Your message here", "rows": 5}
        }
    )
    
    converter = JSONToHTML()
    html = converter.convert(form)
    print("\nGenerated Form HTML:")
    print(html)
    
    return html


def example_4_database():
    """Example 4: Create and query a database."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Database Operations")
    print("="*60)
    
    # Create app with database
    app = JSONWebApp("BlogApp", data_dir="example_data")
    
    # Create posts database
    db = app.create_database("posts", ["id", "title", "content", "author", "date"])
    
    # Insert sample data
    db.insert({
        "id": "1",
        "title": "Getting Started",
        "content": "First post about the framework",
        "author": "Alice",
        "date": "2024-01-15"
    })
    
    db.insert({
        "id": "2",
        "title": "Advanced Usage",
        "content": "Learn advanced patterns",
        "author": "Bob",
        "date": "2024-01-20"
    })
    
    db.insert({
        "id": "3",
        "title": "JSON Best Practices",
        "content": "Tips for organizing JSON data",
        "author": "Alice",
        "date": "2024-01-25"
    })
    
    # Query all
    all_posts = db.get_all()
    print(f"\nAll posts ({len(all_posts)} total):")
    for post in all_posts:
        print(f"  - {post['title']} by {post['author']}")
    
    # Query by author
    alice_posts = db.select({"author": "Alice"})
    print(f"\nAlice's posts ({len(alice_posts)} total):")
    for post in alice_posts:
        print(f"  - {post['title']}")
    
    # Update
    db.update({"id": "1"}, {"content": "Updated first post"})
    updated = db.select_by_id("1")
    print(f"\nUpdated post 1: {updated['content']}")
    
    return db


def example_5_table():
    """Example 5: Generate table from data."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Data Tables")
    print("="*60)
    
    # Sample data
    data = [
        {"id": "1", "product": "Laptop", "price": "$999", "stock": "10"},
        {"id": "2", "product": "Mouse", "price": "$29", "stock": "50"},
        {"id": "3", "product": "Keyboard", "price": "$79", "stock": "25"},
        {"id": "4", "product": "Monitor", "price": "$299", "stock": "8"},
    ]
    
    # Create table
    table = JSONTable.from_list(data, **{"class": "products-table"})
    
    converter = JSONToHTML()
    html = converter.convert(table)
    print("\nGenerated Table HTML:")
    print(html)
    
    return html


def example_6_complete_page():
    """Example 6: Build a complete page with multiple sections."""
    print("\n" + "="*60)
    print("EXAMPLE 6: Complete Website Page")
    print("="*60)
    
    # Sample product data
    products = [
        {"id": "1", "name": "Product A", "price": "$49.99"},
        {"id": "2", "name": "Product B", "price": "$79.99"},
        {"id": "3", "name": "Product C", "price": "$29.99"},
    ]
    
    # Build complete page
    page_json = {
        "head": {
            "title": "Product Showcase",
            "styles": """
                body { font-family: Arial; margin: 0; }
                header { background: #333; color: white; padding: 20px; }
                nav { background: #666; }
                nav a { color: white; padding: 10px 15px; display: inline-block; }
                nav a.ajax:hover { background: #999; }
                main { padding: 20px; }
                .products-table { width: 100%; border-collapse: collapse; }
                .products-table th, .products-table td { border: 1px solid #ddd; padding: 10px; }
                .products-table th { background: #f0f0f0; }
                footer { background: #333; color: white; padding: 20px; text-align: center; }
            """
        },
        "body": [
            # Header
            {
                "tag": "header",
                "children": [
                    {"tag": "h1", "text": "Our Products"}
                ]
            },
            # Navigation
            {
                "tag": "nav",
                "children": [
                    JSONLink.create_internal("/", "Home", target="main"),
                    JSONLink.create_internal("/products", "Products", target="main"),
                    JSONLink.create_internal("/about", "About", target="main"),
                    JSONLink.create_external("https://contact.example.com", "Contact")
                ]
            },
            # Main content
            {
                "tag": "main",
                "attributes": {"id": "main"},
                "children": [
                    {"tag": "h2", "text": "Featured Products"},
                    JSONTable.from_list(products, **{"class": "products-table"}),
                    {
                        "tag": "h2",
                        "text": "Get In Touch"
                    },
                    JSONForm.create_form(
                        "subscribe-form",
                        method="POST",
                        email={
                            "type": "email",
                            "label": "Email",
                            "attributes": {"placeholder": "your@email.com"}
                        }
                    )
                ]
            },
            # Footer
            {
                "tag": "footer",
                "text": "© 2024 My Company. All rights reserved."
            }
        ]
    }
    
    html = JSONPage().build(page_json)
    print("\nGenerated complete page HTML (first 800 chars):")
    print(html[:800] + "...\n")
    
    return html


def example_7_json_structure():
    """Example 7: Show JSON structure format."""
    print("\n" + "="*60)
    print("EXAMPLE 7: JSON Structure Format")
    print("="*60)
    
    # Perfect example of JSON structure
    json_structure = {
        "tag": "div",
        "attributes": {
            "id": "main-container",
            "class": "container",
            "data-type": "page"
        },
        "children": [
            {
                "tag": "h1",
                "text": "Title"
            },
            {
                "tag": "p",
                "text": "Paragraph text"
            },
            {
                "tag": "a",
                "attributes": {
                    "href": "/page",
                    "class": "ajax"
                },
                "text": "Internal Link"
            },
            {
                "tag": "a",
                "attributes": {
                    "href": "https://example.com",
                    "class": "redirect",
                    "target": "_blank"
                },
                "text": "External Link"
            }
        ]
    }
    
    print("\nJSON Structure:")
    print(json.dumps(json_structure, indent=2))
    
    print("\nConverted to HTML:")
    converter = JSONToHTML()
    html = converter.convert(json_structure)
    print(html)
    
    return json_structure


def example_8_csv_workflow():
    """Example 8: Complete CSV workflow."""
    print("\n" + "="*60)
    print("EXAMPLE 8: CSV Database Workflow")
    print("="*60)
    
    # Create database
    db = OptimizedCSVDatabase("example_data/customers.csv")
    
    # Create table if new
    if not db.get_headers():
        db.create_table(["customer_id", "name", "email", "status"])
    
    # Insert records
    print("\n1. Inserting data...")
    customers = [
        {"customer_id": "C001", "name": "John Smith", "email": "john@example.com", "status": "active"},
        {"customer_id": "C002", "name": "Jane Doe", "email": "jane@example.com", "status": "active"},
        {"customer_id": "C003", "name": "Bob Wilson", "email": "bob@example.com", "status": "inactive"},
        {"customer_id": "C004", "name": "Alice Brown", "email": "alice@example.com", "status": "active"},
    ]
    
    for customer in customers:
        db.insert(customer)
    
    print(f"Inserted {len(customers)} customers")
    
    # Query
    print("\n2. Querying data...")
    active = db.select({"status": "active"})
    print(f"Active customers: {len(active)}")
    for c in active:
        print(f"  - {c['name']} ({c['email']})")
    
    # Fast lookup by ID
    print("\n3. Fast lookup by ID...")
    customer = db.select_by_id("C002")
    print(f"Customer C002: {customer['name']}")
    
    # Update
    print("\n4. Updating data...")
    db.update({"customer_id": "C003"}, {"status": "active"})
    updated = db.select_by_id("C003")
    print(f"Updated C003 status to: {updated['status']}")
    
    # Statistics
    print("\n5. Database statistics...")
    print(f"Total records: {db.count()}")
    print(f"Columns: {', '.join(db.get_headers())}")
    
    return db


if __name__ == "__main__":
    print("\n" + "="*60)
    print("JSON Web Framework - Complete Examples")
    print("="*60)
    
    # Run examples
    example_1_simple_page()
    example_2_navigation()
    example_3_form()
    example_4_database()
    example_5_table()
    example_6_complete_page()
    example_7_json_structure()
    example_8_csv_workflow()
    
    print("\n" + "="*60)
    print("All examples completed!")
    print("="*60)
