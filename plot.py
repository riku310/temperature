import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import multiprocessing
from datetime import datetime, time, timedelta
import matplotlib.dates as mdates
from database import init_db, save_to_db  # データベース関数をインポート

# キューを使ってリアルタイムデータを保持
data_queue = deque(maxlen=1440)
time_queue = deque(maxlen=1440)

def plot_init():
    fig, ax = plt.subplots()
    ax.set_ylim(0, 50)  # 温度範囲を設定
    start_of_day = datetime.combine(datetime.today(), time.min)
    end_of_day = datetime.combine(datetime.today(), time.max)
    ax.set_xlim(start_of_day, end_of_day)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    fig.autofmt_xdate()  # X軸のラベルを自動でフォーマット
    line, = ax.plot([], [], 'o')
    return fig, ax, line

def update_plot(frame, line, ax):
    if data_queue and time_queue:
        y_data = list(data_queue)
        x_data = list(time_queue)
        line.set_data(x_data, y_data)
        ax.set_xlim(datetime.combine(datetime.today(), time.min), datetime.combine(datetime.today(), time.max))
    return line,

def plot_process(queue):
    init_db()
    fig, ax, line = plot_init()

    def update(frame):
        while not queue.empty():
            temp_deg_c, timestamp = queue.get()
            data_queue.append(temp_deg_c)
            time_queue.append(timestamp)
            save_to_db(timestamp, temp_deg_c)
        return update_plot(frame, line, ax)

    ani = animation.FuncAnimation(fig, update, interval=1000, blit=True)
    plt.show()

if __name__ == "__main__":
    data_queue = multiprocessing.Queue()
    plot_process(data_queue)
