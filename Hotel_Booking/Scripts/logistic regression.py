# A binary classifier.

import numpy as np
import pandas as pd


def sigmoid(z):
    return 1 / (1 + np.exp(-z))


def forward(X, w):
    weighted_sum = np.matmul(X, w)
    return sigmoid(weighted_sum)


def classify(X, w):
    return np.round(forward(X, w))


def loss(X, Y, w):
    y_hat = forward(X, w)
    first_term = Y * np.log(y_hat)
    second_term = (1 - Y) * np.log(1 - y_hat)
    return -np.average(first_term + second_term)


def gradient(X, Y, w):
    return np.matmul(X.T, (forward(X, w) - Y)) / X.shape[0]


def train(X, Y, iterations, lr):
    w = np.zeros((X.shape[1], 1))
    for i in range(iterations):
        print("Iteration %4d => Loss: %.15f" % (i, loss(X, Y, w)))
        w -= gradient(X, Y, w) * lr
    return w


def test(X, Y, w):
    total_examples = X.shape[0]
    correct_results = np.sum(classify(X, w) == Y)
    success_percent = correct_results * 100 / total_examples
    print("\nSuccess: %d/%d (%.2f%%)" %
          (correct_results, total_examples, success_percent))


# Import data of Resort Hotel

df = pd.read_csv(r'/Users/henning/Portfolio/Hotel_Booking/Data/H1.csv')

df['TotalStay'] = df['StaysInWeekendNights'] + df['StaysInWeekNights']
df['TotalGuest'] = df['Adults'] + df['Children'] + df['Babies']

columns_for_array = ['LeadTime', 'TotalStay', 'TotalGuest', 'BookingChanges', 'IsCanceled']

numpy_array = df[columns_for_array].to_numpy()

# Create individual feature arrays
x0 = numpy_array[:, 0] # LeadTime
x1 = numpy_array[:, 1] # TotalStay
x2 = numpy_array[:, 2] # TotalGuest
x3 = numpy_array[:, 3] # BookingChanges

# Create the target variable array
y = numpy_array[:, 4]  # IsCanceled

# Prepare Data
X = np.column_stack((np.ones(x1.size), x0, x1, x2, x3))
Y = y.reshape(-1, 1)
w = train(X, Y, iterations=10000, lr=0.001)

# Test it
test(X, Y, w)