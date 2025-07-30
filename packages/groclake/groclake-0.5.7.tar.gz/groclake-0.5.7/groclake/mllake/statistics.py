import math
from collections import Counter

class Statistics:
    def __init__(self):
        pass

    def mean(self, data):
        return sum(data) / len(data)

    def median(self, data):
        return sorted(data)[len(data) // 2]
    
    def mode(self, data):
        return max(set(data), key=data.count)

    def standard_deviation(self, data):
        return math.sqrt(sum((x - self.mean(data)) ** 2 for x in data) / len(data))

    def variance(self, data):
        return self.standard_deviation(data) ** 2

    def z_score(self, data):
        return (data - self.mean(data)) / self.standard_deviation(data)

    def iqr(self, data):
        return self.percentile(data, 75) - self.percentile(data, 25)

    def percentile(self, data, percentile):
        return sorted(data)[int(len(data) * percentile / 100)]

    def skewness(self, data):
        return 3 * (self.mean(data) - self.median(data)) / self.standard_deviation(data)

    def kurtosis(self, data):
        return 4 * (self.mean(data) - self.median(data)) / self.standard_deviation(data)

    def covariance(self, data1, data2):
        return sum((x - self.mean(data1)) * (y - self.mean(data2)) for x, y in zip(data1, data2)) / len(data1)

    def correlation(self, data1, data2):
        return self.covariance(data1, data2) / (self.standard_deviation(data1) * self.standard_deviation(data2))

    def histogram(self, data):
        return Counter(data)

    def boxplot(self, data):
        return [self.percentile(data, 25), self.percentile(data, 50), self.percentile(data, 75)]

    def boxplot_outliers(self, data):
        return [x for x in data if x < self.percentile(data, 25) or x > self.percentile(data, 75)]

    def z_score_outliers(self, data, threshold=3):
        mean = self.mean(data)
        std_dev = self.standard_deviation(data)
        return [x for x in data if abs((x - mean) / std_dev) > threshold]

    def iqr_outliers(self, data):
        sorted_data = sorted(data)
        Q1 = self.percentile(sorted_data, 25)
        Q3 = self.percentile(sorted_data, 75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        return [x for x in data if x < lower_bound or x > upper_bound]

    
    def calculate_statistics(self, data):
        return {
            "mean": self.mean(data),
            "median": self.median(data),
            "mode": self.mode(data),
            "standard_deviation": self.standard_deviation(data),
            "variance": self.variance(data),
            "skewness": self.skewness(data),
            "kurtosis": self.kurtosis(data),
            "histogram": self.histogram(data),
            "boxplot": self.boxplot(data),
            "boxplot_outliers": self.boxplot_outliers(data),
            "z_score_outliers": self.z_score_outliers(data),
            "iqr_outliers": self.iqr_outliers(data),
        }

    