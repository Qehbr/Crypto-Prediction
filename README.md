# Crypto-Prediction-Telegram-Bot
Predicts the most high price on the next day

Prediction using linear regression

**RMSE : ~600**

get_binance_data.py:
*  gets all relevant data for prediction from Binance using Binance API
*  saves the data to sqlite database

training.py:
*  retrieves the data from the database
*  uses feature engineering: rolling mean
*  uses linear regression for prediction
*  calculates MSE, RMSE, r squared.
*  RMSE was ~600 in July 2023

update.py:
*  retreives new data from binance and adds it to the database

telegram_bot.py
*  has 2 threads:
    1.  Waits for input from users (/start, /help etc.)
    2.  Checks the time to send notification to all subscribed users
*  all subscribed users are stored in the database
*  when it's time (3:00 in my code) sends retrieves new data from binance, predict new price for the next day and sends to all subscribed users 
