from flask import Flask, render_template, request, redirect, url_for, flash, abort, session, send_file, Response, jsonify
from pymongo import MongoClient
# from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from bson.objectid import ObjectId
import gridfs
import os
import re
import uuid
import io

app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config['UPLOAD_FOLDER'] = 'static/faculty_images'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['user_authentication_data']
users_collection = db['signup']
admin_users_collection = db['admin_users']
blogs_collection = db['blogs']

# Faculty-specific MongoDB connection
collection = db['faculty_members']

# for user prov=file and quizes
# users_profile_data_collection = db['users_profile_data']
# quizzes_collection = db['quizzes']
fs = gridfs.GridFS(db)

# for limiting login upto 2 devices only
MAX_DEVICES = 2

def get_device_id(device_info):
    # This function should generate a unique ID for the device based on its information
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, device_info))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    latest_blog = blogs_collection.find().sort("date", -1).limit(1)
    latest_blog = list(latest_blog)
    if 'user_logged_in' in session and session['user_logged_in']:
        username = session.get('username', 'Guest')
        flash(f'Hi {username}, Welcome to NNF-Sonic!', 'info')
    return render_template('index.html', latest_blog=latest_blog[0] if len(latest_blog) > 0 else None)

# @app.route('/add_questions', methods=['GET', 'POST'])
# def add_questions():
#     if request.method == 'POST':
#         data = request.get_json()
#         quiz_heading = data.get('quiz_heading')
#         questions = data.get('questions')
        
#         quiz_data = {
#             "quiz_heading": quiz_heading,
#             "questions": []
#         }
        
#         for question_data in questions:
#             question = question_data.get('question')
#             options = question_data.get('options')
#             correct_option_index = int(question_data.get('correct_option'))
#             correct_option = options[correct_option_index]
            
#             quiz_data["questions"].append({
#                 "question": question,
#                 "options": options,
#                 "correct_option": correct_option
#             })
        
#         quizzes_collection.insert_one(quiz_data)
        
#         return jsonify({'status': 'success'})
    
#     return render_template('add_question.html')

# @app.route('/quiz_list')
# def quiz_list():
#     quizzes = list(quizzes_collection.find())
#     return render_template('quiz_list.html', quizzes=quizzes)

# @app.route('/quiz/<quiz_id>', methods=['GET', 'POST'])
# def take_quiz(quiz_id):
#     if request.method == 'POST':
#         selected_option = request.form.get('option')
#         correct_option = session.get('correct_option')
        
#         if 'score' not in session:
#             session['score'] = 0
        
#         if selected_option == correct_option:
#             session['score'] += 1
        
#         session['question_index'] += 1
    
#     if 'question_index' not in session:
#         session['question_index'] = 0
    
#     question_index = session['question_index']
    
#     quiz = quizzes_collection.find_one({"_id": ObjectId(quiz_id)})
#     questions = quiz['questions']
#     if question_index >= len(questions):
#         score = session.get('score', 0)
#         session.pop('question_index', None)
#         session.pop('score', None)
#         return render_template('result.html', score=score, total=len(questions))
    
#     question_data = questions[question_index]
#     session['correct_option'] = question_data['correct_option']
    
#     return render_template('quiz.html', question=question_data, question_index=question_index+1, total=len(questions))






@app.route('/student_profile')
def student_profile():
    if not session.get('user_logged_in'):
        flash('You need to be logged in to access this page.', 'warning')
        return redirect(url_for('login'))

    username = session.get('username')
    user = users_collection.find_one({'username': username})
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('index'))

    # Remove sensitive information before sending to the template
    user_data = {
        'name': user.get('name'),
        'contact': user.get('contact'),
        'email': user.get('email'),
        'profile_picture': user.get('profile_picture')
    }

    return render_template('student_profile.html', user=user_data)


# @app.route('/student_profile_list')
# def student_profile_list():
#     students = list(users_collection.find())
#     return render_template('student_profile_list.html', students=students)

# @app.route('/student_profile_picture/<file_id>')
# def student_profile_picture(file_id):
#     try:
#         # Ensure `fs` is the GridFS instance
#         file = fs.get(ObjectId(file_id))
#         return send_file(
#             io.BytesIO(file.read()),
#             attachment_filename=file.filename,
#             mimetype=file.content_type
#         )
#     except Exception as e:
#         # Log the error for debugging
#         print(f"Error: {e}")
#         abort(404)

@app.route('/image/<file_id>', methods=['GET'])
def get_image(file_id):
    try:
        image = fs.get(ObjectId(file_id))
        return send_file(io.BytesIO(image.read()), mimetype=image.content_type)
    except gridfs.errors.NoFile:
        abort(404)  # Image not found

@app.route('/profile/<user_id>')
def profile(user_id):
    user = users_collection.find_one({'_id': ObjectId(user_id)})
    if not user:
        return "User not found", 404
    return render_template('profile.html', user=user)

@app.route('/add_profile', methods=['GET', 'POST'])
def add_profile():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        full_name = request.form.get('full_name')
        bio = request.form.get('bio')
        password = request.form.get('password')

        file = request.files.get('profile_picture')
        profile_picture_id = None
        if file and file.filename:
            profile_picture_id = fs.put(file.read(), content_type=file.content_type, filename=file.filename)

        result = users_collection.insert_one({
            'username': username,
            'email': email,
            'full_name': full_name,
            'bio': bio,
            'password': password,
            'profile_picture': profile_picture_id
        })

        return redirect(url_for('student_profiles'))

    return render_template('add_profile.html')



@app.route('/edit_profile/<user_id>', methods=['GET', 'POST'])
def edit_profile(user_id):
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        full_name = request.form.get('full_name')
        bio = request.form.get('bio')

        file = request.files.get('profile_picture')
        profile_picture_id = None
        if file and file.filename:
            profile_picture_id = fs.put(file.read(), content_type=file.content_type, filename=file.filename)
        
        update_data = {
            'username': username,
            'email': email,
            'full_name': full_name,
            'bio': bio
        }
        
        if profile_picture_id:
            update_data['profile_picture'] = profile_picture_id

        users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )
        
        return redirect(url_for('profile', user_id=user_id))
    
    user = users_collection.find_one({'_id': ObjectId(user_id)})
    if not user:
        return "User not found", 404
    return render_template('edit_profile.html', user=user)

@app.route('/user_profile_list')
def user_profile_list():
    users = list(users_collection.find())
    return render_template('user_profile_list.html', users=users)










@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        admin_user = admin_users_collection.find_one({"username": username})
        
        if admin_user and admin_user['password'] == password:
            session['admin_logged_in'] = True
            session['admin_username'] = username
            flash('Admin Login Successful!', 'success')
            return redirect(url_for('admin_page'))
        else:
            flash('Invalid admin username or password', 'danger')
            return redirect(url_for('admin_login'))
    return render_template('admin_login.html')

@app.route('/admin_register', methods=['GET', 'POST'])
def admin_register():
    if not session.get('admin_logged_in'):
        flash('You need to be logged in as an admin to access this page.', 'warning')
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        name = request.form.get('name')
        contact = request.form.get('contact')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        
        existing_user = admin_users_collection.find_one({"username": username})
        if existing_user:
            flash('Username already exists!', 'danger')
            return redirect(url_for('admin_register'))

        admin_user = {
            "name": name,
            "contact": contact,
            "email": email,
            "username": username,
            "password": password
        }
        admin_users_collection.insert_one(admin_user)
        flash('Admin Registration Successful! Please log in.', 'success')
        return redirect(url_for('admin_login'))
    return render_template('admin_register.html')

@app.route('/admin_page')
def admin_page():
    if not session.get('admin_logged_in'):
        flash('Please log in to access the admin page.', 'warning')
        return redirect(url_for('admin_login'))
    return render_template('admin_page.html')

@app.route('/admin_logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if not session.get('admin_logged_in'):
        flash('You need to be logged in as an admin to access this page.', 'warning')
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        file = request.files['file']
        file_path = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            file_path = f'static/images/uploads/{filename}'
        blog = {
            "title": title,
            "content": content,
            "image_path": file_path,
            "date": datetime.now()
        }
        blogs_collection.insert_one(blog)
        flash('Upload Successful!', 'success')
        return redirect(url_for('index'))
    return render_template('upload.html')

@app.route('/upload_video', methods=['GET', 'POST'])
def upload_video():
    if not session.get('admin_logged_in'):
        flash('You need to be logged in as an admin to access this page.', 'warning')
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        if 'video_upload' in request.form:
            file = request.files['video']
            video_name = request.form.get('video_name')
            video_description = request.form.get('video_description')
            if file and video_name:
                fs.put(file, filename=video_name, description=video_description)
                return redirect(url_for('display_videos'))
        elif 'delete' in request.form:
            video_name = request.form.get('video_name_delete')
            if video_name:
                for video in fs.find({"filename": video_name}):
                    fs.delete(video._id)
                return redirect(url_for('upload_video'))
    return render_template('upload_video.html')

@app.route('/video_lectures')
def video_lectures():
    if not session.get('user_logged_in'):
        flash('You need to be logged in as a user to access this page.', 'warning')
        return redirect(url_for('login'))
    return redirect(url_for('display_videos'))

@app.route('/display_videos')
def display_videos():
    videos = fs.find()
    return render_template('display.html', videos=videos)

@app.route('/video/<video_id>')
def view_video(video_id):
    video = fs.get(ObjectId(video_id))
    return render_template('display.html', videos=[video])

@app.route('/video_data/<video_id>')
def get_video(video_id):
    video = fs.get(ObjectId(video_id))
    range_header = request.headers.get('Range', None)
    if not range_header:
        return Response(video.read(), content_type='video/mp4')
    
    size = video.length
    byte1, byte2 = 0, None
    match = re.search(r'(\d+)-(\d*)', range_header)
    if match:
        g = match.groups()
        if g[0]: byte1 = int(g[0])
        if g[1]: byte2 = int(g[1])
    
    byte2 = byte2 if byte2 else size - 1
    length = byte2 - byte1 + 1
    video.seek(byte1)
    
    data = video.read(length)
    rv = Response(data, 206, mimetype='video/mp4', 
                  content_type='video/mp4', 
                  direct_passthrough=True)
    rv.headers.add('Content-Range', f'bytes {byte1}-{byte2}/{size}')
    rv.headers.add('Accept-Ranges', 'bytes')
    
    return rv



# user student login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        device_info = request.headers.get('User-Agent')  # This is a simple way to get device info

        user = users_collection.find_one({'username': username})
        if user and user['password'] == password:
            device_id = get_device_id(device_info)

            # Check if device is already registered
            registered_devices = user.get('devices', [])
            registered_device_ids = [device['device_id'] for device in registered_devices]

            if device_id not in registered_device_ids:
                if len(registered_devices) >= MAX_DEVICES:
                    flash('Maximum devices reached. You cannot register a new device.', 'warning')
                    return redirect(url_for('login'))
                # Register the new device
                new_device = {
                    'device_id': device_id,
                    'device_info': device_info
                }
                registered_devices.append(new_device)
                users_collection.update_one({'username': username}, {'$set': {'devices': registered_devices}})
            
            # Check for existing session
            # if user.get('session_id'):
            #     flash('You are already logged in from another device. Please log out from the current session before logging in.', 'warning')
            #     return redirect(url_for('login'))

            new_session_id = str(uuid.uuid4())
            session['user_logged_in'] = True
            session['username'] = username
            session['session_id'] = new_session_id
            
            users_collection.update_one(
                {'username': username},
                {'$set': {'session_id': new_session_id}}
            )
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    
    return render_template('login.html')


@app.route('/user_logout', methods=['POST'])
def user_logout():
    username = session.get('username')
    if not username:
        flash('You are not logged in.', 'warning')
        return redirect(url_for('login'))
    
    users_collection.update_one(
        {'username': username},
        {'$unset': {'session_id': ""}}
    )
    session.clear()
    flash('Logout successful.', 'success')
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    
    if request.method == 'POST':
        name = request.form['name']
        contact = request.form['contact']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        file = request.files.get('profile_picture')

        # Check if username already exists
        if users_collection.find_one({'username': username}):
            flash('Username already exists')
            return redirect(url_for('register'))

        profile_picture_id = None
        if file and file.filename:
            filename = secure_filename(file.filename)
            profile_picture_id = fs.put(file.read(), filename=filename, content_type=file.content_type)

        # Create user document
        new_user = {
            'name': name,
            'contact': contact,
            'email': email,
            'username': username,
            'password': password,  # Ensure you hash the password in a real application
            'profile_picture': profile_picture_id
        }
        
        users_collection.insert_one(new_user)
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# @app.route('/dashboard')
# def dashboard():
#     if 'username' in session:
#         return f'Welcome {session["username"]}!'
#     return redirect(url_for('login'))
@app.route('/user_dashboard')
def user_dashboard():
    if 'user_logged_in' in session:
        return render_template('user_dashboard.html')
    else:
        flash('You need to log in to access the dashboard.', 'warning')
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))





@app.route('/blogs', methods=['GET'])
def blogs():
    month = request.args.get('month')
    year = request.args.get('year')
    if month and year:
        blogs = blogs_collection.find({
            "$expr": {
                "$and": [
                    {"$eq": [{"$month": "$date"}, int(month)]},
                    {"$eq": [{"$year": "$date"}, int(year)]}
                ]
            }
        }).sort("date", -1)
    else:
        blogs = blogs_collection.find().sort("date", -1)
    return render_template('blogs.html', blogs=blogs, datetime=datetime)

@app.route('/faculty')
def faculty():
    members = list(collection.find())
    return render_template('faculty.html', members=members)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'jfif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/add_faculty_member', methods=['GET', 'POST'])
def add_faculty_member():
    if not session.get('admin_logged_in'):
        flash('You need to be logged in as an admin to access this page.', 'warning')
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        id = request.form['id']
        name = request.form['name']
        current_affiliation = request.form['current_affiliation']
        designation = request.form['designation']
        expertise = request.form['expertise']
        research_areas = request.form['research_areas']
        extra_qualification = request.form.get('extra_qualification', '')
        contact = request.form['contact']
        google_link = request.form.get('google_link', '')

         # Check if the ID already exists in the database
        if collection.find_one({'id': id},{'contact': contact}):
            flash('This ID or contact is already being used.', 'error')
            return redirect(url_for('add_faculty_member'))

        # Handle image file upload
        file = request.files.get('image')
        image_id = None
        if file and allowed_file(file.filename):
            image_id = fs.put(file.read(), content_type=file.content_type, filename=file.filename)

        # Create a new member dictionary
        new_member = {
            'id': id,
            'name': name,
            'current_affiliation': current_affiliation,
            'designation': designation,
            'expertise': expertise,
            'research_areas': research_areas,
            'extra_qualification': extra_qualification,
            'contact': contact,
            'google_link': google_link,
            'image': image_id
        }

        # Insert into MongoDB
        collection.insert_one(new_member)

        flash('Member added successfully!', 'success')
        return redirect(url_for('faculty'))

    return render_template('add_faculty_member.html')


@app.route('/faculty_member/<member_id>')
def faculty_member(member_id):
    member = collection.find_one({"_id": ObjectId(member_id)})
    if member:
        image_id = member.get('image')
        image_url = url_for('get_image', file_id=image_id) if image_id else None
        return render_template('faculty_member.html', member=member, image_url=image_url)
    else:
        flash('Faculty member not found.', 'danger')
        return redirect(url_for('faculty'))

@app.route('/faculty_image/<file_id>')
def get_faculty_image(file_id):
    image = fs.get(ObjectId(file_id))
    return send_file(io.BytesIO(image.read()), mimetype=image.content_type)



def save_image_to_mongo(image_file, faculty_id):
    # Save image to GridFS
    file_id = fs.put(image_file, filename=faculty_id)
    
    # Save file_id in the faculty_members collection
    collection = db['faculty_members']
    collection.update_one({'_id': faculty_id}, {'$set': {'image_id': file_id}})


if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True, port=1000)
#  host="192.168.15.156",