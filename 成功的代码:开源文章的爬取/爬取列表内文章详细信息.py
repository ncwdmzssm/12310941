#文章详细信息-成功版
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin 
import time 
import random 
from playwright.sync_api import sync_playwright

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:118.0) Gecko/20100101 Firefox/118.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",    # Edge (Windows)
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.1; rv:119.0) Gecko/20100101 Firefox/119.0"
]


df=pd.read_csv("文章基础信息.csv")
link_list=df['link'].tolist()
detail_data = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False,args=["--disable-blink-features=AutomationControlled"])
    page = browser.new_page(user_agent=random.choice(USER_AGENTS))
    # 隐藏自动化痕迹
    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
    """)
    i=0
    for link in link_list:
        i=1
        print(f"正在爬取-{i}")
        page.goto(link, timeout=60000)
        time.sleep(random.uniform(3, 6))
        try:
            # 等待标题元素出现（最长等10秒）
            page.wait_for_selector("div.content", timeout=10000)
            page_content = page.content()
        except Exception as e:
            print("关键元素未加载，跳过该页")
            continue

        soup = BeautifulSoup(page_content, 'html.parser')
        try:
            title=soup.find('span',class_='NLM_article-title hlFld-title').get_text(strip=True) 
            authors=soup.find_all('a',class_='author')
            authors=[a.get_text(strip=True) for a in authors]
            tags=soup.select('div.itemPageRangeHistory span')
            pages=tags[0].get_text(strip=True) if tags else '无页码信息'
            times=tags[1].get_text(strip=True) if len(tags)>1 else '无时间信息'
            journal=soup.find('span',class_="journal-heading").find('a').get_text(strip=True)
            volume=soup.find_all('span',class_="issue-heading")[0].get_text(strip=True)
            abstract=soup.find('p',class_='last').get_text(strip=True)
            keywords=soup.find_all('a',class_='kwd-btn keyword-click')
            keywords=[k.get_text(strip=True) for k in keywords]
            detail_data.append({
                'title': title,
                'authors': authors
                ,'time': times
                ,'journal': journal
                ,'volume': volume
                ,'pages': pages
                ,'abstract': abstract
                ,'keywords': keywords
                ,'link': link
            })
        except Exception as e:  
            print(f"解析文章时出错: {e}")
        i+=1 
        time.sleep(random.uniform(2, 5))
    browser.close()
detail_data=pd.DataFrame(detail_data)
detail_data.to_csv('all_detail.csv', encoding= 'utf-8',index=False)
print("数据已保存到 all_detail.csv")

