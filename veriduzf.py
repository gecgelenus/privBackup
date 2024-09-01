def read_serial_data():
    global arr
    # Serial portu aç
    ser = serial.Serial('/dev/ttyACM0', 115200)

    while True:
        # Seri porttan bir satır oku
        line = ser.readline().decode('utf-8').strip()

        # Satırı " / " işaretine göre ayır
        data_pairs = line.split(' / ')

        for data in data_pairs:
            if '=' in data:
                # Adres ve mesafe kısımlarını ayır
                address, distance = data.split('=')

                # Boşlukları temizle ve mesafe kısmındaki fazlalıkları kaldır
                address = address.strip()
                distance = distance.strip().split(' ')[0]  # Mesafe kısmını ayıkla

                

                arr.append((address, int(distance)))
        # İşlem tamamlandıktan sonra arr listesini döndür
        return arr

# Kullanım
result = read_serial_data()
print(result)
