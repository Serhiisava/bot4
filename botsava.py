import ccxt
import time
from datetime import datetime
import pandas as pd
import ta

# Настройки API Bybit (замените на свои реальные API-ключи)
api_key = 'HfU9ArlVor80ghR6oi'
api_secret = 'gZz5oXxZZbOcmRxKCbPccV3sXusPwT4FVi5l'

# Настройка соединения с Bybit для спотового рынка
bybit = ccxt.bybit({
    'apiKey': api_key,
    'secret': api_secret,
})

# Список криптовалютных пар для анализа
symbols = [
    'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'XRP/USDT', 'ADA/USDT',
    'SOL/USDT', 'DOGE/USDT', 'DOT/USDT', 'LTC/USDT', 'TRX/USDT'
]

# Параметры стратегии
interval = 120  # Интервал проверки в секундах (2 минуты)
timeframe = '1h'  # Таймфрейм данных

# Функция для получения торгового сигнала
def get_trade_signal(symbol):
    try:
        # Получаем данные OHLCV
        ohlcv = bybit.fetch_ohlcv(symbol, timeframe=timeframe, limit=50)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

        # Расчет индикаторов
        df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
        df['ema_short'] = ta.trend.EMAIndicator(df['close'], window=10).ema_indicator()
        df['ema_long'] = ta.trend.EMAIndicator(df['close'], window=30).ema_indicator()

        # Условия Buy/Sell сигналов
        buy_signal = (
            df['rsi'].iloc[-1] < 45 and  # более гибкий порог для RSI Buy-сигнала
            df['close'].iloc[-1] > df['ema_short'].iloc[-1] > df['ema_long'].iloc[-1]  # Цена выше EMA, и EMA10 выше EMA30
        )
        sell_signal = (
            df['rsi'].iloc[-1] > 55 and  # более гибкий порог для RSI Sell-сигнала
            df['close'].iloc[-1] < df['ema_short'].iloc[-1] < df['ema_long'].iloc[-1]  # Цена ниже EMA, и EMA10 ниже EMA30
        )

        # Вывод сигнала
        if buy_signal:
            print(f"[{datetime.now()}] {symbol}: Buy Signal")
        elif sell_signal:
            print(f"[{datetime.now()}] {symbol}: Sell Signal")
        else:
            print(f"[{datetime.now()}] {symbol}: No Signal")
    except Exception as e:
        print(f"Ошибка получения сигнала для {symbol}: {e}")

# Основной цикл
def main():
    print("Бот запущен для анализа рынка на таймфрейме 1 час, проверка каждые 2 минуты.")
    while True:
        for symbol in symbols:
            get_trade_signal(symbol)
        time.sleep(interval)

# Запуск бота
if __name__ == "__main__":
    main()
