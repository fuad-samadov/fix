import sys
import json
import zmq
from PyQt6.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QPushButton, 
    QVBoxLayout, 
    QWidget, 
    QLabel,
    QLineEdit,
    QHBoxLayout,
    QRadioButton,
)
from PyQt6.QtGui import QIntValidator

class TradeUI(QMainWindow):
    IPC_PORT = "tcp://127.0.0.1:5555"

    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UI Initiator - Order Entry")
        
        # ZeroMQ setup
        self.zmq_context = zmq.Context()
        self.zmq_socket = self.zmq_context.socket(zmq.PUSH)
        self.zmq_socket.connect(self.IPC_PORT)

        # UI
        self.symbol_label = QLabel("Ticker:")
        self.symbol_input = QLineEdit()
        self.symbol_input.setPlaceholderText("e.g. AAPL")
        self.symbol_input.setText("AAPL")

        self.shares_label = QLabel("Number of shares:")
        self.shares_input = QLineEdit()
        self.shares_input.setValidator(QIntValidator(1, 9999, self)) # allowed range for num shares
        self.shares_input.setPlaceholderText("e.g. 5")
        self.shares_input.setText("5")

        self.order_side_label = QLabel("Order Side:")
        self.buy_radio = QRadioButton("BUY")
        self.buy_radio.setChecked(True)
        self.sell_radio = QRadioButton("SELL")

        new_order_button = QPushButton("Send Order")
        new_order_button.clicked.connect(self.send_order)

        self.cancel_order_label = QLabel("Order ID:")
        self.cancel_order_input = QLineEdit()
        self.cancel_order_input.setValidator(QIntValidator(1, 9999, self))
        self.cancel_order_input.setPlaceholderText("e.g. 1")
        self.cancel_order_input.setText("1")

        cancel_order_button = QPushButton("Cancel Order")
        cancel_order_button.clicked.connect(self.cancel_order)

        symbol_layout = QHBoxLayout()
        symbol_layout.addWidget(self.symbol_label)
        symbol_layout.addWidget(self.symbol_input)

        shares_layout = QHBoxLayout()
        shares_layout.addWidget(self.shares_label)
        shares_layout.addWidget(self.shares_input)

        side_layout = QHBoxLayout()
        side_layout.addWidget(self.order_side_label)
        side_layout.addWidget(self.buy_radio)
        side_layout.addWidget(self.sell_radio)

        cancel_order_layout = QHBoxLayout()
        cancel_order_layout.addWidget(self.cancel_order_label)
        cancel_order_layout.addWidget(self.cancel_order_input)

        main_layout = QVBoxLayout()
        main_layout.addLayout(symbol_layout)
        main_layout.addLayout(shares_layout)
        main_layout.addLayout(side_layout)
        main_layout.addWidget(new_order_button)
        main_layout.addLayout(cancel_order_layout)
        main_layout.addWidget(cancel_order_button)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def send_order(self):
        
        symbol = self.symbol_input.text().upper().strip()
        quantity = int(self.shares_input.text())
        side = "BUY" if self.buy_radio.isChecked() else "SELL"
        
        order_payload = {
            "action": "NEW_ORDER",
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": 150.00
        }

        self.zmq_socket.send_string(json.dumps(order_payload))
        print(f"[UI] Pushed order to Initiator: {order_payload}")

    
    def cancel_order(self):
        order_id = int(self.cancel_order_input.text())
        
        cancel_order_payload = {
            "action": "CANCEL_ORDER",
            "order_id": order_id
        }

        self.zmq_socket.send_string(json.dumps(cancel_order_payload))
        print(f"[UI] Pushed cancel order to Initiator: {cancel_order_payload}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TradeUI()
    window.show()
    sys.exit(app.exec())
