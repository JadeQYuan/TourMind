import sys

fname = r'frontend\src\views\product\ProductListView.vue'
with open(fname, 'rb') as f:
    data = f.read()

i = 0
while i < len(data) - 2:
    if data[i:i+3] == b'\xef\xbf\xbd':
        next_bytes = data[i+3:i+6]
        ctx_bytes = data[max(0,i-25):i+10]
        ctx_str = ctx_bytes.decode('utf-8', errors='replace')
        sys.stdout.buffer.write(('pos ' + str(i) + ' next=' + next_bytes.hex() + ' ctx=' + repr(ctx_str) + '\n').encode('utf-8'))
        i += 3
    else:
        i += 1
