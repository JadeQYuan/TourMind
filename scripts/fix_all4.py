import sys

def fix_file(fname, fixes):
    with open(fname, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()
    for old, new in fixes:
        if old in text:
            cnt = text.count(old)
            text = text.replace(old, new)
            sys.stdout.buffer.write(('  OK x' + str(cnt) + ': ' + repr(old[:60]) + '\n').encode('utf-8'))
        else:
            sys.stdout.buffer.write(('  MISS: ' + repr(old[:60]) + '\n').encode('utf-8'))
    with open(fname, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    remaining = text.count('\ufffd')
    sys.stdout.buffer.write(('  Remaining FFFD: ' + str(remaining) + '\n').encode('utf-8'))

# ProductListView - 2 remaining
# next=3f2c20 means the char after FFFD is ?, then comma
fix_file(r'frontend\src\views\product\ProductListView.vue', [
    # "{ title: '目的\ufffd?, dataIn" => "{ title: '目的地', dataIn"
    ("{ title: '目的\ufffd?,", "{ title: '目的地',"),
    ("{ title: '状\ufffd?,", "{ title: '状态',"),
])
sys.stdout.buffer.write(b'=== ProductListView ===\n\n')

# OrderListView - 10 remaining
fix_file(r'frontend\src\views\order\OrderListView.vue', [
    # STATUS_LABEL map - next=3f2c (`,`)
    ("'待下\ufffd?,", "'待下架',"),
    ("'待付\ufffd?,", "'待付款',"),
    ("'已完\ufffd?}", "'已完成'}"),
    # Columns - next=3f2c
    ("{ title: '手机\ufffd?,", "{ title: '手机号',"),
    ("{ title: '供应\ufffd?,", "{ title: '供应商',"),
    ("{ title: '状\ufffd?,", "{ title: '状态',"),
    # Error messages - next=3f29 `?)`
    ("'请选择供应\ufffd?);", "'请选择供应商');"),
    ("'请输入客户姓\ufffd?);", "'请输入客户姓名');"),
    ("'请输入价\ufffd?);", "'请输入价格');"),
    # Mobile filter button - next=3f20
    ("筛\ufffd?  ", "筛选  "),
])
sys.stdout.buffer.write(b'=== OrderListView ===\n\n')

# ItineraryFormView - 3 remaining
fix_file(r'frontend\src\views\itinerary\ItineraryFormView.vue', [
    # next=3f29 `?)`
    ("请选择开始日\ufffd?);", "请选择开始日期');"),
    # :header - next=3f24 `?$`  => 第
    # :header="`\ufffd?${day.seq} \ufffd?· ${day.date}`"
    (":header=\"`\ufffd?${day.seq} \ufffd?", ":header=\"`第 ${day.seq} 天 "),
])
sys.stdout.buffer.write(b'=== ItineraryFormView ===\n\n')
