from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QColor


class MessageEnum():
    NO = 65536
    YES = 16384

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
    msg.setText(message)
    msg.setWindowTitle(title)

    if type == "critical":
        msg.setIcon(QMessageBox.Critical)
        msg.setStandardButtons(QMessageBox.Ok)

    elif type == "warning":
        msg.setIcon(QMessageBox.Warning)
        msg.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
    
    ret_val = msg.exec_()

    return ret_val