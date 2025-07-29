from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

def scale_data(X):
    scaler = StandardScaler()
    return scaler.fit_transform(X)

def split_data(X, y, test_size=0.2):
    return train_test_split(X, y, test_size=test_size, random_state=42)