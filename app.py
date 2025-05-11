import random
import qrcode
import matplotlib.pyplot as plt
import time
from flask import Flask, render_template, request

app = Flask(__name__)

# Car Class
class Car:
    def __init__(self, name, rate_hourly, rate_daily, image):
        self.name = name
        self.rate_hourly = rate_hourly
        self.rate_daily = rate_daily
        self.image = image
        self.rented = False

# Car Options
compact_car = Car("Suzuki Swift, Suzuki Alto, Tata Tiago", 11, 70, 'compact_car.jpg')
sedan_car = Car("Suzuki Swift Dzire, Honda City, Honda Amaze", 15, 100, 'sedan_car.jpg')
suv_car = Car("Hyundai Creta, Tata Nexon, Mahindra Thar", 21, 130, 'suv_car.jpg')
xl_car = Car("Mahindra Scorpio, Tata Safari, Suzuki Ertiga", 30, 200, 'xl_car.jpg')

car_options = {
    1: compact_car,
    2: sedan_car,
    3: suv_car,
    4: xl_car
}

# Store Rental Data
rental_data = {}
returned_receipts = set()

# Generate QR Code
def display_qr_code(data):
    qr = qrcode.make(data)
    plt.imshow(qr, cmap='gray')
    plt.axis('off')
    plt.show()

# Home Route
@app.route('/')
def home():
    return render_template('index.html', cars=car_options)

# Rent a Car Route
@app.route('/rent', methods=['POST', 'GET'])
def rent():
    if request.method == 'POST':
        name = request.form['name']
        mobile = request.form['mobile']
        car_choice = int(request.form['car'])
        rental_mode = int(request.form['mode'])

        if car_choice in car_options and not car_options[car_choice].rented:
            selected_car = car_options[car_choice]

            if rental_mode == 1:
                total_hours = int(request.form['hours'])
                total_fare = total_hours * selected_car.rate_hourly
                charge_type = "Hourly"
            else:
                total_days = int(request.form['days'])
                total_fare = total_days * selected_car.rate_daily
                charge_type = "Daily"

            # Generate Receipt Number
            receipt_number = random.randint(1000, 9999)

            # Store Data
            rental_data[receipt_number] = {
                'name': name,
                'mobile': mobile,
                'car': selected_car.name,
                'mode': charge_type,
                'fare': total_fare
            }
            selected_car.rented = True

            # Show receipt WITHOUT payment details
            return render_template('receipt.html', receipt=rental_data[receipt_number], receipt_number=receipt_number)

    return render_template('rent.html', cars=car_options)

# Return a Car Route
@app.route('/return', methods=['POST', 'GET'])
def return_car():
    if request.method == 'POST':
        receipt_number = int(request.form['receipt_number'])

        if receipt_number in rental_data:
            data = rental_data.pop(receipt_number)

            for car in car_options.values():
                if car.name == data['car']:
                    car.rented = False

            # Display Payment QR Code Option
            upi_data = f"upi://pay?pa=your-upi-id@upi&pn=RentalService&am={data['fare']}"
            display_qr_code(upi_data)

            return render_template('return_confirmation.html', receipt=data, receipt_number=receipt_number)

    return render_template('return.html')

# Run Flask App
if __name__ == '__main__':
    app.run(debug=True)
