from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session & flash messages

# Database Connection Function
def connect_db():
    return sqlite3.connect('hospital.db')


# Create Table (If not exists)
def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            mobile_number TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


# Home Page (Registration Page)
@app.route('/')
def index():
    return render_template('createLogin.html')


# Register Route
@app.route('/createLogin', methods=['POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        mobile_number = request.form['mobile_number']
        username = request.form['username']
        password = request.form['password']

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user (first_name, last_name, email, mobile_number, username, password)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (first_name, last_name, email, mobile_number, username, password))
            conn.commit()
            flash("User Registered Successfully! Please login.", "success")
            return redirect(url_for('login_page'))  # Redirect to login page
        
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
            return redirect(url_for('createLogin'))  # Redirect back to registration page
        
        finally:
            conn.close()


# Login Page
@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')


# Login Authentication
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    conn = connect_db()
    cursor = conn.cursor()

    # Check if user exists
    cursor.execute("SELECT id, first_name, last_name, email, mobile_number, username, password FROM user WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    
    conn.close()

    if user:
        session['id'] = user[0] 
        session['first_name'] = user[1] 
        session['last_name'] = user[2] 
        session['email'] = user[3] 
        session['mobile_number'] = user[4] 
        session['username'] = user[5] 
        session['password'] = user[6] 
        flash("Login successful!", "success")
        return redirect(url_for('book'))  # Redirect to dashboard
    else:
        flash("Invalid username or password. Try again.", "danger")
        return redirect(url_for('login_page'))  # Redirect back to login page


#Add Appointmnets
@app.route('/book', methods=['GET'])
def book():
    return render_template('book.html')

@app.route('/add_appointment', methods=['GET', 'POST'])
def add_appointment():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        age = request.form['age']
        mobile_number = request.form['mobile_number']
        address = request.form['address']
        city = request.form['city']
        dr_name = request.form['dr_name']
        date = request.form['date']
        appointment_type = request.form['appointment_type']
        
        # Insert into database
        conn = sqlite3.connect("hospital.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO appointment (first_name, last_name, age, mobile_number, address, city, dr_name, date, type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (first_name, last_name, age, mobile_number, address, city, dr_name, date, appointment_type))

        conn.commit()
        conn.close()

        return redirect(url_for('book'))  # Redirect after submission

    return render_template("book.html")


#View Appointments
@app.route('/view', methods=['GET', 'POST'])
def show_appointments():
    conn = connect_db()
    cursor = conn.cursor()

    # Default query (show all cash payments)
    query = "SELECT id, first_name, last_name, age, mobile_number, dr_name, date, type FROM appointment WHERE type <> 'Emergency'AND status IS NULL"
    params = []

    selected_date = None  # Store selected date

    if request.method == 'POST':
        selected_date = request.form.get('selected_date')
        if selected_date:
            query += " AND date = ?"  # Use AND instead of WHERE
            params.append(selected_date)

    cursor.execute(query, tuple(params))
    data = cursor.fetchall()  # Fetch filtered payments

    # Calculate total amount for the selected date (or all if not filtered)
    sum_query = "SELECT COUNT(first_name) FROM appointment WHERE type <> 'Emergency'AND status IS NULL"
    sum_params = []

    if selected_date:
        sum_query += " AND date = ?"
        sum_params.append(selected_date)

    cursor.execute(sum_query, tuple(sum_params))
    total_patient = cursor.fetchone()[0]  # Get the total sum

    conn.close()

    return render_template('view.html', appointments=data, total_patient=total_patient, selected_date=selected_date)

@app.route('/deleteCancel', endpoint='deleteCancel')
def deleteCancel():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM appointment WHERE status = '1'")
    conn.commit()
    conn.close()

    return redirect(url_for('Cancel')) 

@app.route('/Eview', methods=['GET', 'POST'], endpoint='Eview')
def show_emergency():
    conn = connect_db()
    cursor = conn.cursor()

    # Default query (show all cash payments)
    query = "SELECT id, first_name, last_name, age, mobile_number, dr_name, date FROM appointment WHERE type = 'Emergency' AND status IS NULL"
    params = []

    selected_date = None  # Store selected date

    if request.method == 'POST':
        selected_date = request.form.get('selected_date')
        if selected_date:
            query += " AND date = ?"  # Use AND instead of WHERE
            params.append(selected_date)

    cursor.execute(query, tuple(params))
    data = cursor.fetchall()  # Fetch filtered payments

    # Calculate total amount for the selected date (or all if not filtered)
    sum_query = "SELECT COUNT(first_name) FROM appointment WHERE type = 'Emergency'AND status IS NULL"
    sum_params = []

    if selected_date:
        sum_query += " AND date = ?"
        sum_params.append(selected_date)

    cursor.execute(sum_query, tuple(sum_params))
    total_patient = cursor.fetchone()[0]  # Get the total sum

    conn.close()

    return render_template('Eview.html', appointments=data, total_patient=total_patient, selected_date=selected_date)

@app.route('/Cancel', methods=['GET', 'POST'], endpoint='Cancel')
def show_Cancel():
    conn = connect_db()
    cursor = conn.cursor()

    # Default query (show all cash payments)
    query = "SELECT first_name, last_name, age, mobile_number, dr_name, date, type FROM appointment WHERE status = '1'"
    params = []

    selected_date = None  # Store selected date

    if request.method == 'POST':
        selected_date = request.form.get('selected_date')
        if selected_date:
            query += " AND date = ?"  # Use AND instead of WHERE
            params.append(selected_date)

    cursor.execute(query, tuple(params))
    data = cursor.fetchall()  # Fetch filtered payments

    # Calculate total amount for the selected date (or all if not filtered)
    sum_query = "SELECT COUNT(first_name) FROM appointment WHERE status = '1'"
    sum_params = []

    if selected_date:
        sum_query += " AND date = ?"
        sum_params.append(selected_date)

    cursor.execute(sum_query, tuple(sum_params))
    total_patient = cursor.fetchone()[0]  # Get the total sum

    conn.close()

    return render_template('Cancel.html', appointments=data, total_patient=total_patient, selected_date=selected_date)

@app.route('/checked', methods=['GET', 'POST'], endpoint='checked')
def show_cheacked():
    conn = connect_db()
    cursor = conn.cursor()

    # Default query (show all cash payments)
    query = "SELECT first_name, last_name, age, mobile_number, dr_name, date, type FROM appointment WHERE status = '2'"
    params = []

    selected_date = None  # Store selected date

    if request.method == 'POST':
        selected_date = request.form.get('selected_date')
        if selected_date:
            query += " AND date = ?"  # Use AND instead of WHERE
            params.append(selected_date)

    cursor.execute(query, tuple(params))
    data = cursor.fetchall()  # Fetch filtered payments

    # Calculate total amount for the selected date (or all if not filtered)
    sum_query = "SELECT COUNT(first_name) FROM appointment WHERE status = '2'"
    sum_params = []

    if selected_date:
        sum_query += " AND date = ?"
        sum_params.append(selected_date)

    cursor.execute(sum_query, tuple(sum_params))
    total_patient = cursor.fetchone()[0]  # Get the total sum

    conn.close()

    return render_template('checked.html', appointments=data, total_patient=total_patient, selected_date=selected_date)

@app.route('/deletechecked', endpoint='deletechecked')
def deletechecked():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM appointment WHERE status = '2'")
    conn.commit()
    conn.close()

    return redirect(url_for('checked')) 


#Cancel and checked buttons
@app.route('/cancelled/<int:appointment_id>')
def cancelled(appointment_id):
    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()
    
    # Update status column to 1 for the given appointment ID
    cursor.execute("""
        UPDATE appointment 
        SET status = 1
        WHERE id = ?
    """, (appointment_id,))  # Use (1,) to ensure it's a tuple

    conn.commit()
    conn.close()

    return redirect(url_for('view'))  # Redirect to view page

@app.route('/check/<int:appointment_id>')
def check(appointment_id):
    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()
    
    # Update status column to 1 for the given appointment ID
    cursor.execute("""
        UPDATE appointment 
        SET status = 2
        WHERE id = ?
    """, (appointment_id,))  # Use (1,) to ensure it's a tuple

    conn.commit()
    conn.close()

    return redirect(url_for('view'))


#Add Payments
@app.route('/add_payment', methods=['GET', 'POST'])
def add_payment():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        date = request.form['date']
        mobile_number = request.form['mobile_number']
        city = request.form['city']
        doctor_name = request.form['doctor_name']
        total_paid = request.form['total_paid']
        payment_mode = request.form['payment_mode']
        transaction_id = request.form.get('transaction_id') or None
        cheaque_no = request.form.get('cheaque_no') or None
        cheaque_date = request.form.get('cheaque_date') or None
        bank_name = request.form.get('bank_name') or None


        # Insert into database
        conn = sqlite3.connect("hospital.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO payment (first_name, last_name, date, mobile_number, city, doctor_name, total_paid,payment_mode, transaction_id, cheaque_no, cheaque_date, bank_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (first_name, last_name, date, mobile_number, city, doctor_name, total_paid, payment_mode, transaction_id, cheaque_no, cheaque_date, bank_name))

        conn.commit()
        conn.close()

        return redirect(url_for('payment'))  # Redirect after submission

    return render_template("payment.html")


#Veiw Payments
@app.route('/cash', methods=['GET', 'POST'])
def cash():
    conn = connect_db()
    cursor = conn.cursor()

    # Default query (show all cash payments)
    query = "SELECT first_name, last_name, mobile_number, doctor_name, date, total_paid FROM payment WHERE payment_mode = 'Cash'"
    params = []

    selected_date = None  # Store selected date

    if request.method == 'POST':
        selected_date = request.form.get('selected_date')
        if selected_date:
            query += " AND date = ?"  # Use AND instead of WHERE
            params.append(selected_date)

    cursor.execute(query, tuple(params))
    data = cursor.fetchall()  # Fetch filtered payments

    # Calculate total amount for the selected date (or all if not filtered)
    sum_query = "SELECT SUM(total_paid) FROM payment WHERE payment_mode = 'Cash'"
    sum_params = []

    if selected_date:
        sum_query += " AND date = ?"
        sum_params.append(selected_date)

    cursor.execute(sum_query, tuple(sum_params))
    total_amount = cursor.fetchone()[0]  # Get the total sum

    conn.close()

    return render_template('cash.html', payments=data, total_amount=total_amount, selected_date=selected_date)

@app.route('/deletecash', endpoint='deletecash')
def deletecash():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM payment WHERE payment_mode = 'Cash'")
    conn.commit()
    conn.close()

    return redirect(url_for('cash')) 

@app.route('/online', methods=['GET', 'POST'])
def online():
    conn = connect_db()
    cursor = conn.cursor()

    # Default query (show all cash payments)
    query = "SELECT first_name, last_name, mobile_number, doctor_name, date, total_paid, transaction_id FROM payment WHERE payment_mode = 'Online'"
    params = []

    selected_date = None  # Store selected date

    if request.method == 'POST':
        selected_date = request.form.get('selected_date')
        if selected_date:
            query += " AND date = ?"  # Use AND instead of WHERE
            params.append(selected_date)

    cursor.execute(query, tuple(params))
    data = cursor.fetchall()  # Fetch filtered payments

    # Calculate total amount for the selected date (or all if not filtered)
    sum_query = "SELECT SUM(total_paid) FROM payment WHERE payment_mode = 'Online'"
    sum_params = []

    if selected_date:
        sum_query += " AND date = ?"
        sum_params.append(selected_date)

    cursor.execute(sum_query, tuple(sum_params))
    total_amount = cursor.fetchone()[0]  # Get the total sum

    conn.close()

    return render_template('online.html', payments=data, total_amount=total_amount, selected_date=selected_date)

@app.route('/deleteonline', endpoint='deleteonline')
def deleteonline():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM payment WHERE payment_mode = 'Online'")
    conn.commit()
    conn.close()

    return redirect(url_for('online')) 

@app.route('/cheaque', methods=['GET', 'POST'])
def cheaque():
    conn = connect_db()
    cursor = conn.cursor()

    # Default query (show all cash payments)
    query = "SELECT first_name, last_name, mobile_number, doctor_name, date, total_paid, cheaque_no, cheaque_date, bank_name FROM payment WHERE payment_mode = 'Cheque'"
    params = []

    selected_date = None  # Store selected date

    if request.method == 'POST':
        selected_date = request.form.get('selected_date')
        if selected_date:
            query += " AND date = ?"  # Use AND instead of WHERE
            params.append(selected_date)

    cursor.execute(query, tuple(params))
    data = cursor.fetchall()  # Fetch filtered payments

    # Calculate total amount for the selected date (or all if not filtered)
    sum_query = "SELECT SUM(total_paid) FROM payment WHERE payment_mode = 'Cheque'"
    sum_params = []

    if selected_date:
        sum_query += " AND date = ?"
        sum_params.append(selected_date)

    cursor.execute(sum_query, tuple(sum_params))
    total_amount = cursor.fetchone()[0]  # Get the total sum

    conn.close()

    return render_template('cheaque.html', payments=data, total_amount=total_amount, selected_date=selected_date)

@app.route('/deletecheaque', endpoint='deletecheaque')
def deletecheaque():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM payment WHERE payment_mode = 'Cheaque'")
    conn.commit()
    conn.close()

    return redirect(url_for('cheaque')) 

@app.route('/total', methods=['GET', 'POST'])
def total():
    conn = connect_db()
    cursor = conn.cursor()

    # Default query (show all cash payments)
    query = "SELECT first_name, last_name, mobile_number, doctor_name, date, total_paid, payment_mode FROM payment"
    params = []

    selected_date = None  # Store selected date

    if request.method == 'POST':
        selected_date = request.form.get('selected_date')
        if selected_date:
            query += " WHERE date = ?"  # Use AND instead of WHERE
            params.append(selected_date)

    cursor.execute(query, tuple(params))
    data = cursor.fetchall()  # Fetch filtered payments

    # Calculate total amount for the selected date (or all if not filtered)
    sum_query = "SELECT SUM(total_paid) FROM payment"
    sum_params = []

    if selected_date:
        sum_query += " WHERE date = ?"
        sum_params.append(selected_date)

    cursor.execute(sum_query, tuple(sum_params))
    total_amount = cursor.fetchone()[0]  # Get the total sum

    conn.close()

    return render_template('total.html', payments=data, total_amount=total_amount, selected_date=selected_date)

@app.route('/deletetotal', endpoint='deletetotal')
def deletetotal():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM payment")
    conn.commit()
    conn.close()

    return redirect(url_for('total')) 

#Profile
@app.route('/profile', methods=['GET'])
def profile():
    if "id" not in session:
        return redirect(url_for("login"))
    else:
        return render_template('profile.html', user=session)

@app.route("/logout")
def logout():
    session.clear()  # Clear session data
    return redirect(url_for("login"))

@app.route('/delete_profile')
def delete_profile():
    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user WHERE username = ?", (session['username'],))
    conn.commit()
    conn.close()
    session.clear()
    return redirect(url_for('login'))


@app.route('/emergency', methods=['GET'])
def emergency():
    return render_template('emergency.html')

@app.route('/updateProfile', methods=['GET'])
def updateProfile():
    return render_template('updateProfile.html')

@app.route('/view', methods=['GET'])
def view():
    return render_template('view.html')

@app.route('/payment', methods=['GET'])
def payment():
    return render_template('payment.html')




# def get_appointments():
#     conn = sqlite3.connect('hospital.db')
#     cursor = conn.cursor()
#     cursor.execute("SELECT first_name, last_name, age, mobile_number, dr_name, date, type FROM appointment WHERE type='Checkup' AND 'Follow-up'")
#     appointments = cursor.fetchall()
#     conn.close()

#     return [{"first_name": row[0], "last_name": row[1], "age": row[2], "mobile_number": row[3], "dr_name": row[4], "date": row[5], "type": row[6]} for row in appointments]

# @app.route('/get_appointments', methods=['GET'])
# def get_appointments_api():
#     return jsonify(get_appointments())


if __name__ == '__main__':
    create_table()
    app.run(debug=True)
