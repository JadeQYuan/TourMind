import re

fixes_product = [
    ("30 天行程模\ufffd)", "30 天行程模板)"),
    ("请输入产品名\ufffd", "请输入产品名称"),
    ("已上\ufffd", "已上架"),
    ("已下\ufffd", "已下架"),
    ("目的\ufffd,", "目的地,"),
    ("参考价(\ufffd", "参考价(元"),
    ("'状\ufffd,", "'状态,"),
    ("桌面端筛选表\ufffd", "桌面端筛选表单"),
    ('label="状\ufffd>', 'label="状态">'),
    ("移动端筛选按\ufffd", "移动端筛选按钮"),
    ("筛\ufffd</a-button>", "筛选</a-button>"),
    ("移动端卡\ufffd", "移动端卡片"),
    ("天\ufffd</div>", "天</div>"),
    ("桌面端表\ufffd", "桌面端表格"),
    ("`共 ${t} 条\ufffd", "`共 ${t} 条`"),
    ("移动端筛选抽\ufffd", "移动端筛选抽屉"),
    ('title="筛\ufffd', 'title="筛选"'),
    ('label="状\ufffd>\n          <a-select v-model:value="mobileFilter', 'label="状态">\n          <a-select v-model:value="mobileFilter'),
    ("目的\ufffd\" required>", "目的地\" required>"),
    ("住宿区域（选填\ufffd", "住宿区域（选填）"),
    ("备注（选填\ufffd", "备注（选填）"),
    ("不含的费用项\ufffd", "不含的费用项目"),
    ("包含的费用项\ufffd", "包含的费用项目"),
    ("退改政策说\ufffd", "退改政策说明"),
    ("第{{ day.seq }}\ufffd", "第{{ day.seq }}天"),
    ("+ 添加一\ufffd", "+ 添加一天"),
    ('目的\ufffd" required>', '目的地" required>'),
]

fixes_order = [
    ("待下\ufffd,", "待下架,"),
    ("待付\ufffd,", "待付款,"),
    ("已完\ufffd ", "已完成 "),
    ("手机\ufffd,", "手机号,"),
    ("供应\ufffd,", "供应商,"),
    ("价格(\ufffd", "价格(元"),
    ("'状\ufffd,", "'状态,"),
    ("关键\ufffd>", "关键词>"),
    ("手机\ufffd订单", "手机号订单"),
    ("订单\ufffd allow", "订单号 allow"),
    ("供应\ufffd>", "供应商>"),
    ('label="状\ufffd>', 'label="状态">'),
    ("移动端筛选按\ufffd", "移动端筛选按钮"),
    ("筛\ufffd  ", "筛选  "),
    ("片列\ufffd", "片列表"),
    ("桌面端表\ufffd", "桌面端表格"),
    ("`共 ${t} 条\ufffd", "`共 ${t} 条`"),
    ("移动端筛选抽\ufffd", "移动端筛选抽屉"),
    ('title="筛\ufffd\n', 'title="筛选"\n'),
    ("关键\ufffd>\n    <a-input", "关键词>\n    <a-input"),
    ("手机\ufffd订单", "手机号订单"),
    ("订单\ufffd allow", "订单号 allow"),
    ("供应\ufffd>\n    <a-input", "供应商>\n    <a-input"),
    ("供应\ufffd\" required>", "供应商\" required>"),
    ("手机\ufffd\" required>", "手机号\" required>"),
    ("客户姓\ufffd\" required>", "客户姓名\" required>"),
    ("供应\ufffd\" allow", "供应商\" allow"),
    ("销售价格(\ufffd元\ufffd\" required>", "销售价格(元)\" required>"),
    ("格(\ufffd元\ufffd\"", "格(元)\""),
    ("定金(\ufffd元\ufffd\"", "定金(元)\""),
    ("成本(\ufffd元\ufffd\"", "成本(元)\""),
    ("待下\ufffd, val", "待下架, val"),
    ("待付\ufffd, val", "待付款, val"),
    ("已完\ufffd, val", "已完成, val"),
]

fixes_itinerary = [
    ("继续\ufffd,\n", "继续），\n"),
    ("始日\ufffd)", "始日期)"),
    ("[，,\\\ufffd\\s\\n]", "[，,，\\s\\n]"),
    ("目的\ufffd\" required>", "目的地\" required>"),
    ("`第\ufffd${day", "`第 ${day"),
    ("天\ufffd", "天 "),
    ("区\ufffd\"", "区域\""),
    ("项\ufffd\"", "项等\""),
]

for fname, fixes in [
    (r"e:\Code\TourMind\frontend\src\views\product\ProductListView.vue", fixes_product),
    (r"e:\Code\TourMind\frontend\src\views\order\OrderListView.vue", fixes_order),
    (r"e:\Code\TourMind\frontend\src\views\itinerary\ItineraryFormView.vue", fixes_itinerary),
]:
    with open(fname, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()
    for old, new in fixes:
        count = text.count(old)
        if count > 0:
            text = text.replace(old, new)
            print(f"Fixed {count}x: {repr(old[:40])} -> {repr(new[:40])}")
        else:
            print(f"NOT FOUND: {repr(old[:50])}")
    with open(fname, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(f"Wrote: {fname}")
    print()
