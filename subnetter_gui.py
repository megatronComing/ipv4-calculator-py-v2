import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QDesktopWidget
import find_subnet_v21 as sbn

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('IPv4 subnetting calculator')
        self.setGeometry(100, 100, 900, 400)

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
    tableHeader = ['Host Number', 'SubnetID', 'Subnet Mask', 'Mask Len', 'Usable Hosts', 'First Host', 'Last Host', 'Broadcast Addr']
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
