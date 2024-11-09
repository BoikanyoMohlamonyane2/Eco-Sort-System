from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'a3d9b8f1a12d4c7e8e9f15c33f4b6a29'  # For session handling and flash messages

# Database configuration
db_config = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',  # or your database server IP
    'database': 'ecosortdb'
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def show_register():
    return render_template('register.html')

# Route for handling form submission and storing data
@app.route('/store', methods=['POST'])
def store_registration():
    # Get form data
    name = request.form['name']
    email = request.form['email']

    # Establish a database connection
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Insert data into the rewardcard table
        cursor.execute("INSERT INTO rewardcard (name, email) VALUES (%s, %s)", (name, email))
        conn.commit()

        # Get the last inserted ID (rewardCardId)
        rewardCardId = cursor.lastrowid

        # Flash success message and render the reward card
        flash(f'Registration successful for {name}!', 'success')
        return render_template('reward_card.html', name=name, email=email, rewardCardId=rewardCardId)

    except mysql.connector.Error as err:
        flash(f"Error: {err}", 'danger')
        return redirect(url_for('show_register'))

    finally:
        # Close database connection
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

@app.route('/verify', methods=['GET'])
def verify():
    user_email = request.args.get('email')
    user_password = request.args.get('password')
    
    try:
        # Connect to the MySQL database
        conn = mysql.connector.connect(**db_config)
        
        if conn.is_connected():
            cursor = conn.cursor()
            # Use a parameterized query to retrieve the admin record with the given email and password
            cursor.execute('SELECT email, password FROM admin WHERE email = %s AND password = %s', (user_email, user_password))
            admin_records = cursor.fetchall()

            # If a matching record is found, redirect to the dashboard
            if admin_records:
                session['admin_id'] = user_email  # Store the user's email or ID in the session
                return redirect(url_for('admin_dashboard'))

    except Error as e:
        print(f"Error: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

    # If no matching record is found, prompt to try logging in again
    return redirect(url_for('login'))

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin_id' in session:
        # Example of fetching data; replace with your logic
        reuse_data = {
            'Monday': 20,
            'Tuesday': 15,
            'Wednesday': 30,
            'Thursday': 25,
            'Friday': 40,
            'Saturday': 10,
            'Sunday': 5
        }
        
        return render_template('dashboard.html', reuse_data=reuse_data)
    else:
        flash("Please log in first.", 'warning')
        return redirect(url_for('login'))

@app.route('/login')
def login():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
