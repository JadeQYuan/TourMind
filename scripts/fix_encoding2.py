import sys

# Fix all U+FFFD corruption in 3 files
# Each fix is (corrupted_text, correct_text)

fixes_product = [
    # All occurrences use actual UTF-8 repr with \ufffd
    # The garbled bytes before \ufffd are GBK-encoded Chinese that was read as UTF-8
    # We fix by replacing the entire garbled+? sequence with correct Chinese

    # "行程模板)" - pos 3160: 澶╄绋嬫ā锟?) 
    ("澶╄绋嬫ā\ufffd)", "行程模板)"),
    # "目的地," - 鐩殑锟?
    ("鐩殑\ufffd", "目的地"),
    # "状态," - 鐘讹拷?
    ("鐘讹拷\ufffd", "状态"),
    # "筛选</a-button>" - 绛涳拷?/a-button>
    ("绛涳拷\ufffd", "筛选"),
    # "天</div>" - 锟?/div>
    # context: record.days }}锟?/div>
    ("record.days }}\ufffd</div>", "record.days }}天</div>"),
    # "共 ${t} 条`" - 锟?${t} 鏉
    ("锟?\ufffd${t} 鏉", "共 ${t} 条"),  # Note: 鏉 is corrupted "条"
    # Wait, checking context: `锟?${t} 鏉 }"  - 鏉 is GBK for 条
    # Let's handle it more carefully
]

# Since the files are a mix of valid UTF-8 parts (from original file) and
# corrupted GBK-as-UTF-8 parts (from the Set-Content rewrite),
# the best approach is to convert the garbled sequences back.

# GBK -> UTF-8 garbling: when a UTF-8 sequence is read as GBK on GB2312 system
# and written back, bytes get re-encoded. The specific pattern:
# Original UTF-8 bytes: E7 9B AE E7 9A 84 E5 9C B0 (目的地)
# Read as GBK strings (with errors): 鐩殑 + 0xB0 = 鐩殑锟? (since 0xB0 alone is invalid GBK -> replaced)
# 
# The actual fix we need: replace specific garbled sequences with correct Chinese.

# Let me look at what exact byte sequences we see in the garbled parts
# "鐩殑" in UTF-8 = E9 90 A9 E6 AE 91 - wait these are already re-encoded...
# This is getting complex. Let me just do string replacements on what
# the UTF-8 file shows (with replacement chars).

# Reading the corruption report, the patterns are clear. Let me fix them:

files_fixes = {
    r'e:\Code\TourMind\frontend\src\views\product\ProductListView.vue': [
        # GBK-encoded Chinese sequences that got corrupted
        # Each pair: (what we see with errors='replace', what it should be)
        
        # "行程模板" - 30 澶╄绋嬫ā锟?) -> 30 天行程模板)
        ("30 澶╄绋嬫ā\ufffd)", "30 天行程模板)"),
        
        # "目的地" (column title) - '鐩殑锟?
        ("'鐩殑\ufffd'", "'目的地'"),
        
        # "状态" (column title) - '鐘讹拷?  
        ("'鐘讹拷\ufffd'", "'状态'"),
        
        # "筛选</a-button>
        ("绛涳拷\ufffd</a-button>", "筛选</a-button>"),
        
        # "天</div> - record.days }}锟?/div>
        ("record.days }}\ufffd</div>", "record.days }}天</div>"),
        
        # "共 ${t} 条`" - 锟?${t} 鏉 }"
        ("锟?\ufffd${t} 鏉 }", "共 ${t} 条 }"),
        
        # label="状态"> (mobile filter drawer)  
        ('label="鐘讹拷\ufffd>', 'label="状态">'),
        
        # label="目的地" required> (form)
        ('label="鐩殑\ufffd', 'label="目的地"'),
    ],
    
    r'e:\Code\TourMind\frontend\src\views\order\OrderListView.vue': [
        # STATUS_LABEL
        ("寰呬笅\ufffd", "待下架"),
        ("寰呬粯\ufffd", "待付款"),
        ("宸插畬\ufffd", "已完成"),
        
        # Column titles
        ("'鎵嬫満\ufffd'", "'手机号'"),
        ("'渚涘簲\ufffd'", "'供应商'"),
        ("'鐘讹拷\ufffd'", "'状态'"),
        
        # Error messages
        ("'璇烽€夋嫨渚涘簲\ufffd'", "'请选择供应商'"),
        ("'璇疯緭鍏ュ鎴峰\ufffd'", "'请输入客户姓名'"),
        ("'璇疯緭鍏ヤ环\ufffd'", "'请输入价格'"),
        
        # Comments  
        ("妗岄潰绔瓫閫夎〃\ufffd", "桌面端筛选表单"),
        
        # Labels
        ('label="鍏抽敭\ufffd>', 'label="关键词">'),
        ('label="渚涘簲\ufffd>', 'label="供应商">'),
        ('label="鐘讹拷\ufffd>', 'label="状态">'),
        
        # Placeholder
        ('placeholder="瀹㈡埛濮撳悕/鎵嬫満\ufffd璁㈠崟\ufffd', 
         'placeholder="客户姓名/手机号/订单号'),
        
        # Mobile filter button text
        ("绛涳拷\ufffd", "筛选"),
        
        # Pagination total
        ("锟?\ufffd${t} 鏉,", "共 ${t} 条,"),
        
        # Mobile drawer title
        ('title="绛涳拷\ufffd', 'title="筛选"'),
        
        # Mobile filter labels
        ('label="渚涘簲\ufffd>', 'label="供应商">'),
        ('label="鐔讹拷\ufffd>', 'label="状态">'),
        
        # Form placeholders
        ('placeholder="璇疯緭鍏ュ鎴峰\ufffd', 'placeholder="请输入客户姓名'),
        
        # Form labels
        ('label="鎵嬫満\ufffd', 'label="手机号"'),
        ('label="渚涘簲\ufffd', 'label="供应商"'),
        ('placeholder="璇烽€夋嫨渚涘簲\ufffd', 'placeholder="请选择供应商'),
        
        # Sales price label: 閿€鍞环锟?锟?"  -> 销售价格(元)"
        ('label="閿€鍞环\ufffd\ufffd"', 'label="销售价格(元)"'),
        
        # Deposit label: 瀹氶噾(锟?" -> 定金(元)"
        ('label="瀹氶噾(\ufffd"', 'label="定金(元)"'),
        
        # Cost label: 鎴愭湰(锟?" -> 成本(元)"
        ('label="鎴愭湰(\ufffd"', 'label="成本(元)"'),
    ],
    
    r'e:\Code\TourMind\frontend\src\views\itinerary\ItineraryFormView.vue': [
        # Modal content: 宸叉湁姣忔棩鏄庣粏鍐呭锛屽垏鎹㈣鍗曞皢瑕嗙洊宸插～鍐欏唴瀹癸紝鏄惁缁х画锟?
        # -> 当前已有每日明细内容，切换订单将覆盖已填写内容，是否继续"),
        ("鎹㈣鍗曞皢瑕嗙洊宸插～鍐欏唴瀹癸紝鏄惁缁х画\ufffd", 
         "切换订单将覆盖已填写内容，是否继续"),
        # Also the start of the content string
        ("褰撳墠宸叉湁姣忔棩鏄庣粏鍐呭锛屽垏", "当前已有每日明细内容，切换订单将覆盖已填写内容，是否继续"),
        
        # Error: 璇烽€夋嫨寮€濮嬫棩锟?) -> 请选择开始日期
        ("'璇烽€夋嫨寮€濮嬫棩\ufffd'", "'请选择开始日期'"),
        
        # travelers split regex: .split(/[锟?\\s\\n]+/) -> split(/[，,，\s\n]+/)
        (".split(/[\ufffd\\s\\n]+/)", ".split(/[，,，\\s\\n]+/)"),
        
        # label="目的地" required> - 鐩殑锟?
        ('label="鐩殑\ufffd', 'label="目的地"'),
        
        # :header="`锟?${day.seq} 锟?路 ${day.date}`" -> :header="`第 ${day.seq} 天 · ${day.date}`"
        (':header="`\ufffd${day.seq} \ufffd 路 ${day.date}`"',
         ':header="`第 ${day.seq} 天 · ${day.date}`"'),
        
        # placeholder="当晚住宿城市或区锟? -> 区域
        ('placeholder="褰撴櫄浣忓鍩庡競鎴栧尯\ufffd', 'placeholder="当晚住宿城市或区域'),
        
        # placeholder="注意事项锟? -> 注意事项等
        ('placeholder="娉ㄦ剰浜嬮」\ufffd', 'placeholder="注意事项等'),
    ],
}

for fname, fixes in files_fixes.items():
    with open(fname, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()
    
    changed = 0
    for old, new in fixes:
        count = text.count(old)
        if count > 0:
            text = text.replace(old, new)
            changed += count
            sys.stdout.buffer.write(f"  Fixed {count}x\n".encode('utf-8'))
        else:
            sys.stdout.buffer.write(f"  NOT FOUND: {repr(old[:60])}\n".encode('utf-8'))
    
    with open(fname, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    
    sys.stdout.buffer.write(f"Wrote {changed} fixes to {fname.split(chr(92))[-1]}\n".encode('utf-8'))
    sys.stdout.buffer.write(b'\n')

sys.stdout.buffer.write(b"Done!\n")
