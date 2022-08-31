from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import time
import sys

"""
    配置项
"""

download_min = 200  # 最小可选的访问量
download_max = 10000  # 最大可选的访问量

total_page_num_min = 1  # 最少下载页数(含该页数)
total_page_num_max = 15  # 最大下载页数(含该页数)


"""
    置顶异常，用于后续可能出现的报错
"""
class ValueTooSmallOrBig(Exception):
    def __init__(self):
        pass

"""
    选择区域模块
"""
driver = webdriver.Firefox()
driver.get("https://t66y.com/index.php")  # 登录 t66y.com 主页

choice = "1"  # 选择主题区域的默认值为 "1"
while True:
    print('''
    请输入数字：
    1.亚洲无码
    2.亚洲有码
    3.欧美原创
    4.动漫原创
    5.国产原创
    6.中字原创(中文字幕)
    0.退出
    ''')

    choice = input().strip()
    # print(choice)
    if choice in ("1", "2", "3", "4", "5", "6"):  # 选择区域后，推出当前循环
        break
    elif choice == "0":  # 选择 0 后，终止程序
        sys.exit(0)
    else:  # 输入错误后，重新进入循环
        print("您输入有误，请重新输入")
        time.sleep(2)  # 暂停 2 秒钟

print(choice)

driver.find_element(By.CSS_SELECTOR, "#cate_1 tr:nth-child(" + choice + ") th h2 a").click()  # 根据输入内容 进入 相应分区

"""
    进入分区之后
"""

download_input = 5000
download_input_str = "5000"  # 默认的bt下载量

while True:  # 判断输入的浏览量是否合法
    print(f"请输入要高于多少浏览量才下载？({download_min}~{download_max}之间)")
    download_input_str = input()
    try:
        download_input = int(download_input_str)
        if (download_input < download_min) or (download_input > download_max):
            raise ValueTooSmallOrBig
        else:
            break
    except ValueTooSmallOrBig:
        print(f"请输入({download_min}~{download_max}之间)的数字")
    except Exception as e:
        print("输入的并非数字！！！")
        print(e.args)


"""
    要下载前多少页的bt种子
"""
total_page_num = 1  # 下载 几页 的bt种子，默认 1 页
total_page_num_str = "1"
while True:
    print(f'请输入要下载前几页的内容？({total_page_num_min}~{total_page_num_max}之间)')
    total_page_num_str = input()
    try:
        total_page_num = int(total_page_num_str)
        if (total_page_num < total_page_num_min) or (total_page_num > total_page_num_max):
            raise ValueTooSmallOrBig
        else:
            break
    except ValueTooSmallOrBig:
        print(f'请输入({total_page_num_min}~{total_page_num_max}之间)的数字')
    except Exception as e:
        print('输入的并非数字！！！')
        print(e.args)


def download_func():
    """
    下载符合规则的bt种子方法
    """

    driver.implicitly_wait(20)  # 等待页面加载完成 不可以删除~~

    down_td_s = driver.find_elements(By.CSS_SELECTOR, "#tbody tr td:nth-child(5)")

    tr_num = 1
    tr_num_list = list()

    for down_td in down_td_s:
        if down_td.text == '--':
            continue
        down_count = int(down_td.text)

        if down_count >= download_input:
            down_tr = down_td.find_element(By.XPATH, "..")
            down_tr.find_element(By.XPATH, "./td[2]/h3/a").click()

            windows = driver.window_handles
            driver.switch_to.window(windows[-1])

            try:
                driver.implicitly_wait(20)
                driver.find_element(By.CSS_SELECTOR, 'a[href*="rmdown.com/link.php?hash="]').click()
                driver.implicitly_wait(20)
            except Exception as e:
                print("报错：", e)
                windows = driver.window_handles
                driver.close()
                driver.switch_to.window(windows[0])
                continue

            windows = driver.window_handles
            driver.switch_to.window(windows[-1])

            driver.implicitly_wait(20)
            driver.find_element(By.CSS_SELECTOR, 'button[title="Download file"]').click()
            driver.close()

            windows = driver.window_handles
            driver.switch_to.window(windows[-1])
            driver.close()

            windows = driver.window_handles
            driver.switch_to.window(windows[0])

            tr_num_list.append(tr_num)
            print(f'{tr_num}----------{down_count}')  # 打印种子的真实下载数量
        tr_num += 1



while total_page_num_min <= total_page_num:

    download_func()     # 执行下载函数

    # windows = driver.window_handles         # 切换回列表页
    # driver.switch_to.window(windows[0])

    # 获取当前页码，并 下一页
    total_page_num_min += 1
    page_input = driver.find_element(By.CSS_SELECTOR, 'a[class="w70"] input')
    page_input.click()
    page_input.clear()
    page_input.send_keys(str(total_page_num_min))
    page_input.send_keys(Keys.ENTER)
    time.sleep(5)







