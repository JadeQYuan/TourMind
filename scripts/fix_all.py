import sys

def fix_file(fname, fixes):
    with open(fname, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()
    for old, new in fixes:
        if old in text:
            text = text.replace(old, new)
            sys.stdout.buffer.write(('  OK: ' + repr(old[:50]) + '\n').encode('utf-8'))
        else:
            sys.stdout.buffer.write(('  MISS: ' + repr(old[:50]) + '\n').encode('utf-8'))
    with open(fname, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)

FFFD = '\ufffd'

# ProductListView.vue
fix_file(r'frontend\src\views\product\ProductListView.vue', [
    ('天行程模' + FFFD + ')', '天行程模板)'),
    ("'目的" + FFFD + "'", "'目的地'"),
    ("'状" + FFFD + "'", "'状态'"),
    ('筛' + FFFD + '</a-button>', '筛选</a-button>'),
    ('record.days }}' + FFFD + '</div>', 'record.days }}天</div>'),
    (FFFD + '${t} 条`', '共 ${t} 条`'),
    ('label="状' + FFFD + '>', 'label="状态">'),
    ('label="目的' + FFFD + ' required>', 'label="目的地" required>'),
])
sys.stdout.buffer.write(b'=== ProductListView done ===\n\n')

# OrderListView.vue
fix_file(r'frontend\src\views\order\OrderListView.vue', [
    ("'待下" + FFFD + "'", "'待下架'"),
    ("'待付" + FFFD + "'", "'待付款'"),
    ("'已完" + FFFD + "'", "'已完成'"),
    ("{ label: '待下" + FFFD + "'", "{ label: '待下架'"),
    ("{ label: '待付" + FFFD + "'", "{ label: '待付款'"),
    ("{ label: '已完" + FFFD + "'", "{ label: '已完成'"),
    ("'手机" + FFFD + "'", "'手机号'"),
    ("'供应" + FFFD + "'", "'供应商'"),
    ("'状" + FFFD + "'", "'状态'"),
    ("'请选择供应" + FFFD + "'", "'请选择供应商'"),
    ("'请输入客户姓" + FFFD + "'", "'请输入客户姓名'"),
    ("'请输入价" + FFFD + "'", "'请输入价格'"),
    ('桌面端筛选表' + FFFD, '桌面端筛选表单'),
    ('label="关键' + FFFD + '>', 'label="关键词">'),
    ('placeholder="客户姓名/手机' + FFFD + '订单' + FFFD, 'placeholder="客户姓名/手机号/订单号'),
    ('筛' + FFFD + '\n        </a-button', '筛选\n        </a-button'),
    (FFFD + '${t} 条`', '共 ${t} 条`'),
    ('title="筛' + FFFD + '"', 'title="筛选"'),
    ('label="供应' + FFFD + '>', 'label="供应商">'),
    ('label="状' + FFFD + '>', 'label="状态">'),
    ('placeholder="客户姓名/手机' + FFFD + '订单' + FFFD + ' allow-clear />', 'placeholder="客户姓名/手机号/订单号" allow-clear />'),
    ('label="手机' + FFFD + ' required>', 'label="手机号" required>'),
    ('label="供应' + FFFD + ' required>', 'label="供应商" required>'),
    ('placeholder="请选择供应' + FFFD + ' allow-clear', 'placeholder="请选择供应商" allow-clear'),
    ('label="销售价' + FFFD + FFFD + '" required>', 'label="销售价格(元)" required>'),
    ('label="定金(' + FFFD + '">', 'label="定金(元)">'),
    ('label="成本(' + FFFD + '">', 'label="成本(元)">'),
    ('placeholder="请输入客户姓' + FFFD + ' />', 'placeholder="请输入客户姓名" />'),
])
sys.stdout.buffer.write(b'=== OrderListView done ===\n\n')

# ItineraryFormView.vue
fix_file(r'frontend\src\views\itinerary\ItineraryFormView.vue', [
    ('是否继续' + FFFD + ',', '是否继续），'),
    ('请选择开始日' + FFFD + "'", '请选择开始日期\''),
    ('.split(/[' + FFFD + '\\s\\n]+/)', '.split(/[，,，\\s\\n]+/)'),
    ('label="目的' + FFFD + ' required>', 'label="目的地" required>'),
    (':header="`' + FFFD + '${day.seq} ' + FFFD + ' · ${day.date}`"', ':header="`第 ${day.seq} 天 · ${day.date}`"'),
    ('placeholder="当晚住宿城市或区' + FFFD + ' />', 'placeholder="当晚住宿城市或区域" />'),
    ('placeholder="注意事项' + FFFD + ' />', 'placeholder="注意事项等" />'),
])
sys.stdout.buffer.write(b'=== ItineraryFormView done ===\n\n')

sys.stdout.buffer.write(b'All done!\n')
