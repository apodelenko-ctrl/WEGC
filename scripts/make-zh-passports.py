#!/usr/bin/env python3
"""Generate Chinese (zh) passport pages from the English source for the
clean-template condos (Vivana, Sierra, Olive) and wire cross-links/hreflang."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJ = ROOT / "projects"

# Slugs that have a real ZH passport (for cross-link rewriting)
ZH_SLUGS = ['casa-de-monte', 'the-title-vivana', 'the-title-sierra', 'the-olive']

# --- shared (global) EN -> ZH replacements, longest/most specific first ---
GLOBAL = [
    # nav / chrome
    ('<span class="tag">Project passport · ', '<span class="tag">项目档案 · '),
    ('>Catalog</a>', '>项目目录</a>'),
    ('>Mechanics</a>', '>购买机制</a>'),
    ('>Locations</a>', '>地段</a>'),
    ('>Process</a>', '>流程</a>'),
    ('>FAQ</a>', '>常见问题</a>'),
    ('class="topbar-cta">Enquire<', 'class="topbar-cta">咨询<'),
    ('← Back to catalog', '← 返回项目目录'),
    # hero tags / meta labels
    ('Condominium · Freehold quota', '公寓 · 永久产权配额'),
    ('ETA Q4 2028', '预计交付 Q4 2028'),
    ('ETA Oct 2028', '预计交付 2028 年 10 月'),
    ('ETA 2028', '预计交付 2028'),
    ('<div class="l">Developer</div>', '<div class="l">开发商</div>'),
    ('<div class="l">Location</div>', '<div class="l">地段</div>'),
    ('<div class="l">Price</div>', '<div class="l">价格</div>'),
    ('<div class="l">Completion</div>', '<div class="l">交付</div>'),
    ('<div class="l">Foreign quota</div>', '<div class="l">外籍配额</div>'),
    ('<div class="l">Type</div>', '<div class="l">类型</div>'),
    ('<div class="l">4 buildings</div>', '<div class="l">4 栋</div>'),
    ('<div class="l">2 buildings</div>', '<div class="l">2 栋</div>'),
    ('360 units', '360 套'),
    ('287 units', '287 套'),
    # hero disclaimer (identical)
    ('Indicative yield bands are general guidance based on observed performance in the relevant Phuket micro-market. Not a forecast, not a commitment, not a guarantee. Specific economics depend on the project, developer terms, rental performance, taxes, fees and market conditions.',
     '参考收益区间仅为基于相关普吉岛细分市场已观察表现的一般性指引,并非预测、承诺或保证。具体收益取决于项目、开发商条款、租赁表现、税费及市场状况。'),
    # kickers
    ('<span class="kicker">Project overview</span>', '<span class="kicker">项目概览</span>'),
    ('<span class="kicker">Specifications</span>', '<span class="kicker">规格参数</span>'),
    ('<span class="kicker">Pricing &amp; floor plans</span>', '<span class="kicker">价格与户型</span>'),
    ('<span class="kicker">Pricing & floor plans</span>', '<span class="kicker">价格与户型</span>'),
    ('<span class="kicker">Payment plan</span>', '<span class="kicker">付款计划</span>'),
    ('<span class="kicker">Location</span>', '<span class="kicker">地段</span>'),
    ('<span class="kicker">Amenities</span>', '<span class="kicker">配套设施</span>'),
    ('<span class="kicker">Visualisation</span>', '<span class="kicker">效果展示</span>'),
    ('<span class="kicker">FAQ</span>', '<span class="kicker">常见问题</span>'),
    ('<span class="kicker">Developer</span>', '<span class="kicker">开发商</span>'),
    ('<span class="kicker">Explore more</span>', '<span class="kicker">更多项目</span>'),
    ('<span>Investment Opportunity · Independent agent</span>', '<span>投资机会 · 独立代理</span>'),
    # shared headings
    ('Hard parameters of the project.', '项目硬参数。'),
    ('Indicative pricing and apartment layouts.', '参考价格与户型。'),
    ('Pre-sale pricing and apartment layouts.', '预售价格与户型。'),
    ('Interest-free instalment schedule.', '免息分期付款计划。'),
    ('0% interest-free pre-sale instalments.', '0% 免息预售分期。'),
    ('On-site facilities.', '项目内配套。'),
    ('Project gallery.', '项目相册。'),
    ('Frequently asked questions.', '常见问题。'),
    ('The Title — by Rhom Bho Property.', 'The Title — 开发商 Rhom Bho Property。'),
    ('Other projects.', '其他项目。'),
    ('Direct developer pricing — on a direct contract.', '开发商直签价格 — 直接合同。'),
    # spec labels
    ('<div class="l">Key features</div>', '<div class="l">核心亮点</div>'),
    ('<span class="l">Project name</span>', '<span class="l">项目名称</span>'),
    ('<span class="l">Developer</span>', '<span class="l">开发商</span>'),
    ('<span class="l">Location</span>', '<span class="l">地段</span>'),
    ('<span class="l">Distance to beach</span>', '<span class="l">距海滩</span>'),
    ('<span class="l">Type</span>', '<span class="l">类型</span>'),
    ('<span class="l">Tenure</span>', '<span class="l">产权</span>'),
    ('<span class="l">Inventory</span>', '<span class="l">房源</span>'),
    ('<span class="l">Starting price</span>', '<span class="l">起价</span>'),
    ('<span class="l">Completion (ETA)</span>', '<span class="l">交付(预计)</span>'),
    ('<span class="l">Settlement currency</span>', '<span class="l">结算货币</span>'),
    # spec / fp values
    ('Condominium (fully furnished)', '公寓(全装修)'),
    ('Freehold (foreign quota)', '永久产权(外籍配额)'),
    ('two 8-storey buildings', '两栋 8 层楼'),
    ('<span class="v">Condominium</span>', '<span class="v">公寓</span>'),
    ('<div class="v">Condominium</div>', '<div class="v">公寓</div>'),
    ('<div class="v">Freehold</div>', '<div class="v">永久产权</div>'),
    ('<div class="v">From ', '<div class="v">自 '),
    # fp spec keys
    ('<span class="k">Area</span>', '<span class="k">面积</span>'),
    ('<span class="k">Bedrooms</span>', '<span class="k">卧室</span>'),
    ('<span class="k">Bathrooms</span>', '<span class="k">浴室</span>'),
    ('<span class="k">Type</span>', '<span class="k">类型</span>'),
    ('<span class="k">Buildings</span>', '<span class="k">楼栋</span>'),
    ('<span class="k">Units</span>', '<span class="k">户数</span>'),
    ('<span class="k">Pet-friendly</span>', '<span class="k">可养宠物</span>'),
    ('<span class="k">Beach</span>', '<span class="k">海滩</span>'),
    ('<span class="k">Floor plan</span>', '<span class="k">户型图</span>'),
    ('<span class="val">Floor plan on request</span>', '<span class="val">户型图按需提供</span>'),
    ('<span class="val">Apartment</span>', '<span class="val">公寓单位</span>'),
    ('<span class="val">Penthouse</span>', '<span class="val">顶层公寓</span>'),
    ('3 × 8 floors', '3 栋 × 8 层'),
    ('2 × 8 floors', '2 栋 × 8 层'),
    ('291 total', '共 291 套'),
    ('450 m to Nai Yang', '距奈杨 450 m'),
    ('Building A', 'A 栋'),
    # pricing cards
    ('<div class="l">Starting from</div>', '<div class="l">起价</div>'),
    ('<div class="l">Up to</div>', '<div class="l">至高</div>'),
    ('<div class="l">Price per m²</div>', '<div class="l">每平方米价格</div>'),
    ('aria-label="Apartment types"', 'aria-label="公寓户型"'),
    # fp panel h3 fragments
    ('<h3>1 Bedroom S (BS)</h3>', '<h3>1 居室 S (BS)</h3>'),
    ('<h3>1 Bedroom Plus (BP)</h3>', '<h3>1 居室 Plus (BP)</h3>'),
    ('<h3>1 Bedroom Plus</h3>', '<h3>1 居室 Plus</h3>'),
    ('<h3>1 Bedroom S</h3>', '<h3>1 居室 S</h3>'),
    ('<h3>1 Bedroom M</h3>', '<h3>1 居室 M</h3>'),
    ('<h3>1 Bedroom L</h3>', '<h3>1 居室 L</h3>'),
    ('<h3>1 Bedroom</h3>', '<h3>1 居室</h3>'),
    ('<h3>2 Bedroom S</h3>', '<h3>2 居室 S</h3>'),
    ('<h3>2 Bedroom M</h3>', '<h3>2 居室 M</h3>'),
    ('<h3>2 Bedroom Penthouse 01</h3>', '<h3>2 居室顶层公寓 01</h3>'),
    ('<h3>2 Bedroom Plus Penthouse 02</h3>', '<h3>2 居室 Plus 顶层公寓 02</h3>'),
    ('<h3>2 Bedroom</h3>', '<h3>2 居室</h3>'),
    # fp prices
    ('<div class="fp-price">On request</div>', '<div class="fp-price">按需报价</div>'),
    ('From ~3.7M THB (115K/m²)', '自约 3.7M THB(115K/m²)'),
    ('From ~5.1M THB (115K/m²)', '自约 5.1M THB(115K/m²)'),
    ('From ~6.4M THB (115K/m²)', '自约 6.4M THB(115K/m²)'),
    ('<div class="fp-price">From ', '<div class="fp-price">自 '),
    # payment shared p fragments
    ('Four equal 25% instalments during construction, per The Title standard schedule for off-plan condominiums.',
     '施工期间四期等额各 25%,采用 The Title 期房公寓标准付款表。'),
    ('Four equal 25% instalments during construction.', '施工期间四期等额各 25%。'),
    ('Four equal 25% instalments on a fixed timeline during construction. Pre-sale launch 2026;',
     '施工期间按固定时间表四期等额各 25%。2026 年开启预售;'),
    ('Completion targeted Q4 2028.', '预计 Q4 2028 交付。'),
    ('Completion targeted Q3 2028.', '预计 Q3 2028 交付。'),
    ('completion targeted Q1 2029.', '预计 Q1 2029 交付。'),
    # payment steps (shared)
    ('<div class="lbl">Reservation deposit<small>On reservation — credited against the purchase price</small></div>',
     '<div class="lbl">预订定金<small>预订时支付 — 抵扣房款</small></div>'),
    ('<div class="lbl">Reservation deposit<small>On pre-sale reservation</small></div>',
     '<div class="lbl">预订定金<small>预售预订时</small></div>'),
    ('<div class="lbl">Contract signing<small>On execution of the sale & purchase agreement</small></div>',
     '<div class="lbl">签订合同<small>签署买卖合同时</small></div>'),
    ('<div class="lbl">Contract signing<small>Within 30 days of contract execution</small></div>',
     '<div class="lbl">签订合同<small>合同签署后 30 天内</small></div>'),
    ('<div class="lbl">2nd instalment<small>During construction</small></div>',
     '<div class="lbl">第二期<small>施工期间</small></div>'),
    ('<div class="lbl">3rd instalment<small>During construction</small></div>',
     '<div class="lbl">第三期<small>施工期间</small></div>'),
    ('<div class="lbl">2nd instalment<small>7 months after contract signing</small></div>',
     '<div class="lbl">第二期<small>签约后 7 个月</small></div>'),
    ('<div class="lbl">3rd instalment<small>7 months after 2nd payment</small></div>',
     '<div class="lbl">第三期<small>第二期后 7 个月</small></div>'),
    ('<div class="lbl">Transfer of ownership<small>Keys handover · completion Q4 2028</small></div>',
     '<div class="lbl">产权过户<small>交钥匙 · Q4 2028 交付</small></div>'),
    ('<div class="lbl">Transfer of ownership<small>Keys handover · completion Q3 2028</small></div>',
     '<div class="lbl">产权过户<small>交钥匙 · Q3 2028 交付</small></div>'),
    ('<div class="lbl">Transfer of ownership<small>Completion & handover · Q1 2029</small></div>',
     '<div class="lbl">产权过户<small>竣工交付 · Q1 2029</small></div>'),
    # pay note (identical)
    ('Interest-free instalments during construction. Percentages are of the total unit price; the reservation deposit is credited against the first instalment. Schedule is indicative and confirmed in the reservation agreement and sale & purchase agreement; subject to developer terms, applicable taxes and fees. Not an offer.',
     '施工期间免息分期。百分比基于房屋总价计算;预订定金抵扣首期。该付款表为参考性质,以预订协议及买卖合同为准;须遵守开发商条款、相关税费。非要约。'),
    # investment block (identical)
    ("WEGC works on a direct contract with the developer. You buy at the developer's published list price — there is no separate buyer-side agency markup. As part of a Singapore corporate group with international banking infrastructure, we can also arrange settlement to the developer in your own jurisdiction and currency where available.",
     'WEGC 与开发商直接签约。您按开发商公布的挂牌价购买 — 不存在单独的买方代理加价。作为拥有国际银行基础设施的新加坡企业集团的一部分,在可行情况下我们还可安排在您所在的司法辖区以您的货币向开发商结算。'),
    ('<div class="v">List price</div><div class="l">No buyer-side markup</div>',
     '<div class="v">挂牌价</div><div class="l">买方无额外加价</div>'),
    ('<div class="v">Direct contract</div><div class="l">Official sales channel</div>',
     '<div class="v">直接合同</div><div class="l">官方销售渠道</div>'),
    ('<div class="v">Your jurisdiction</div><div class="l">Settlement where available</div>',
     '<div class="v">您的辖区</div><div class="l">可行时本地结算</div>'),
    ('Analyze Investment Potential', '分析投资潜力'),
    ('Indicative figures; not an offer. All transactions are subject to onboarding, KYC/AML, source-of-funds verification and applicable law. WEGC is not a bank or a licensed payment institution and does not provide money-transmission services.',
     '数据为参考性质,非要约。所有交易均须经过准入、KYC/AML、资金来源核查及适用法律的约束。WEGC 并非银行或持牌支付机构,不提供货币转移服务。'),
    # amenities
    ("<span>Communal & kids' pool</span>", '<span>公共及儿童泳池</span>'),
    ('<span>Communal pool</span>', '<span>公共泳池</span>'),
    ('<span>Fitness centre</span>', '<span>健身中心</span>'),
    ('<span>Sauna & steam</span>', '<span>桑拿与蒸汽房</span>'),
    ('<span>Co-working / meeting room</span>', '<span>共享办公 / 会议室</span>'),
    ('<span>Yoga area</span>', '<span>瑜伽区</span>'),
    ('<span>Lounge</span>', '<span>休息区</span>'),
    ('<span>Reception / lobby</span>', '<span>接待大堂</span>'),
    ('<span>Covered parking</span>', '<span>室内停车场</span>'),
    ('<span>Parking</span>', '<span>停车场</span>'),
    ('<span>24h security & CCTV</span>', '<span>24 小时安保及监控</span>'),
    ('<span>Landscaped gardens</span>', '<span>景观花园</span>'),
    ("<span>Kids' area</span>", '<span>儿童活动区</span>'),
    # FAQ (shared Q + A)
    ('<summary>Can a foreigner buy a unit here?</summary>', '<summary>外籍人士可以在此购房吗?</summary>'),
    ("Yes. As a condominium, units can be held by foreign buyers in their own name under Thailand's freehold foreign-ownership quota. We confirm the available quota and structure each purchase with documentation and legal review.",
     '可以。作为公寓项目,外籍买家可在泰国永久产权外籍配额内以个人名义持有单位。我们会确认可用配额,并在文件与法律审查下安排每笔交易。'),
    ('<summary>What is the starting price and what is included?</summary>', '<summary>起价是多少,包含哪些内容?</summary>'),
    ('<summary>How does payment and completion work?</summary>', '<summary>付款与交付如何进行?</summary>'),
    ('A reservation deposit secures the unit, followed by a contract payment and milestone-linked instalments per the developer schedule. Completion is targeted for Q4 2028.',
     '预订定金锁定单位,随后按开发商付款表支付合同款及与施工节点挂钩的分期。预计 Q4 2028 交付。'),
    ('A reservation deposit secures the unit, followed by a contract payment and milestone-linked instalments per the developer schedule. Completion is targeted for 2028.',
     '预订定金锁定单位,随后按开发商付款表支付合同款及与施工节点挂钩的分期。预计 2028 年交付。'),
    ('A reservation deposit secures the unit, followed by a contract payment and milestone-linked instalments per the developer schedule. Completion is scheduled for October 2028.',
     '预订定金锁定单位,随后按开发商付款表支付合同款及与施工节点挂钩的分期。预计 2028 年 10 月交付。'),
    ('<summary>Can I pay in my own country and currency?</summary>', '<summary>我可以在本国以本币付款吗?</summary>'),
    ('In many cases, yes. As an independent agent on a direct contract with the developer within a Singapore group with international banking infrastructure, we can arrange settlement in your own jurisdiction and currency where available — subject to KYC/AML, source-of-funds verification and applicable law.',
     '多数情况下可以。作为新加坡集团内与开发商直接签约的独立代理,并拥有国际银行基础设施,在可行情况下我们可安排在您所在辖区以您的货币结算 — 须遵守 KYC/AML、资金来源核查及适用法律。'),
    # developer block (identical)
    ('Every project in this catalogue is built by <strong>Rhom Bho Property Public Company Limited</strong> under the well-established <strong>The Title</strong> brand. Based in Phuket, the company has delivered a portfolio of <strong>20+ residential projects</strong> across the island\'s prime corridors — Bang Tao, Kamala, Surin, Nai Yang, Rawai, Kata and Koh Kaew — with a focus on amenity-rich, design-led leisure residences.',
     '本目录中的每个项目均由 <strong>Rhom Bho Property Public Company Limited</strong> 以成熟的 <strong>The Title</strong> 品牌开发。公司总部位于普吉岛,已在岛上核心地段 — 邦涛、卡马拉、苏林、奈杨、拉威、卡塔及 Koh Kaew — 交付 <strong>20 多个住宅项目</strong>,专注于配套丰富、设计主导的度假型住宅。'),
    ("WEGC works on a <strong>direct contract with the developer</strong> as a direct-contract agent — you buy at the developer's list price, with no buyer-side agency markup.",
     'WEGC 作为直签代理与<strong>开发商直接签约</strong> — 您按开发商挂牌价购买,买方无额外代理加价。'),
    ('<div class="l">Brand</div><div class="v">The Title</div><p>Rhom Bho Property PLC.</p>',
     '<div class="l">品牌</div><div class="v">The Title</div><p>Rhom Bho Property PLC。</p>'),
    ('<div class="l">Portfolio</div><div class="v">20+ projects</div><p>Across Phuket\'s prime corridors.</p>',
     '<div class="l">业绩</div><div class="v">20+ 项目</div><p>遍布普吉岛核心地段。</p>'),
    ('<div class="l">Our role</div><div class="v">Direct contract</div><p>Direct contract · developer list price.</p>',
     '<div class="l">我们的角色</div><div class="v">直接合同</div><p>直接合同 · 开发商挂牌价。</p>'),
    # similar / footer / cta
    ('<span class="go">View passport →</span>', '<span class="go">查看项目档案 →</span>'),
    (' dossier — price list, layouts, payment plan.', ' 完整资料 — 价格表、户型、付款计划。'),
    ('Request the full <strong>', '索取 <strong>'),
    ('Curated Phuket properties under a single mandate — developer-direct contracts, GIDR-screened territory, full execution from brief to handover.',
     '在单一授权下精选普吉岛房产 — 开发商直签合同、GIDR 筛选地段,从需求到交付的全流程执行。'),
    ('<h5>Catalog</h5>', '<h5>项目目录</h5>'),
    ('<h5>Legal &amp; contact</h5>', '<h5>法律与联系</h5>'),
    ('>WEGC Home</a>', '>WEGC 首页</a>'),
    ('>Real Estate</a>', '>房产</a>'),
    ('>Private Capital</a>', '>私募资本</a>'),
    ('>Corporate</a>', '>企业</a>'),
    ('>Privacy Policy</a>', '>隐私政策</a>'),
    # generic value words (after the specific ones above)
    ('<span class="v">From ', '<span class="v">自 '),
    # nav targets to ZH agency page
    ('/wet-agency-en.html', '/wet-agency-zh.html'),
    # place names — multi-word (containing Phuket) BEFORE the bare 'Phuket' rule
    ('Phuket International Airport', '普吉国际机场'),
    ('Central Phuket (Floresta)', '普吉 Central(Floresta)'),
    ('Central Phuket', '普吉 Central'),
    ('Phuket Town', '普吉镇'),
    ('Sirinat National Park', '西林纳特国家公园'),
    ('Bang Tao', '邦涛'),
    ('Nai Yang', '奈杨'),
    ('Mai Khao', '迈考'),
    ('Kamala', '卡马拉'),
    ('Patong', '巴东'),
    ('Surin', '苏林'),
    ('Thailand', '泰国'),
    ('Phuket', '普吉岛'),
    ('international schools', '国际学校'),
    ('UWC / 国际学校', 'UWC / 国际学校'),
    ('nearby</span>', '附近</span>'),
    ('adjacent</span>', '紧邻</span>'),
    ('min</span>', '分钟</span>'),
]

# --- per-project unique replacements ---
PROJECTS = {
    'the-title-vivana': {
        'title': ('The Title Vivana — Kamala · Phuket · from ~3.75M THB · Project Passport · WEGC',
                  'The Title Vivana — 普吉岛 卡马拉 · 约 362 万泰铢起 · 项目档案 · WEGC'),
        'reps': [
            ('The Title Vivana by Rhom Bho Property (The Title) — Kamala, Phuket. A resort-style condominium near Kamala Beach. From ~3.62M THB. Direct developer contract, full documentation.',
             'The Title Vivana — 开发商 Rhom Bho Property(The Title),位于普吉岛卡马拉,临近卡马拉海滩的度假式公寓。约 362 万泰铢起。与开发商直接签约,文件齐全。'),
            ('The Title Vivana — Kamala, Phuket', 'The Title Vivana — 普吉岛 卡马拉'),
            ('<h1>The Title Vivana — <strong>Kamala</strong>.</h1>', '<h1>The Title Vivana — <strong>卡马拉</strong>。</h1>'),
            ('A low-rise, resort-style condominium in Kamala on Phuket\'s west coast — roughly 1.5 km (a 7-minute walk) from Kamala Beach and positioned between Patong and Bang Tao. 360 fully-furnished apartments across four buildings, from compact studios to two-bedroom layouts, with a full resort amenity deck. Freehold under the foreign-ownership quota. From approximately 3.62M THB.',
             '位于普吉岛西海岸卡马拉的低层度假式公寓 — 距卡马拉海滩约 1.5 公里(步行 7 分钟),坐落于巴东与邦涛之间。四栋楼共 360 套全装修公寓,从紧凑开间到两居室,配齐全度假设施。永久产权(外籍配额)。约 362 万泰铢起。'),
            ('The ocean, a short walk away.', '大海,近在咫尺。'),
            ('<strong>The Title Vivana</strong> is a low-rise, resort-style condominium in Kamala — one of the more balanced west-coast beach communities, set between the energy of Patong and the polish of Bang Tao. The project sits about 1.5 km from Kamala Beach, an easy walk, with green hillside surroundings.',
             '<strong>The Title Vivana</strong> 是位于卡马拉的低层度假式公寓 — 这里是西海岸较为均衡的海滨社区之一,介于巴东的活力与邦涛的精致之间。项目距卡马拉海滩约 1.5 公里,步行可达,周边绿意山坡环绕。'),
            ('The development comprises 360 fully-furnished apartments across four buildings, from studios to two-bedroom layouts, with a resort amenity deck — pool and kids\' pool, gym, sauna and steam, jacuzzi, co-working and yoga areas. Pet-friendly buildings are available. Foreign buyers can own under the condominium freehold quota; completion is targeted for Q4 2028.',
             '项目由四栋楼共 360 套全装修公寓组成,从开间到两居室,配有度假设施 — 泳池及儿童泳池、健身房、桑拿蒸汽房、按摩池、共享办公及瑜伽区。提供可养宠物的楼栋。外籍买家可在公寓永久产权配额内持有;预计 Q4 2028 交付。'),
            ('<li><span>Kamala — balanced west-coast beach community</span></li>', '<li><span>卡马拉 — 均衡的西海岸海滨社区</span></li>'),
            ('<li><span>≈ 1.5 km (7-min walk) to Kamala Beach</span></li>', '<li><span>距卡马拉海滩约 1.5 公里(步行 7 分钟)</span></li>'),
            ('<li><span>360 fully-furnished apartments · 4 buildings</span></li>', '<li><span>360 套全装修公寓 · 4 栋</span></li>'),
            ('<li><span>From approximately 3.62M THB</span></li>', '<li><span>约 362 万泰铢起</span></li>'),
            ('<li><span>Freehold under foreign-ownership quota</span></li>', '<li><span>永久产权(外籍配额内)</span></li>'),
            ('<li><span>Pet-friendly · full resort amenities</span></li>', '<li><span>可养宠物 · 齐全度假配套</span></li>'),
            ('Seven layout types across four 8-storey buildings — studios to penthouses, 30–128 m². Pricing is indicative and subject to availability, unit selection and final developer confirmation — not an offer.',
             '四栋 8 层楼共七种户型 — 从开间到顶层公寓,30–128 m²。价格为参考性质,以房源、选房及开发商最终确认为准 — 非要约。'),
            ('approx. $111,000 · 1 Bedroom S (30 m²)', '约 $111,000 · 1 居室 S(30 m²)'),
            ('2 Bedroom Penthouse · top configuration', '2 居室顶层公寓 · 顶配'),
            ('Kamala — west-coast beach, between Patong and Bang Tao.', '卡马拉 — 西海岸海滨,介于巴东与邦涛之间。'),
            ('The Title Vivana sits in Kamala on Phuket’s west coast — a balanced beach community about 1.5 km from Kamala Beach, between the energy of Patong and the polish of Bang Tao.',
             'The Title Vivana 位于普吉岛西海岸的卡马拉 — 一个均衡的海滨社区,距卡马拉海滩约 1.5 公里,介于巴东的活力与邦涛的精致之间。'),
            ('Indicatively from ~3.75M THB. Exact pricing per unit, the furniture package and what is included are confirmed in the developer quote — we provide the current price list on request.',
             '参考起价约 362 万泰铢。每套的具体价格、家具包及包含内容以开发商报价为准 — 我们可应需提供最新价格表。'),
        ],
    },
    'the-title-sierra': {
        'title': ('The Title Sierra — Bang Tao · Phuket · from 2.87M THB · Project Passport · WEGC',
                  'The Title Sierra — 普吉岛 邦涛 · 287 万泰铢起 · 项目档案 · WEGC'),
        'reps': [
            ('The Title Sierra by Rhom Bho Property (The Title) — Bang Tao, Phuket. A new condominium in the Bang Tao corridor. From 2.87M THB. Direct developer contract, full documentation.',
             'The Title Sierra — 开发商 Rhom Bho Property(The Title),位于普吉岛邦涛走廊的全新公寓。287 万泰铢起。与开发商直接签约,文件齐全。'),
            ('The Title Sierra — Bang Tao, Phuket', 'The Title Sierra — 普吉岛 邦涛'),
            ('<h1>The Title Sierra — <strong>Bang Tao</strong>.</h1>', '<h1>The Title Sierra — <strong>邦涛</strong>。</h1>'),
            ("A new condominium in Bang Tao — The Title's home corridor on Phuket's west coast, anchored by Laguna, Boat Avenue and Porto de Phuket. A green, lower-density setting with quick access to beaches, international schools and the island's main lifestyle hubs. One of the most accessible entry points into the Bang Tao market, from 2.87M THB.",
             '位于邦涛的全新公寓 — 这里是 The Title 在普吉岛西海岸的大本营走廊,以 Laguna、Boat Avenue 和 Porto de Phuket 为核心。绿意、低密度的环境,可快速抵达海滩、国际学校及岛上主要生活枢纽。是进入邦涛市场最易入手的切入点之一,287 万泰铢起。'),
            ('Nature and urban life within reach.', '自然与都市,触手可及。'),
            ('<strong>The Title Sierra</strong> is a new condominium development in Bang Tao, the established west-coast corridor where The Title has concentrated much of its portfolio. The area combines a green, residential feel with the convenience of Laguna Phuket, Boat Avenue, Porto de Phuket and a short drive to Bang Tao and Layan beaches.',
             '<strong>The Title Sierra</strong> 是位于邦涛的全新公寓项目,这条成熟的西海岸走廊集中了 The Title 大量作品。该区域兼具绿意宜居氛围,以及 Laguna Phuket、Boat Avenue、Porto de Phuket 的便利,并可短途驱车至邦涛与 Layan 海滩。'),
            ("Positioned as one of the most accessible entry points into the Bang Tao market, Sierra targets buyers who want a foothold in Phuket's strongest appreciation corridor without a premium ticket. Foreign buyers can own under the condominium freehold quota. Completion is targeted for 2028.",
             '作为进入邦涛市场最易入手的切入点之一,Sierra 面向希望以较低门槛在普吉岛最具升值潜力走廊立足的买家。外籍买家可在公寓永久产权配额内持有。预计 2028 年交付。'),
            ('<li><span>Bang Tao — Phuket’s prime west-coast corridor</span></li>', '<li><span>邦涛 — 普吉岛核心西海岸走廊</span></li>'),
            ('<li><span>Starting price from 2.87M THB</span></li>', '<li><span>起价 287 万泰铢</span></li>'),
            ('<li><span>Freehold under foreign-ownership quota</span></li>', '<li><span>永久产权(外籍配额内)</span></li>'),
            ('<li><span>Resort-style facilities</span></li>', '<li><span>度假式配套设施</span></li>'),
            ('<li><span>Close to Laguna, Boat Avenue, Porto de Phuket</span></li>', '<li><span>临近 Laguna、Boat Avenue、Porto de Phuket</span></li>'),
            ('<li><span>Strong long-term rental corridor</span></li>', '<li><span>长期租赁需求强劲走廊</span></li>'),
            ('Five layout types across three 8-storey buildings — compact studios to two-bedroom units, 28–62 m². Pricing is indicative and subject to availability — not an offer.',
             '三栋 8 层楼共五种户型 — 从紧凑开间到两居室,28–62 m²。价格为参考性质,以房源为准 — 非要约。'),
            ('approx. $94,000 · 1 Bedroom S (28 m²)', '约 $94,000 · 1 居室 S(28 m²)'),
            ('1 Bedroom Plus · larger layout', '1 居室 Plus · 大户型'),
            ("Bang Tao — Phuket's prime west-coast lifestyle corridor.", '邦涛 — 普吉岛核心西海岸生活走廊。'),
            ('The Title Sierra sits in the Bang Tao corridor — anchored by Laguna Phuket, Boat Avenue and Porto de Phuket, with quick access to beaches, international schools and the island’s main lifestyle hubs.',
             'The Title Sierra 位于邦涛走廊 — 以 Laguna Phuket、Boat Avenue 和 Porto de Phuket 为核心,可快速抵达海滩、国际学校及岛上主要生活枢纽。'),
            ('Indicatively from 2.87M THB. Exact pricing per unit, the furniture package and what is included are confirmed in the developer quote — we provide the current price list on request.',
             '参考起价 287 万泰铢。每套的具体价格、家具包及包含内容以开发商报价为准 — 我们可应需提供最新价格表。'),
        ],
    },
    'the-olive': {
        'title': ('The Olive — Nai Yang · Phuket · from 4.99M THB · Project Passport · WEGC',
                  'The Olive — 普吉岛 奈杨 · 499 万泰铢起 · 项目档案 · WEGC'),
        'reps': [
            ('The Olive by Rhom Bho Property (The Title) — Nai Yang, Phuket. A beachside Mediterranean condominium in Nai Yang. From 4.99M THB. Direct developer contract, full documentation.',
             'The Olive — 开发商 Rhom Bho Property(The Title),位于普吉岛奈杨的海滨地中海风格公寓。499 万泰铢起。与开发商直接签约,文件齐全。'),
            ('The Olive — Nai Yang, Phuket', 'The Olive — 普吉岛 奈杨'),
            ('<h1>The Olive — <strong>Nai Yang</strong>.</h1>', '<h1>The Olive — <strong>奈杨</strong>。</h1>'),
            ("A beachside condominium in Nai Yang on Phuket's quieter northern coast — about 450 m from the beach and minutes from the international airport and Sirinat National Park. A modern Mediterranean concept across two eight-storey residential buildings and a dedicated facility building, 287 units in total, with green, garden-led common areas. Completion in October 2028. From 4.99M THB.",
             '位于普吉岛较为宁静的北海岸奈杨的海滨公寓 — 距海滩约 450 米,几分钟即达国际机场和西林纳特国家公园。现代地中海概念,由两栋 8 层住宅楼及一栋独立配套楼组成,共 287 套,拥有绿意花园式公共区域。2028 年 10 月交付。499 万泰铢起。'),
            ('Where life prospers, beachside.', '海滨,生活欣欣向荣。'),
            ("<strong>The Olive</strong> is a beachside condominium in Nai Yang on Phuket's northern coast — a calm, conservation-protected corridor anchored by Sirinat National Park, the long Nai Yang and Mai Khao beaches and the international airport just minutes away. The setting is green, low-key and family-oriented.",
             '<strong>The Olive</strong> 是位于普吉岛北海岸奈杨的海滨公寓 — 这是一条宁静、受保护的生态走廊,以西林纳特国家公园、绵长的奈杨与迈考海滩为核心,国际机场仅数分钟车程。环境绿意盎然、低调且适合家庭。'),
            ("Designed in a modern Mediterranean idiom, the project spans two eight-storey residential buildings and a dedicated facility building — 287 units in total, with resort amenities, garden-led common areas, a kids' club and pet-friendly buildings. Foreign buyers can own under the condominium freehold quota; completion is scheduled for October 2028.",
             '项目采用现代地中海风格,由两栋 8 层住宅楼及一栋独立配套楼组成 — 共 287 套,配有度假设施、花园式公共区域、儿童俱乐部及可养宠物的楼栋。外籍买家可在公寓永久产权配额内持有;预计 2028 年 10 月交付。'),
            ('<li><span>Nai Yang — quiet, conservation-protected northern coast</span></li>', '<li><span>奈杨 — 宁静、受保护的北海岸</span></li>'),
            ('<li><span>≈ 450 m to the beach · minutes to the airport</span></li>', '<li><span>距海滩约 450 米 · 数分钟到机场</span></li>'),
            ('<li><span>Modern Mediterranean concept</span></li>', '<li><span>现代地中海概念</span></li>'),
            ('<li><span>287 units · two 8-storey buildings</span></li>', '<li><span>287 套 · 两栋 8 层楼</span></li>'),
            ('<li><span>From 4.99M THB</span></li>', '<li><span>499 万泰铢起</span></li>'),
            ('<li><span>Freehold under foreign-ownership quota</span></li>', '<li><span>永久产权(外籍配额内)</span></li>'),
            ('<span class="v">The Olive (The Title Olive)</span>', '<span class="v">The Olive(The Title Olive)</span>'),
            ('Three layout groups across two 8-storey Mediterranean-style buildings — 32–63 m². Pre-sale from 115,000 THB/m². Pricing is indicative — not an offer.',
             '两栋 8 层地中海风格楼宇共三组户型 — 32–63 m²。预售价每平方米 115,000 泰铢起。价格为参考性质 — 非要约。'),
            ('115,000 THB/m² · 1 Bedroom (32 m²)', '115,000 泰铢/m² · 1 居室(32 m²)'),
            ('Pre-sale · up to 10% discount available', '预售 · 最高 10% 折扣'),
            ('Nai Yang — quiet, conservation-protected northern coast.', '奈杨 — 宁静、受保护的北海岸。'),
            ('The Olive sits in Nai Yang on Phuket’s northern coast — a calm corridor anchored by Sirinat National Park and the long Nai Yang beach, about 450 m from the sea and minutes from the international airport.',
             'The Olive 位于普吉岛北海岸的奈杨 — 一条以西林纳特国家公园和绵长奈杨海滩为核心的宁静走廊,距海约 450 米,数分钟即达国际机场。'),
            ('Indicatively from 4.99M THB. Exact pricing per unit, the furniture package and what is included are confirmed in the developer quote — we provide the current price list on request.',
             '参考起价 499 万泰铢。每套的具体价格、家具包及包含内容以开发商报价为准 — 我们可应需提供最新价格表。'),
        ],
    },
}


def fix_head(text, slug):
    # html lang
    text = text.replace('<html lang="en">', '<html lang="zh">', 1)
    # canonical & og:url to zh
    text = text.replace(f'<link rel="canonical" href="https://wegc.fund/projects/{slug}-en.html"/>',
                        f'<link rel="canonical" href="https://wegc.fund/projects/{slug}-zh.html"/>', 1)
    text = text.replace(f'<meta property="og:url" content="https://wegc.fund/projects/{slug}-en.html"/>',
                        f'<meta property="og:url" content="https://wegc.fund/projects/{slug}-zh.html"/>', 1)
    # add hreflang zh after ru line
    ru_line = f'<link rel="alternate" hreflang="ru" href="https://wegc.fund/projects/{slug}.html"/>'
    zh_line = f'<link rel="alternate" hreflang="zh" href="https://wegc.fund/projects/{slug}-zh.html"/>'
    if zh_line not in text:
        text = text.replace(ru_line, ru_line + '\n' + zh_line, 1)
    # lang switcher: deactivate EN, activate ZH and point it to the zh file
    text = text.replace(
        f'<a href="/projects/{slug}-en.html" class="lang-sw-a active" hreflang="en">EN</a>',
        f'<a href="/projects/{slug}-en.html" class="lang-sw-a" hreflang="en">EN</a>', 1)
    text = text.replace(
        '<a href="/wet-agency-zh.html#catalog" class="lang-sw-a" hreflang="zh">中文</a>',
        f'<a href="/projects/{slug}-zh.html" class="lang-sw-a active" hreflang="zh">中文</a>', 1)
    return text


def rewrite_crosslinks(text):
    # passport links -> zh where a zh page exists
    for s in ZH_SLUGS:
        text = text.replace(f'/projects/{s}-en.html', f'/projects/{s}-zh.html')
    return text


def build(slug, cfg):
    en = (PROJ / f'{slug}-en.html').read_text(encoding='utf-8')
    out = en
    # title first (unique)
    out = out.replace(cfg['title'][0], cfg['title'][1], 1)
    # per-project reps
    for a, b in cfg['reps']:
        if a not in out:
            print(f'  WARN missing (per-proj) in {slug}: {a[:60]}')
        out = out.replace(a, b)
    # head fixups BEFORE global (so en.html anchors are matchable)
    out = fix_head(out, slug)
    # global reps
    for a, b in GLOBAL:
        out = out.replace(a, b)
    # cross-links to zh
    out = rewrite_crosslinks(out)
    (PROJ / f'{slug}-zh.html').write_text(out, encoding='utf-8')
    print('wrote', f'{slug}-zh.html')


def main():
    for slug, cfg in PROJECTS.items():
        build(slug, cfg)


if __name__ == '__main__':
    main()
