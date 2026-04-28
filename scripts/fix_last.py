import sys
fname = r'frontend\src\views\order\OrderListView.vue'
with open(fname, 'r', encoding='utf-8', errors='replace') as f:
    text = f.read()
idx = text.find('\ufffd')
ctx = text[max(0,idx-30):idx+20]
sys.stdout.buffer.write(repr(ctx).encode('utf-8'))
sys.stdout.buffer.write(b'\n')
# Fix: '已完\ufffd? } => '已完成' }
old = '\u5df2\u5b8c\ufffd? }'
new = '\u5df2\u5b8c\u6210\' }'
if old in text:
    text = text.replace(old, new)
    sys.stdout.buffer.write(b'OK\n')
else:
    sys.stdout.buffer.write(b'MISS - trying without space\n')
    old2 = '\u5df2\u5b8c\ufffd?}'
    if old2 in text:
        text = text.replace(old2, '\u5df2\u5b8c\u6210\'}')
        sys.stdout.buffer.write(b'OK2\n')
    else:
        sys.stdout.buffer.write(b'Still MISS\n')
with open(fname, 'w', encoding='utf-8', newline='\n') as f:
    f.write(text)
sys.stdout.buffer.write(('Remaining: ' + str(text.count('\ufffd')) + '\n').encode())
