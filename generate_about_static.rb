#!/usr/bin/env ruby

require 'erb'

# Read the About template from Rails app
about_template = File.read('../app/views/pages/about.html.erb')

# Read the footer partial
footer_template = File.read('../app/views/shared/_footer_faq.html.erb')

# Create a simple binding context for ERB
class TemplateContext
  def content_for(key, value = nil)
    # For static generation, we'll handle this differently
    @content ||= {}
    @content[key] = value if value
    @content[key]
  end
  
  def render(partial)
    case partial
    when 'shared/footer_faq'
      footer_content
    else
      ""
    end
  end
  
  def footer_content
    File.read('../app/views/shared/_footer_faq.html.erb')
  end
  
  def get_binding
    binding
  end
end

# Process the about template
context = TemplateContext.new
about_erb = ERB.new(about_template)
about_content = about_erb.result(context.get_binding)

# Process the footer
footer_erb = ERB.new(footer_template)
footer_content = footer_erb.result(context.get_binding)

# Replace the render call with actual footer content
about_content = about_content.gsub('<%= render \'shared/footer_faq\' %>', footer_content)

# Create the full HTML document
html_output = <<-HTML
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>About ResidentCheckin.co | Built on IamFine's Proven Platform</title>
  <meta name="description" content="ResidentCheckin.co is powered by IamFine's proven wellness check platform, serving assisted living facilities with automated resident monitoring since 2012.">
  <meta name="keywords" content="about residentcheckin, iamfine platform, assisted living wellness checks, senior care technology">
  
  <!-- Tailwind CSS -->
  <script src="https://cdn.tailwindcss.com"></script>
  
  <!-- Alpine.js for interactivity -->
  <script defer src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js"></script>
</head>
<body>
  #{about_content}
</body>
</html>
HTML

# Write the output file
File.write('about.html', html_output)
puts "About page generated successfully!"