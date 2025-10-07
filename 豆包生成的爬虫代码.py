import time
import random
import pandas as pd
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# 随机用户代理列表（覆盖不同设备和浏览器）
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36"
]

# 模拟人类滚动行为（随机滚动+停顿）
def human_scroll(page):
    # 随机滚动次数（2-4次）
    for _ in range(random.randint(2, 4)):
        # 每次滚动随机距离（100-600像素）
        scroll_distance = random.randint(100, 600)
        page.mouse.wheel(0, scroll_distance)
        # 滚动后停顿（模拟阅读，1-3秒）
        time.sleep(random.uniform(1, 3))
    # 30%概率轻微回滚（更自然）
    if random.random() < 0.3:
        page.mouse.wheel(0, -random.randint(50, 150))
        time.sleep(random.uniform(0.5, 1.5))

base_url = "https://www.tandfonline.com/action/showOpenAccess?journalCode=mmis20"
current_url = base_url
all_articles = []

with sync_playwright() as p:
    # 启动浏览器（禁用自动化标识，更难被检测）
    browser = p.chromium.launch(
        headless=False,
        args=["--disable-blink-features=AutomationControlled"]
    )
    # 新建页面（随机用户代理+模拟桌面分辨率）
    page = browser.new_page(
        user_agent=random.choice(USER_AGENTS),
        viewport={"width": 1920, "height": 1080}
    )
    # 隐藏自动化痕迹
    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
    """)

    while current_url:
        print(f"正在爬取页面: {current_url}")
        # 访问页面（模拟人类输入网址后的加载等待）
        page.goto(current_url, wait_until="networkidle")
        time.sleep(random.uniform(2, 4))  # 页面加载后停顿
        
        # 模拟人类浏览：随机滚动页面
        human_scroll(page)
        try:
            # 等待标题元素出现（最长等10秒）
            page.wait_for_selector("div.art_title span", timeout=10000)
            page_content = page.content()
        except Exception as e:
            print("关键元素未加载，跳过该页")
            continue

        soup = BeautifulSoup(page_content, 'html.parser')
        articles = soup.select("div.articleEntryContainer")
        for article in articles:
            try:
                art_title = article.find('div', class_='art_title').find('span').get_text(strip=True)
                art_authors = [auth.get_text(strip=True) for auth in article.find('div', class_='articleEntryAuthor').find_all('span')]
                art_date = article.find('span', class_='article-date').get_text(strip=True)
                all_articles.append({"title": art_title, "authors": art_authors, "date": art_date})
            except Exception as e:
                print(f"解析文章出错: {e}")
        
        # 查找并点击下一页（模拟人类点击行为）
        next_btn = page.locator('a.nextPage.js__ajaxSearchTrigger')
        if next_btn.count() > 0:  # 检查下一页按钮是否存在
            # 获取按钮位置，计算点击偏移（避免精确点击中心）
            btn_bbox = next_btn.bounding_box()
            if btn_bbox:
                # 随机偏移量（±10像素内）
                click_x = btn_bbox["x"] + random.randint(5, int(btn_bbox["width"]) - 5)
                click_y = btn_bbox["y"] + random.randint(5, int(btn_bbox["height"]) - 5)
                
                # 模拟鼠标从随机位置移动到按钮（非直线移动）
                start_x = random.randint(100, 300)
                start_y = random.randint(200, 500)
                page.mouse.move(start_x, start_y)  # 起始位置
                time.sleep(random.uniform(0.3, 0.8))  # 停顿后再移动
                
                # 分2-3步移动到目标（模拟犹豫）
                for _ in range(random.randint(2, 3)):
                    mid_x = start_x + (click_x - start_x) * random.uniform(0.3, 0.7)
                    mid_y = start_y + (click_y - start_y) * random.uniform(0.3, 0.7)
                    page.mouse.move(mid_x, mid_y)
                    time.sleep(random.uniform(0.1, 0.3))
                page.mouse.move(click_x, click_y)  # 最终移动到点击位置
                
                # 点击（带随机延迟，模拟真实点击速度）
                time.sleep(random.uniform(0.1, 0.4))
                page.mouse.click(click_x, click_y, delay=random.randint(50, 200))  # 用字符串"left"默认左键
                
                # 切换页面后等待（模拟阅读时间）
                time.sleep(random.uniform(6, 10))
                current_url = page.url  # 直接从页面获取当前URL（避免手动拼接错误）
        else:
            current_url = None  # 无下一页时结束循环
    
    browser.close()

# 保存数据
pd.DataFrame(all_articles).to_csv('data.csv', encoding='utf-8', index=False)
print("数据已保存到 data.csv")