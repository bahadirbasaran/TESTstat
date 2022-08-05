from core.utils import MessageEnum
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QColor


class ColorEnum():
    FAILURE = QColor("#FFB8B8")
    FAILURE_SECOND_HOST = QColor("#E2D4BA")
    SUCCESS = QColor("#D4FCD7")
    TIMEOUT = QColor("#F5B445")
    BLACK = QColor("#000000")
    WHITE = QColor("#FFFFFF")
    UI_FONT = QColor("#424D70")


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
