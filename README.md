<h2>草榴社区的爬虫脚本</h2>

本脚本由 `python` 和 `selenium` 编写

草榴社区：t66y.com

本脚本根据 `视频的区域` 、`种子下载总量` 、 `论坛帖子的前多少页数` 、 `是否下载破坏版` 批量下载bt种子

使用前须知：

1. 至少需要 `python 3.8`，以及 `selenium 4.4.3`
  
2. 需要根据自己的浏览器的 `类型` 和 `版本` 下载相应的 `webdriver驱动`，并且放在python解释器的 `根目录`
   本脚本是默认是`Chrome`浏览器，如需使用其他浏览器，请修改 `main.py` 第 `33` 行
   
   
   [Web Driver下载使用说明地址](https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/)
   
   
   
   ```yaml
   Firefox浏览器
   driver = webdriver.Firefox()
   ```
   
  
   ```yaml
   Chromium Edge浏览器
   driver = webdriver.Edge("这里写Edge WebDriver路径")
   ```
   
   
3. 脚本在执行的过程中，需要 `全程外网` 环境(因为草榴只有在外网才可以访问)



使用时，使用`pycharm`运行main.py文件即可
