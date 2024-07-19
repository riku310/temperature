import asyncio
from bleak import BleakScanner, BleakClient
import struct
import multiprocessing
from plot import plot_process  # plot_processをインポート
from datetime import datetime

# UUIDの定義
_ENV_SENSE_UUID = "0000181a-0000-1000-8000-00805f9b34fb"  # org.bluetooth.service.environmental_sensing
_ENV_SENSE_TEMP_UUID = "00002a6e-0000-1000-8000-00805f9b34fb"  # org.bluetooth.characteristic.temperature

# Helper to decode the temperature characteristic encoding (sint16, hundredths of a degree).
def _decode_temperature(data):
    """
    受信したデータを、温度センサ値にデコードする関数

    具体的には、以下のことを行っている
    ・binaryをバイトに変換(unpack)
    ・温度センサ値を1/100する
    """
    return struct.unpack("<h", data)[0] / 100

async def find_temp_sensor():
    # ５秒間、周辺のAdvertiseをスキャン
    devices = await BleakScanner.discover(timeout=5)
    for device in devices:
        # 目的の端末（「名称がmpy-temp」かつ「サービスに環境センシングが含まれている」）の場合、デバイス情報を返す
        if device.name == "mpy-temp":
            return device
    return None

async def main(queue):
    device = await find_temp_sensor()
    if not device:  # 目的の端末が見つからなかった場合
        print("Temperature sensor not found")
        return

    # 目的の端末が見つかった場合、以下の処理も実行される
    try:
        print("Connecting to", device)
        async with BleakClient(device) as client:
            while True:
                temp_characteristic = await client.read_gatt_char(_ENV_SENSE_TEMP_UUID)
                temp_deg_c = _decode_temperature(temp_characteristic)  # 受信データから温度センサ値を復元
                print("Temperature: {:.2f}".format(temp_deg_c))  # コンソールに表示
                timestamp = datetime.now()
                queue.put((temp_deg_c, timestamp))  # queueに温度データと時刻を追加
                await asyncio.sleep(1)  # 1秒一時停止
    except asyncio.TimeoutError:
        print("Timeout during connection")  # 接続がTimeoutErrorとなった場合
        return

if __name__ == "__main__":
    data_queue = multiprocessing.Queue()
    plot_process_instance = multiprocessing.Process(target=plot_process, args=(data_queue,))
    plot_process_instance.start()

    asyncio.run(main(data_queue))
