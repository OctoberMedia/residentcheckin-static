#!/usr/bin/env python3
"""
Update the contact form to use Cloudflare Pages Functions
"""

import re

def update_form_to_cloudflare():
    with open('public/index.html', 'r') as f:
        content = f.read()
    
    # Find the form and replace action and add JavaScript handler
    # Replace the form action
    content = content.replace(
        'action="https://formspree.io/f/YOUR_FORM_ID"',
        'action="/api/contact" data-contact-form'
    )
    
    # Add JavaScript for form handling at the end of body
    form_handler_script = '''
<!-- Contact Form Handler -->
<script>
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('[data-contact-form]');
    const submitButton = form.querySelector('button[type="submit"]');
    const originalButtonText = submitButton.textContent;
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Disable submit button
        submitButton.disabled = true;
        submitButton.textContent = 'Sending...';
        
        try {
            const formData = new FormData(form);
            const response = await fetch('/api/contact', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                // Success - show thank you message
                form.innerHTML = `
                    <div class="text-center py-8">
                        <div class="mb-4">
                            <svg class="w-16 h-16 text-green-500 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                        </div>
                        <h3 class="text-2xl font-semibold text-gray-900 mb-2">Thank You!</h3>
                        <p class="text-gray-600">${result.message || "We'll be in touch soon."}</p>
                    </div>
                `;
            } else {
                // Error - show message
                alert(result.message || 'There was an error submitting the form. Please try again.');
                submitButton.disabled = false;
                submitButton.textContent = originalButtonText;
            }
        } catch (error) {
            console.error('Form submission error:', error);
            alert('There was an error submitting the form. Please try again later.');
            submitButton.disabled = false;
            submitButton.textContent = originalButtonText;
        }
    });
});
</script>
'''
    
    # Insert the script before closing body tag
    content = content.replace('</body>', form_handler_script + '\n</body>')
    
    with open('public/index.html', 'w') as f:
        f.write(content)
    
    print("✅ Form updated to use Cloudflare Pages Functions!")
    print("\nThe form will now submit to /api/contact which is handled by")
    print("the serverless function in functions/api/contact.js")

if __name__ == "__main__":
    update_form_to_cloudflare()