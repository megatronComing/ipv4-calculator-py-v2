'''
GUI for searching for a minimum subnet for every host number required out of a give IPV4 network address.
Requirements:
    find_subnet_v21
By Huafeng Yu, hfyu.hzcn@gmail.com
'''
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QDesktopWidget, QMessageBox
import find_subnet_v21 as sbn
import traceback

def exception_hook(exctype, value, trace):
    """
    Global exception handler
    :param exctype: exception type
    :param value: exception object
    :param trace: Traceback object
    """
    error_msg = ''.join(traceback.format_exception(exctype, value, trace))
    QMessageBox.critical(None, 'An Exception Occurred', f'An unexpected error has occurred:\n{error_msg}', QMessageBox.Ok)
    sys.exit(1)

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('IPv4 subnetting calculator')
        self.setGeometry(100, 100, 700, 400)

        # Main vertical layout
        mainLayout = QVBoxLayout(self)

        # Horizontal layout for labels
        labelLayout = QHBoxLayout()
        LabelIP = QLabel('Enter IPv4 address with subnet mask length:')
        labelHosts = QLabel('Enter required host numbers, seperated by spaces:')
        labelLayout.addWidget(LabelIP)
        labelLayout.addWidget(labelHosts)

        # Horizontal layout for input fields
        inputLayout = QHBoxLayout()
        self.inputIpAddr = QLineEdit(self)
        self.inputIpAddr.setPlaceholderText('192.168.1.0/24')  # Set placeholder for input A
        self.inputHostNums = QLineEdit(self)
        self.inputHostNums.setPlaceholderText('59 7 15 29 2')  # Set placeholder for input B
        inputLayout.addWidget(self.inputIpAddr)
        inputLayout.addWidget(self.inputHostNums)

        # Button to run myfunc
        self.button = QPushButton('Find required subnets', self)
        self.button.clicked.connect(self.on_click)

        # Table to display results
        self.tableWidget = QTableWidget()
        
        # Author and contact information
        authorLabel = QLabel('Created by: Huafeng Yu - hfyu.hzcn@gmail.com', self)
        #authorLabel.setAlignment(Qt.AlignCenter)  # Center the text

        # Add layouts and button to the main layout
        mainLayout.addLayout(labelLayout)
        mainLayout.addLayout(inputLayout)
        mainLayout.addWidget(self.button)
        mainLayout.addWidget(self.tableWidget)
        mainLayout.addWidget(authorLabel)  # Add the author label at the bottom
    
    def on_click(self):
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)

        ip = self.inputIpAddr.text()
        hosts_str = self.inputHostNums.text().split(' ')
        hosts = []
        #hosts = [int(host) for host in hosts_str]
        for host in hosts_str:
            try:
                hosts.append(int(host))
            except:
                pass
        isvalid, tmp1, tmp2 = sbn.validate_ip(ip)
        if not isvalid:
            QMessageBox.critical(self, 'Invalid input', "Please input a valid ip address, like 192.168.1.0/24", QMessageBox.Ok )
            return

        if len(hosts) == 0:
            QMessageBox.critical(self, 'Invalid input', "Please input valid host numbers", QMessageBox.Ok )
            return
        myip = sbn.IPV4_SUBNET(ip, hosts)
        headers, data = myip.get_formatted_result()
        
        self.tableWidget.setColumnCount(len(headers))
        self.tableWidget.setHorizontalHeaderLabels(headers)
        self.tableWidget.setRowCount(len(data))

        for row_num, row_data in enumerate(data):
            for col_num, cell_data in enumerate(row_data):
                self.tableWidget.setItem(row_num, col_num, QTableWidgetItem(str(cell_data)))

        self.tableWidget.resizeColumnsToContents()
        # Set a minimum width for each column
        min_column_width = 70
        for col_index in range(self.tableWidget.columnCount()):
            current_width = self.tableWidget.columnWidth(col_index)
            if current_width < min_column_width:
                self.tableWidget.setColumnWidth(col_index, min_column_width)

def main():
    sys.excepthook = exception_hook
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
