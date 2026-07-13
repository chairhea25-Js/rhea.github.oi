from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.colors import HexColor, Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from PIL import Image

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output" / "pdf" / "chaiyun-portfolio-2026.pdf"
ASSETS = ROOT / "assets"
CACHE = ROOT / "tmp" / "pdfs" / "image-cache"
W, H = landscape(A4)

paper = HexColor("#F7F3EE")
surface = HexColor("#FBF9F5")
ink = HexColor("#454852")
muted = HexColor("#656A75")
quiet = HexColor("#7D8390")
blue = HexColor("#98ABC2")
deep = HexColor("#5F616F")
warm = HexColor("#E8D3C1")
line = Color(.37, .38, .44, alpha=.22)

pdfmetrics.registerFont(TTFont("Songti", "/System/Library/Fonts/Supplemental/Songti.ttc", subfontIndex=0))
FONT = "Songti"

def p(rel):
    return str(ASSETS / rel)

def image_size(path):
    with Image.open(path) as img:
        return img.size

def prepared_image(path):
    """Downsample originals for a shareable PDF while preserving print-quality detail."""
    source = Path(path)
    CACHE.mkdir(parents=True, exist_ok=True)
    target = CACHE / f"{source.stem}-{source.stat().st_mtime_ns}.jpg"
    if not target.exists():
        with Image.open(source) as img:
            img = img.convert("RGB")
            img.thumbnail((1800, 1800), Image.Resampling.LANCZOS)
            img.save(target, "JPEG", quality=85, optimize=True, progressive=True)
    return str(target)

def bg(c, page):
    c.setFillColor(paper)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setStrokeColor(Color(.60, .67, .76, alpha=.12))
    c.setLineWidth(.35)
    for x in range(0, int(W) + 1, 24): c.line(x, 0, x, H)
    for y in range(0, int(H) + 1, 24): c.line(0, y, W, y)
    c.setFillColor(quiet); c.setFont(FONT, 7)
    c.drawString(38, 24, "CY · 柴蕴的观察手记 · 想让你，看见我。")
    c.drawRightString(W - 38, 24, f"{page:02d}")

def text(c, x, y, value, size=12, color=ink, leading=None, max_width=None):
    c.setFillColor(color); c.setFont(FONT, size)
    if not max_width:
        c.drawString(x, y, value); return y - (leading or size * 1.5)
    leading = leading or size * 1.65
    line, lines = "", []
    for char in value:
        trial = line + char
        if pdfmetrics.stringWidth(trial, FONT, size) <= max_width:
            line = trial
        else:
            lines.append(line); line = char
    if line: lines.append(line)
    for item in lines:
        c.drawString(x, y, item); y -= leading
    return y

def title(c, kicker, heading, desc=None):
    c.setFillColor(deep); c.setFont(FONT, 9); c.drawString(48, H - 54, kicker)
    c.setFillColor(ink); c.setFont(FONT, 31)
    c.drawString(48, H - 96, heading)
    if desc: text(c, 48, H - 122, desc, 11, muted, max_width=600)
    c.setStrokeColor(warm); c.setLineWidth(1.2); c.line(48, H - 138, 260, H - 138)

def cover_image(c, path, x, y, w, h, stroke=True):
    iw, ih = image_size(path); scale = max(w / iw, h / ih)
    dw, dh = iw * scale, ih * scale
    dx, dy = x + (w - dw) / 2, y + (h - dh) / 2
    c.saveState(); path_obj = c.beginPath(); path_obj.rect(x, y, w, h); c.clipPath(path_obj, stroke=0, fill=0)
    c.drawImage(ImageReader(prepared_image(path)), dx, dy, dw, dh, mask='auto')
    c.restoreState()
    if stroke:
        c.setStrokeColor(line); c.setLineWidth(.8); c.rect(x, y, w, h, fill=0, stroke=1)

def contain_image(c, path, x, y, w, h, fill=surface):
    c.setFillColor(fill); c.rect(x, y, w, h, fill=1, stroke=0)
    iw, ih = image_size(path); scale = min(w / iw, h / ih)
    dw, dh = iw * scale, ih * scale
    c.drawImage(ImageReader(prepared_image(path)), x + (w-dw)/2, y + (h-dh)/2, dw, dh, mask='auto')
    c.setStrokeColor(line); c.setLineWidth(.7); c.rect(x, y, w, h, fill=0, stroke=1)

def note(c, x, y, w, h, label, heading, body):
    c.setFillColor(HexColor("#F3E5D9")); c.setStrokeColor(line)
    c.roundRect(x, y, w, h, 4, fill=1, stroke=1)
    c.setFillColor(deep); c.setFont(FONT, 8); c.drawString(x+18, y+h-24, label)
    c.setFillColor(ink); c.setFont(FONT, 20); c.drawString(x+18, y+h-56, heading)
    text(c, x+18, y+h-84, body, 10, muted, max_width=w-36)

def page_cover(c):
    bg(c, 1)
    c.setFillColor(deep); c.setFont(FONT, 13); c.drawString(54, H-58, "柴蕴 · PORTFOLIO 2026")
    c.setFillColor(ink); c.setFont(FONT, 49); c.drawString(54, H-132, "对人保持敏感，")
    c.drawString(54, H-195, "把事情接住。")
    text(c, 58, H-240, "想让你，看见我。", 18, deep)
    text(c, 58, H-278, "内容运营 · 活动制片 · 项目统筹 · 人力资源", 11, muted)
    c.setFillColor(warm); c.rect(54, H-311, 176, 5, fill=1, stroke=0)
    cover_image(c, p("photos/hero-snow.JPG"), 510, 74, 245, 374)
    c.setFillColor(surface); c.rect(486, 55, 290, 423, fill=1, stroke=0)
    cover_image(c, p("photos/hero-snow.JPG"), 504, 96, 254, 342)
    c.setFillColor(muted); c.setFont(FONT, 10); c.drawString(530, 72, "在新疆长大，后来来到南京")
    c.showPage()

def page_overview(c):
    bg(c, 2); title(c, "PORTFOLIO OVERVIEW", "把想法，变成真实发生的事。", "我关注内容，也关注内容背后的人。")
    notes = [
        ("01", "作品展厅", "社服、海报、三折页与舞台物料。"),
        ("02", "项目故事", "活动策划、持续迭代与复杂协作。"),
        ("03", "关于我", "人、内容、现场，以及持续的好奇心。"),
    ]
    for i, item in enumerate(notes): note(c, 48+i*250, 180, 220, 178, *item)
    metrics = [("1.8万", "单条视频最高播放"), ("200+", "单场活动参与者"), ("6000+", "机器人共舞现场观众")]
    for i,(big,small) in enumerate(metrics):
        x=70+i*245; c.setFillColor(deep); c.setFont(FONT, 29); c.drawString(x, 108, big)
        text(c,x,82,small,9,muted)
    c.showPage()

def story_page(c, page, kicker, heading, body, role, main, pairs, accent):
    bg(c,page); title(c,kicker,heading,role)
    c.setFillColor(accent); c.roundRect(48, 86, 332, 335, 5, fill=1, stroke=0)
    text(c, 74, 388, body, 12, ink, leading=22, max_width=280)
    c.setFillColor(deep); c.setFont(FONT, 10); c.drawString(74, 116, "把看见的需要，认真接住。")
    cover_image(c, p(main), 406, 215, 380, 206)
    gap=12; sw=(380-gap)/2
    for i,(path,label) in enumerate(pairs):
        x=406+i*(sw+gap); cover_image(c,p(path),x,86,sw,110)
        c.setFillColor(muted); c.setFont(FONT,8); c.drawString(x,70,label)
    c.showPage()

def apparel_page(c, page, kicker, heading, intro, files, captions):
    bg(c,page); title(c,kicker,heading,intro)
    x_positions=[48, 291, 534]; widths=[220,220,260]
    for x,w,path,caption in zip(x_positions,widths,files,captions):
        contain_image(c,p(path),x,104,w,310)
        c.setFillColor(muted); c.setFont(FONT,9); c.drawCentredString(x+w/2,88,caption)
    c.showPage()

def image_grid_page(c, page, kicker, heading, intro, files, cols, labels=None, contain=False):
    bg(c,page); title(c,kicker,heading,intro)
    left, bottom, top = 48, 54, H-162
    gap=14; rows=(len(files)+cols-1)//cols; cellw=(W-96-gap*(cols-1))/cols; cellh=(top-bottom-gap*(rows-1))/rows
    for i,path in enumerate(files):
        row, col = divmod(i,cols); x=left+col*(cellw+gap); y=top-(row+1)*cellh-row*gap
        if contain: contain_image(c,p(path),x,y,cellw,cellh)
        else: cover_image(c,p(path),x,y,cellw,cellh)
        if labels:
            c.setFillColor(surface); c.rect(x+7,y+7,min(cellw-14,104),15,fill=1,stroke=0)
            c.setFillColor(deep); c.setFont(FONT,7.5); c.drawString(x+12,y+12,labels[i])
    c.showPage()

def about_page(c):
    bg(c, 14); title(c,"ABOUT ME","关于我","新疆长大的汉族姑娘，河海大学人力资源管理专业学生，也是 200+ 人街舞社的社长。")
    cover_image(c,p("photos/lake-sunset.JPG"),48,100,294,280)
    cover_image(c,p("photos/dance-stage.JPG"),362,222,180,158)
    cover_image(c,p("photos/casual-sport.JPG"),562,222,180,158)
    c.setFillColor(HexColor("#DFE5EB")); c.roundRect(362,100,380,100,4,fill=1,stroke=0)
    text(c,384,174,"不同的人、语言和生活方式从小就在身边，这让我习惯先理解一个人所处的环境，再判断一件事。",11,ink,max_width=330)
    text(c,384,118,"能接住事 · 对人敏感 · 有生命力",10,deep)
    c.showPage()

def contact_page(c):
    bg(c,15); c.setFillColor(deep); c.roundRect(48,72,W-96,H-144,5,fill=1,stroke=0)
    c.setFillColor(surface); c.setFont(FONT,11); c.drawString(86,H-92,"04 · SAY HELLO")
    c.setFont(FONT,36); c.drawString(86,H-156,"如果你也在寻找")
    c.drawString(86,H-204,"一个能接住事的人。")
    text(c,86,H-258,"期待内容运营、制片人助理、活动运营与人力资源方向的机会。",12,HexColor("#D9DDE1"),max_width=395)
    c.setFillColor(surface); c.setFont(FONT,15); c.drawString(86,H-332,"rhea_25@163.com")
    cover_image(c,p("photos/contact-portrait.JPG"),572,112,145,270,stroke=False)
    c.setFillColor(HexColor("#D9DDE1")); c.setFont(FONT,9); c.drawCentredString(645,92,"谢谢你读到这里")
    c.showPage()

def build():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    c=canvas.Canvas(str(OUT),pagesize=(W,H),pageCompression=1)
    c.setTitle("柴蕴 - 个人作品集 2026")
    c.setAuthor("柴蕴")
    c.setSubject("内容、活动与人的故事")
    page_cover(c); page_overview(c)
    story_page(c,3,"PROJECT STORY · 01","“童年快乐行，我来保护你”","2024 年春天，我在校青协策划儿童安全科普活动。15 名志愿者、4 个小组，在童前社区落地。我把身体边界保护和性教育加入标准安全科普，并从孩子们口中重新理解了“安全”——也包括不被理解与不敢说出来。", "对人敏感 · 活动策划", "projects/children-class-wide.jpg", [("projects/children-activity-wide.jpg","互动活动现场"),("projects/children-workshop.jpg","用孩子听得懂的方式讲安全")], HexColor("#F3E5D9"))
    story_page(c,4,"PROJECT STORY · 02","从几十人到两百人","六场随机舞蹈，从操场角落的一次尝试，到一套能够持续运转的活动。它不只是热闹的夜晚，也是我持续校准现场、节奏和参与者体验的过程。", "活动制片 · 持续迭代 · 6 场活动 · 40+ 新成员", "projects/random-dance-cover-2026.jpg", [("projects/random-dance-group-day.JPG","白天活动大合照"),("projects/random-dance-group-night.JPG","夜间活动大合照")], HexColor("#DFE5EB"))
    story_page(c,5,"PROJECT STORY · 03","当街舞社遇见机器人","一个没人接住的想法，在两周里变成了 6000 多名观众面前的舞台。我负责连接导演要求、社团能力、成员时间与最终呈现。", "复杂协作 · 项目统筹 · 音乐与选题 · 排练协调 · 编舞调整 · 传播文案", "projects/robot-dance-stage.jpg", [("projects/robot-dance-team.jpg","与机器人共同完成的现场"),("projects/stage-show.jpg","真实舞台呈现")], HexColor("#D9E3ED"))
    story_page(c,6,"AN EARLY ACTION · 高中","让一盒卫生巾，成为可以开口的需要","高中时期，我组织推动由学校与学生会正式举办、安装的卫生巾互助箱项目。它让一个容易被隐藏的需要被看见、被讨论，也被持续回应。", "发现需求 · 从 0 到 1 · 女性关怀", "projects/pad-box.jpg", [("projects/pad-planning.jpg","策划案与宣传材料"),("projects/img-5061.jpg","项目落地记录")], HexColor("#F3E5D9"))
    apparel_page(c,7,"APPAREL ARCHIVE · 01","两代社服，把社团气质穿在身上。","从第一版白色 T 恤到第二版棒球衫，我关心的不只是设计图，也关心它有没有被真的穿上、被记住。",["projects/shirt-v1-design-2026.jpg","projects/shirt-v1-worn.jpg","projects/shirt-v1-detail.png"],["第一版设计图","第一版实穿成果","“藻”与“山”的图形细节"])
    apparel_page(c,8,"APPAREL ARCHIVE · 02","纪念感更强的棒球衫","在参考棒球衫视觉语言的基础上，重新组织黑白条纹、版型、“Lanzao Crew”字样与二十周年标识，强化团队感和纪念属性。",["projects/shirt-v2-design-2026.jpg","projects/shirt-v2-worn-2026.jpg","projects/shirt-v2-cover-group.jpg"],["第二版设计图","第二版实穿成果","成员集体合影"])
    posters=[f"projects/poster-stack-{i:02d}{'-full' if i in (1,7) else ''}.jpg" for i in range(1,9)]
    image_grid_page(c,9,"VISUAL ARCHIVE · 海报档案","每一场活动，都有独一无二的体验。","八张海报与传播物料，记录不同时间、主题和情绪下长出的视觉表达。",posters[:4],4,["蓝藻街舞协会","节目单","随机舞蹈 2025","随舞歌单"],True)
    image_grid_page(c,10,"VISUAL ARCHIVE · 海报档案","从招新到春日现场","同一套活动，在不同的语境里建立各自清晰的视觉记忆。",posters[4:],4,["Random Dance 2026","随舞歌单 2026","蓝藻街舞协会招新","春日随机舞蹈"],True)
    image_grid_page(c,11,"BROCHURE STACK · 三折页","把社团的信息，折进一张纸里。","两套三折页的正反面，从社团介绍到舞种说明，都在有限版面里建立清晰的阅读秩序。",["projects/brochure-2024-front.png","projects/brochure-2024-back.png","projects/brochure-2025-front.jpg","projects/brochure-2025-back.jpg"],2,["2024 正面","2024 背面","2025 正面","2025 背面"],True)
    stage=[f"projects/stage-directed-{i:02d}.jpg" for i in range(1,11)]
    image_grid_page(c,12,"STAGE STACK · 舞台呈现","音乐、影像与身体，在舞台上汇合。","项目职责：导演 · 音乐剪辑 · 背景视频",stage[:5],5,[f"现场 {i:02d}" for i in range(1,6)])
    image_grid_page(c,13,"STAGE STACK · 舞台呈现","灯光、群像与屏幕内容","十张现场照，完整记录从灯光、调度到最终呈现的舞台过程。",stage[5:],5,[f"现场 {i:02d}" for i in range(6,11)])
    about_page(c); contact_page(c)
    c.save()

if __name__ == "__main__": build()
