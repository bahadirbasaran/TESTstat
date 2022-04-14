from PyQt5 import QtWidgets, QtGui


class MessageEnum():
    NO = 65536
    YES = 16384


class ColorEnum():
    FAILURE = QtGui.QColor("#FFB8B8")
    SUCCESS = QtGui.QColor("#D4FCD7")
    TIMEOUT = QtGui.QColor("F5B445")
    BLACK = QtGui.QColor("#000000")
    WHITE = QtGui.QColor("#FFFFFF")
    UI_FONT = QtGui.QColor("#424D70")


def filter_param_set(param_set, filtered_param_set={}, current_level=None):

    def _filter(val):
        return val.lower().replace(' ', '')

    for k, v in param_set.items():

        if isinstance(v, str):
            if current_level:
                filtered_param_set[current_level][_filter(k)] = _filter(v)
            else:
                filtered_param_set[_filter(k)] = _filter(v)

        # bools should be checked first, since boolean is a subclass of int,
        # any bool variable matches with the following isinstance too!
        elif isinstance(v, bool):
            if current_level:
                filtered_param_set[current_level][_filter(k)] = "true" if v else "false"
            else:
                filtered_param_set[_filter(k)] = "true" if v else "false"

        elif isinstance(v, (int, float)):
            if current_level:
                filtered_param_set[current_level][_filter(k)] = str(v)
            else:
                filtered_param_set[_filter(k)] = str(v)

        elif v is None:
            if current_level:
                filtered_param_set[current_level][_filter(k)] = "none"
            else:
                filtered_param_set[_filter(k)] = "none"

        elif isinstance(v, list):
            v_new = []
            for list_item in v:
                if isinstance(list_item, str):
                    v_new.append(_filter(list_item))
                elif isinstance(list_item, bool) and list_item:
                    v_new.append("true")
                elif isinstance(list_item, bool):
                    v_new.append("false")
                elif isinstance(list_item, (int, float)):
                    v_new.append(str(list_item))
                elif list_item is None:
                    v_new.append("none")
                elif isinstance(list_item, list):
                    v_inner = []
                    for inner_item in list_item:
                        v_inner.append(
                            filter_param_set(inner_item, {})
                        )
                    v_new.append(v_inner)
                else:
                    v_new.append(
                        filter_param_set(list_item, {})
                    )

            if current_level:
                filtered_param_set[current_level][_filter(k)] = v_new
            else:
                filtered_param_set[_filter(k)] = v_new
        
        else:
            filtered_param_set[k] = {}
            filtered_param_set = filter_param_set(v, filtered_param_set, k)

    return filtered_param_set


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