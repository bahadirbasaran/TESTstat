from core.utils import MessageEnum
from PyQt5.QtWidgets import QMessageBox, QStyledItemDelegate


HOSTS = ["Local Host", "stat.ripe.net"] + [f"dev00{n}.stat.ripe.net" for n in range(1, 9)]


class ColorEnum():

    FAILURE = "#FFB8B8"
    FAILURE_BOLD = "#CC0000"
    FAILURE_SECOND_HOST = "#E2D4BA"
    SUCCESS = "#D4FCD7"
    SUCCESS_BOLD = "#0FD71C"
    TIMEOUT = "#F5B445"
    TIMEOUT_BOLD = "#F29E0D"
    UI_FONT = "#424D70"
    UI_BG = "#EBECF4"
    BLACK = "#000000"
    WHITE = "#FFFFFF"
    GRAY = "#E1E2E8"


class StyleEnum():

    UI = f"background-color: {ColorEnum.UI_BG}; color:{ColorEnum.UI_FONT};"
    TABLE_LINE_EDIT = f"background-color: {ColorEnum.WHITE}; font-size:16px;"
    BTN_LABEL_CHECKBOX = "font-weight: bold; font-size:16px;"
    COMBOBOX = "QComboBox { combobox-popup: 0; }"
    INFO = "font-size:16px;"
    BOLD = "font-weight: bold;"
    STATS_PASSED = f"color: {ColorEnum.SUCCESS_BOLD}"
    STATS_FAILURE = f"color: {ColorEnum.FAILURE_BOLD}"
    STATS_TIMEOUT = f"color: {ColorEnum.TIMEOUT_BOLD}"
    INPUT_ENABLED = f"background-color: {ColorEnum.WHITE};"
    INPUT_DISABLED = f"background-color: {ColorEnum.GRAY};"


class ReadOnlyDelegator(QStyledItemDelegate):
    """Make columns read-only"""

    def createEditor(self, parent, option, index):
        return


def throw_message(type, title, message):

    msg = QMessageBox()
    msg.setText(str(message))
    msg.setWindowTitle(title)

    if type == MessageEnum.CRITICAL:
        msg.setIcon(QMessageBox.Critical)
        msg.setStandardButtons(QMessageBox.Ok)

    elif type == MessageEnum.WARNING:
        msg.setIcon(QMessageBox.Warning)
        msg.setStandardButtons(QMessageBox.No | QMessageBox.Yes)

    ret_val = msg.exec_()

    return ret_val


def format_table_item(text, csv_to_table=True):
    """
    if param csv_to_table = True, csv fields are formatted to load into table:
    resource = 1111;sort_by = count     ->  resource = 1111
                                            sort_by = count
    irr_sources = ripe&radb             ->  irr_sources = ripe,radb

    if param csv_to_table = False, table items are converted to save into csv:
    resource = 1111
    sort_by = count             -> resource = 1111;sort_by = count
    irr_sources = ripe,radb     -> irr_sources = ripe&radb
    """

    if csv_to_table:
        return text.replace(';', "\n").replace('&', ',')
    else:
        return text.replace("\n", ';').replace(',', '&')
