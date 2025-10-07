#开源第一页爬取
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin 
import time 
import random 
from playwright.sync_api import sync_playwright
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36"
]
base_url = "https://www.tandfonline.com/action/showOpenAccess?journalCode=mmis20"
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False,args=["--disable-blink-features=AutomationControlled"])
    page = browser.new_page(user_agent=random.choice(USER_AGENTS))
    page.goto("https://www.tandfonline.com/action/showOpenAccess?journalCode=mmis20")
    time.sleep(random.uniform(3, 6))
    try:
    # 等待标题元素出现（最长等10秒）
        page.wait_for_selector("div.art_title span", timeout=10000)
        page_content = page.content()
    except Exception as e:
        print("关键元素未加载，跳过该页")
    page.screenshot(path="example.png")
    page_content = page.content()
    browser.close()

soup3=BeautifulSoup(page_content, 'html.parser')
arts=soup3.select("div.articleEntryContainer")
articles=[]
page_num=1
for article in arts:
    try:
        #find都是输出HTML,不能直接用
        art_title=article.find('div', class_='art_title').find('span').get_text(strip=True)
        art_link=article.find('div', class_='art_title').find('a')['href']
        articles.append({'title':art_title,'link':urljoin(base_url,art_link)})
    except Exception as e:
        print(f"解析文章时出错: {e}")

    time.sleep(random.uniform(1, 3))  # 随机延时1到3秒，模拟人类行为，避免被封IP
df1=pd.DataFrame(articles)
df1.to_csv('文章链接.csv', encoding= 'utf-8',index=False)
print("数据已保存到 文章链接.csv")

print("爬取完成")
