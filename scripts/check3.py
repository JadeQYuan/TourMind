import sys

fname = r'frontend\src\views\product\ProductListView.vue'
with open(fname, 'rb') as f:
    data = f.read()

# Find EF BF BD pattern (U+FFFD in UTF-8)
i = 0
count = 0
while i < len(data) - 2:
    if data[i:i+3] == b'\xef\xbf\xbd':
        ctx_bytes = data[max(0,i-20):i+10]
        ctx_str = ctx_bytes.decode('utf-8', errors='replace')
        next_bytes = data[i+3:i+6]
        sys.stdout.buffer.write(f'FFFD at byte {i}: next={next_bytes.hex()} ctx={repr(ctx_str)}\n'.encode('utf-8'))
        count += 1
        i += 3
    else:
        i += 1

sys.stdout.buffer.write(f'Total FFFD: {count}\n'.encode())
