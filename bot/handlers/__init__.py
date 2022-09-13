from .common.cmd_start import register_cmd_start

from .user.select_college_group import register_select_college_group
from .user.show_timetable import register_show_timetable


def register_handlers(dp):
    register_cmd_start(dp)

    register_select_college_group(dp)
    register_show_timetable(dp)