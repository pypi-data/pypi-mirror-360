import calendar
import datetime
class DateUtils:
    @staticmethod
    def get_months_in_range(start_date, end_date, format_type=1):
        """
        :param start_date:
        :param end_date:
        :param format_type: 1： '2024-04' 2:4月
        :return:
        """
        # 转换为 datetime 对象
        start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.datetime.strptime(end_date, "%Y-%m-%d")

        # 确保起始日期在结束日期之前
        if start > end:
            start, end = end, start

        # 获取每个月的日期
        months = []
        current = start

        while current <= end:
            if format_type == 1:
                months.append(current.strftime("%Y-%m"))  # 以 "YYYY-MM" 格式添加月份
            else:
                months.append(f"{current.month}月")
            # 跳到下一个月
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)
        return months

    @staticmethod
    def get_years_in_range(start_date, end_date):
        # 转换为 datetime 对象
        start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.datetime.strptime(end_date, "%Y-%m-%d")

        # 确保起始日期在结束日期之前
        if start > end:
            start, end = end, start

        # 获取每年的日期
        years = []
        current = start

        while current <= end:
            years.append(current.year)
            # 跳到下一个年份
            current = current.replace(year=current.year + 1)

        return years

    @staticmethod
    def get_days_in_intervals(start_date, end_date, interval_days=7, format_str=None):
        # 转换为 datetime 对象
        start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.datetime.strptime(end_date, "%Y-%m-%d")

        # 确保起始日期在结束日期之前
        if start > end:
            start, end = end, start

        # 获取时间区间内以7天为间隔的日期列表
        intervals = []
        current = start

        while current + datetime.timedelta(days=interval_days) <= end:
            start_time = current.strftime("%Y-%m-%d")
            end_time = (current + datetime.timedelta(days=interval_days - 1)).strftime("%Y-%m-%d")
            if format_str:
                intervals.append(f"{start_time}{format_str}{end_time}")
            else:
                intervals.append({"Start": start_time, "End": end_time})   #添加7天区间
            current += datetime.timedelta(days=interval_days)  # 移动到下一个7天区间

        # 处理最后的不足7天的区间
        if current <= end:
            start_time = current.strftime("%Y-%m-%d")
            end_time = end.strftime("%Y-%m-%d")
            if format_str:
                intervals.append(f"{start_time}{format_str}{end_time}")
            else:
                intervals.append({"Start": start_time, "End": end_time})  # 如果剩余时间不满7天，直接返回剩余时间
        return intervals

    @staticmethod
    def get_days_in_range(start_date, end_date):
        # 转换为 datetime 对象
        start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.datetime.strptime(end_date, "%Y-%m-%d")

        # 确保起始日期在结束日期之前
        if start > end:
            start, end = end, start

        # 获取每一天的日期
        days = []
        current = start

        while current <= end:
            days.append(current.strftime("%Y-%m-%d"))  # 添加当前日期
            current += datetime.timedelta(days=1)  # 增加一天

        return days

    @staticmethod
    def get_half_months_in_range(start_date, end_date, format_str=None):
        # 转换为 datetime 对象
        start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.datetime.strptime(end_date, "%Y-%m-%d")

        # 确保起始日期在结束日期之前
        if start > end:
            start, end = end, start

        half_months = []
        current = start

        # 调整开始日期：如果开始日期不是1号或16号，调整为1号或16号
        if current.day > 15:
            current = current.replace(day=16)
        else:
            current = current.replace(day=1)

        while current <= end:
            # 获取当前月的最后一天
            last_day_of_month = calendar.monthrange(current.year, current.month)[1]
            if current.day == 1:
                # 前半月：1号到15号
                first_half_end = current.replace(day=15)
                if format_str:
                   half_months.append(f"{current.strftime('%Y-%m-%d')}{format_str}{first_half_end.strftime('%m-%d')}")
                else:
                    half_months.append({
                        "Start": current.strftime('%Y-%m-%d'),
                        "End": first_half_end.strftime('%Y-%m-%d')
                    })
                current = current.replace(day=16)  # 更新为后半月的开始日期
            else:
                # 后半月：16号到月底
                second_half_end = current.replace(day=last_day_of_month)
                if format_str:
                    half_months.append(f"{current.strftime('%Y-%m-%d')}{format_str}{second_half_end.strftime('%m-%d')}")
                else:
                    half_months.append({
                        "Start": current.strftime('%Y-%m-%d'),
                        "End": second_half_end.strftime('%Y-%m-%d')
                    })
                # 更新为下个月的1号
                current = (current.replace(day=1) + datetime.timedelta(days=31)).replace(day=1)

        return half_months

    def generate_axis(self, start_date, end_date, axis_type):
        if axis_type == 'month':
            return self.get_months_in_range(start_date, end_date, 2)
        elif axis_type == 'year':
            return self.get_years_in_range(start_date, end_date)
        elif axis_type == 'day':
            return self.get_days_in_range(start_date, end_date)
        elif axis_type == 'half_month':
            return self.get_half_months_in_range(start_date, end_date, '~')
        elif axis_type == 'week':
            return self.get_days_in_intervals(start_date, end_date, 7, '~')
        else:
            raise ValueError("Invalid axis type")


