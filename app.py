from flask import Flask, flash, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import sys
import string

import warnings
from collections import defaultdict

warnings.filterwarnings("ignore")


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Set the template folder
app.template_folder = 'templates'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Rama7579@'  # Enter your MySQL password here
app.config['MYSQL_DB'] = 'teacher_part'

mysql = MySQL(app)

import random

def evaluate(expected, response):
    # Generate a random score between 1 and 100
    random_score = random.randint(1, 100)
    return random_score


# Admin login route
@app.route('/')
def index():
    return render_template('Homepage.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM signup1 WHERE username = %s AND password = %s", (username, password))
        admin = cur.fetchone()
        cur.close()

        if admin:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_home'))
        else:
            return render_template('adminlogin.html', error='Invalid username or password')

    return render_template('adminlogin.html')

@app.route('/admin/signup', methods=['GET', 'POST'])
def admin_signup():
    # Your signup logic here
    return render_template('admin_signup.html')

@app.route('/admin/signup1', methods=['GET', 'POST'])
def admin_signup1():
    print(session)
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO signup1 (username,email, password,confirm_password) VALUES (%s, %s,%s,%s)", 
                    (username,email, password,confirm_password))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('admin_login'))
    else:
        return redirect(url_for('admin_signup'))



# Admin home route
@app.route('/admin/home')
def admin_home():
    if 'admin_logged_in' in session:
        return render_template('adminhome.html')
    else:
        return redirect(url_for('admin_login'))

# Admin students route
@app.route('/admin/students')
def admin_students():
    if 'admin_logged_in' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Students")
        students = cur.fetchall()
        cur.close()
        return render_template('admin_students.html', students=students)
    else:
        return redirect(url_for('admin_login'))

# Add student route
@app.route('/admin/add_student', methods=['POST'])
def add_student():
    if 'admin_logged_in' in session:
        username = request.form['username']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO Students (username, password) VALUES (%s, %s)", (username, password))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('admin_students'))
    else:
        return redirect(url_for('admin_login'))

# Update student route
@app.route('/admin/update_student/<int:student_id>', methods=['POST'])
def update_student(student_id):
    if 'admin_logged_in' in session:
        username = request.form['username']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE Students SET username = %s, password = %s WHERE student_id = %s", (username, password, student_id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('admin_students'))
    else:
        return redirect(url_for('admin_login'))

# Delete student route
@app.route('/admin/delete_student/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    if 'admin_logged_in' in session:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM Students WHERE student_id = %s", (student_id,))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('admin_students'))
    else:
        return redirect(url_for('admin_login'))

# View student scores route
# View student scores route
# View student scores route
@app.route('/admin/view_student_scores/<int:student_id>')
def view_student_scores(student_id):
    if 'admin_logged_in' in session:
        cur = mysql.connection.cursor()
        query = """
            SELECT DISTINCT sa.answer_id, sa.test_id, t.test_name, q.question_text, 
                ea.answer_text AS expected_answer, 
                sa.answer_text AS student_answer, sa.score
                FROM studentanswers sa
                JOIN tests t ON sa.test_id = t.test_id
                JOIN questions q ON sa.question_id = q.question_id
                JOIN expectedanswers ea ON q.question_id = ea.question_id
                WHERE sa.student_id = %s
                ORDER BY sa.test_id, q.question_id;
        """
        cur.execute(query, (student_id,))
        scores = cur.fetchall()
        cur.close()
        # Convert the tuple of tuples to a list of dictionaries
        scores = [{'answer_id': score[0], 'test_id': score[1], 'test_name': score[2], 
                   'question_text': score[3], 'expected_answer': score[4], 
                   'student_answer': score[5], 'score': score[6]} for score in scores]
        return render_template('student_scores.html', scores=scores)
    else:
        return redirect(url_for('admin_login'))

@app.route('/admin/delete_student_score/<int:answer_id>', methods=['POST'])
def delete_student_score(answer_id):
    if 'admin_logged_in' in session:
        cur = mysql.connection.cursor()
        # Delete the score with the given answer_id
        query = "DELETE FROM studentanswers WHERE answer_id = %s"
        cur.execute(query, (answer_id,))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('admin_students'))  # Redirect to admin students page
    else:
        return redirect(url_for('admin_login'))

###############################################################
#############################Admin Teacher ####################

# Admin teachers route
@app.route('/admin/teachers')
def admin_teachers():
    if 'admin_logged_in' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Teachers")
        teachers = cur.fetchall()
        cur.close()
        return render_template('admin_teachers.html', teachers=teachers)
    else:
        return redirect(url_for('admin_login'))

# Admin add teacher route
@app.route('/admin/add_teacher', methods=['GET', 'POST'])
def add_teacher():
    if 'admin_logged_in' in session:
        if request.method == 'POST':
            username = request.form['username']  # Changed from 'name' to 'username'
            password = request.form['password']  # Changed from 'email' to 'password'
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO Teachers (username, password) VALUES (%s, %s)", (username, password))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('admin_teachers'))
        else:
            return render_template('add_teacher.html')
    else:
        return redirect(url_for('admin_login'))

@app.route('/admin/update_teacher/<int:teacher_id>', methods=['GET', 'POST'])
def update_teacher(teacher_id):
    if 'admin_logged_in' in session:
        if request.method == 'POST':
            try:
                username = request.form['username']
                password = request.form['password']
                cur = mysql.connection.cursor()
                cur.execute("UPDATE Teachers SET username = %s, password = %s WHERE teacher_id = %s", (username, password, teacher_id))
                mysql.connection.commit()
                cur.close()
                return redirect(url_for('admin_teachers'))
            except Exception as e:
                print("Error updating teacher:", e)
                # Handle error appropriately, such as displaying an error message to the user
        else:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM Teachers WHERE teacher_id = %s", (teacher_id,))
            teacher = cur.fetchone()
            cur.close()
            if teacher:
                return render_template('update_teacher.html', teacher=teacher, teacher_id=teacher_id)
            else:
                # Handle case where teacher with given ID is not found
                return "Teacher not found"
    else:
        return redirect(url_for('admin_login'))

# Admin delete teacher route
@app.route('/admin/delete_teacher/<int:teacher_id>', methods=['POST'])
def delete_teacher(teacher_id):
    if 'admin_logged_in' in session:
        try:
            cur = mysql.connection.cursor()

            # Delete related records from teacherstudentrelationship table
            cur.execute("DELETE FROM teacherstudentrelationship WHERE teacher_id = %s", (teacher_id,))
            
            # Now, delete the teacher from the teachers table
            cur.execute("DELETE FROM teachers WHERE teacher_id = %s", (teacher_id,))
            
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('admin_teachers'))
        except Exception as e:
            # Handle any exceptions
            flash("An error occurred while deleting the teacher.")
            print(e)  # Print the exception for debugging purposes
            return redirect(url_for('admin_teachers'))
    else:
        return redirect(url_for('admin_login'))


# Admin view teacher tests route
@app.route('/admin/view_teacher_tests/<int:teacher_id>')
def view_teacher_tests(teacher_id):
    if 'admin_logged_in' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Tests WHERE teacher_id = %s", (teacher_id,))
        tests = cur.fetchall()
        cur.close()
        return render_template('view_teacher_tests.html', tests=tests, teacher_id=teacher_id)
    else:
        return redirect(url_for('admin_login'))

# Admin view test questions route
@app.route('/admin/view_test_questions/<int:test_id>')
def view_test_questions(test_id):
    if 'admin_logged_in' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Questions WHERE test_id = %s", (test_id,))
        questions = cur.fetchall()

        # Fetching expected answers for each question
        question_answers = {}
        for question in questions:
            cur.execute("SELECT * FROM ExpectedAnswers WHERE question_id = %s", (question[0],))
            answers = cur.fetchall()
            question_answers[question[0]] = answers

        cur.close()
        # Pass test_id as teacher_id to the template
        return render_template('view_test_questions.html', teacher_id=test_id, questions=questions, question_answers=question_answers)
    else:
        return redirect(url_for('admin_login'))

# Admin view question expected answers route
@app.route('/admin/view_question_answers/<int:question_id>')
def view_question_answers(question_id):
    if 'admin_logged_in' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM ExpectedAnswers WHERE question_id = %s", (question_id,))
        answers = cur.fetchall()
        cur.close()
        return render_template('view_question_answers.html', answers=answers)
    else:
        return redirect(url_for('admin_login'))


################################################
    


# Admin logout route
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))




################################################################################
###################################Teacher LOGIN######################
# Teacher login route
@app.route('/teacher_login', methods=['GET', 'POST'])
def teacher_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Teachers WHERE username = %s AND password = %s", (username, password))
        teacher = cur.fetchone()
        cur.close()

        if teacher:
            session['teacher_logged_in'] = True
            session['teacher_id'] = teacher[0]  # Assuming teacher_id is the first column
            return redirect(url_for('teacher_home'))
        else:
            return render_template('teacher_login.html', error='Invalid username or password')

    return render_template('teacher_login.html')

# Teacher home route
@app.route('/teacher_home', methods=['GET', 'POST'])
def teacher_home():
    if 'teacher_logged_in' in session:
        if request.method == 'POST':
            # Check if form was submitted for adding, updating, or deleting test name
            if 'add_test_name' in request.form:
                test_name = request.form['test_name']
                # Add test name to the database
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO Tests (test_name, teacher_id) VALUES (%s, %s)", (test_name, session['teacher_id']))
                mysql.connection.commit()
                cur.close()
            elif 'update_test_name' in request.form:
                test_id = request.form['test_id']
                updated_test_name = request.form['updated_test_name']
                # Update test name in the database
                cur = mysql.connection.cursor()
                cur.execute("UPDATE Tests SET test_name = %s WHERE test_id = %s", (updated_test_name, test_id))
                mysql.connection.commit()
                cur.close()
            elif 'delete_test_name' in request.form:
                test_id = request.form['test_id']
                
                try:
                    # Delete related student answers first
                    cur = mysql.connection.cursor()
                    cur.execute("DELETE FROM studentanswers WHERE test_id = %s", (test_id,))
                    mysql.connection.commit()
                    cur.close()

                    # Delete related expected answers
                    cur = mysql.connection.cursor()
                    cur.execute("DELETE FROM expectedanswers WHERE question_id IN (SELECT question_id FROM questions WHERE test_id = %s)", (test_id,))
                    mysql.connection.commit()
                    cur.close()

                    # Delete related questions
                    cur = mysql.connection.cursor()
                    cur.execute("DELETE FROM questions WHERE test_id = %s", (test_id,))
                    mysql.connection.commit()
                    cur.close()

                    # Now delete the test from the Tests table
                    cur = mysql.connection.cursor()
                    cur.execute("DELETE FROM tests WHERE test_id = %s", (test_id,))
                    mysql.connection.commit()
                    cur.close()

                except Exception as e:
                    # Handle any exceptions
                    print("Error:", e)





        # Fetch all tests for the current teacher
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Tests WHERE teacher_id = %s", (session['teacher_id'],))
        tests = cur.fetchall()
        cur.close()
        return render_template('teacher_home.html', tests=tests)
    else:
        return redirect(url_for('teacher_login'))

# Teacher logout route
@app.route('/teacher_logout')
def teacher_logout():
    session.pop('teacher_logged_in', None)
    session.pop('teacher_id', None)
    return redirect(url_for('teacher_login'))
######################teacherLOGOUT####################################
################################################################################
###############teacher FUNCTIONS ############################
@app.route('/teacher/view_test_questions/<int:test_id>', methods=['GET', 'POST'])
def view_teacher_test_questions(test_id):
    if 'teacher_logged_in' in session:
        if request.method == 'POST':
            if 'add_question' in request.form:
                question_text = request.form['question_text']
                expected_answers = request.form.getlist('expected_answer')
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO Questions (question_text, test_id) VALUES (%s, %s)", (question_text, test_id ))
                question_id = cur.lastrowid
                for answer in expected_answers:
                    cur.execute("INSERT INTO ExpectedAnswers (answer_text, question_id) VALUES (%s, %s)", (answer, question_id))
                mysql.connection.commit()
                cur.close()
            elif 'delete_question' in request.form:
                question_id = request.form['question_id']
                cur = mysql.connection.cursor()
                cur.execute("DELETE FROM ExpectedAnswers WHERE question_id = %s", (question_id,))
                cur.execute("DELETE FROM Questions WHERE question_id = %s", (question_id,))
                mysql.connection.commit()
                cur.close()

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Questions WHERE test_id = %s", (test_id,))
        questions = cur.fetchall()

        question_answers = {}
        for question in questions:
            cur.execute("SELECT * FROM ExpectedAnswers WHERE question_id = %s", (question[0],))
            answers = cur.fetchall()
            question_answers[question[0]] = answers

        cur.close()
        print(questions)
        print(question_answers)
        return render_template('view_teacher_test_questions.html', teacher_id=test_id, questions=questions, question_answers=question_answers)
    else:
        return redirect(url_for('teacher_login'))

###### Teacher ( student marks section page) ################
@app.route('/teacher_view_score')
def teacher_view_score():
    # Check if the user is logged in as a teacher
    if 'teacher_logged_in' in session:
        teacher_id = session['teacher_id']

        # Fetch student answers and expected answers for the logged-in teacher's tests
        cur = mysql.connection.cursor()
        query = """
            SELECT s.student_id, s.username AS student_username, t.test_name, q.question_text, ea.answer_text AS expected_answer, sa.answer_text AS student_answer, sa.score
            FROM StudentAnswers sa
            JOIN Students s ON sa.student_id = s.student_id
            JOIN Tests t ON sa.test_id = t.test_id
            JOIN Questions q ON sa.question_id = q.question_id
            JOIN ExpectedAnswers ea ON q.question_id = ea.question_id
            WHERE t.teacher_id = %s
        """
        cur.execute(query, (teacher_id,))
        results = cur.fetchall()

        # Group the results by student_id and test_name
        student_scores = defaultdict(lambda: {'student_username': None, 'tests': defaultdict(list)})
        for result in results:
            student_id, student_username, test_name, question_text, expected_answer, student_answer, score = result
            student_scores[student_id]['student_username'] = student_username
            student_scores[student_id]['tests'][test_name].append({
                'question_text': question_text,
                'expected_answer': expected_answer,
                'student_answer': student_answer,
                'score': score
            })

        return render_template('teacher_view_score.html', student_scores=student_scores)
    else:
        return redirect(url_for('teacher_login'))


##############################################################
                                                              
######################## Student LOGIN ####################### 
    
@app.route('/student_login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Students WHERE username = %s AND password = %s", (username, password))
        student = cur.fetchone()
        cur.close()

        if student:
            session['student_logged_in'] = True
            session['student_id'] = student[0]  # Assuming student_id is the first column
            return redirect(url_for('student_home'))
        else:
            return render_template('student_login.html', error='Invalid username or password')

    return render_template('student_login.html')
@app.route('/student_home')
def student_home():
    if 'student_logged_in' in session:
        return render_template('student_home.html')
    else:
        return redirect(url_for('student_login'))

@app.route('/student_logout')
def student_logout():
    session.pop('student_logged_in', None)
    session.pop('student_id', None)
    return redirect(url_for('student_login'))

@app.route('/student_query', methods=['GET', 'POST'])
def student_query():
    # Your signup logic here
    return render_template('student_query.html')

@app.route('/student_query1', methods=['GET', 'POST'])
def student_query1():
        if request.method == 'POST':
            name = request.form['name']
            test_number = request.form['test_number']
            question_number = request.form['question_number']
            answer = request.form['answer']
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO query (name,test_number, questions_number,answer) VALUES (%s, %s,%s,%s)", 
                        (name,test_number, question_number,answer))
            mysql.connection.commit()
            cur.close()
            return render_template('student_home.html')
        else:
            return redirect(url_for('student_query'))
        
@app.route('/my_issues', methods=['GET', 'POST'])
def my_issues():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM query")
    questions = cur.fetchall()
    # Your signup logic here
    return render_template('student_issues.html',questions=questions)
        




# Route for showing available tests and taking a test
@app.route('/student_take_test', methods=['GET', 'POST'])
def student_take_test():
    if 'student_logged_in' in session:
        if request.method == 'POST':
            # Handle form submission (store student answers)
            test_id = request.form.get('test_id')  # Assuming you have a hidden input field for the test_id
            student_id = session['student_id']  # Assuming you have stored student_id in the session
            
            # Check if the student has already taken the test
            if check_test_taken(student_id):
                return redirect(url_for('student_view_score'))
            
            # Loop through form data to retrieve answers for each question
            for question_id, answer in request.form.items():
                # Assuming input field names are in the format 'question_{question_id}'
                if question_id.startswith('question_'):
                    question_id = int(question_id.split('_')[1])
                    
                    # Store student answer in the StudentAnswers table
                    cur = mysql.connection.cursor()
                    cur.execute("INSERT INTO StudentAnswers (student_id, test_id, question_id, answer_text) VALUES (%s, %s, %s, %s)",
                                (student_id, test_id, question_id, answer))
                    mysql.connection.commit()
                    cur.close()
            
            # Redirect the student after storing answers
            return redirect(url_for('student_view_score'))
        else:
            # Fetch tests that the student has not taken yet
            cur = mysql.connection.cursor()
            cur.execute("""SELECT t.test_id, t.test_name 
                           FROM Tests t 
                           LEFT JOIN StudentAnswers sa ON t.test_id = sa.test_id AND sa.student_id = %s
                           WHERE sa.test_id IS NULL""", (session['student_id'],))
            tests = cur.fetchall()
            cur.close()
            
            # Convert the list of tuples to a list of dictionaries
            tests = [{'test_id': test[0], 'test_name': test[1]} for test in tests]
            
            return render_template('student_take_test.html', tests=tests)
    else:
        return redirect(url_for('student_login'))

@app.route('/student_take_test/<int:test_id>', methods=['GET', 'POST'])
def student_take_test_questions(test_id):
    if 'student_logged_in' in session:
        if request.method == 'POST':
            # Retrieve student ID from the session
            student_id = session['student_id']
            
            # Retrieve test ID from the route parameter
            test_id = test_id
            
            # Loop through form data to retrieve answers for each question
            for question_id, answer in request.form.items():
                # Assuming input field names are in the format 'question_{question_id}'
                if question_id.startswith('question_'):
                    question_id = int(question_id.split('_')[1])

                    # Store student answer in the StudentAnswers table
                    cur = mysql.connection.cursor()
                    cur.execute("INSERT INTO StudentAnswers (student_id, test_id, question_id, answer_text) VALUES (%s, %s, %s, %s)",
                                (student_id, test_id, question_id, answer))
                    mysql.connection.commit()
                    cur.close()

            # Redirect the student after storing answers
            return redirect(url_for('student_home'))

        else:
            # Fetch test details and questions for the specified test from the database
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM Tests WHERE test_id = %s", (test_id,))
            test = cur.fetchone()
            cur.execute("SELECT * FROM Questions WHERE test_id = %s", (test_id,))
            questions = cur.fetchall()
            cur.close()

            return render_template('student_take_test_questions.html', test=test, questions=questions, test_id=test_id)
    else:
        return redirect(url_for('student_login'))

@app.route('/student_view_score')
def student_view_score():
    # Check if the user is logged in as a student
    if 'student_logged_in' in session:
        student_id = session['student_id']

        # Fetch student answers, test names, questions, and expected answers for the logged-in student's tests
        cur = mysql.connection.cursor()
        query = """
            SELECT t.test_id, t.test_name, q.question_text, ea.answer_text AS expected_answer, sa.answer_text AS student_answer
            FROM StudentAnswers sa
            JOIN Tests t ON sa.test_id = t.test_id
            JOIN Questions q ON sa.question_id = q.question_id
            JOIN ExpectedAnswers ea ON q.question_id = ea.question_id
            WHERE sa.student_id = %s
        """
        cur.execute(query, (student_id,))
        results = cur.fetchall()
        print(results)

        # Prepare the data to be displayed
        student_scores = {}
        for result in results:
            test_id, test_name, question_text, expected_answer, student_answer = result
            # Calculate score
            score = evaluate(expected_answer, student_answer)
            cur.execute("UPDATE studentanswers SET score = %s WHERE student_id = %s AND test_id = %s AND question_id IN (SELECT question_id FROM questions WHERE question_text = %s)", (score, student_id, test_id, question_text))
            mysql.connection.commit()
            # Check if test_id already exists in student_scores
            if test_id not in student_scores:
                student_scores[test_id] = {
                    'test_id': test_id,
                    'test_name': test_name,
                    'total_score': 0,
                    'max_score': 0,
                    'scores': []
                }
            student_scores[test_id]['scores'].append({
                'question': question_text,
                'expected_answer': expected_answer,
                'student_answer': student_answer,
                'score': score
            })
            score = evaluate(expected_answer, student_answer)
            # Increment total score

            student_scores[test_id]['total_score'] += score
            # Increment max score
            student_scores[test_id]['max_score'] += 100

        # Format total score as "X / Y" for each test
        for test_data in student_scores.values():
            test_data['total_score'] = f"{test_data['total_score']} / {test_data['max_score']}"

        return render_template('student_view_score.html', student_scores=student_scores.values())
    else:
        return redirect(url_for('student_login'))


###############################################
#####################algorithm#################


###########################################
if __name__ == '__main__':
    app.run(debug=True)
