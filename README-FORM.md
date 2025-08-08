# Contact Form Setup with Cloudflare Pages Functions

This implementation uses Cloudflare Pages Functions for FREE form handling - no external services needed!

## How It Works

1. **Form Submission**: When a user submits the contact form, it's sent to `/api/contact`
2. **Serverless Function**: The Cloudflare Pages Function in `functions/api/contact.js` processes the form
3. **Multiple Notification Options**: You can configure it to send notifications via:
   - Discord webhook (recommended - easiest to set up)
   - Custom webhook to your Rails app
   - Email (requires additional setup)
   - Cloudflare KV storage

## Setup Instructions

### Option 1: Discord Notifications (Recommended)

1. Create a Discord webhook:
   - Go to your Discord server
   - Server Settings → Integrations → Webhooks
   - Create New Webhook
   - Copy the webhook URL

2. In Cloudflare Pages dashboard:
   - Go to Settings → Environment variables
   - Add: `DISCORD_WEBHOOK_URL` = `your-discord-webhook-url`

### Option 2: Send to n8n Webhook (Recommended for automation)

1. Create a webhook in n8n:
   - Create a new workflow in n8n
   - Add a Webhook node
   - Set to "POST" method
   - Copy the webhook URL (e.g., `https://your-n8n.domain/webhook/contact-form`)

2. In n8n, connect the webhook to:
   - Google Sheets node (to log submissions)
   - Slack node (for notifications)
   - Pipedrive node (to create deals/contacts)

3. In Cloudflare Pages dashboard:
   - Go to Settings → Environment variables
   - Add: `CUSTOM_WEBHOOK_URL` = `your-n8n-webhook-url`

This gives you a powerful automation flow:
- Form → Cloudflare Function → n8n → Google Sheets + Slack + Pipedrive

### Option 3: Store in Cloudflare KV

1. Create a KV namespace in Cloudflare dashboard
2. Bind it to your Pages project:
   - Settings → Functions → KV namespace bindings
   - Variable name: `CONTACT_FORMS`
   - KV namespace: Select your namespace

## Features

- ✅ **FREE** - No external services required
- ✅ **Spam Protection** - Honeypot field included
- ✅ **Validation** - Server-side validation for all fields
- ✅ **Multiple Notifications** - Send to multiple destinations
- ✅ **User Feedback** - Shows success message after submission
- ✅ **Error Handling** - Graceful error messages

## Testing Locally

Unfortunately, Cloudflare Pages Functions don't work with simple HTTP servers. To test locally:

1. Install Wrangler:
   ```bash
   npm install -g wrangler
   ```

2. Run the development server:
   ```bash
   wrangler pages dev public --port 3456
   ```

3. The form will now work locally at http://localhost:3456

## Deployment

When you deploy to Cloudflare Pages, the function will automatically be deployed and available at `/api/contact`.

## Customization

To modify the form handler, edit `functions/api/contact.js`:
- Add new fields
- Change validation rules
- Add new notification methods
- Customize response messages