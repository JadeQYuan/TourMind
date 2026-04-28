import sys

def check_fffd(fname, label):
    with open(fname, 'rb') as f:
        data = f.read()
    sys.stdout.buffer.write(('=== ' + label + ' ===\n').encode())
    i = 0
    while i < len(data) - 2:
        if data[i:i+3] == b'\xef\xbf\xbd':
            next_bytes = data[i+3:i+6]
            ctx_bytes = data[max(0,i-25):i+12]
            ctx_str = ctx_bytes.decode('utf-8', errors='replace')
            sys.stdout.buffer.write(('  pos ' + str(i) + ' next=' + next_bytes.hex() + ' ctx=' + repr(ctx_str) + '\n').encode('utf-8'))
            i += 3
        else:
            i += 1
    sys.stdout.buffer.write(b'\n')

check_fffd(r'frontend\src\views\product\ProductListView.vue', 'ProductListView')
check_fffd(r'frontend\src\views\order\OrderListView.vue', 'OrderListView')
check_fffd(r'frontend\src\views\itinerary\ItineraryFormView.vue', 'ItineraryFormView')
