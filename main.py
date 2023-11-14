import random
import time

import aliyundrive_check_in
import weibo_supertopic_chickin

if __name__ == '__main__':
    print(" 微博超话任务 ".center(30, "#"))
    weibo_supertopic_chickin.main()
    print(" 结束微博超话任务 ".center(30, "#"))
    time.sleep(random.randint(3, 5))
    print(" 阿里云盘任务 ".center(30, "#"))
    aliyundrive_check_in.main()
    print(" 结束阿里云盘任务 ".center(30, "#"))
