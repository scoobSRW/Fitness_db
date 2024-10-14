from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
import mysql.connector
from mysql.connector import Error
from password import my_password

app = Flask(__name__)
ma = Marshmallow(app)

def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='Fitness_db',
            user='root',
            password=my_password
        )
        if connection.is_connected():
            print("Connected to MySQL database")
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None

# Welcome page route
@app.route('/', methods=['GET'])
def welcome():
    return ("<h1>Welcome to Fitness Database</h1>")

class MemberSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'age')


member_schema = MemberSchema()
members_schema = MemberSchema(many=True)


@app.route('/members', methods=['POST'])
def add_member():
    data = request.get_json()
    name = data['name']
    age = data['age']

    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO Members (name, age) VALUES (%s, %s)", (name, age))
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"message": "Member added successfully!"}), 201


@app.route('/members/<int:id>', methods=['GET'])
def get_member(id):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Members WHERE id = %s", (id,))
    member = cursor.fetchone()
    cursor.close()
    connection.close()

    if member:
        return member_schema.jsonify({
            'id': member[0],
            'name': member[1],
            'age': member[2]
        })
    else:
        return jsonify({"error": "Member not found"}), 404


@app.route('/members/<int:id>', methods=['PUT'])
def update_member(id):
    data = request.get_json()
    name = data['name']
    age = data['age']

    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE Members SET name = %s, age = %s WHERE id = %s", (name, age, id))
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"message": "Member updated successfully!"})


@app.route('/members/<int:id>', methods=['DELETE'])
def delete_member(id):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM Members WHERE id = %s", (id,))
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"message": "Member deleted successfully!"})


class WorkoutSessionSchema(ma.Schema):
    class Meta:
        fields = ('session_id', 'member_id', 'session_date', 'session_time', 'activity')


workout_session_schema = WorkoutSessionSchema()
workout_sessions_schema = WorkoutSessionSchema(many=True)


@app.route('/workout_sessions', methods=['POST'])
def add_workout_session():
    data = request.get_json()
    member_id = data['member_id']
    session_date = data['session_date']
    session_time = data['session_time']
    activity = data['activity']

    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO WorkoutSessions (member_id, session_date, session_time, activity)
        VALUES (%s, %s, %s, %s)
    """, (member_id, session_date, session_time, activity))
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"message": "Workout session added successfully!"}), 201


@app.route('/workout_sessions/member/<int:member_id>', methods=['GET'])
def get_workouts_for_member(member_id):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM WorkoutSessions WHERE member_id = %s", (member_id,))
    sessions = cursor.fetchall()
    cursor.close()
    connection.close()

    session_list = []
    for session in sessions:
        session_dict = {
            'session_id': session[0],
            'member_id': session[1],
            'session_date': session[2],
            'session_time': session[3],
            'activity': session[4]
        }
        session_list.append(session_dict)

    if session_list:
        return workout_sessions_schema.jsonify(session_list)
    else:
        return jsonify({"error": "No workout sessions found for this member"}), 404



if __name__ == "__main__":
    app.run(debug=True)
