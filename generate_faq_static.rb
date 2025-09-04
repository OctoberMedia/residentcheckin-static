#!/usr/bin/env ruby
# Generate static FAQ page from Rails data

require 'erb'
require 'json'

# FAQ data structure
faqs = [
  {
    section: "Getting Started",
    questions: [
      {
        q: "How quickly can we get set up?",
        a: "Most facilities are up and running within 24-48 hours. Our onboarding process includes:<ul class='list-disc list-inside text-gray-600 mt-2 ml-4'><li>Phone number configuration and testing</li><li>Resident enrollment (can be done in batches)</li><li>Staff training on the dashboard</li><li>Security team notification setup</li><li>Test calls to ensure everything works</li></ul>"
      },
      {
        q: "What information do we need to provide?",
        a: "To get started, we need:<ul class='list-disc list-inside text-gray-600 mt-2 ml-4'><li>Facility contact information and preferred check-in time</li><li>Resident list with names and phone numbers</li><li>Security team contact information for alerts</li></ul>"
      },
      {
        q: "Is there a minimum contract length?",
        a: "No long-term contracts required. We have a 90 day cancellation clause. You can cancel at any time with 90 days notice."
      }
    ]
  },
  {
    section: "How It Works",
    questions: [
      {
        q: "What types of phones work with the system?",
        a: "Our system works with ANY phone type - landlines, basic cell phones, flip phones, smartphones. No smartphone or internet required. Residents just need to be able to answer calls and press \"1\" on their keypad."
      },
      {
        q: "What happens if a resident doesn't answer the automated call?",
        a: "We call at the check-in time, then retry every 15 minutes for an hour. If the resident still hasn't responded after an hour, the security team is automatically notified to check on them."
      },
      {
        q: "Can residents check in early?",
        a: "Yes! Residents can check in early by:<ul class='list-disc list-inside text-gray-600 mt-2 ml-4'><li>Calling our toll-free number</li><li>Sending a text message</li><li>Using our custom smartphone Big Button App</li><li>Letting the security team know they're okay (staff can check them in manually)</li></ul>"
      },
      {
        q: "What if a resident forgets to check in but is fine?",
        a: "Staff can manually check in residents directly from the dashboard when they see them in person. This immediately stops any automated calls and updates the system."
      },
      {
        q: "How do vacations and time away work?",
        a: "Our vacation management system makes it easy:<ul class='list-disc list-inside text-gray-600 mt-2 ml-4'><li>Schedule vacations, family visits, or medical stays in advance</li><li>Check-in calls automatically pause during vacation periods</li><li>Calls resume automatically on the return date</li><li>Dashboard shows who's on vacation and when they return</li></ul>"
      }
    ]
  },
  {
    section: "Technical & Security",
    questions: [
      {
        q: "What happens if your system goes down?",
        a: "We have multiple safeguards:<ul class='list-disc list-inside text-gray-600 mt-2 ml-4'><li>99.9% uptime guarantee with redundant systems</li><li>Automatic failover to backup servers</li><li>24/7 monitoring and immediate alert response</li><li>Emergency contact procedures for extended outages</li></ul>"
      },
      {
        q: "Do you integrate with our existing systems?",
        a: "We can provide daily reports via email or secure file transfer. For deeper integrations with property management systems, contact us to discuss custom solutions."
      }
    ]
  },
  {
    section: "Billing & Pricing",
    questions: [
      {
        q: "Are there any additional fees?",
        a: "There is a one-time setup fee of $500. No cancellation fees, no per-call charges. The monthly fee includes everything: unlimited automated calls, text messaging, dashboard access, and support."
      },
      {
        q: "What payment methods do you accept?",
        a: "We accept all major credit cards and ACH bank transfers. Billing is monthly in advance with automatic payment processing."
      }
    ]
  },
  {
    section: "Support & Training",
    questions: [
      {
        q: "What kind of support do you provide?",
        a: "Comprehensive support including:<ul class='list-disc list-inside text-gray-600 mt-2 ml-4'><li>Email and phone support during business hours</li><li>Emergency support for system issues 24/7</li><li>Initial staff training and onboarding</li><li>Ongoing training for new staff members</li><li>Regular check-ins to ensure optimal usage</li></ul>"
      },
      {
        q: "How much training does our staff need?",
        a: "Minimal training required. Most staff learn the dashboard in 15-20 minutes. We provide live training sessions, video tutorials, and written guides. The system is designed to be intuitive for staff of all technical skill levels."
      },
      {
        q: "Can you help us explain the system to residents?",
        a: "Yes! We provide resident information sheets, talking points for staff, and can participate in resident meetings to explain the system and answer questions."
      }
    ]
  },
  {
    section: "Compliance & Regulations",
    questions: [
      {
        q: "Does this help with state regulations and funding compliance?",
        a: "Yes. Many housing authorities and facilities use our system to demonstrate systematic wellness monitoring for compliance reporting. We provide detailed logs and reports that document your wellness check procedures."
      }
    ]
  }
]

# Change to the cloudflare-pages directory to ensure paths work correctly
Dir.chdir(File.dirname(__FILE__))

# Generate the HTML
template = ERB.new(File.read('faq_template.erb'))
html = template.result(binding)

# Save the file
File.write('public/faq.html', html)
puts "FAQ page generated successfully!"