#!/usr/bin/env python3
"""
Extract and convert Rails pages to static HTML for Cloudflare Pages
Handles: home, faq, privacy, cookies, terms
"""

import re
import os
import json
import subprocess
from datetime import datetime

def get_page_content(page_path):
    """Fetch a page from the Rails dev server"""
    try:
        # Use curl to fetch the page content
        result = subprocess.run(
            ['curl', '-s', f'https://dev.residentcheckin.co{page_path}'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout
        else:
            print(f"Error fetching {page_path}: {result.stderr}")
            return None
    except Exception as e:
        print(f"Exception fetching {page_path}: {e}")
        return None

def extract_home_page():
    """Extract and process the home page from Rails ERB template"""
    print("Extracting home page...")
    
    # Read the home page ERB template
    with open('../app/views/pages/home.html.erb', 'r') as f:
        content = f.read()
    
    # Read the home page navigation
    with open('shared_nav_home.html', 'r') as f:
        nav_content = f.read()
    
    # Read the footer partial
    with open('../app/views/shared/_footer.html.erb', 'r') as f:
        footer_content = f.read()
    
    # Replace the Rails navigation with shared navigation
    # Find and replace the entire nav section
    nav_start = content.find('<!-- Navigation -->')
    nav_end = content.find('</nav>', nav_start) + len('</nav>')
    
    if nav_start != -1 and nav_end != -1:
        # Also remove the mobile menu script that's specific to the Rails version
        script_start = content.find('<script>', nav_end)
        script_end = content.find('</script>', script_start) + len('</script>')
        if script_start - nav_end < 100:  # Script is close to nav, likely the mobile menu script
            content = content[:nav_start] + nav_content + content[script_end:]
        else:
            content = content[:nav_start] + nav_content + content[nav_end:]
    
    # Replace the Rails form with a static contact form
    form_start = content.find('<%= form_with')
    form_end = content.find('<% end %>', form_start) + len('<% end %>')
    
    if form_start != -1 and form_end != -1:
        # Create a static HTML form that uses Cloudflare Pages Functions
        static_form = '''
            <form action="/api/contact" method="POST" class="space-y-4" id="contact-form" data-contact-form>
              <div>
                <label for="topic" class="block text-sm font-medium text-gray-700 mb-2">I'm interested in:</label>
                <select name="topic" id="topic" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500" required onchange="toggleOtherField(this)">
                  <option value="">Select an option</option>
                  <option value="Requesting a demo">Requesting a demo</option>
                  <option value="Pricing information">Pricing information</option>
                  <option value="Technical questions">Technical questions</option>
                  <option value="Partnership opportunities">Partnership opportunities</option>
                  <option value="Other">Other</option>
                </select>
              </div>
              
              <div id="other-topic-field" style="display: none;">
                <label for="other_topic" class="block text-sm font-medium text-gray-700 mb-2">Please specify:</label>
                <input type="text" name="other_topic" id="other_topic" placeholder="Tell us what you're interested in..." class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500">
              </div>
              
              <div class="grid md:grid-cols-2 gap-4">
                <div>
                  <label for="name" class="block text-sm font-medium text-gray-700 mb-2">Name</label>
                  <input type="text" name="name" id="name" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500">
                </div>
                <div>
                  <label for="email" class="block text-sm font-medium text-gray-700 mb-2">Email *</label>
                  <input type="email" name="email" id="email" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500" required>
                </div>
              </div>
              
              <div class="grid md:grid-cols-2 gap-4">
                <div>
                  <label for="facility_name" class="block text-sm font-medium text-gray-700 mb-2">Facility Name</label>
                  <input type="text" name="facility_name" id="facility_name" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500">
                </div>
                <div>
                  <label for="resident_count" class="block text-sm font-medium text-gray-700 mb-2">Number of Residents</label>
                  <input type="number" name="resident_count" id="resident_count" placeholder="Approximate" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500">
                </div>
              </div>
              
              <div>
                <label for="phone" class="block text-sm font-medium text-gray-700 mb-2">Phone *</label>
                <input type="tel" name="phone" id="phone" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500" required>
              </div>
              
              <div>
                <label for="current_solution" class="block text-sm font-medium text-gray-700 mb-2">Current Wellness Check Solution</label>
                <input type="text" name="current_solution" id="current_solution" placeholder="Manual checks, flags, other system, etc." class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500">
              </div>
              
              <div>
                <label for="contact_preference" class="block text-sm font-medium text-gray-700 mb-2">Best Time/Way to Contact You</label>
                <textarea name="contact_preference" id="contact_preference" rows="3" placeholder="Morning/afternoon, phone/email preference, any special instructions" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"></textarea>
              </div>
              
              <!-- Honeypot field for bot protection -->
              <div style="display: none;">
                <input type="text" name="_gotcha" tabindex="-1" autocomplete="off">
              </div>
              
              <div class="pt-4">
                <button type="submit" class="w-full bg-indigo-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-indigo-700 transition">
                  Submit Contact Request
                </button>
              </div>
            </form>'''
        
        # Replace the Rails form with the static form
        content = content[:form_start] + static_form + content[form_end:]
    
    # Load version info
    version_file = 'version.json'
    try:
        with open(version_file, 'r') as f:
            version_data = json.load(f)
            version = version_data.get('version', '1.01')
    except FileNotFoundError:
        version = '1.01'
    
    # Update version in footer content
    footer_content = re.sub(r'v\d+\.\d+', f'v{version}', footer_content)
    
    # Replace the footer render tag
    footer_tag = '<%= render \'shared/footer\' %>'
    content = content.replace(footer_tag, footer_content)
    
    # Remove any remaining ERB tags
    content = re.sub(r'<%=?[^%>]*%>', '', content)
    
    # Update links to point to dev site for testing
    content = content.replace('href="/facility/onboarding"', 'href="https://dev.residentcheckin.co/facility/onboarding"')
    content = content.replace('href="/users/sign_in"', 'href="https://dev.residentcheckin.co/users/sign_in"')
    # Keep FAQ link local since we'll have that page
    content = content.replace('href="https://dev.residentcheckin.co/users/sign_in"', 'href="https://dev.residentcheckin.co/users/sign_in"')
    
    return content

def create_html_wrapper(content, title, description):
    """Wrap content in a full HTML document"""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{description}">
    
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- Favicon -->
    <link rel="icon" type="image/x-icon" href="/favicon.ico">
    
    <!-- Open Graph Tags -->
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="/Facility-screenshot.png">
    <meta property="og:url" content="https://residentcheckin.co">
    <meta property="og:type" content="website">
    
    <style>
        html {{
            scroll-behavior: smooth;
        }}
        
        .faq-question {{
            transition: all 0.3s ease;
        }}
        .faq-question:hover {{
            background-color: #f3f4f6;
        }}
        .rotate-180 {{
            transform: rotate(180deg);
        }}
        .faq-icon {{
            transition: transform 0.3s ease;
        }}
    </style>
</head>
<body>
{content}

<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-C2J67LGNNQ"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', 'G-C2J67LGNNQ');
</script>

<!-- FAQ Page Scripts -->
<script>
document.addEventListener('DOMContentLoaded', function() {{
    // FAQ accordion functionality
    const faqButtons = document.querySelectorAll('[data-answer-id]');
    
    faqButtons.forEach(button => {{
        button.addEventListener('click', function() {{
            const answerId = this.dataset.answerId;
            const answer = document.getElementById(answerId);
            const icon = this.querySelector('.faq-icon');
            
            if (answer.classList.contains('hidden')) {{
                answer.classList.remove('hidden');
                answer.classList.add('block');
                icon.classList.add('rotate-180');
                this.setAttribute('aria-expanded', 'true');
            }} else {{
                answer.classList.add('hidden');
                answer.classList.remove('block');
                icon.classList.remove('rotate-180');
                this.setAttribute('aria-expanded', 'false');
            }}
        }});
    }});
    
    // Expand All functionality
    const expandAll = document.querySelector('[data-action="expandAll"]');
    if (expandAll) {{
        expandAll.addEventListener('click', function() {{
            document.querySelectorAll('[data-answer-id]').forEach(button => {{
                const answerId = button.dataset.answerId;
                const answer = document.getElementById(answerId);
                const icon = button.querySelector('.faq-icon');
                
                answer.classList.remove('hidden');
                answer.classList.add('block');
                icon.classList.add('rotate-180');
                button.setAttribute('aria-expanded', 'true');
            }});
        }});
    }}
    
    // Collapse All functionality
    const collapseAll = document.querySelector('[data-action="collapseAll"]');
    if (collapseAll) {{
        collapseAll.addEventListener('click', function() {{
            document.querySelectorAll('[data-answer-id]').forEach(button => {{
                const answerId = button.dataset.answerId;
                const answer = document.getElementById(answerId);
                const icon = button.querySelector('.faq-icon');
                
                answer.classList.add('hidden');
                answer.classList.remove('block');
                icon.classList.remove('rotate-180');
                button.setAttribute('aria-expanded', 'false');
            }});
        }});
    }}
    
    // Contact form handler
    const form = document.querySelector('[data-contact-form]');
    if (form) {{
        const submitButton = form.querySelector('button[type="submit"]');
        const originalButtonText = submitButton.textContent;
        
        form.addEventListener('submit', async function(e) {{
            e.preventDefault();
            
            submitButton.disabled = true;
            submitButton.textContent = 'Sending...';
            
            try {{
                const formData = new FormData(form);
                const response = await fetch('/api/contact', {{
                    method: 'POST',
                    body: formData
                }});
                
                const result = await response.json();
                
                if (response.ok && result.success) {{
                    form.innerHTML = `
                        <div class="text-center py-8">
                            <div class="mb-4">
                                <svg class="w-16 h-16 text-green-500 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                </svg>
                            </div>
                            <h3 class="text-2xl font-semibold text-gray-900 mb-2">Thank You!</h3>
                            <p class="text-gray-600">${{result.message || "We'll be in touch soon."}}</p>
                        </div>
                    `;
                }} else {{
                    alert(result.message || 'There was an error submitting the form. Please try again.');
                    submitButton.disabled = false;
                    submitButton.textContent = originalButtonText;
                }}
            }} catch (error) {{
                console.error('Form submission error:', error);
                alert('There was an error submitting the form. Please try again later.');
                submitButton.disabled = false;
                submitButton.textContent = originalButtonText;
            }}
        }});
    }}
    
    // Mobile menu functionality
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    const menuIcon = document.getElementById('menu-icon');

    if (mobileMenuButton && mobileMenu && menuIcon) {{
        mobileMenuButton.addEventListener('click', function() {{
            const isHidden = mobileMenu.classList.contains('hidden');
            
            if (isHidden) {{
                mobileMenu.classList.remove('hidden');
                menuIcon.setAttribute('d', 'M6 18L18 6M6 6l12 12'); // X icon
            }} else {{
                mobileMenu.classList.add('hidden');
                menuIcon.setAttribute('d', 'M4 6h16M4 12h16M4 18h16'); // Hamburger icon
            }}
        }});
    }}
}});

function toggleOtherField(select) {{
    const otherField = document.getElementById('other-topic-field');
    if (select.value === 'Other') {{
        otherField.style.display = 'block';
    }} else {{
        otherField.style.display = 'none';
    }}
}}
</script>

</body>
</html>'''

def extract_other_pages():
    """Generate FAQ using template, extract other pages from Rails"""
    
    # Generate FAQ using our clean template
    print("Generating FAQ page from template...")
    os.system("ruby generate_faq_static.rb")
    print("  Saved to public/faq.html")
    
    # Extract other pages from Rails
    pages = [
        {
            'path': '/privacy',
            'output': 'public/privacy.html',
            'title': 'Privacy Policy | ResidentCheckin.co',
            'description': 'ResidentCheckin.co privacy policy. Learn how we collect, use, and protect your personal information.'
        },
        {
            'path': '/cookies',
            'output': 'public/cookies.html',
            'title': 'Cookie Policy | ResidentCheckin.co',
            'description': 'ResidentCheckin.co cookie policy. Learn about the cookies we use and how to manage your preferences.'
        },
        {
            'path': '/terms',
            'output': 'public/terms.html',
            'title': 'Terms of Service | ResidentCheckin.co',
            'description': 'ResidentCheckin.co terms of service. Read our terms and conditions for using our automated wellness monitoring service.'
        }
    ]
    
    for page in pages:
        print(f"Extracting {page['path']}...")
        content = get_page_content(page['path'])
        
        if content:
            # Remove ALL Rails-specific JavaScript module imports
            content = re.sub(r'<link rel="modulepreload"[^>]*>', '', content)
            content = re.sub(r'<script type="module">import "application"</script>', '', content)
            
            # Clean up Rails-specific elements
            # Remove Rails asset pipeline references
            content = re.sub(r'<link[^>]*data-turbo-track[^>]*>', '', content)
            content = re.sub(r'<script[^>]*data-turbo-track[^>]*>.*?</script>', '', content, flags=re.DOTALL)
            
            # Remove CSRF tokens
            content = re.sub(r'<meta name="csrf-[^"]*"[^>]*>', '', content)
            
            # Fix links to point to appropriate locations
            content = content.replace('href="/facility/onboarding"', 'href="https://dev.residentcheckin.co/facility/onboarding"')
            content = content.replace('href="/users/sign_in"', 'href="https://dev.residentcheckin.co/users/sign_in"')
            
            # Keep internal navigation working
            content = content.replace('href="/#', 'href="/#')
            
            # Save the page
            with open(page['output'], 'w') as f:
                f.write(content)
            print(f"  Saved to {page['output']}")
        else:
            print(f"  Failed to extract {page['path']}")

def main():
    """Main extraction process"""
    print("Starting static page extraction...")
    print("=" * 50)
    
    # Load and update version
    version_file = 'version.json'
    try:
        with open(version_file, 'r') as f:
            version_data = json.load(f)
    except FileNotFoundError:
        version_data = {
            "version": "1.01",
            "last_updated": datetime.now().isoformat() + 'Z',
            "deployed_version": None,
            "deployment_history": []
        }
    
    # Increment version (minor version bump)
    current_version = version_data.get('version', '1.01')
    major, minor = current_version.split('.')
    minor = int(minor) + 1
    new_version = f"{major}.{minor:02d}"
    
    # Update version data
    version_data['version'] = new_version
    version_data['last_updated'] = datetime.now().isoformat() + 'Z'
    
    # Save updated version
    with open(version_file, 'w') as f:
        json.dump(version_data, f, indent=2)
    
    print(f"Building version {new_version}...")
    
    # Extract home page
    home_content = extract_home_page()
    home_html = create_html_wrapper(
        home_content, 
        "ResidentCheckin.co - Automated Wellness Checks for Senior Living Communities",
        "Save 20+ hours per week on wellness checks. Automated safety monitoring and resident communications for independent living facilities. Trusted since 2012."
    )
    
    # Save home page
    with open('public/index.html', 'w') as f:
        f.write(home_html)
    print("Home page extracted and saved to public/index.html")
    
    # Extract other pages
    extract_other_pages()
    
    print("\n" + "=" * 50)
    print(f"Version {new_version} generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nPages generated:")
    print("  - Home page (index.html) - extracted from Rails")
    print("  - FAQ page (faq.html) - generated from clean template")
    print("  - Privacy page (privacy.html) - extracted from Rails")
    print("  - Cookies page (cookies.html) - extracted from Rails")
    print("  - Terms page (terms.html) - extracted from Rails")
    print("\nNext steps:")
    print("1. Commit and push to deploy to Cloudflare Pages")
    print("2. All pages will be available on the public site")

if __name__ == "__main__":
    main()