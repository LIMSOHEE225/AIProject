import re

with open('d:/sohee/ARproject/frontend/minihompy.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    '<div class=\"news-item\" style=\"color:#999; justify-content:center; padding:10px;\">',
    '<div class=\"news-item\" style=\"color:#999; justify-content:center; padding:10px; font-size:16px;\">'
)

content = content.replace(
    '<div class=\"guest-msg\" style=\"color:#999; justify-content:center;\">',
    '<div class=\"guest-msg\" style=\"color:#999; justify-content:center; font-size:16px; padding: 10px;\">'
)

with open('d:/sohee/ARproject/frontend/minihompy.html', 'w', encoding='utf-8') as f:
    f.write(content)
