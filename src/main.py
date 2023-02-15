import os
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Flask, make_response, redirect, render_template, request, jsonify, url_for, send_from_directory, send_file
from sqlalchemy import Boolean, DateTime, create_engine, Column, Integer, String, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, joinedload
from flask_wtf import FlaskForm
from wtforms import HiddenField
from base64 import b64encode
from models import Image, Archive

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
            image = Image(name=name, data=data)
            session = Session()
            session.add(image)
            session.commit()
        else:
            archive = Archive(name=name, data=data)
            session = Session()
            session.add(archive)
            session.commit()
    return jsonify({'message': f"{len(request.files.getlist('file[]'))} file(s) uploaded successfully."})

@app.route('/files/<filename>')
def get_file(filename):
    session = Session()
    archive = session.query(Archive).filter_by(name=filename).first()
    image = session.query(Image).filter_by(name=filename).first()
    session.close()

    if image:
        response = make_response(image.data)
        response.headers.set('Content-Disposition', 'attachment', filename=image.name)
        return response
    elif archive:
        response = make_response(archive.data)
        response.headers.set('Content-Disposition', 'attachment', filename=archive.name)
        return response
    else:
        return jsonify({'error': 'File not found.'}), 404 

@app.route('/files')
def files():
    session = Session()
    archives = session.query(Archive).filter(Archive.deleted == False).all()
    images = session.query(Image).filter(Image.deleted == False).all()
    session.close()

    return render_template('files.html', images=images, archives=archives)

# @app.route('/delete/<int:id>', methods=['DELETE'])
# def delete(id):
#     session = Session()
#     image = session.query(Image).filter_by(id=id).first()
#     if image:
#         session.delete(image)
#         session.commit()
#         return jsonify({'message': 'Image deleted successfully.'})
#     return jsonify({'error': 'Image not found.'}), 404

@app.route('/delete/<filename>/<id>', methods=['GET', 'POST'])
def delete(filename, id):
    session = Session()
    archive = session.query(Archive).filter_by(name=filename, id=id).first()
    image = session.query(Image).filter_by(name=filename, id=id).first()

    if request.form.get('_method') == 'DELETE':
        if image:
            session.delete(image)
            session.commit()
            return jsonify({'message': 'Image deleted successfully.'})
        elif archive:
            session.delete(archive)
            session.commit()
            return jsonify({'message': 'Archive deleted successfully.'})
        delete_form = DeleteForm()
        return render_template('delete.html', image=image, archive=archive, delete_form=delete_form)

    if image:
        image.deleted = True
        image.deleted_at = datetime.now()
        session.commit()

        return jsonify({'message': 'Image deleted successfully.'})
    elif archive:
        archive.deleted = True
        archive.deleted_at = datetime.now()
        session.commit()
        
        return jsonify({'message': 'File deleted successfully.'})
        
    return jsonify({'error': 'Image not found.'}), 404


@app.route('/restore/<filename>/<id>', methods=['POST', 'PUT'])
def restore(filename, id):
    session = Session()
    archive = session.query(Archive).filter_by(name=filename, id=id).first()
    image = session.query(Image).filter_by(name=filename, id=id).first()

    if request.form.get('_method') == 'PUT':
        if image:
            image.deleted = False
            image.deleted_at = None
            session.commit()

            return jsonify({'message': 'Image restored successfully.'})
        elif archive:
            archive.deleted = False
            archive.deleted_at = None
            session.commit()

            return jsonify({'message': 'Archive restored successfully.'})
        
    if image:
        image.deleted = False
        image.deleted_at = None
        session.commit()
    elif archive:
        archive.deleted = False
        archive.deleted_at = None
        session.commit()

        return jsonify({'message': 'Image restored successfully.'})
        
    return jsonify({'error': 'Image not found.'}), 404


@app.route('/trash')
def trash():
    session = Session()
    archives = session.query(Archive).filter_by(deleted=True).all()
    images = session.query(Image).filter_by(deleted=True).all()

    return render_template('trash.html', images=images, archives=archives)


if __name__ == '__main__':
    app.run(debug=True)

