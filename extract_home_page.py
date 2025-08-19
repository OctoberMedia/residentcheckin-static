#!/usr/bin/env python3
"""
Extract and convert the Rails home page to static HTML for Cloudflare Pages
"""

import re
import os
import json
from datetime import datetime

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

# Read the home page content
with open('../app/views/pages/home.html.erb', 'r') as f:
    content = f.read()

# Read the footer partial
with open('../app/views/shared/_footer.html.erb', 'r') as f:
    footer_content = f.read()

# Replace the Rails form with a static contact form
# Find the form section
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

# Update version in footer content
footer_content = re.sub(r'v\d+\.\d+', f'v{new_version}', footer_content)

# Replace the footer render tag
footer_tag = '<%= render \'shared/footer\' %>'
content = content.replace(footer_tag, footer_content)

# Remove any remaining ERB tags (shouldn't be any, but just in case)
content = re.sub(r'<%=?[^%>]*%>', '', content)

# Create the full HTML document
html_document = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ResidentCheckin.co - Automated Wellness Checks for Senior Living Communities</title>
    <meta name="description" content="Save 20+ hours per week on wellness checks. Automated safety monitoring and resident communications for independent living facilities. Trusted since 2012.">
    
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- Favicon -->
    <link rel="icon" type="image/x-icon" href="/favicon.ico">
    
    <!-- Open Graph Tags -->
    <meta property="og:title" content="ResidentCheckin.co - Automated Wellness Checks">
    <meta property="og:description" content="Save 20+ hours per week on wellness checks with automated safety monitoring for senior living communities.">
    <meta property="og:image" content="/og-image.jpg">
    <meta property="og:url" content="https://residentcheckin.co">
    <meta property="og:type" content="website">
    
    <!-- Custom CSS for animations and additional styling -->
    <style>
        /* Smooth scroll behavior */
        html {{
            scroll-behavior: smooth;
        }}
        
        /* Form field focus states */
        input:focus, select:focus, textarea:focus {{
            outline: none;
            ring: 2;
        }}
        
        /* Contact form JavaScript */
        function toggleOtherField(select) {{
            const otherField = document.getElementById('other-topic-field');
            if (select.value === 'Other') {{
                otherField.style.display = 'block';
            }} else {{
                otherField.style.display = 'none';
            }}
        }}
        
        /* Mobile menu toggle */
        function toggleMobileMenu() {{
            const menu = document.getElementById('mobile-menu');
            menu.classList.toggle('hidden');
        }}
    </style>
</head>
<body>
{content}

<!-- Mobile Menu Script -->
<script>
// Add mobile menu functionality if needed
document.addEventListener('DOMContentLoaded', function() {{
    // Any additional JavaScript initialization
}});
</script>

<!-- Contact Form Handler -->
<script>
document.addEventListener('DOMContentLoaded', function() {{
    const form = document.querySelector('[data-contact-form]');
    if (!form) return;
    
    const submitButton = form.querySelector('button[type="submit"]');
    const originalButtonText = submitButton.textContent;
    
    form.addEventListener('submit', async function(e) {{
        e.preventDefault();
        
        // Disable submit button
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
                // Success - show thank you message
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
                // Error - show message
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
}});
</script>

<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-C2J67LGNNQ"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());

  gtag('config', 'G-C2J67LGNNQ');
</script>

</body>
</html>'''

# Write the output file
with open('public/index.html', 'w') as f:
    f.write(html_document)

print(f"Home page extracted and converted successfully!")
print(f"Version {new_version} generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("\nVersion info saved to version.json")
print("The version number has been updated in the footer copyright line.")
print("\nForm Configuration:")
print("- Contact form uses Cloudflare Pages Functions (/api/contact)")
print("- No external services required - runs on Cloudflare's edge network")
print("\nNext steps:")
print("1. Commit and push to deploy to Cloudflare Pages")
print("2. Version will be visible at the bottom of the page")