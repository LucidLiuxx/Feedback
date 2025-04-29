from flask import Flask, redirect, render_template, request, flash, session, url_for # Flask modules for web application
import csv # CSV module for reading and writing CSV files
import re # Regular expression module for password validation

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flashing messages


# Route to redirect to the homepage.
@app.route('/')
def index():
    return redirect('/home')


# Route to render the homepage.
@app.route('/home')
def renderHome():
    return render_template("homepage.html")


# Route to handle the carbon footprint calculator.
@app.route('/calculator', methods=['GET', 'POST'])
def renderTesting():
    return render_template('carboncalculator.html')


# Route to handle login.
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Read the CSV file and check credentials
        with open('customerDetails.csv', mode='r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                if row['Email'] == email and row['Password'] == password:
                    session['email'] = email  # Store the logged-in user's email in the session
                    return redirect('/bookings')  # Redirect to bookings on successful login

        # If no match is found, flash an error message
        flash('Invalid email or password. Please try again.')
        return redirect('/login')
    return render_template('login.html')


# Route to handle logout.
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('email', None)  # Remove the user's email from the session
    if request.method == 'POST':
        return '', 204  # Return a 204 No Content response for the fetch request
    flash('You have been logged out.')
    return redirect('/login')


# Route to handle account registration.
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if the email already exists in the CSV
        with open('customerDetails.csv', mode='r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                if row['Email'] == email:
                    flash('Email already exists. Please use a different email.')
                    return redirect('/signup')
                
        # Validate the password
        if len(password) < 8:
            flash('Password must be at least 8 characters long.')
            return redirect('/signup')
        if not re.search(r'[A-Z]', password):
            flash('Password must contain at least one uppercase letter.')
            return redirect('/signup')
        if not re.search(r'[a-z]', password):
            flash('Password must contain at least one lowercase letter.')
            return redirect('/signup')
        if not re.search(r'[0-9]', password):
            flash('Password must contain at least one number.')
            return redirect('/signup')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            flash('Password must contain at least one symbol (e.g., !, @, #, etc.).')
            return redirect('/signup')
        if email.split('@')[0].lower() in password.lower():
            flash('Password must not contain a sequence of 3 or more characters from the email address.')
            return redirect('/signup')

        # Append the new user to the CSV file
        with open('customerDetails.csv', mode='a', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow([email, password])

        flash('Signup successful! You can now log in.')
        return redirect('/login')

    return render_template('signup.html')

    
# Route to handle bookings.
@app.route('/bookings', methods=['GET', 'POST'])
def bookings():
    if 'email' not in session:
        flash('You must be logged in to access bookings.')
        return redirect('/login')

    user_email = session['email']

    if request.method == 'POST':
        booking_type = request.form['booking_type']
        date = request.form['date']

        # Append the new booking to bookings.csv
        with open('bookings.csv', mode='a', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow([user_email, booking_type, date, 'Pending'])

        flash('Booking created successfully!')
        return redirect('/bookings')

    # Retrieve bookings for the logged-in user
    user_bookings = []
    with open('bookings.csv', mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if row['Email'] == user_email:
                user_bookings.append(row)

    return render_template('bookings.html', bookings=user_bookings)


# Route to handle booking editing.
@app.route('/edit_booking', methods=['POST'])
def edit_booking():
    if 'email' not in session:
        flash('You must be logged in to edit bookings.')
        return redirect('/login')

    # Retrieve booking details from the form
    booking_type = request.form['booking_type']
    date = request.form['date']

    return render_template('edit_booking.html', booking_type=booking_type, date=date)


# Route to handle booking updates.
@app.route('/update_booking', methods=['POST'])
def update_booking():
    if 'email' not in session:
        flash('You must be logged in to update bookings.')
        return redirect('/login')

    user_email = session['email']
    old_booking_type = request.form['old_booking_type']
    old_date = request.form['old_date']
    new_booking_type = request.form['new_booking_type']
    new_date = request.form['new_date']

    # Update the booking in bookings.csv
    updated_bookings = []
    with open('bookings.csv', mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if row['Email'] == user_email and row['BookingType'] == old_booking_type and row['Date'] == old_date:
                row['BookingType'] = new_booking_type
                row['Date'] = new_date
            updated_bookings.append(row)

    with open('bookings.csv', mode='w', newline='') as file:
        fieldnames = ['Email', 'BookingType', 'Date', 'Status']
        csv_writer = csv.DictWriter(file, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_writer.writerows(updated_bookings)

    flash('Booking updated successfully!')
    return redirect('/bookings')

# Route to handle booking deletion.
@app.route('/delete_booking', methods=['POST'])
def delete_booking():
    if 'email' not in session:
        flash('You must be logged in to delete bookings.')
        return redirect('/login')

    user_email = session['email']
    booking_type = request.form['booking_type']
    date = request.form['date']

    # Remove the booking from bookings.csv
    updated_bookings = []
    with open('bookings.csv', mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if not (row['Email'] == user_email and row['BookingType'] == booking_type and row['Date'] == date):
                updated_bookings.append(row)

    with open('bookings.csv', mode='w', newline='') as file:
        fieldnames = ['Email', 'BookingType', 'Date', 'Status']
        csv_writer = csv.DictWriter(file, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_writer.writerows(updated_bookings)

    flash('Booking deleted successfully!')
    return redirect('/bookings')


# Route to handle account deletion.
@app.route('/delete_account', methods=['POST'])
def delete_account():
    if 'email' not in session:
        flash('You must be logged in to delete your account.')
        return redirect('/login')

    user_email = session['email']

    # Remove the user's account from customerDetails.csv
    updated_users = []
    with open('customerDetails.csv', mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if row['Email'] != user_email:
                updated_users.append(row)

    with open('customerDetails.csv', mode='w', newline='') as file:
        fieldnames = ['Email', 'Password']
        csv_writer = csv.DictWriter(file, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_writer.writerows(updated_users)

    # Remove the user's bookings from bookings.csv
    updated_bookings = []
    with open('bookings.csv', mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if row['Email'] != user_email:
                updated_bookings.append(row)

    with open('bookings.csv', mode='w', newline='') as file:
        fieldnames = ['Email', 'BookingType', 'Date', 'Status']
        csv_writer = csv.DictWriter(file, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_writer.writerows(updated_bookings)

    # Log the user out and flash a success message
    session.pop('email', None)
    flash('Your account and all associated bookings have been deleted successfully.')
    return redirect('/login')



@app.route('/products')
def products():
    return render_template('products.html')



if __name__ == '__main__':
    app.run(debug=True)