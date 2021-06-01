from flask import Flask, render_template, request, redirect, url_for, session,flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from functools import wraps


app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'aikins'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'aikins'

# Intialize MySQL
mysql = MySQL(app)



@app.route('/login/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM admin WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            print('Logged in successfully!')
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('login.html', msg=msg) 


    
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

@app.route('/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/department')
def dashboard():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page

    # Create cursor
        cur = mysql.connection.cursor()

  
        result = cur.execute("SELECT * FROM department")
        data= cur.fetchall()
        

    if result > 0:
        return render_template('department/dashboard.html', data=data)
    else:
        msg = 'No departments Found'
        return render_template('department/dashboard.html', msg=msg)
    # Close connection
    cur.close()
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))



@app.route('/add_dept', methods=('GET', 'POST'))
def create():
    cur = mysql.connection.cursor()
    
    if 'loggedin' in session:

        if request.method == 'POST':
            dept_name = request.form['dept_name']
            location = request.form['location']
            error = None
            

            if not dept_name:
                error = 'Department name is required.'

            if not location:
                error = 'Department location is required.'

            if error is not None:
                flash(error)
            else:
                cur = mysql.connection.cursor()
            
                cur.execute(
                    
                    "INSERT INTO department (dept_name, location)"
                     "VALUES (%s, %s)",
                    (dept_name, location)
                )
                mysql.connection.commit()
                cur.close()
                flash('Department Created','Success')
                return redirect(url_for('dashboard'))

        return render_template('department/add_dept.html')

    return redirect(url_for('login'))

def get_post(dept_name, check_author=False):
    cur = mysql.connection.cursor()
    post = cur.execute(
        'SELECT dept_name, location'
        ' FROM department  JOIN  ON dept_name'
        ' WHERE dept_name = ?',
        (dept_name),
    ).fetchone()

    if post is None:
        abort(404, "dept_name{0} doesn't exist.".format(id))

    return post

@app.route ('/edit_dept/<string:dept_name>', methods=('GET', 'POST'))
def editd(dept_name):
    
    
    if 'loggedin' in session:
        cur= mysql.connection.cursor()
        result = cur.execute("SELECT * FROM department WHERE dept_name = %s",[dept_name])
        dept= cur.fetchone()
        cur.close()
       
        
        if request.method == 'POST':
            
            if not dept_name:
                error = 'Department name is required.'

            else:

                dept_name = request.form['dept_name']
                location = request.form['location']
                error = None
                
                cur = mysql.connection.cursor()
                app.logger.info(dept_name)
                
                cur.execute("UPDATE department SET dept_name=%s, location=%s",[dept_name,location])
                mysql.connection.commit()
                cur.close()
        
            return redirect(url_for('dashboard'))
        #print(result)
        return render_template('department/edit_dept.html', department=dept)
        
    return redirect(url_for('login'))



@app.route('/instructor')
def dashinstr():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page

    # Create cursor
        cur = mysql.connection.cursor()

  
        result = cur.execute("SELECT * FROM instructor")
        data= cur.fetchall()
        

    if result > 0:
        return render_template('instructors/dashinstr.html', data=data)
    else:
        msg = 'No instructor Found'
        return render_template('instructors/dashinstr.html', msg=msg)
    # Close connection
    cur.close()
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/add_instr', methods=('GET', 'POST'))
def create_instr():
    cur = mysql.connection.cursor() 
    if 'loggedin' in session:
        msg=''
        check =''
        if request.method == 'POST':
            dept_name = request.form['dept_name']
            headedBy= request.form['headedBy']
            firstName= request.form['firstName']
            lastName= request.form['lastName']
            Phone = request.form['Phone']
            instructorID= request.form['instructorID']
            error = None

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT location,dept_name FROM department" )
            check = cursor.fetchall()
            if not check:
                    msg= "You must choose an existing department from the instructor dashboard"

            elif error is not None:
                flash(error)
            else:
                try:
                    cur = mysql.connection.cursor()
                
                    cur.execute(
                        "INSERT INTO instructor (dept_name, headedBy , firstName ,lastName , Phone , instructorID)"
                        "VALUES (%s, %s,%s,%s,%s,%s)",
                        (dept_name, headedBy, firstName,lastName,Phone,instructorID)
                    )
                    mysql.connection.commit()
                    cur.close()

                    flash('Instructor Created','Success')


                    return redirect(url_for('dashinstr',msg=msg))

                except mysql.connection.IntegrityError as err:
                 flash('"Error: {}".format(err)')
                    
                return "An instructor can head 1 departments or work in only 1 department "

        return render_template('instructors/add_instr.html', check=check)

    return redirect(url_for('login'))



@app.route('/courses')
def dash_course():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page

    # Create cursor
        cur = mysql.connection.cursor()

  
        result = cur.execute("SELECT * FROM course")
        data= cur.fetchall()
        

    if result > 0:
        return render_template('courses/dash_course.html', data=data)
    else:
        msg = 'No course Found'
        return render_template('courses/dash_course.html', msg=msg)
    # Close connection
    cur.close()
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route ('/edit_instr', methods=('GET', 'POST'))
def edit_instr():
    
    
    if 'loggedin' in session:
        
        if request.method == 'POST':
            
            if not instructorID:
                error = 'Instructor ID is required.'

            else:
                dept_name = request.form['dept_name']
                headedBy = request.form['headedBy']
                firstName=request.form['firstName']
                lastName=request.form['lastName']
                studentPhone = request.form['studentPhone']
                instructorID = request.form['instructorID']

                error = None
                
                cur = mysql.connection.cursor()
                cur.execute("UPDATE instructors SET dept_name=%s, headedBy=%s,firstName=%s,lastName=%s, studentPhone=%s, instructorID=%s WHERE dept_name=%s",(dept_name,headedBy,firstName,lastName,studentPhone,instructorID))
                mysql.connection.commit()
                cur.close()
        
            return redirect(url_for('dashinstr'))

        return render_template('instructors/edit_instr.html')
        
    return redirect(url_for('login'))


@app.route('/course_add', methods=('GET', 'POST'))
def create_course():
    cur = mysql.connection.cursor() 
    if 'loggedin' in session:
        msg=''
        check =''
        if request.method == 'POST':
            course_id= request.form['course_id']
            dept_name = request.form['dept_name'] 
            instructorID= request.form['instructorID']
            duration= request.form['duration']
            name = request.form['name']
            error = None

            if error is not None:
                flash(error)
            else:
                try:
                    cur = mysql.connection.cursor()
                
                    cur.execute(
                        "INSERT INTO course (course_id, dept_name , instructorID ,duration , name )"
                        "VALUES ( %s,%s,%s,%s,%s)",
                        (course_id, dept_name, instructorID, duration ,name)
                    )
                    mysql.connection.commit()
                    cur.close()

                    flash('Course Created','Success')


                    return redirect(url_for('course_dash',msg=msg))

                except mysql.connection.IntegrityError as err:
                 flash('"Error: {}".format(err)')
                    
                return "An instructor can head 1 departments or work in only 1 department "

        return render_template('courses/course_add.html', check=check)

    return redirect(url_for('login'))

@app.route ('/course_edit', methods=('GET', 'POST'))
def course_edit():
    

    if 'loggedin' in session:
        
        if request.method == 'POST':
            course_id = ''
            if not course_id:
                error = 'Course ID is required.'

            else:
                course_id = request.form['course_id']
                dept_name = request.form['dept_name']
                instructorID = request.form['instructorID']
                duration = request.form['duration']
                name = request.form['name']
                error = None
                
                cur = mysql.connection.cursor()
                cur.execute("UPDATE course SET course_id=%s, dept_name =%s,instructorID=%s,duration=%s,name=%s WHERE course_id=%s",(course_id,dept_name,instructorID,duration,name))
                mysql.connection.commit()
                cur.close()
        
            return redirect(url_for('dash_course'))

        return render_template('courses/course_edit.html')
        
    return redirect(url_for('login'))


@app.route('/students')
def dash_student():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page

    # Create cursor
        cur = mysql.connection.cursor()

  
        result = cur.execute("SELECT * FROM student")
        data= cur.fetchall()
        

    if result > 0:
        return render_template('students/dash_student.html', data=data)
    else:
        msg = 'No Student Found'
        return render_template('students/dash_student.html', msg=msg)
    # Close connection
    cur.close()
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/stud_add', methods=('GET', 'POST'))
def createStudent():
    cur = mysql.connection.cursor()
    
    if 'loggedin' in session:

        if request.method == 'POST':
            studentID= request.form['studentID']
            firstName = request.form['firstName']
            lastName = request.form['lastName']
            studentPhone = request.form['studentPhone']
            error = None
            

            if error is not None:
                flash(error)
            else:
                cur = mysql.connection.cursor()
            
                cur.execute(
                    
                    "INSERT INTO student (studentID, firstName,lastName,studentPhone)"
                     "VALUES (%s, %s,%s, %s)",
                    (studentID, firstName,lastName,studentPhone)
                )
                mysql.connection.commit()
                cur.close()
                flash('Student Created','Success')
                return redirect(url_for('dash_student.html'))

        return render_template('students/stud_add.html')

    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)