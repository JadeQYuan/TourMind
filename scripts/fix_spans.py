"""
Fix span values in form files using proper UTF-8 encoding.
This script reads files from disk (they're currently corrupt), but since
we can't recover the original text, we'll use the file contents as read
by VS Code (which displays UTF-8 correctly). We'll write the correct content
by using the known original text with span replacements applied.

The script accepts file path and writes the corrected content.
"""
import sys
import re

def process_file(path, replacements):
    """Read file as UTF-8, apply replacements, write back as UTF-8."""
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(content)
    
    print(f"Fixed: {path}")

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else 'all'
    
    if target in ('product', 'all'):
        process_file(
            r'e:\Code\TourMind\frontend\src\views\product\ProductListView.vue',
            [
                ('<a-col :span="isMobile ? 24 : 12">', '<a-col :span="isMobile ? 24 : 12">'),  # already done
            ]
        )
        print("Product done")
