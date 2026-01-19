#!/usr/bin/env python3
"""Helper script to analyze the saved bookings page HTML and identify card structure."""

from pathlib import Path
from bs4 import BeautifulSoup
import sys

def analyze_html_file(html_file: str):
    """Analyze HTML file to find booking card structure."""
    file_path = Path(html_file)
    
    if not file_path.exists():
        print(f"File not found: {html_file}")
        return
    
    print(f"Analyzing: {html_file}")
    print("="*80)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Look for common card patterns
    print("\n1. Looking for elements with 'card' in class name:")
    cards = soup.find_all(class_=lambda x: x and 'card' in ' '.join(x).lower())
    print(f"   Found {len(cards)} elements")
    if cards:
        for i, card in enumerate(cards[:5], 1):  # Show first 5
            classes = ' '.join(card.get('class', []))
            print(f"   {i}. Classes: {classes}")
            text = card.get_text(strip=True)[:100]
            print(f"      Text preview: {text}...")
    
    print("\n2. Looking for elements with 'booking' in class name:")
    bookings = soup.find_all(class_=lambda x: x and 'booking' in ' '.join(x).lower())
    print(f"   Found {len(bookings)} elements")
    
    print("\n3. Looking for elements with 'registration' in class name:")
    registrations = soup.find_all(class_=lambda x: x and 'registration' in ' '.join(x).lower())
    print(f"   Found {len(registrations)} elements")
    
    print("\n4. Looking for cancel/remove buttons:")
    cancel_texts = ['cancel', 'remove', 'delete', 'withdraw', 'drop']
    for text in cancel_texts:
        buttons = soup.find_all(string=lambda x: x and text.lower() in x.lower())
        if buttons:
            print(f"   Found {len(buttons)} elements with text '{text}'")
            # Find parent elements
            for btn in buttons[:3]:
                parent = btn.parent
                if parent:
                    classes = ' '.join(parent.get('class', []))
                    print(f"      - Parent classes: {classes}")
    
    print("\n5. Looking for date/time patterns:")
    # Common date patterns
    date_keywords = ['date', 'time', 'day', 'when', 'schedule']
    for keyword in date_keywords:
        elements = soup.find_all(string=lambda x: x and keyword.lower() in x.lower())
        if elements:
            print(f"   Found {len(elements)} elements with '{keyword}'")
    
    print("\n6. Sample of all unique class names (first 20):")
    all_classes = set()
    for element in soup.find_all(class_=True):
        all_classes.update(element.get('class', []))
    
    for cls in sorted(list(all_classes))[:20]:
        count = len(soup.find_all(class_=cls))
        print(f"   .{cls} ({count} elements)")
    
    print("\n" + "="*80)
    print("To inspect the HTML visually, open it in a browser:")
    print(f"   open {html_file}")

if __name__ == "__main__":
    html_file = sys.argv[1] if len(sys.argv) > 1 else "data/bookings_page.html"
    analyze_html_file(html_file)

