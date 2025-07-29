import numpy as np

from datetime import datetime

def to_excel_int_time(dt):
    """
    接受datetime对象，将其转成excel内部存储的整数。
    """
    excel_date_modify_factor = datetime(1900, 1, 1).toordinal() - 2
    excel_int_time = dt.toordinal() - excel_date_modify_factor
    return excel_int_time

to_excel_int_time_v = np.vectorize(to_excel_int_time)


