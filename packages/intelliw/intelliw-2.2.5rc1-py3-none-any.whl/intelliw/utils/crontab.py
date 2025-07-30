'''
Author: Hexu
Date: 2022-05-05 12:07:16
LastEditors: Hexu
LastEditTime: 2022-09-22 19:58:12
FilePath: /iw-algo-fx/intelliw/utils/crontab.py
Description: crontab
'''
import datetime
import types

try:
    from apscheduler.schedulers.blocking import BlockingScheduler
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
except ImportError:
    raise ImportError(
        "\033[31mIf use cronjob, you need: pip install apscheduler\033[0m")


def _convert_special_day(day_of_week):
    """
    将特殊的星期几表示转换为标准表示。
    ? 转换为 *，7 或者 0 转换为 0。
    """
    if day_of_week == "?":
        return "*"
    elif day_of_week == "7":
        return "0"
    return day_of_week


class CrontabError(Exception):
    pass


class MyCronTrigger(CronTrigger):

    @classmethod
    def from_crontab(cls, expr, timezone=None):
        """
        Create a :class:`~CronTrigger` from a standard crontab expression.

        See https://en.wikipedia.org/wiki/Cron for more information on the format accepted here.

        :param expr: minute, hour, day of month, month, day of week
        :param datetime.tzinfo|str timezone: time zone to use for the date/time calculations (
            defaults to scheduler timezone)
        :return: a :class:`~CronTrigger` instance

        """
        if not expr:
            raise ValueError("时间表达式不能为空")
        values = expr.split()

        if len(values) not in [5, 6, 7]:
            raise ValueError(f"时间表达式长度不正确，应为5、6或7，实际为{len(values)}")

        if len(values) == 5:
            return cls(minute=values[0], hour=values[1], day=values[2], month=values[3],
                       day_of_week=_convert_special_day(values[4]), timezone=timezone)
        if len(values) == 6:
            return cls(second=values[0], minute=values[1], hour=values[2], day=values[3], month=values[4],
                       day_of_week=_convert_special_day(values[5]), timezone=timezone)
        if len(values) == 7:
            return cls(second=values[0], minute=values[1], hour=values[2], day=values[3], month=values[4],
                       day_of_week=_convert_special_day(values[5]), year=values[6], timezone=timezone)


class Crontab:
    def __init__(self, joblist, asynchronous=False) -> None:
        self.jobs = joblist
        self.asynchronous = asynchronous
        if self.asynchronous:
            self.sched = BackgroundScheduler(timezone='Asia/Shanghai')
        else:
            self.sched = BlockingScheduler(timezone='Asia/Shanghai')
        self._check()
        self._add_jobs()

    def _check(self):
        def raise_display():
            raise CrontabError(
                "joblist like [ {'crontab':str,'func':FunctionType,'args':tuple}, ... ]")

        k = ['func', 'args', 'crontab']
        for job in self.jobs:
            for i in k:
                if i not in job.keys():
                    raise_display()
                if type(job['crontab']) is not str:
                    raise_display()
                if not isinstance(job['func'], types.FunctionType):
                    raise_display()
                if type(job.get('args', tuple)) is not tuple:
                    raise_display()
        return 0

    def _add_jobs(self):
        for job in self.jobs:
            func = job["func"]
            crontab = job["crontab"]
            args = job.get("args")
            self._add_job(func, crontab, args)

    def _add_job(self, func, crontab, args=None):
        cron = MyCronTrigger.from_crontab(crontab)
        self.sched.add_job(func, cron, args=args)

    def start(self):
        if self.asynchronous:
            self.sched._daemon = True
        self.sched.start()


if __name__ == '__main__':
    def p(*args):
        print(args, datetime.datetime.now())
        print('====\n')


    joblist = [
        {'crontab': '0/1 * * * *', 'func': p, 'args': ('job1',)},
        {'crontab': '0 */2 * * * ?', 'func': p, 'args': ('job2',)},
        {'crontab': '0 */3 * * * ? *', 'func': p, 'args': ('job3',)},
    ]

    # sync
    crontab1 = Crontab(joblist)
    crontab1.start()

    # async
    # import time
    # crontab2 = Crontab(joblist, True)
    # crontab2.start()
    # time.sleep(999999)
