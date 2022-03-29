from PyQt5 import QtWidgets, QtGui


TEST_CASES_PATH = "test_cases.csv"


class MESSAGE_ENUM():
    NO = 65536
    YES = 16384

class COLOR_ENUM():
    FAILURE = QtGui.QColor("#FFB8B8")
    SUCCESS = QtGui.QColor("#D4FCD7")
    TIMEOUT = QtGui.QColor("F5B445")
    BLACK = QtGui.QColor("#000000")
    WHITE = QtGui.QColor("#FFFFFF")
    UI_FONT = QtGui.QColor("#424D70")


def reshape_param_set(param_set):
    """ param_set:
            param = 'exact->inetnum'          value = 'a'
            param = 'exact->netname'          value = 'b'
            param = 'more_specific'           value = 'notempty'
            param = 'stats->stripped->avg'    value = 'c'
            param = 'stats->stripped->min'    value = 'd'
            param = 'stats->unstripped->avg'  value = 'e'
    =>> reshaped_param_set = {
            'exact': {
                'inetnum': 'a',
                'netname': 'b'                              
            },

            'more_specific': "notempty",

            'stats': {
                'stripped': {
                    'avg': 'c',
                    'min': 'd'
                },
                'unstripped': {
                    'avg': 'e'
                }                            
            }
        }
    """

    reshaped_param_set = {}

    for key, value in param_set.items():

        current_dict = reshaped_param_set
        *parts, last = key.split('->')

        for part in parts:

            if part not in current_dict:
                current_dict[part] = {}

            current_dict = current_dict[part]

        current_dict[last] = value

    return reshaped_param_set


def throw_message(type, title, message):

    msg = QtWidgets.QMessageBox()

    msg.setText(message)
    msg.setWindowTitle(title)

    if type == "critical":
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
    elif type == "warning":
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setStandardButtons(QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes)
    
    ret_val = msg.exec_()

    return ret_val