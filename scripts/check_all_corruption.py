import sys
import re

# Check all 3 files for U+FFFD replacement characters
files = [
    r'e:\Code\TourMind\frontend\src\views\product\ProductListView.vue',
    r'e:\Code\TourMind\frontend\src\views\order\OrderListView.vue',
    r'e:\Code\TourMind\frontend\src\views\itinerary\ItineraryFormView.vue',
]

for fname in files:
    with open(fname, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()
    
    matches = [(m.start(), text[max(0,m.start()-50):m.start()+50]) for m in re.finditer('\ufffd', text)]
    short = fname.split('\\')[-1]
    sys.stdout.buffer.write(f"\n=== {short}: {len(matches)} corrupted chars ===\n".encode('utf-8'))
    for pos, ctx in matches:
        sys.stdout.buffer.write(f"  pos {pos}: {repr(ctx)}\n".encode('utf-8'))
