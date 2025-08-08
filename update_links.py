#!/usr/bin/env python3
"""
Update links in the static HTML to point to production Rails app
"""

import sys

# Configuration
RAILS_APP_URL = "https://app.residentcheckin.co"  # Update this to your Rails app URL
FORMSPREE_ID = "YOUR_FORM_ID"  # Update this to your Formspree form ID

def update_links(filename):
    with open(filename, 'r') as f:
        content = f.read()
    
    # Update Rails app links
    links_to_update = [
        ('/facility/onboarding', f'{RAILS_APP_URL}/facility/onboarding'),
        ('/users/sign_in', f'{RAILS_APP_URL}/users/sign_in'),
        ('/faq', f'{RAILS_APP_URL}/faq'),
    ]
    
    for old_link, new_link in links_to_update:
        content = content.replace(f'href="{old_link}"', f'href="{new_link}"')
    
    # Update Formspree form ID
    content = content.replace('YOUR_FORM_ID', FORMSPREE_ID)
    
    with open(filename, 'w') as f:
        f.write(content)
    
    print(f"Updated links in {filename}")
    print(f"Rails app URL: {RAILS_APP_URL}")
    print(f"Formspree ID: {FORMSPREE_ID}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        RAILS_APP_URL = sys.argv[1]
    if len(sys.argv) > 2:
        FORMSPREE_ID = sys.argv[2]
    
    update_links('public/index.html')
    print("\nUsage: python3 update_links.py [RAILS_APP_URL] [FORMSPREE_ID]")