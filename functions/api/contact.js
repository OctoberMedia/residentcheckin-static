/**
 * Cloudflare Pages Function to handle contact form submissions
 * This runs on Cloudflare's edge network - no external services needed
 */

export async function onRequestPost(context) {
  const { request, env } = context;

  try {
    // Parse form data
    const formData = await request.formData();
    
    // Extract form fields
    const data = {
      topic: formData.get('topic'),
      other_topic: formData.get('other_topic'),
      name: formData.get('name'),
      email: formData.get('email'),
      facility_name: formData.get('facility_name'),
      resident_count: formData.get('resident_count'),
      phone: formData.get('phone'),
      current_solution: formData.get('current_solution'),
      contact_preference: formData.get('contact_preference'),
      timestamp: new Date().toISOString(),
      ip: request.headers.get('CF-Connecting-IP'),
      country: request.headers.get('CF-IPCountry')
    };

    // Check honeypot field for bot protection
    const honeypot = formData.get('_gotcha');
    if (honeypot) {
      return new Response('Form submission detected as spam', { status: 400 });
    }

    // Validate required fields
    if (!data.email || !data.phone || !data.topic) {
      return new Response('Missing required fields', { status: 400 });
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(data.email)) {
      return new Response('Invalid email address', { status: 400 });
    }

    // Format the data for sending
    const emailBody = formatEmailBody(data);
    const discordMessage = formatDiscordMessage(data);

    // Send notifications in parallel
    const notifications = [];

    // 1. Send email notification (if configured)
    if (env.SEND_EMAIL_TO) {
      notifications.push(sendEmail(env, data, emailBody));
    }

    // 2. Send to Discord webhook (if configured)
    if (env.DISCORD_WEBHOOK_URL) {
      notifications.push(sendDiscordNotification(env.DISCORD_WEBHOOK_URL, discordMessage));
    }

    // 3. Send to custom webhook (if configured)
    if (env.CUSTOM_WEBHOOK_URL) {
      notifications.push(sendCustomWebhook(env.CUSTOM_WEBHOOK_URL, data));
    }

    // 4. Store in KV storage (if configured)
    if (env.CONTACT_FORMS) {
      notifications.push(storeInKV(env.CONTACT_FORMS, data));
    }

    // Wait for all notifications to complete
    await Promise.all(notifications);

    // Return success response
    return new Response(JSON.stringify({
      success: true,
      message: 'Thank you for your interest! We\'ll be in touch soon.'
    }), {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      }
    });

  } catch (error) {
    console.error('Form submission error:', error);
    return new Response(JSON.stringify({
      success: false,
      message: 'An error occurred. Please try again later.'
    }), {
      status: 500,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      }
    });
  }
}

// Handle preflight requests
export async function onRequestOptions() {
  return new Response(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Access-Control-Max-Age': '86400'
    }
  });
}

// Format email body
function formatEmailBody(data) {
  return `
New Contact Form Submission from ResidentCheckin.co

Topic: ${data.topic}
${data.other_topic ? `Other Topic: ${data.other_topic}` : ''}

Contact Information:
- Name: ${data.name || 'Not provided'}
- Email: ${data.email}
- Phone: ${data.phone}
- Facility: ${data.facility_name || 'Not provided'}
- Number of Residents: ${data.resident_count || 'Not provided'}

Current Solution: ${data.current_solution || 'Not provided'}

Contact Preference:
${data.contact_preference || 'Not specified'}

Submission Details:
- Time: ${data.timestamp}
- IP: ${data.ip}
- Country: ${data.country}
`;
}

// Format Discord message
function formatDiscordMessage(data) {
  return {
    embeds: [{
      title: '📬 New Contact Form Submission',
      color: 0x5865F2,
      fields: [
        {
          name: 'Topic',
          value: data.topic + (data.other_topic ? ` - ${data.other_topic}` : ''),
          inline: false
        },
        {
          name: 'Name',
          value: data.name || 'Not provided',
          inline: true
        },
        {
          name: 'Email',
          value: data.email,
          inline: true
        },
        {
          name: 'Phone',
          value: data.phone,
          inline: true
        },
        {
          name: 'Facility',
          value: data.facility_name || 'Not provided',
          inline: true
        },
        {
          name: 'Residents',
          value: data.resident_count || 'Not provided',
          inline: true
        },
        {
          name: 'Current Solution',
          value: data.current_solution || 'Not provided',
          inline: false
        },
        {
          name: 'Contact Preference',
          value: data.contact_preference || 'Not specified',
          inline: false
        }
      ],
      footer: {
        text: `From ${data.country} • ${new Date(data.timestamp).toLocaleString()}`
      }
    }]
  };
}

// Send email using Cloudflare Email Workers (requires configuration)
async function sendEmail(env, data, body) {
  if (!env.SEND_EMAIL_TO) return;
  
  // This is a placeholder - you would implement actual email sending
  // using Cloudflare Email Workers or a service like SendGrid
  console.log('Email would be sent to:', env.SEND_EMAIL_TO);
}

// Send Discord notification
async function sendDiscordNotification(webhookUrl, message) {
  const response = await fetch(webhookUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(message)
  });
  
  if (!response.ok) {
    throw new Error(`Discord webhook failed: ${response.status}`);
  }
}

// Send to custom webhook
async function sendCustomWebhook(webhookUrl, data) {
  const response = await fetch(webhookUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  
  if (!response.ok) {
    throw new Error(`Custom webhook failed: ${response.status}`);
  }
}

// Store in Cloudflare KV
async function storeInKV(kvNamespace, data) {
  const key = `contact_${Date.now()}_${data.email}`;
  await kvNamespace.put(key, JSON.stringify(data), {
    expirationTtl: 60 * 60 * 24 * 90 // 90 days
  });
}