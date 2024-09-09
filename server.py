from flask import render_template
import sqlite3
from flask import Flask
from flask import request,redirect,url_for,session,flash
import datetime

app = Flask(__name__)
app.secret_key = "Pravin"

#home
@app.route('/')
def homepage():
    return redirect(url_for('index'))

@app.route('/dashlab')
def dashlab():
    return render_template('/dashlab.html')

# @app.route('/contact_us')
# def contact_us():
#     return render_template('/contact_us.html')
    
#index for home
@app.route('/index',methods = ['POST','GET'])
def index():
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute("select qty from blood_stock",())
    result = cur.fetchall()
    con.close()    
    return render_template('index.html',blood=result)

#to create an user account
@app.route('/register',methods = ['POST', 'GET'])
def registration():
    

    if request.method == 'POST':
        # try:
            conn = sqlite3.connect('database.db')
            cur = conn.cursor()
            cur.execute('CREATE TABLE IF NOT EXISTS user_info\
                            (email EMAIL,phone INT, password TEXT)')
            conn.commit()

            email = request.form['email']
            con = sqlite3.connect('database.db')
            cur = con.cursor()
            cur.execute("select email from user_info where email=?",(email,))
            search = cur.fetchall()

            if not search:
                try:
                    phone = request.form['phone']
                    password = request.form['password']
                    cur = conn.cursor()
                    cur.execute("INSERT INTO user_info values (?,?,?)",(email,phone,password))
                    conn.commit()
                    
                except sqlite3.IntegrityError:
                    msg = "Email already exists."
                    return render_template("adddonor.html",msg=msg)
                else:
                    msg = "Donor registerd successfully."
                    return render_template("registration.html",msg=msg)


            else:
                msg = "Email already exists."
                return render_template("registration.html",msg=msg)

    else:
        return render_template('registration.html')

#login
@app.route('/login',methods = ['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('/login.html')
    else:
        email = request.form['email']
        password = request.form['password']

        con = sqlite3.connect('database.db')
        cur = con.cursor()
        cur.execute("select count(*) from user_info where email=? and password =?",(email,password))
        result = cur.fetchone()
        con.close()    
        if (int(result[0]) == 1):
            session["email"] = email
            session['logged_in'] = True
            return redirect(url_for('index'))
        
        else:
            messege="Please enter valid Email and Password!"
            return render_template("login.html",msg=messege)

@app.route('/logout')
def logout():
   #remove the username from the session if it is there
    session.pop('email', None)
    session.pop('logged_in',None)
    try:
        session.pop('admin',None)
    except KeyError as e:
        print("I got a KeyError - reason " +str(e))
    else:
        msg = "Logged Out Successfully"
        return render_template('login.html',msg = msg)
    
#admin login
@app.route("/admin_login",methods = ['POST', 'GET'])
def admin_login():
    if request.method == 'GET':
        return render_template('admin_login.html')
    else:
        email = request.form['email']
        password = request.form['password']
        if email =="admin123@gmail.com" and password =="admin@123":
            session["email"] = email
            session['logged_in'] = True
            return redirect(url_for("dashhboard"))
        else:
            messege="Please enter valid Email and Password!"
            return render_template("admin_login.html",msg=messege)
        
#to show admin homepage
@app.route('/admin_dashboard',methods = ['POST', 'GET'])
def dashhboard():
    return render_template("admin_dashboard.html")

#to show blood stock at admin side
@app.route('/blood_stock',methods = ['POST','GET'])
def blood_stock():
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute("select qty from blood_stock",())
    result = cur.fetchall()
    con.close()    
    return render_template('blood_stock.html',blood=result)

    
#donor list in admin side
@app.route('/donor_list')
def donor_list():
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute("select * from donor_details")
    donors = cur.fetchall()
    return render_template("donor_list.html",donors = donors)

#patient list in admin side
@app.route('/patient_list')
def patient_list():
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute("select * from patient_details")
    patients = cur.fetchall()
    return render_template("patient_list.html",patients = patients)


#notify list in admin side
@app.route('/Notification')
def Notification():
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM notification")
    notify = cur.fetchall()
    return render_template("notification_list.html", notify=notify)



#to donate blood after login
@app.route('/donate_blood',methods =['POST','GET'])
def donate_blood():
    email = session.get('email')
    
    if request.method == 'POST':
            email = session.get('email')
            blood_group = request.form['blood_group']
            donorname = request.form['donorname']
            gender = request.form['gender']
            qty = int(request.form['qty'])
            dweight = request.form['dweight']
            donor_email = request.form['donor_email']
            phone = request.form['phone']
            address = request.form['address']
            donation_date = datetime.datetime.today().date()

            con = sqlite3.connect("database.db")
            cur = con.cursor()

            cur.execute('CREATE TABLE IF NOT EXISTS donor_details \
                        (email EMAIL, blood_group TEXT, donorname TEXT,gender TEXT, qty NUMERIC, dweight NUMERIC,donor_email EMAIL, phone NUMERIC, address TEXT, donation_date DATE)')
            con.commit()

            cur.execute("INSERT INTO donor_details (email,blood_group,donorname,gender,qty,dweight,donor_email,phone,address,donation_date) \
                        VALUES (?,?,?,?,?,?,?,?,?,?)",(email,blood_group,donorname,gender,qty,dweight,donor_email,phone,address,donation_date) )
            con.commit()
            
            cur.execute('CREATE TABLE IF NOT EXISTS blood_stock \
                        (blood_group TEXT, qty NUMERIC)')
            con.commit()
            cur.execute("select qty from blood_stock where blood_group =?",(blood_group,))
            result = cur.fetchone()
            
            qty_db = int(result[0])
            qty_db = qty_db + qty

            cur.execute("UPDATE blood_stock SET qty = ? WHERE blood_group =?",(qty_db,blood_group))
            con.commit()

          
            con.close()
            msg = "Donor successfully added..."
            return redirect(url_for('index'))

    else:
        email = session.get('email')
        if email:
            return render_template("add_blood.html")
        else:
            msg = "Login First..."
            return render_template('login.html',msg=msg)

#edit donor details
@app.route("/edit", methods=('GET', 'POST'))
def editdonor():
    if request.method == 'GET':
        email = session.get('email')
        con = sqlite3.connect('database.db')
        cur = con.cursor()
        cur.execute("select * from user_info where email=?",(email,))
        result = cur.fetchall()
        return render_template("edit_details.html",result = result)
    
    if request.method == 'POST':
        email = session.get('email')
        # try:
        new_email = request.form['email']
        con = sqlite3.connect('database.db')
        cur = con.cursor()
        cur.execute("select email from user_info where email=?",(new_email,))
        search = cur.fetchall()
        if not search:
            phone = request.form['phone']
            password = request.form['password']
            cur = con.cursor()
            cur.execute("UPDATE user_info SET email=?, phone=?, password=? WHERE email=?", (new_email, phone, password, email))
            con.commit()
            msg = "Details updated successfully."
            return render_template("login.html",msg=msg)
        
        else:
            msg = "Email already exists."
            return render_template("editdonor.html",msg=msg)
            
# patient blood request
@app.route("/sale_blood", methods=('GET', 'POST'))
def sale_blood():
    if request.method == 'POST':
            blood_group = request.form['blood_group']
            qty = int(request.form['qty'])
            con = sqlite3.connect("database.db")
            cur = con.cursor()
            cur.execute("select qty from blood_stock where blood_group =?",(blood_group,))
            result1 = cur.fetchone()
            qty_db = int(result1[0])
            if qty_db > qty:
                email = session.get('email')
                blood_group = request.form['blood_group']
                patientname = request.form['patientname']
                gender = request.form['gender']
                qty = int(request.form['qty'])
                patient_email = request.form['patient_email']
                phone = request.form['phone']
                address = request.form['address']
                purchase_date = datetime.datetime.today().date()

                con = sqlite3.connect("database.db")
                cur = con.cursor()

                cur.execute('CREATE TABLE IF NOT EXISTS patient_details \
                            (email EMAIL, blood_group TEXT, patientname TEXT,gender TEXT, qty NUMERIC, patient_email EMAIL, phone NUMERIC, address TEXT, purchase_date DATE)')
                con.commit()

                cur.execute("INSERT INTO patient_details (email,blood_group,patientname,gender,qty,patient_email,phone,address,purchase_date) \
                            VALUES (?,?,?,?,?,?,?,?,?)",(email,blood_group,patientname,gender,qty,patient_email,phone,address,purchase_date) )
                con.commit()
                
                cur.execute('CREATE TABLE IF NOT EXISTS blood_stock \
                            (blood_group TEXT, qty NUMERIC)')
                con.commit()
                cur.execute("select qty from blood_stock where blood_group =?",(blood_group,))
                result = cur.fetchone()
                
                qty_db = int(result[0])
                qty_db = qty_db - qty

                cur.execute("UPDATE blood_stock SET qty = ? WHERE blood_group =?",(qty_db,blood_group))
                con.commit()

            
                con.close()
                msg = "Patient successfully added..."
                return redirect(url_for('index'))
            else:
                msg = "Requested quantity not available..."
                return render_template("sale_blood.html",msg1=msg)

    else:
        email = session.get('email')
        if email:
            return render_template("sale_blood.html")
        else:
            msg = "Login First..."
            return render_template('login.html',msg=msg)


@app.route('/history',methods=('GET','POST'))
def history():
   
    email = session.get('email')
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("select * from donor_details where email =?",(email,))
    donors = cur.fetchall()

    cur.execute("select * from patient_details where email =?",(email,))
    patients = cur.fetchall()
    con.close()
    return render_template("blood_history.html",donors = donors,patients = patients)


#show all users at admin side
@app.route("/all_users",methods=('GET','POST'))
def all_users():
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("select * from user_info")
    all_users = cur.fetchall()
    return render_template("all_users.html",users = all_users)


if __name__ == '__main__':
    app.run(debug=True)