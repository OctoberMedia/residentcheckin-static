# Complete Cloudflare Pages Deployment Guide

## Prerequisites
- GitHub account
- Cloudflare account (free tier is fine)
- n8n instance running (for form handling)

## Step 1: Prepare Your Repository

1. **Create a new GitHub repository**
   ```bash
   # Go to github.com and create a new repository called "residentcheckin-static"
   # Then locally:
   cd /Users/pdh/RubymineProjects/fft/cloudflare-pages
   git init
   git add .
   git commit -m "Initial commit - static homepage"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/residentcheckin-static.git
   git push -u origin main
   ```

## Step 2: Set Up n8n Webhook

1. **Open your n8n instance**
2. **Create a new workflow**
3. **Import the template**:
   - Click the menu (three dots) → Import from File
   - Select `n8n-workflow-template.json`
4. **Configure credentials**:
   - Google Sheets: Click on Google Sheets node → Credentials → Create New
   - Slack: Click on Slack node → Credentials → Create New  
   - Pipedrive: Click on Pipedrive nodes → Credentials → Create New
5. **Update settings**:
   - In Google Sheets node: Replace `YOUR_GOOGLE_SHEET_ID` with your actual sheet ID
   - In Slack node: Change `#sales` to your preferred channel
6. **Activate the workflow**:
   - Toggle the Active switch at the top
   - Click on the Webhook node
   - Copy the Production URL (it will look like: `https://your-n8n.domain/webhook/abc123`)

## Step 3: Connect to Cloudflare Pages

1. **Log in to Cloudflare Dashboard**
2. **Go to Pages** (in the left sidebar)
3. **Create a project**:
   - Click "Create a project"
   - Select "Connect to Git"
   - Choose GitHub
   - Authorize Cloudflare to access your GitHub
   - Select your `residentcheckin-static` repository

4. **Configure build settings**:
   - **Framework preset**: None
   - **Build command**: (leave empty)
   - **Build output directory**: `public`
   - **Root directory**: (leave empty)

5. **Add environment variables**:
   - Click "Environment variables"
   - Add variable:
     - **Variable name**: `CUSTOM_WEBHOOK_URL`
     - **Value**: Your n8n webhook URL from Step 2
   - Click "Save and Deploy"

## Step 4: Wait for Deployment

1. Cloudflare will now build and deploy your site
2. This usually takes 1-2 minutes
3. You'll get a URL like: `residentcheckin-static.pages.dev`

## Step 5: Configure Custom Domain (Optional)

1. In your Cloudflare Pages project, go to "Custom domains"
2. Click "Set up a custom domain"
3. Enter your domain (e.g., `residentcheckin.co`)
4. Follow the DNS configuration instructions

## Step 6: Test Your Form

1. **Visit your deployed site**
2. **Fill out the contact form**
3. **Submit it**
4. **Check**:
   - You should see a success message on the website
   - Check your Google Sheet for the new row
   - Check Slack for the notification
   - Check Pipedrive for the new contact/deal

## Troubleshooting

### Form not working?

1. **Check Cloudflare Pages Functions logs**:
   - In Cloudflare dashboard → Your Pages project → Functions → Real-time logs
   - Submit the form and watch for errors

2. **Check n8n execution**:
   - In n8n → Executions
   - Look for failed executions
   - Click to see error details

3. **Common issues**:
   - Wrong webhook URL in environment variable
   - n8n workflow not activated
   - Google Sheets permissions not set correctly
   - Incorrect credentials in n8n

### Need to update the webhook URL?

1. Go to Cloudflare Pages → Settings → Environment variables
2. Edit `CUSTOM_WEBHOOK_URL`
3. Trigger a new deployment: Settings → Deployments → Retry deployment

---

# Updating from Rails App Changes

When you make changes to the home page in your Rails app, here's how to sync them to Cloudflare Pages:

## Method 1: Manual Update (Quick Changes)

1. **Make your changes in Rails**
2. **Extract the updated content**:
   ```bash
   cd /Users/pdh/RubymineProjects/fft/cloudflare-pages
   python3 extract_home_page.py
   python3 update_form_handler.py
   ```
3. **Commit and push**:
   ```bash
   git add .
   git commit -m "Update from Rails app"
   git push
   ```
4. Cloudflare Pages will automatically redeploy

## Method 2: Automated Sync Script

1. **Create sync script** (`sync_from_rails.sh`):
   ```bash
   #!/bin/bash
   echo "Syncing from Rails app..."
   
   # Extract latest home page
   python3 extract_home_page.py
   python3 update_form_handler.py
   
   # Copy any new images
   cp ../public/iamfine-logo-v2.png public/ 2>/dev/null
   cp ../public/Facility-screenshot.png public/ 2>/dev/null
   cp ../public/facility-allclear.png public/ 2>/dev/null
   
   # Commit and push if there are changes
   if [[ $(git status --porcelain) ]]; then
     git add .
     git commit -m "Auto-sync from Rails app - $(date)"
     git push
     echo "✅ Changes pushed to GitHub"
   else
     echo "✅ No changes detected"
   fi
   ```

2. **Make it executable**:
   ```bash
   chmod +x sync_from_rails.sh
   ```

3. **Run after Rails changes**:
   ```bash
   ./sync_from_rails.sh
   ```

## Best Practices

1. **Test locally first**:
   ```bash
   npm run serve  # View at http://localhost:3456
   ```

2. **Use preview deployments**:
   - Push to a branch instead of main
   - Cloudflare creates a preview URL
   - Test there before merging to main

3. **Monitor after deployment**:
   - Check Functions logs
   - Test the form
   - Verify all images load

## Rollback if Needed

1. Go to Cloudflare Pages → Deployments
2. Find a previous working deployment
3. Click "Rollback to this deployment"