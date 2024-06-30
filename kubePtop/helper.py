import time
import math
import datetime

class Helper:
    def __init__(self):
        pass

    def seconds_to_human_readable(self, seconds):
        units = [
            ('d', 24 * 3600),
            ('h', 3600),
            ('m', 60),
            ('s', 1)
        ]

        result = []

        for unit, duration in units:
            if seconds >= duration:
                value, seconds = divmod(seconds, duration)
                result.append(f"{int(value)}{unit}")

        if not result:
            result.append("0s")

        return ' '.join(result)

    def milliseconds_to_human_readable(self, milliseconds):
        seconds = milliseconds / 1000
        units = [
            ('d', 24 * 3600),
            ('h', 3600),
            ('m', 60),
            ('s', 1)
        ]

        result = []

        for unit, duration in units:
            if seconds >= duration:
                value, seconds = divmod(seconds, duration)
                result.append(f"{int(value)}{unit}")

        if not result:
            result.append("0s")

        return ' '.join(result)

    def bytes_to_kb_mb_gb(self,size_bytes):
        """
        Converts bytes to kb, mb, gb
        INPUT: size in bytes
        """
        if size_bytes == 0:
            return "0B"
        size_name = ("b", "kb", "mb", "gb", "tb", "pb", "eb", "zb", "yb")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return "%s %s" % (s, size_name[i])


    def bytes_to_kb_mb_gb_split(self, size_bytes):
        """
        Converts bytes to kb, mb, gb
        INPUT: size in bytes
        RETURNS: (value, unit)
        """
        if size_bytes == 0:
            return (0, "B")
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return (s, size_name[i])

    # def bytes_to_kb(self, size_bytes):
    #     """
    #     Converts bytes to kb, mb, gb
    #     INPUT: size in bytes
    #     """
    #     if size_bytes == 0:
    #         return "0B"
    #     size_name = ("b", "kb")
    #     i = int(math.floor(math.log(size_bytes, 1024)))
    #     p = math.pow(1024, i)
    #     s = round(size_bytes / p, 2)
    #     return "%s %s" % (s, size_name[i])


    def bytes_to_kb(self, bytes):
        """
        Converts kilobytes to Megabytes
        INPUT: size in kilobytes
        """
        return bytes / 1000

    def bytes_to_mb(self, bytes):
        """
        Converts kilobytes to Megabytes
        INPUT: size in kilobytes
        """
        kb = bytes / 1000
        return kb / 1024

    def sec_to_m_h(self, total_seconds):
        """
        Converts seconds to Minutes or Hours
        INPUT: seconds
        """
        out = '%.2f' % total_seconds
        unit = "sec"
        if (total_seconds > 60) and (total_seconds < 3600):
            n = total_seconds / 60
            out = '%.2f' % n
            unit = "min"
        elif total_seconds > 3600:
            n = total_seconds / 60 / 60
            out = '%.2f' % n
            unit = "hour/s"
        return f"{out} {unit}"


    def sec_to_m_h_d(self, total_seconds):
        """
        Converts seconds to Minutes, Hours or Days
        INPUT: seconds
        """
        out = '%.2f' % total_seconds
        unit = "s"
        if (total_seconds > 60) and (total_seconds < 3600):
            n = total_seconds / 60
            out = '%.2f' % n
            unit = "m"
        elif total_seconds > 3600:
            n = total_seconds / 60 / 60
            out = '%.2f' % n
            unit = "h"
        if total_seconds >= 86400:
            n = (total_seconds / 60 / 60) / 24
            day =  int(n)
            hour_percentage =  int(str('%.2f' % n).split(".")[1])
            hour = (24 * hour_percentage // 100)
            out = f"{day}d{hour}h"
            return out
        return f"{out}{unit}"

    def millisec_to_sec_m_h(self, milliseconds):
        """
        Converts milliseconds to seconds, Minutes or Hours
        INPUT: milliseconds
        """
        out = '%.2f' % milliseconds
        unit = "ms" # millis
        if milliseconds < 1000:
            return f"{out} {unit}"
        total_seconds = (milliseconds/1000)
        return self.sec_to_m_h(total_seconds)

    def millisec_to_d_h_m(self, milliseconds):
        """
        Converts milliseconds to format similar to 15d 08h 19m
        """
        return datetime.datetime.fromtimestamp(milliseconds/1000.0).strftime("%dd %Hh %Mm") # %Ss -> For seconds


    def percentage(self, part, whole):
        Percentage = 100 * float(part)/float(whole)
        return str(math.floor(Percentage)) + "%"

    def convert_epoch_timestamp(self, timestamp):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))

    def convert_data_unit(self, value, metric_unit):
        if metric_unit == 'None':
            return value
        if value == float('inf'):
            value = "INF"
        elif metric_unit == 'byte':
            value = self.bytes_to_kb_mb_gb(value)
        elif metric_unit == 'seconds':
            value =  self.seconds_to_human_readable(value)
        elif metric_unit == 'milliseconds':
            value =  self.milliseconds_to_human_readable(value)
        elif metric_unit == 'timestamp':
            value =  self.convert_epoch_timestamp(value)
        elif  metric_unit == 'percentage':
            value =  f"{round(value)}%"
        return value

    def safe_eval(self, custom_key, labels):
        for key, value in labels.items():
            custom_key = custom_key.replace(f"{{{{{key}}}}}", f"{value}")
        return custom_key

    def check_thread_status(self, thread):
        try:
            if thread.is_alive():
                return "[green]ALIVE"
            else:
                return "[red]DEAD"
        except Exception as e:
                return str(e)
