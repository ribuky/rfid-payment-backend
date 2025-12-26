from flask import Blueprint, render_template, jsonify, request

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('login.html')