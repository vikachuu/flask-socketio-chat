from flask import Flask, render_template, request
from flask_socketio import SocketIO, send
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask("Flask socketio chat app")
socketio = SocketIO(app)

uri = "postgres://dppisxtjohrogg:ac0f787289d92afa180b96b5ff7f4cbdf9fee7ba93add22e30f692ed26b48cfa@ec2-54-217-225-16.eu-west-1.compute.amazonaws.com:5432/d186d9us985s0l"
app.config["SQLALCHEMY_DATABASE_URI"] = uri
db = SQLAlchemy(app)


class History(db.Model):
    __tablename__ = "history"

    message_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(100), nullable=False) 
    message_time = db.Column(db.Time, nullable=False)
    message_text = db.Column(db.String(1000), nullable=False)

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/room", methods=["POST"])
def chatroom():
    messages = History.query.all()
    username = request.form["username"]
    return render_template("session.html", messages=messages, username=username)


@socketio.on("message")
def handle_message(data: dict):
    message, username, time = data["message"], data["username"], datetime.now().time()

    message = History(message_text=message, user_name=username, message_time=time)
    db.session.add(message)
    db.session.commit()

    data.update({"time": time.strftime("%H:%M:%S")})
    send(data, broadcast=True)


if __name__ == "__main__":
    socketio.run(app, "0.0.0.0", 8080)
