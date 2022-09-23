from .owner.main_menu.cmd_start import register_owner__cmd_start
from .owner.main_menu.menu import register_owner__main_menu
from .owner.change_role.change_role import register_change_role__section
from .owner.owners_section.owners import register_owners__section
from .owner.deploy.deploy import register_deploy__section

from .admin.main_menu.cmd_start import register_admin__cmd_start
from .admin.timetable.timetable_section import register_admin_timetable__section
from .admin.timetable.new_timetable import register_new_timetable
from .admin.timetable.download_file import register_download_file


from .user.main_menu.cmd_start import register_user__cmd_start
from .user.registration.registration import register_college_group__input
from .user.main_menu.break_timetable import register_break_timetable
from .user.timetable.timetable_of_classes import register_timetable_of_classes
from .user.settings.settings import register_setting__section
from .user.settings.change_college_group import register_change_college_group
from .user.settings.send_message_to_lucifer import register_send_message_to_lucifer


def register_handlers(dp):
    register_owner__cmd_start(dp)
    register_owner__main_menu(dp)
    register_change_role__section(dp)
    register_owners__section(dp)
    register_deploy__section(dp)

    register_admin__cmd_start(dp)
    register_admin_timetable__section(dp)
    register_new_timetable(dp)
    register_download_file(dp)

    register_user__cmd_start(dp)
    register_college_group__input(dp)
    register_break_timetable(dp)
    register_timetable_of_classes(dp)
    register_setting__section(dp)
    register_change_college_group(dp)
    register_send_message_to_lucifer(dp)

