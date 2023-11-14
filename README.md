# 基于青龙面板的自动签到

## 基础配置

1. 确保你已安装并配置好[青龙面板](https://github.com/whyour/qinglong)
2. 在青龙面板的```依赖管理```中，新建类型为```Python3```的依赖，名称为```requests```
   ![requests.png](assets%2Frequests.png)
3. 在青龙面板的```订阅管理```中，创建订阅，将下面内容粘贴
   ```ql repo https://github.com/Seven66677731/auto_checkin.git```
   然后名称自定，定时类型选```interval```,文件后缀中添加```py```
   ,把自动添加任务和自动删除任务选项取消勾选![img.png](assets%2Fimg.png)![img_1.png](assets%2Fimg_1.png)
   点击确定保存后，运行该订阅。
4. 需要推送服务的，打开[pushplus](https://www.pushplus.plus/push1.html),复制你的token，在青龙面板中```环境变量```
   中添加```pushplus_token```值为你的token
5. 最后在青龙面板的```脚本管理```中，打开```Seven66677731_auto_checkin```文件夹中的```main.py```
   文件。编辑该文件选择你需要的签到的软件![img_2.png](assets%2Fimg_2.png)
   根据下方说明，配置你要签到应用的相关配置

## 微博超话签到

## 阿里云盘签到