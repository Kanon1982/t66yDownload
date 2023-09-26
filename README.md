<h2>草榴社区的爬虫脚本</h2>

本脚本由 `python` 和 `selenium` 编写，

1.需要 `全程外网` 环境(因为草榴只有在外网才可以访问)
2.如果选择`直接下载种子`需要暂时卸载迅雷(执行完脚本，再安装即可)，因为下载种子的时候，浏览器会调用外部的迅雷，导致程序卡死。

草榴社区：t66y.com

本脚本根据 `视频的区域分类` 、`种子下载总量` 、 `论坛帖子发布了多少天` 、 `是否下载破坏版` 、 `直接下载种子or保存磁力链接到指定目录` 批量下载bt种子

使用前须知：

1. 至少需要 `python 3.8.10`，以及 `selenium 4.4.3`
  
2. 需要根据自己的浏览器的 `类型` 和 `版本` 下载相应的 `webdriver驱动`，并且放在python解释器的 `根目录`
3. 本脚本是默认是`Chrome`浏览器，如需使用其他浏览器，请修改 `main.py` 第 `33` 行
   
   
   [Web Driver下载地址](https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/)，下载链接在本链接页尾
   
   
   
   ```yaml
   # Firefox浏览器
   driver = webdriver.Firefox()
   ```
   
  
   ```yaml
   # Chromium Edge浏览器
   driver = webdriver.Edge("这里写Edge WebDriver路径")
   ```
   
   
4. 如果，选择保存磁力链接，默认的保存路径是 `c:/t66y.com.txt`



使用时，使用`pycharm`运行main.py文件即可
