import random
import time

import aliyundrive_check_in
import weibo_supertopic_chickin

if __name__ == '__main__':
    weibo_supertopic_chickin.main()
    time.sleep(random.randint(3, 5))
    aliyundrive_check_in.main()
