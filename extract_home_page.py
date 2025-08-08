#!/usr/bin/env python3
"""
Extract and convert the Rails home page to static HTML for Cloudflare Pages
"""

import re
import os

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
    # Create a static HTML form
    static_form = '''
            <form action="https://formspree.io/f/YOUR_FORM_ID" method="POST" class="space-y-4" id="contact-form">
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

<!-- Analytics (add your tracking code here) -->

</body>
</html>'''

# Write the output file
with open('public/index.html', 'w') as f:
    f.write(html_document)

print("Home page extracted and converted successfully!")
print("\nNext steps:")
print("1. Replace 'YOUR_FORM_ID' with your Formspree form ID")
print("2. Copy image assets to the public directory:")
print("   - /iamfine-logo-v2.png")
print("   - /Facility-screenshot.png")
print("   - /facility-allclear.png")
print("   - /favicon.ico")
print("3. Update internal links to point to the Rails app")
print("4. Deploy to Cloudflare Pages")