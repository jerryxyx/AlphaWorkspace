import json

# Extracted note text (from web_fetch)
note_text = """女生solo trip越南15天六城✈攻略分享
出行、住宿、换汇、租车、吃喝全整理好了！！
过年有计划去越南的姐妹赶紧🐎住，直接抄作业就行～
·
✍🏻 出行准备
通讯：买20天电话卡，提前在国内买好，落地插卡就能用，流量足够全程用
保障：重点说！女生独自出行一定要买旅行险！我这次买的是支付宝上的无忧保·境外旅行险，全程安心感拉满！我在河内逛夜市吃坏肚子去看急诊，语言不通正手足无措，联系了24 小时中文救援，不仅帮对接医院沟通病情，看病花的2000多也顺利报销了！
·
1️⃣河内：
出站后换汇，汇率3680
住宿：青旅hanoi central pod，女生间45一晚，很大！
市区换汇1:3710，地址：QUANG HUY GEMSTONE
2️⃣岘港
住宿Jim's House，70块钱一晚
换汇1:3700 地址：Hiệu Vàng Kim Yến Hương
租电动车，地址：97 nguyen xuan khoat，130k一天
租桨板，定位sup station，Man Thai beach，一块板150k
3️⃣会安
骑车去安古镇，椰子船在klook上订票
4️⃣大叻
住宿Myrtle Boutique Hotel
吃饭：Goc ha thanh
喝咖啡：Golden Bistro & Coffee
5️⃣胡志明
不好玩所以随便逛逛
胡志明换汇我去了两家，汇率都是3650
地址：Kim Mai Jewelry Shop（不用排队就在范五老街附近
地址：HA TAM金店（巨多人排队排了半个小时
6️⃣美奈
胡志明去美奈大巴，现场买票：Nam Hải Limousine
住宿：Wanderlust garden inn
酒店出来往右手边走，摆摊卖榴莲的40k/kg
地址：Ham Tien Market
🙋🏻♀️ 安全小贴士&旅行险推荐
越南饮食偏酸辣，加上热带地区湿热，很容易吃坏肚子；骑行电动车、海边玩水也可能有小意外，而且当地部分医疗条件一般，费用也不低。所以一定要买旅行险，我这款是有100万医疗保额，而且是0免赔额的，门诊、住院费用，一块钱都能报，不管是突发肠胃炎还是小擦伤都能覆盖。
打算去越南的姐妹，攻略赶紧码好，旅行险也记得提前安排上，让旅途既自由又安心～
祝大家旅途愉快🫡
[#越南旅游](/search_result?keyword=%25E8%25B6%258A%25E5%258D%2597%25E6%2597%2585%25E6%25B8%25B8&type=54&source=web_note_detail_r10) [#女性独自旅行](/search_result?keyword=%25E5%25A5%25B3%25E6%2580%25A7%25E7%258B%25AC%25E8%2587%25AA%25E6%2597%2585%25E8%25A1%258C&type=54&source=web_note_detail_r10) [#越南旅游攻略](/search_result?keyword=%25E8%25B6%258A%25E5%258D%2597%25E6%2597%2585%25E6%258B%2582%25E7%2595%25A5&type=54&source=web_note_detail_r10) [#越南](/search_result?keyword=%25E8%25B6%258A%25E5%258D%2597&type=54&source=web_note_detail_r10) [#一个人旅游](/search_result?keyword=%25E4%25B8%2580%25E4%25B8%25AA%25E4%25BA%25BA%25E6%2597%2585%25E6%25B8%25B8&type=54&source=web_note_detail_r10) [#solotrip](/search_result?keyword=solotrip&type=54&source=web_note_detail_r10) [#旅行险](/search_result?keyword=%25E6%2597%2585%25E8%25A1%258C%25E9%2599%25A9&type=54&source=web_note_detail_r10)
01-23"""

# Parse into blocks
blocks = []

# Heading
blocks.append({
    "content_block": {
        "content": "🧳 Focus: Solo Female Travel (15‑day 6‑city guide)",
        "block_property": "heading_2"
    }
})

# Note link paragraph
note_url = "https://www.xiaohongshu.com/discovery/item/6973227f000000000b00804d?app_platform=ios&app_version=9.22.1&share_from_user_hidden=true&xsec_source=app_share&type=normal&xsec_token=CBT_XW_njZAv9FHWsaRFB4adg-uTcMhk11GfW6cpRjckg=&author_share=1&xhsshare=WeixinSession&shareRedId=ODdHQ0dISU82NzUyOTgwNjczOTc9STpL&apptime=1774150740&share_id=ec4ed9192e2b4426a7e8fd27b91afbdc"
blocks.append({
    "content_block": {
        "content": f"Note: [女生solo trip越南15天六城✈攻略分享]({note_url})",
        "block_property": "paragraph"
    }
})

# Split into lines and create bullet points for key sections
lines = note_text.split('\n')
current_section = []
for line in lines:
    line = line.strip()
    if not line:
        continue
    # If line starts with emoji number or bullet, treat as new bullet
    if line.startswith('1️⃣') or line.startswith('2️⃣') or line.startswith('3️⃣') or line.startswith('4️⃣') or line.startswith('5️⃣') or line.startswith('6️⃣'):
        # Flush previous section as bullet
        if current_section:
            bullet_text = ' '.join(current_section)
            if len(bullet_text) > 2000:
                # split
                pass
            blocks.append({
                "content_block": {
                    "content": bullet_text,
                    "block_property": "bulleted_list_item"
                }
            })
        current_section = [line]
    elif line.startswith('✍🏻'):
        # Subheading, maybe treat as paragraph
        blocks.append({
            "content_block": {
                "content": line,
                "block_property": "paragraph"
            }
        })
    elif line.startswith('🙋🏻♀️'):
        # Safety tips heading
        blocks.append({
            "content_block": {
                "content": line,
                "block_property": "paragraph"
            }
        })
    else:
        current_section.append(line)

# Add last bullet
if current_section:
    bullet_text = ' '.join(current_section)
    blocks.append({
        "content_block": {
            "content": bullet_text,
            "block_property": "bulleted_list_item"
        }
    })

# Create final args
parent_block_id = "32a271cf-ee80-81bb-94e9-f0c48e3374ed"
with open("/Users/xyx/.openclaw/workspace/after_block_id.txt", "r") as f:
    after_block_id = f.read().strip()

args = {
    "parent_block_id": parent_block_id,
    "after": after_block_id,
    "content_blocks": blocks
}

# Write to file
with open("/Users/xyx/.openclaw/workspace/solo_trip_args.json", "w") as f:
    json.dump(args, f, ensure_ascii=False, indent=2)

print("Generated solo_trip_args.json")