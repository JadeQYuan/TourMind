import sys

fname = r'frontend\src\views\product\ProductListView.vue'
with open(fname, 'rb') as f:
    data = f.read()

# Find first occurrence of '?' byte (0x3F) after some Chinese chars
# Chinese UTF-8 is E4-E9 range typically
for i in range(len(data)-1):
    if data[i] == 0x3F and data[i-1] >= 0x80:
        # Found a ? after a high byte - suspicious
        ctx = data[max(0,i-15):i+5]
        sys.stdout.buffer.write(f'pos {i}: bytes={ctx.hex()} | text attempt:\n'.encode())
        try:
            sys.stdout.buffer.write(ctx.decode('utf-8', errors='replace').encode('utf-8') + b'\n')
        except:
            pass
        if i > 3300:
            break
