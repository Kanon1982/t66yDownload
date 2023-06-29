from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import timedelta, datetime

import time
import sys

"""
    配置项
"""

download_min = 200  # 最小可选的访问量
download_max = 10000  # 最大可选的访问量

page_min = 1  # 最少下载页数(含该页数)
page_max = 15  # 最大下载页数(含该页数)

day_min = 1  # 最少下载天数(含该天数)
day_max = 30  # 最多下载天数(含该天数)


# 注意：等待时长不可以 删除 或者 太小，否则会被网站发现是在爬虫，导致报错
implicitly_time = 15  # 隐式等待时长
sleep_time = 3  # 强制等待时长



# web driver 驱动
driver = webdriver.Chrome()
driver.get("https://t66y.com/index.php")  # 登录 t66y.com 主页


"""
    置顶异常，用于后续可能出现的报错
"""

class ValueTooSmallOrBig(Exception):
    pass

def is_exist_element(elem1, elem2_xpath_str):
    """
    检验 elem1 中 是否含有 elem2 元素
    :param elem1: 父元素
    :param elem2_xpath_str: 选择子元素的xpath字符串
    :return: elem1中 是否含有 elem2？
    """
    s = elem1.find_elements(By.XPATH, elem2_xpath_str)
    if len(s) == 0:
        print("不存在元素")
        return False
    if len(s) >= 1:
        print("存在元素")
        return True

def get_download_days():
    """
    得到下载天数的方法
    :return: 返回下载的天数
    """
    download_days = 3   # 默认为 3
    download_days_str = "3"     # 默认为 3
    while True:
        print(f'请输入要下载前几天的bt种子？({day_min}~{day_max}之间)')
        download_days_str = input()      # 要下载的天数字符串
        try:
            download_days = int(download_days_str)
            if (download_days < day_min) or (download_days > day_max):
                raise ValueTooSmallOrBig
            else:
                return download_days
        except ValueTooSmallOrBig:
            print(f'输入的数字不合法，应在{day_min}~{day_max}之间')
        except Exception:
            print('您输入的并非数字，请重新输入！！！')


def get_days_list(download_days):
    """
    根据 下载前?页 生成 时间列表
    :param download_days: 下载前？天的bt种子
    :return: 返回 前？天 的字符串
    """
    days_list = list()  # 日期str的列表
    if download_days >= 1:
        days_list = list()  # 日期str的列表
        day_flag = 0
        while day_flag < download_days:
            days_list.append((datetime.today() - timedelta(days=day_flag)).strftime('%Y-%m-%d'))
            day_flag += 1
    # 打印时间列表中的字符串
    for day_str in days_list:
        print(day_str)
    return days_list


def download_by_days_1_page(download_input, down_break, days_list):
    keep_next_page = False  # 是否继续下一页？ 默认为False

    # 获取最后一行的日期span元素的title属性
    last_tr_span_title = driver.find_element(By.CSS_SELECTOR, "#tbody > tr:last-child td:nth-child(3) div span")\
        .get_attribute("title")
    print(last_tr_span_title)    # 打印该页最后一行的发布日期(字符串类型)

    # 字符串类型查看本页最后一行的日期，是否需要翻页
    for day_str in days_list:
        if last_tr_span_title.find(day_str) != -1:
            keep_next_page = True
            print(day_str + "在字符串" + last_tr_span_title + "中")

    driver.implicitly_wait(implicitly_time)  # 等待页面加载完成 不可以删除~~
    time.sleep(sleep_time)

    down_tr_s = driver.find_elements(By.CSS_SELECTOR, "#tbody tr")  # 获取每一行的tr

    is_next_tr = True  # 是否下一行

    tr_num = 0  # 行号计数器，用于下面的for循环

    for down_tr in down_tr_s:  # 遍历每一个 tr 标签
        print("\n")     # 用于打印每个种子详细信息的时候，换行

        # 获取下载量td元素
        down_num_td = down_tr.find_element(By.XPATH, "./td[5]")
        # 获取种子title的a标签
        bt_title_tag = down_tr.find_element(By.XPATH, "./td[2]/h3/a")
        # 获取种子日期标签
        bt_day_tag = down_tr.find_element(By.XPATH, "./td[3]/div/span")
        # 获取种子日期标签的 title属性
        bt_day_tag_title = down_tr.find_element(By.XPATH, "./td[3]/div/span").get_attribute("title")

        # print(down_num_td.text)
        # print(bt_title_tag.text)
        # print(bt_day_tag.text)
        # print(bt_day_tag_title)

        # 检验标题是否包含孙元素font (因为如果包含的话，说明该行tr是公告，不是种子)
        # 注意：不可以跳过 Top-marks 字符串检验，否则会 极其极其慢 !!!
        if bt_day_tag.text.find("Top-marks") != -1:
            if is_exist_element(bt_title_tag, "./descendant::font"):
                print("含有font标签，本行为公告，跳过该行")
                tr_num += 1
                continue

        if down_num_td.text == '--':  # 如果没有下载量，跳过该次循环
            tr_num += 1
            continue

        # 注意：这里的两个“破解”看上去相同，但是分别是 简体 和 繁体
        # ("破解" or "破坏" or "破壊" or "破解")
        if (not down_break) and (
                "破解" in bt_title_tag.text or
                "破坏" in bt_title_tag.text or
                "破壊" in bt_title_tag.text or
                "破解" in bt_title_tag.text
        ):  # 如果标题包含破坏or破解，跳过该次循环
            tr_num += 1
            continue

        down_num = int(down_num_td.text)  # 将str的下载量转换为int类型
        if down_num < download_input:  # 如果下载量低于标准，则跳过该次循环
            tr_num += 1
            continue

        is_include_the_day = False  # 根据日期，判断种子是否是需要下载的？
        for day_str in days_list:
            if bt_day_tag_title.find(day_str) != -1:
                is_include_the_day = True
                print(day_str + "在字符串" + bt_day_tag_title + "中")
                tr_num += 1  # 如果tr符合日期，则 行号flag增加
                break
        else:
            tr_num += 1

        if is_include_the_day:
            # 显示bt种子的详细信息
            print(down_num_td.text)
            print(bt_title_tag.text)
            print(bt_day_tag.text)
            print(bt_day_tag_title)

            bt_title_tag.click()  # 进入视频介绍详情页

            windows = driver.window_handles
            driver.switch_to.window(windows[-1])

            try:
                driver.implicitly_wait(implicitly_time)
                time.sleep(sleep_time)
                click_ele_s = driver.find_elements(By.CSS_SELECTOR, 'a[href*="rmdown.com/link.php?hash="]')
                click_ele_s[0].click()
                driver.implicitly_wait(implicitly_time)
                time.sleep(sleep_time)
            except Exception as e:
                print("报错：", e)
                windows = driver.window_handles
                driver.close()
                driver.switch_to.window(windows[0])
                continue

            windows = driver.window_handles
            driver.switch_to.window(windows[-1])

            driver.implicitly_wait(implicitly_time)
            time.sleep(sleep_time)
            driver.find_element(By.CSS_SELECTOR, 'button[title="Download file"]').click()
            driver.close()

            windows = driver.window_handles
            driver.switch_to.window(windows[-1])
            driver.close()

            windows = driver.window_handles
            driver.switch_to.window(windows[0])

            print(f'{tr_num}----------{down_num_td.text}')  # 打印种子的真实下载数量

    return keep_next_page


def download_by_days(download_input, down_break):
    """
    下载前？天的种子 函数
    :param download_days: 下载前多少天
    :param download_input:  下载量高于多少？
    :param down_break: 是否下载破坏版？
    """
    download_days = get_download_days()  # 获取下载前?天的bt种子
    days_list = get_days_list(download_days)  # 得到日期的list列表

    page_num = 1    # 目前的页数是多少？

    while True:
        keep_next_page = download_by_days_1_page(download_input, down_break, days_list)

        page_input = driver.find_element(By.CSS_SELECTOR, 'a[class="w70"] input')
        page_num += 1
        page_input.click()
        page_input.clear()
        page_input.send_keys(str(page_num))
        page_input.send_keys(Keys.ENTER)
        time.sleep(5)

        if not keep_next_page:      # 如果不继续，则打断本循环
            break



def main_func():
    """
        选择区域模块
    """

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
            7.AI破解原创区
            0.退出
            ''')

        choice = input().strip()
        # print(choice)
        if choice in ("1", "2", "3", "4", "5", "6", "7"):  # 选择区域后，推出当前循环
            break
        elif choice == "0":  # 选择 0 后，终止程序
            sys.exit(0)
        else:  # 输入错误后，重新进入循环
            print("您输入有误，请重新输入")
            time.sleep(2)  # 暂停 2 秒钟

    print(choice)

    # 根据输入内容 进入
    driver.find_element(By.CSS_SELECTOR, "#cate_1 tr:nth-child(" + choice + ") th h2 a").click()

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
        是否下载破坏版
    """

    down_break = False  # 是否下载破坏版 默认：不下载
    while True:
        down_break_str = input("是否下载破坏(破解)版? (y/n)")
        if down_break_str.strip().upper() == "Y":
            down_break = True
            break
        elif down_break_str.strip().upper() == "N":
            break
        else:
            print('您的输入有误，请重新输入！！！')

    # 进入下载方法
    download_by_days(download_input, down_break)

if __name__ == '__main__':
    main_func()

