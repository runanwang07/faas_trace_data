import os
import csv
import numpy as np


def get_subdirectories(directory):
    return [subdir.path for subdir in os.scandir(directory) if subdir.is_dir()]


# 去除极端值
def remove_outliers(data):
    q1 = np.percentile(data, 10)
    q3 = np.percentile(data, 90)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    return [x for x in data if lower_bound <= x <= upper_bound]


def read_csv_files_in_directory(directory):
    durations = []
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            file_path = os.path.join(directory, filename)
            with open(file_path, "r") as csvfile:
                csv_reader = csv.DictReader(csvfile)
                for row in csv_reader:
                    if row['ParentID'] == 'root':
                        durations.append(int(row['Duration']))

    filtered_durations = remove_outliers(durations)
    mean_duration = sum(filtered_durations) / \
        len(filtered_durations) if filtered_durations else 0
    print(directory, mean_duration)


def main():
    current_directory = os.getcwd()
    subdirectories = get_subdirectories(current_directory)
    subdirectories.sort()

    for subdir in subdirectories:
        subdir = subdir + "/data"
        read_csv_files_in_directory(subdir)


if __name__ == "__main__":
    main()
    # import math
    # import datetime

    # start = datetime.datetime.now()
    # n = 6
    # a = 1
    # # print("%-15s%-20s" % ("内接正n边形", "π计算结果"))
    # # print("%-20d%-20.12f" % (n, n*a/2))
    # for i in range(14):
    #     n = 2*n
    #     a = math.sqrt(2-2*math.sqrt(1-(a/2)**2))
    #     # print("%-20d%-20.12f" % (n, n*a/2))
    # # main()
    # print((datetime.datetime.now()-start).microseconds)
