#!/bin/bash
# Update the package repository and install httpd
yum update -y
yum install -y httpd

# Create a custom index.html with your message
cat << 'EOF' > /var/www/html/index.html
<html>
  <head>
    <title>Welcome</title>
  </head>
  <body>
    <h1>Wow - this was made with AWS CDK</h1>
  </body>
</html>
EOF

# Start httpd service and configure it to start on boot
systemctl start httpd
systemctl enable httpd