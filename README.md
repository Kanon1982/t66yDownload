<h1>草榴社区的爬虫脚本</h1>

本脚本由 `python` 编写，

草榴社区：t66y.com

本脚本根据 `视频的区域分类` 、`种子的下载总量` 、 `论坛帖子发布了多少天` 、 `是否下载破坏版` 的选项，保存磁力到项目路径

注意：只能保存磁力，不能下载bt种子，因为草榴社区，下载种子的话，有反爬机制 <br>
注意：只能保存磁力，不能下载bt种子，因为草榴社区，下载种子的话，有反爬机制 <br>
注意：只能保存磁力，不能下载bt种子，因为草榴社区，下载种子的话，有反爬机制 <br>

<h2>使用前须知：</h2>

<h4>1. 至少需要 `python>=3.11`</h4>

<h4>2. 因为需要 `requests` `beautifulsoup4` `lxml` 这三个库进行安装，可以自行手动安装，或者图省事，也可以在python命令行中执行以下命令：</h4>

    ```bash
     pip install requests beautifulsoup4 lxml
    ```

<h4>3. 如果在封闭地区，比如中国、伊朗、朝鲜、俄罗斯等地区，需要在爬虫过程中，`全程外网环境`。因为，草榴社区只有在外网环境，才可以访问。</h4>

<h4>4. 磁力保存的路径，在项目的根路径下的magnets文件夹中 <br></h4>
   其中，以 `all_magnets.txt`结尾的文件，是本次爬虫遇到的所有的磁力的信息的文件 <br>
   其中，以 `magnets.txt`结尾的文件，是符合用户需求的磁力信息的文件。 <br>
   其中，以 `pure_magnets.txt`结尾的文件，是符合用户需求的磁力的文件，不包含磁力的其他信息。 <br>


<h4>5. 注意：</h4>
   运行完该脚本之后，会在项目根路径下生成 `crawler_record.json` 文件，该文件是用来保存缓存的。<br>
   缓存的作用：假如执行脚本过程中途忽然被停止，再次重新执行脚本的时候，就不会下载之前下载过的磁力文件了。<br>
   如果想清除缓存，或者，从零开始保存磁力的话，直接删除 `crawler_record.json` 就好。


<h2>如何运行：</h2><br>
    <h3>1. 下载 `t66y_bt_crawler.py` 到本地，</h3>
    <p></p><p></p>
    <h3>2. 运行该py脚本：</h3><br>
    &nbsp;&nbsp;&nbsp;&nbsp; A. 交互式运行：<br>
        &nbsp;&nbsp;&nbsp;&nbsp;```bash
        python t66y_bt_crawler.py
        &nbsp;&nbsp;&nbsp;&nbsp;```
        <br>
&nbsp;&nbsp;&nbsp;&nbsp;然后，按照提示进行输入<br><p></p>
&nbsp;&nbsp;&nbsp;&nbsp;B. 命令行参数模式，跳过交互输入。直接用一条命令运行：<br>
        &nbsp;&nbsp;&nbsp;&nbsp;```bash
        python t66y_bt_crawler.py --forum 2 --pages 5 --min-dl 50 --days 2 --no-crack
        &nbsp;&nbsp;&nbsp;&nbsp;```

        
| 参数 | 说明 | 示例 |
| :--- | :--- | :--- |
| `--forum` | 板块编号 (1-6)，0=全部 | `--forum 2` |
| `--min-dl` | 最低下载量 | `--min-dl 50` |
| `--pages` | 按页数爬取 | `--pages 5` |
| `--days` | 按天数爬取（与 `--pages` 二选一） | `--days 2` |
| `--no-crack` | 排除破解版（不加则包含） | `--no-crack` |
