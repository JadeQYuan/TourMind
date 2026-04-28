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

F = '\ufffd?'

# Fix remaining 4 in ProductListView
fix_file(r'frontend\src\views\product\ProductListView.vue', [
    # FFFD followed by , (not space)
    ("{ title: '目的" + '\ufffd' + "?', data", "{ title: '目的地', data"),
    ("{ title: '状" + '\ufffd' + "?', data", "{ title: '状态', data"),
    ('筛' + '\ufffd' + '?/a-but', '筛选</a-but'),
    ('record.days }}' + '\ufffd' + '?/div>', 'record.days }}天</div>'),
])

sys.stdout.buffer.write(b'\n=== ProductListView ===\n')

# All OrderListView
fix_file(r'frontend\src\views\order\OrderListView.vue', [
    ("'待下" + F + "'", "'待下架'"),
    ("'待付" + F + "'", "'待付款'"),
    ("'已完" + F + "'", "'已完成'"),
    ("{ label: '待下" + F, "{ label: '待下架'"),
    ("{ label: '待付" + F, "{ label: '待付款'"),
    ("{ label: '已完" + F, "{ label: '已完成'"),
    ("'手机" + F + "'", "'手机号'"),
    ("'供应" + F + "'", "'供应商'"),
    ("'状" + F + "'", "'状态'"),
    ("'请选择供应" + F + "'", "'请选择供应商'"),
    ("'请输入客户姓" + F + "'", "'请输入客户姓名'"),
    ("'请输入价" + F + "'", "'请输入价格'"),
    ('label="关键' + F + '>', 'label="关键词">'),
    ('placeholder="客户姓名/手机' + F + '订单' + F, 'placeholder="客户姓名/手机号/订单号'),
    ('筛' + F + '\n', '筛选\n'),
    (F + '${t}', '共 ${t}'),
    ('title="筛' + F + '"', 'title="筛选"'),
    ('label="供应' + F + '>', 'label="供应商">'),
    ('label="状' + F + '>', 'label="状态">'),
    ('label="手机' + F + ' required>', 'label="手机号" required>'),
    ('label="供应' + F + ' required>', 'label="供应商" required>'),
    ('placeholder="请选择供应' + F + ' allow-clear', 'placeholder="请选择供应商" allow-clear'),
    ('label="销售价' + F + F + '" required>', 'label="销售价格(元)" required>'),
    ('label="定金(' + F + '">', 'label="定金(元)">'),
    ('label="成本(' + F + '">', 'label="成本(元)">'),
    ('placeholder="请输入客户姓' + F + ' />', 'placeholder="请输入客户姓名" />'),
])
sys.stdout.buffer.write(b'\n=== OrderListView ===\n')

# ItineraryFormView
fix_file(r'frontend\src\views\itinerary\ItineraryFormView.vue', [
    ('是否继续' + F + ',', '是否继续），'),
    ("请选择开始日" + F + "'", "请选择开始日期'"),
    ('.split(/[' + F + '\\s\\n]+/)', '.split(/[，,，\\s\\n]+/)'),
    ('label="目的' + F + ' required>', 'label="目的地" required>'),
    (':header="`' + F + '${day.seq} ' + F + ' · ${day.date}`"', ':header="`第 ${day.seq} 天 · ${day.date}`"'),
    ('placeholder="当晚住宿城市或区' + F + ' />', 'placeholder="当晚住宿城市或区域" />'),
    ('placeholder="注意事项' + F + ' />', 'placeholder="注意事项等" />'),
])
sys.stdout.buffer.write(b'\n=== ItineraryFormView ===\n')
