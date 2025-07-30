import csv


def main():
    with \
            open('/home/eric/Downloads/yellow_tripdata_2015-01.csv', 'r', encoding='utf-8') as source, \
            open('cabs.csv', 'w', encoding='utf-8') as target:
        reader = csv.reader(source)
        writer = csv.writer(target)

        # header
        _, *header = next(reader)

        writer.writerow([
            'pickup_datetime', 'dropoff_datetime', 'passenger_count', 'trip_distance',
            'pickup_longitude', 'pickup_latitude', 'dropoff_longitude', 'dropoff_latitude',
            'total_amount'
        ])

        # data
        rows = []

        for (
                vendor, tpep_pickup_datetime, tpep_dropoff_datetime, passenger_count, trip_distance, pickup_longitude,
                pickup_latitude, RateCodeID, store_and_fwd_flag, dropoff_longitude, dropoff_latitude, payment_type,
                fare_amount, extra, mta_tax, tip_amount, tolls_amount, improvement_surcharge, total_amount
        ) in reader:
            # filter vendor
            if vendor != '1':
                continue

            # filter pickup / dropoff
            pickup_year, pickup_month, pickup_day = map(int, tpep_pickup_datetime[:10].split('-'))
            pickup_hour, pickup_minute, pickup_second = map(int, tpep_pickup_datetime[11:].split(':'))
            dropoff_year, dropoff_month, dropoff_day = map(int, tpep_dropoff_datetime[:10].split('-'))
            dropoff_hour, dropoff_minute, dropoff_second = map(int, tpep_dropoff_datetime[11:].split(':'))

            if pickup_month != 1 or dropoff_month != 1 or pickup_day != 15 or dropoff_day != 15:
                continue
            if pickup_hour < 6 or dropoff_hour >= 20:
                continue

            # filter lat/lon
            pickup_lon, pickup_lat = float(pickup_longitude), float(pickup_latitude)
            dropoff_lon, dropoff_lat = float(dropoff_longitude), float(dropoff_latitude)

            if abs(pickup_lon) < 0.01 or abs(pickup_lat) < 0.01 or abs(dropoff_lon) < 0.01 or abs(dropoff_lat) < 0.01:
                continue
            if abs(pickup_lon - dropoff_lon) < 0.001 and abs(pickup_lat - dropoff_lat) < 0.001:
                continue

            # store
            rows.append([
                tpep_pickup_datetime, tpep_dropoff_datetime, passenger_count, trip_distance,
                pickup_longitude, pickup_latitude, dropoff_longitude, dropoff_latitude,
                total_amount
            ])

        # sort
        sorted_rows = sorted(rows, key=lambda r: (r[0], -int(r[2]), r[1]))

        # sample
        sampled_rows = []

        last_hour, last_minute, last_second = -1, -1, -1
        for pickup_datetime, *row in sorted_rows:
            hour, minute, second = map(int, pickup_datetime[11:].split(':'))

            if hour == last_hour and minute == last_minute and second == last_second:
                continue

            last_hour, last_minute, last_second = hour, minute, second
            sampled_rows.append([pickup_datetime, *row])

        # write
        writer.writerows(sampled_rows)


if __name__ == '__main__':
    main()
