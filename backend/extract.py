import re

# Example line-based text
lines_text = """
Policy No.          : 12334
Insured             : abc
Address             : 123 Main Street
"""

# Convert to dict for easier access
policy_data = {}
for line in lines_text.split('\n'):
    match = re.match(r'(.+?)\s*:\s*(.+)', line)
    if match:
        key = match.group(1).strip()
        value = match.group(2).strip()
        policy_data[key] = value

print(policy_data)
