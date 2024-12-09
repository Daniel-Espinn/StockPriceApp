from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox, QHBoxLayout, QGridLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mdates
import yfinance as yf

class StockApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Stock Price Viewer")
        self.setGeometry(100, 100, 800, 600)

        # Widgets
        self.ticker_label = QLabel("Ticker Symbol:")
        self.ticker_input = QLineEdit()
        self.period_label = QLabel("Period:")
        self.period_combo = QComboBox()
        self.period_combo.addItems(["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"])
        self.chart_type_label = QLabel("Chart Type:")
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems(["Line", "Candlestick", "Volume"])
        self.fetch_button = QPushButton("Fetch Data")
        self.fetch_button.clicked.connect(self.fetch_data)

        # Labels for additional information
        self.current_price_label = QLabel("Current Price: N/A")
        self.max_price_label = QLabel("Max Price: N/A")
        self.min_price_label = QLabel("Min Price: N/A")

        # Layout
        layout = QGridLayout()
        layout.addWidget(self.ticker_label, 0, 0)
        layout.addWidget(self.ticker_input, 0, 1)
        layout.addWidget(self.period_label, 1, 0)
        layout.addWidget(self.period_combo, 1, 1)
        layout.addWidget(self.chart_type_label, 2, 0)
        layout.addWidget(self.chart_type_combo, 2, 1)
        layout.addWidget(self.fetch_button, 3, 0, 1, 2)

        # Additional information layout
        info_layout = QHBoxLayout()
        info_layout.addWidget(self.current_price_label)
        info_layout.addWidget(self.max_price_label)
        info_layout.addWidget(self.min_price_label)
        layout.addLayout(info_layout, 4, 0, 1, 2)

        # Matplotlib Figure
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas, 5, 0, 1, 2)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Apply styles
        self.apply_styles()

    def apply_styles(self):
        # Set font
        font = QFont("Arial", 12)
        self.setFont(font)

        # Set stylesheet
        stylesheet = """
            QMainWindow {
                background-color: #f0f0f0;
            }
            QLabel {
                color: #333333;
                font-weight: bold;
            }
            QLineEdit, QComboBox, QPushButton {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton {
                background-color: #007acc;
                color: #ffffff;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005c99;
            }
            QComboBox::drop-down {
                border: 0px;
            }
            QComboBox::down-arrow {
                image: url(:/icons/down_arrow.png);
                width: 14px;
                height: 14px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #cccccc;
                selection-background-color: #007acc;
                selection-color: #ffffff;
            }
        """
        self.setStyleSheet(stylesheet)

    def fetch_data(self):
        ticker = self.ticker_input.text()
        period = self.period_combo.currentText()
        chart_type = self.chart_type_combo.currentText()

        if not ticker:
            QMessageBox.warning(self, "Error", "Please enter a ticker symbol.")
            return

        try:
            data = get_stock_data(ticker, period)
            self.plot_data(data, chart_type)
            self.update_info(data)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch data: {e}")

    def plot_data(self, data, chart_type):
        self.figure.clear()
        ax1 = self.figure.add_subplot(111)

        if chart_type == "Line":
            data['Close'].plot(ax=ax1)
            ax1.set_title(f"Line Chart for {self.ticker_input.text()}")
        elif chart_type == "Candlestick":
            data['Date'] = mdates.date2num(data.index.to_pydatetime())
            ohlc = data[['Date', 'Open', 'High', 'Low', 'Close']].values
            candlestick_ohlc(ax1, ohlc, width=0.6, colorup='g', colordown='r')
            ax1.xaxis_date()
            ax1.set_title(f"Candlestick Chart for {self.ticker_input.text()}")
        elif chart_type == "Volume":
            data['Volume'].plot(ax=ax1, color='blue')
            ax1.set_title("Volume")

        ax1.set_xlabel("Date")
        ax1.set_ylabel("Price (USD)" if chart_type != "Volume" else "Volume")
        self.canvas.draw()

    def update_info(self, data):
        current_price = data['Close'][-1]
        max_price = data['Close'].max()
        min_price = data['Close'].min()

        self.current_price_label.setText(f"Current Price: ${current_price:.2f}")
        self.max_price_label.setText(f"Max Price: ${max_price:.2f}")
        self.min_price_label.setText(f"Min Price: ${min_price:.2f}")

def get_stock_data(ticker, period="1y"):
    stock = yf.Ticker(ticker)
    data = stock.history(period=period)
    return data

if __name__ == "__main__":
    app = QApplication([])
    window = StockApp()
    window.show()
    app.exec()