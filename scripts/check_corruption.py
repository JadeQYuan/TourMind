import sys
import re

fname = r'e:\Code\TourMind\frontend\src\views\product\ProductListView.vue'
with open(fname, 'r', encoding='utf-8', errors='replace') as f:
    text = f.read()

# Find replacement chars (U+FFFD = 0xFFFD) 
matches = [(m.start(), text[max(0,m.start()-30):m.start()+30]) for m in re.finditer('\ufffd', text)]
print(f"Total U+FFFD replacement chars in ProductListView: {len(matches)}")
for pos, ctx in matches[:10]:
    # Print as repr to avoid encoding issues
    sys.stdout.buffer.write(f"pos {pos}: {repr(ctx)}\n".encode('utf-8'))
