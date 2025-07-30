import random
import string
from collections.abc import Sequence
from _datetime import datetime,timedelta

class Randomer:
    """测试数据生成函数"""

    @staticmethod
    def random_int(m=0, n=100):
        """生成 (m,n)之间的一个整数"""
        return  random.randint(m, n)

    @staticmethod
    def random_float(m=0, n=100, l=2):
        """生成 (m,n)之间的一个小数, 保留l位小数"""
        return  round(random.uniform(m, n), l)

    @staticmethod
    def random_str(k=10):
        """生成 (m,n)之间的一个小数, 保留n位小数"""
        return  "".join(random.choices(string.ascii_letters+string.digits, k=k))

    @staticmethod
    def random_item(*items: Sequence):
        """用于选择随机枚举值, 从提供的集合里随机挑选一个选择"""
        if len(items) ==1:
            return random.choice(items[0])
        return  random.choice(items)

    @staticmethod
    def _random_time(days: int) -> datetime :
        """用于选择随机枚举值, 从提供的集合里随机挑选一个选择"""
        now = datetime.now()

        if days > 0:
            random_days = random.randint(0, days)  # 在未来0到days天内生成
        else:
            random_days = random.randint(days, 0)  # 在过去abs(days)天内生成
        random_time = now + timedelta(days=random_days)

        return random_time

    @staticmethod
    def random_date(days: int =100) -> str:
        """生成 (现在, days) 区间的一个日期, 负数则为过去的时间
            eg:2025-01-25
        """
        return Randomer._random_time(days).strftime("%Y-%m-%d")

    @staticmethod
    def random_datetime(days: int =100) -> str:
        """生成 (现在, days) 区间的一个日期时间, 负数则为过去的时间
            eg: 2025-01-17 11:56:27
        """
        return Randomer._random_time(days).strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def random_digit_string(length):
        return ''.join(str(random.randint(0, 9)) for _ in range(length))

