from datetime import datetime, timezone, timedelta
from typing import Optional


class BaseTime(object):
    @staticmethod
    def get_utc_now() -> datetime:
        """获取当前UTC时间"""
        return datetime.now(timezone.utc)

    @staticmethod
    def to_beijing_time(dt: datetime) -> datetime:
        """将datetime对象转换为北京时间(UTC+8)"""
        return dt.astimezone(timezone(timedelta(hours=8)))

    @staticmethod
    def get_current_beijing_time() -> datetime:
        """获取当前北京时间"""
        return BaseTime.to_beijing_time(BaseTime.get_utc_now())

    @staticmethod
    def get_beijing_time_str(format: str = "%Y-%m-%d %H:%M:%S") -> str:
        """
        获取当前北京时间的字符串表示
        :param format: 时间字符串的格式 格式为'YYYY-MM-DD HH:MM:SS'
        """
        beijing_time = BaseTime.get_current_beijing_time()
        return beijing_time.strftime(format)

    @staticmethod
    def get_current_month_str() -> str:
        """获取当前月份的字符串表示，格式为'YYYYMM'"""
        beijing_time = BaseTime.get_current_beijing_time()
        return beijing_time.strftime("%Y%m")

    @staticmethod
    def parse_beijing_time(time_str: str, format: str = "%Y-%m-%d %H:%M:%S") -> datetime:
        """
        解析时间字符串为北京时间的datetime对象

        :param time_str: 时间字符串
        :param format: 时间字符串的格式
        :return: 带有时区信息的datetime对象(UTC+8)
        """
        dt = datetime.strptime(time_str, format)
        return dt.replace(tzinfo=timezone(timedelta(hours=8)))

    @staticmethod
    def get_time_difference(time_str: str) -> timedelta:
        """
        计算当前时间与给定时间字符串的时间差

        :param time_str: 时间字符串，格式为"YYYY-MM-DD HH:MM:SS"
        :return: timedelta对象，表示时间差
        """
        current_time = BaseTime.get_current_beijing_time()
        target_time = BaseTime.parse_beijing_time(time_str)
        difference = current_time - target_time
        # print(f"时间差: {difference}")
        # print(f"总秒数: {difference.total_seconds()}秒")
        # print(f"天数: {difference.days}天")
        # print(f"小时数: {difference.total_seconds() / 3600:.2f}小时")
        # print(f"分钟数: {difference.total_seconds() / 60:.2f}分钟")

        return difference

    @staticmethod
    def is_hour_changed(last_time_str: str) -> bool:
        """
        检查最后一次记录时间与当前时间是否跨越了小时边界

        :param last_time_str: 最后一次记录的时间字符串，格式为"YYYY-MM-DD HH:MM:SS"
        :return: True表示跨越了小时边界，False表示仍在同一小时内
        """
        current_time = BaseTime.get_current_beijing_time()
        last_time = BaseTime.parse_beijing_time(last_time_str)
        return current_time.hour != last_time.hour
