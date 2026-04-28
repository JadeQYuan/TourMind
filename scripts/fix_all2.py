import sys

def fix_file(fname, fixes):
    with open(fname, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()
    total_ok = 0
    for old, new in fixes:
        if old in text:
            cnt = text.count(old)
            text = text.replace(old, new)
            total_ok += cnt
            sys.stdout.buffer.write(('  OK x' + str(cnt) + ': ' + repr(old[:50]) + '\n').encode('utf-8'))
        else:
            sys.stdout.buffer.write(('  MISS: ' + repr(old[:50]) + '\n').encode('utf-8'))
    with open(fname, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    remaining = text.count('\ufffd')
    sys.stdout.buffer.write(('  Remaining FFFD: ' + str(remaining) + '\n\n').encode('utf-8'))

F = '\ufffd?'  # The actual pattern: FFFD followed by literal ?

# ProductListView.vue
fix_file(r'frontend\src\views\product\ProductListView.vue', [
    ('天行程模' + F + ')', '天行程模板)'),
    ("'目的" + F + "'", "'目的地'"),
    ("'状" + F + "'", "'状态'"),
    ('筛' + F + '</a-button>', '筛选</a-button>'),
    ('record.days }}' + F + '</div>', 'record.days }}天</div>'),
    (F + '${t}', '共 ${t}'),
    ('label="状' + F + '>', 'label="状态">'),
    ('label="目的' + F + ' required>', 'label="目的地" required>'),
])
sys.stdout.buffer.write(b'=== ProductListView done ===\n\n')

# OrderListView - check its pattern too
fname_o = r'frontend\src\views\order\OrderListView.vue'
with open(fname_o, 'rb') as f:
    data = f.read()
i = 0
count = 0
while i < len(data) - 2:
    if data[i:i+3] == b'\xef\xbf\xbd':
        next_bytes = data[i+3:i+4]
        ctx_bytes = data[max(0,i-20):i+8]
        ctx_str = ctx_bytes.decode('utf-8', errors='replace')
        sys.stdout.buffer.write(('O pos ' + str(i) + ' next=' + next_bytes.hex() + ' ctx=' + repr(ctx_str) + '\n').encode('utf-8'))
        count += 1
        if count >= 5:
            break
        i += 3
    else:
        i += 1
