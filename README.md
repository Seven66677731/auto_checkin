# 基于青龙面板的自动签到
[![996.icu](https://img.shields.io/badge/link-996.icu-red.svg)](https://996.icu)
![Python](https://img.shields.io/badge/python-3.7+-blue) 


## 基础配置

1. 确保你已安装并配置好[青龙面板](https://github.com/whyour/qinglong)
2. 在青龙面板的```依赖管理```中，新建类型为```Python3```的依赖，名称为```requests```
   ![requests.png](assets%2Frequests.png)
3. 在青龙面板的```订阅管理```中，创建订阅，将下面内容粘贴
   ```
   ql repo https://github.com/Seven66677731/auto_checkin.git
   ```
   然后名称自定，定时类型选```interval```,文件后缀中添加```py```
   ,把自动添加任务和自动删除任务选项取消勾选![img.png](assets%2Fimg.png)![img_1.png](assets%2Fimg_1.png)
   点击确定保存后，运行该订阅。
4. 需要推送服务的，打开[pushplus](https://www.pushplus.plus/push1.html),复制你的token，在青龙面板中```环境变量```
   中添加```pushplus_token```值为你的token
5. 在青龙面板的```脚本管理```中，打开```Seven66677731_auto_checkin```文件夹中的```main.py```
   文件。编辑该文件选择你需要的签到的软件![img_2.png](assets%2Fimg_2.png)
   根据下方说明，配置你要签到应用的相关配置
6. 最后在青龙面板中的```定时任务```中创建任务
   名称自定，命令输入
   ```
    task Seven66677731_auto_checkin_main/main.py
   ```
   定时规则```45 7 * * *```(每天7点45分执行)，定时规则可以自行修改。
   保存运行即可。
   ![img_3.png](assets%2Fimg_3.png)

## 微博超话签到

1. 手机登录微博打开超话列表，使用抓包软件进行抓包
2. 搜索```cardlist```
3. 找到以```https[:]//api.weibo.cn/2/cardlist```开头的链接
4. 将请求参数中的```gsid ``` ```from``` ```s``` ```uid```复制
5. 在青龙面板的```环境变量```中添加```weibo_gsid``` ```weibo_from``` ```weibo_s``` ```weibo_uid```
   值为4个参数的值

## 阿里云盘签到

1. 登录[阿里云盘](https://www.aliyundrive.com/drive/),控制台粘贴
   ```
   copy(JSON.parse(localStorage.token).refresh_token); console.log(JSON.parse(localStorage.token).refresh_token);
   ```
   将结果复制到剪贴板中。
2. 在青龙面板的```环境变量```中添加```refresh_token```值为刚刚复制token

## 申明

- 本项目仅做学习交流, 禁止用于各种非法途径
- 项目中的所有内容均源于互联网, 仅限于小范围内学习参考,
  如有侵权请第一时间联系[本项目作者](https://github.com/Seven66677731)进行删除

## 鸣谢

特别感谢以下作者及所开发的程序，本项目参考过以下几位开发者代码及思想。

- @mrabit:[mrabit/aliyundriveDailyCheck](https://github.com/mrabit/aliyundriveDailyCheck)
- @script:[arcturus-script/weibo](https://github.com/arcturus-script/weibo)