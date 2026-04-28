import sys, re

# Find all instances where the pattern EFBFBD3F appears (FFFD followed by ?)
# This is the corruption signature

for fname in [
    r'e:\Code\TourMind\frontend\src\views\product\ProductListView.vue',
    r'e:\Code\TourMind\frontend\src\views\order\OrderListView.vue',
    r'e:\Code\TourMind\frontend\src\views\itinerary\ItineraryFormView.vue',
]:
    with open(fname, 'rb') as f:
        data = f.read()
    
    pattern = b'\xef\xbf\xbd?'  # FFFD + 0x3F
    
    positions = []
    i = 0
    while i < len(data):
        idx = data.find(pattern, i)
        if idx == -1:
            break
        positions.append(idx)
        i = idx + 1
    
    if positions:
        short = fname.split('\\')[-1]
        sys.stdout.buffer.write(f'{short}: {len(positions)} corruptions\n'.encode())
        for pos in positions:
            ctx = data[max(0,pos-30):pos+10]
            sys.stdout.buffer.write(f'  byte {pos}: {repr(ctx.decode("utf-8", "replace"))}\n'.encode('utf-8'))
    else:
        short = fname.split('\\')[-1]
        sys.stdout.buffer.write(f'{short}: CLEAN\n'.encode())
    
    sys.stdout.buffer.write(b'\n')
