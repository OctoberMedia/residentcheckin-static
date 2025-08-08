# ResidentCheckin.co Static Homepage for Cloudflare Pages

This is a standalone version of the ResidentCheckin.co homepage, optimized for deployment on Cloudflare Pages.

## Setup Instructions

1. **Set up Form Handling with n8n**
   - Create a webhook in your n8n instance
   - Import the workflow template from `n8n-workflow-template.json`
   - Configure your Google Sheets, Slack, and Pipedrive credentials
   - Copy the webhook URL from n8n
   - In Cloudflare Pages dashboard, add environment variable:
     - `CUSTOM_WEBHOOK_URL` = `your-n8n-webhook-url`

2. **Update Links**
   - The following links currently point to the Rails application and should be updated to your production URLs:
     - `/facility/onboarding` → Your onboarding URL
     - `/users/sign_in` → Your login URL
     - `/faq` → Your FAQ page URL

3. **Deploy to Cloudflare Pages**
   - Connect your GitHub repository to Cloudflare Pages
   - Set the build command to: (leave empty)
   - Set the build output directory to: `public`
   - Deploy!

## File Structure

```
cloudflare-pages/
├── public/
│   ├── index.html              # Main homepage
│   ├── iamfine-logo-v2.png     # Logo image
│   ├── Facility-screenshot.png  # Dashboard screenshot
│   └── facility-allclear.png   # All clear status image
└── README.md                   # This file
```

## Features

- Fully static HTML page with embedded Tailwind CSS
- Contact form handled by Formspree
- Responsive design optimized for all devices
- Fast loading with CDN-hosted Tailwind CSS
- SEO-optimized with meta tags

## Customization

- To update content, edit `public/index.html`
- Tailwind CSS classes can be modified directly in the HTML
- Custom CSS is included in the `<style>` tag in the document head

## Performance

This static version loads significantly faster than the Rails-rendered version:
- No server-side rendering
- CDN-hosted assets
- Minimal JavaScript
- Optimized for Cloudflare's edge network