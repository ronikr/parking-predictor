import random
import csv
total_day_to_generate = 30
num_samples_per_day = 24   # 24 for hourly

icons = ['panui', 'male', 'pail', 'meat', None]
weights = [0.5, 0.2, 0.15, 0.1, 0.05]  # Must sum to 1.0 or can be relative
lot_numbers = [87, 65, 129, 81, 95, 32, 108, 45, 23, 75, 39, 13, 90, 74, 38, 37, 15, 99, 34, 68, 24, 33, 31, 63, 54, 12,
               124, 80, 114, 42, 41, 98, 48, 96, 132, 69, 10, 91, 29, 137, 50, 58, 53, 8, 62, 70, 134, 131, 7, 88, 76,
               126, 120, 4, 79, 40, 138, 67, 93, 85, 135, 127, 94, 26, 89, 28, 72, 21, 3, 19, 123, 110, 1, 44, 57, 20,
               122, 133, 47, 77, 64, 18, 56, 121, 25, 16, 55]

data = []
timestamp_pre = '2025-05-'
timestamp_post = ':14:32.685Z'
for j in range(total_day_to_generate):
    day = str(j+1).zfill(2)
    for i in range(num_samples_per_day):
        for lot in lot_numbers:
            row = []
            random_icon = random.choices(icons, weights=weights, k=1)[0]
            row.append(random_icon)
            hour = str(i).zfill(2)  # Converts 0 → '00', 1 → '01', etc.
            full_timestamp = timestamp_pre + day + 'T' + hour + timestamp_post
            row.append(lot)
            row.append(full_timestamp)
            data.append(row)


with open('../data/apify/test_data.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['icon', 'id', 'timestamp'])  # Optional header
    writer.writerows(data)

if len(data) == total_day_to_generate*num_samples_per_day*len(lot_numbers):
    print(f"Total rows: {len(data)}")
else:
    print('no discrepancy')

# for row in data:
#     print(row)




