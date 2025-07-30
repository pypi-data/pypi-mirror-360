import csv
import datetime
import random

CITIES = ['Weimar', 'Ilmenau', 'Erfurt', 'Jena']
PRODUCTS = ['SmartDesk', 'HealthHub', 'QuantumStorage', 'LearningSphere', 'AutoPilot']

START_DATE = datetime.date(2017, 1, 1)
END_DATE = datetime.date(2023, 12, 31)


def main(filename: str):
    data = []
    for product in PRODUCTS:
        for city in CITIES:
            random_seed = sum(ord(c) for c in product + city)
            random.seed(random_seed)

            coef = [
                int(200 + random.random() * 1_000),
                2 * (random.random() - 0.6) if random.random() < 0.75 else 0.0,
                # random.random() - 0.5 if random.random() < 0.1 else 0.0
            ]

            today = START_DATE
            x = 0
            last_value = coef[0]

            while today <= END_DATE:
                dow = today.weekday()

                if dow in (5, 6):
                    value = 0
                else:
                    if dow == 0:
                        modifier = 1.00
                    elif dow == 1:
                        modifier = 0.67
                    elif dow == 2:
                        modifier = 0.80
                    elif dow == 3:
                        modifier = 0.92
                    else:
                        modifier = 0.72

                    noise = (random.random() - 0.5) * last_value / 3

                    value = sum(a * (x ** i) for i, a in enumerate(coef))
                    value = (value + noise) * modifier
                    value = max(0, value)

                    last_value = value

                data.append((today, city, product, int(value)))

                today += datetime.timedelta(days=1)
                x += 1

    data.sort(key=lambda x: (x[0], x[1]))
    with open(filename, 'w', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',')
        csv_writer.writerow(['Datum', 'Ort', 'Produkt', 'Anzahl'])

        for row in data:
            csv_writer.writerow(row)


if __name__ == '__main__':
    main('sales.csv')
