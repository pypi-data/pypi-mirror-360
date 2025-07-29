# ClassIn API - eeo

**如果你有任何疑问，可以通过eeoapisupport@eeoa.com联系我们**

**If you have any questions you can contact us at eeoapisupport@eeoa.com**

**ClassIn APIDoc：https://docs.eeo.cn/api/**

**GitHub：https://github.com/Qingche99/eeoAPI**

## Installation

```sh
pip install eeo
```

## Simple Usage Example

```python

import eeo


if __name__ == '__main__':
    sid = 123456  # 学校账号UID
    secret = '2222BBC'  # 学校API secret
    api_sender = eeo.API(school_uid=sid, school_secret=secret)
    api_sender.register(account, name, pwd, addToSchoolMember)
```