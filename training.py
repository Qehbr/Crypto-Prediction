import sqlite3
import numpy as np
import pandas as pd
from sklearn.model_selection import KFold
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression


def train_data(coins):
    conn = sqlite3.connect('crypto.db')
    res_coins = dict()
    for coin in coins:
        btc_data = pd.read_sql(f"SELECT * FROM {coin}", conn)
        btc_data.set_index(btc_data.columns[0], inplace=True)
        btc_data['Next High Price'] = btc_data['High Price'].shift(-1)
        btc_data['Next Low Price'] = btc_data['Low Price'].shift(-1)
        btc_data['Next Close Price'] = btc_data['Close Price'].shift(-1)

        btc_data["hp_ma7"] = btc_data['High Price'].rolling(window=7).mean()
        btc_data["lp_ma7"] = btc_data['Low Price'].rolling(window=7).mean()
        btc_data["cp_ma7'"] = btc_data['Close Price'].rolling(window=7).mean()
        btc_data["op_ma7"] = btc_data['Open Price'].rolling(window=7).mean()

        X_predict = btc_data.tail(1)
        btc_data = btc_data.dropna(axis=0)

        X = btc_data.drop(['Next High Price', 'Next Low Price', 'Next Close Price'], axis=1)
        X_predict = X_predict.drop(['Next High Price', 'Next Low Price', 'Next Close Price'], axis=1)
        y = btc_data.loc[:, ['Next High Price']]

        model = LinearRegression(fit_intercept=False)
        kfold = KFold(n_splits=5, shuffle=True)

        mse_scores = []
        rmse_scores = []
        r2_scores = []

        # Iterate over each fold
        for train_indices, test_indices in kfold.split(X):
            # Split the data into training and test sets
            X_train, X_test = X.iloc[train_indices], X.iloc[test_indices]
            y_train, y_test = y.iloc[train_indices], y.iloc[test_indices]

            y_train = np.ravel(y_train)
            y_test = np.ravel(y_test)

            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)

            # Calculate mean squared error (MSE)
            mse = mean_squared_error(y_test, y_pred)
            mse_scores.append(mse)

            # Calculate root mean squared error (RMSE)
            rmse = np.sqrt(mse)
            rmse_scores.append(rmse)

            # Calculate coefficient of determination (R-squared)
            r2 = r2_score(y_test, y_pred)
            r2_scores.append(r2)

        avg_mse = np.mean(mse_scores)
        avg_rmse = np.mean(rmse_scores)
        avg_r2 = np.mean(r2_scores)

        model.fit(X, y)

        prediction = model.predict(X_predict)[0]

        res = {
            'prediction': prediction,
            'mse': avg_mse,
            'rmse': avg_rmse,
            'r2': avg_r2
        }

        res_coins[coin] = res

    return res_coins


