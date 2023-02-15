import os
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from flask import Flask, make_response, redirect, render_template, request, jsonify, url_for, send_from_directory, send_file
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_wtf import FlaskForm
from wtforms import HiddenField
from base64 import b64encode
from models import File

app = Flask(__name__)
app.jinja_env.filters['b64encode'] = b64encode


class DeleteForm(FlaskForm):
        _method = HiddenField(default="DELETE")

engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgres', echo=True)
Session = sessionmaker(bind=engine)

session = Session()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif'}

    for file in request.files.getlist('file[]'):
        name = secure_filename(file.filename)
        data = file.read()
        _, ext = os.path.splitext(name)

        if ext.lower() in image_extensions:
            file = File(name=name, data=data)
            session = Session()
            session.add(file)
            file.created_at = datetime.now()
            session.commit()
        else:
            file = File(name=name, data=data)
            session = Session()
            session.add(file)
            file.created_at = datetime.now()
            session.commit()

    return jsonify({'message': f"{len(request.files.getlist('file[]'))} file(s) uploaded successfully."})

@app.route('/files/<filename>')
def get_file(filename):
    session = Session()
    file = session.query(File).filter_by(name=filename).first()
    session.close()

    if file:
        response = make_response(file.data)
        response.headers.set('Content-Disposition', 'attachment', filename=file.name)
        return response
    else:
        return jsonify({'error': 'File not found.'}), 404 

@app.route('/files')
def files():
    session = Session()
    files = session.query(File).filter(File.deleted == False).all()
    session.close()

    return render_template('files.html', files=files)

@app.route('/delete/<filename>/<id>', methods=['GET', 'POST'])
def delete(filename, id):
    session = Session()
    file = session.query(File).filter_by(name=filename, id=id).first()

    if request.form.get('_method') == 'DELETE':
        if file:
            session.delete(file)
            session.commit()
            return jsonify({'message': 'File deleted successfully.'})

    if file:
        file.deleted = True
        file.deleted_at = datetime.now()
        session.commit()

        return jsonify({'message': 'File deleted successfully.'})
        
    return jsonify({'error': 'File not found.'}), 404


@app.route('/restore/<filename>/<id>', methods=['POST', 'PUT'])
def restore(filename, id):
    session = Session()
    file = session.query(File).filter_by(name=filename, id=id).first()

    if request.form.get('_method') == 'PUT':
        if file:
            file.deleted = False
            file.deleted_at = None
            session.commit()

            return jsonify({'message': 'File restored successfully.'})

    if file:
        file.deleted = False
        file.deleted_at = None
        file.commit()

        return jsonify({'message': 'File restored successfully.'})
        
    return jsonify({'error': 'Image not found.'}), 404


@app.route('/trash')
def trash():
    session = Session()
    files = session.query(File).filter_by(deleted=True).all()

    return render_template('trash.html', files=files)


if __name__ == '__main__':
    app.run(debug=True)

