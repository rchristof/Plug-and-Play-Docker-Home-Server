from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Flask, make_response, redirect, render_template, request, jsonify, url_for
from sqlalchemy import Boolean, DateTime, create_engine, Column, Integer, String, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from flask_wtf import FlaskForm
from wtforms import HiddenField
from base64 import b64encode

app = Flask(__name__)
Base = declarative_base()
app.jinja_env.filters['b64encode'] = b64encode

class Image(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    data = Column(LargeBinary, nullable=False)
    deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)

class DeleteForm(FlaskForm):
        _method = HiddenField(default="DELETE")

engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgres', echo=True)
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist('file[]')

    for file in files:
        name = secure_filename(file.filename)
        data = file.read()
        image = Image(name=name, data=data)

        session = Session()
        session.add(image)
        session.commit()
    return jsonify({'message': f"{len(files)} image(s) uploaded successfully."})

@app.route('/images/<int:image_id>')
def get_image(image_id):
    session = Session()
    image = session.query(Image).filter_by(id=image_id).first()
    session.close()

    if not image:
        return jsonify({'error': 'Image not found.'}), 404

    response = make_response(image.data)
    response.headers.set('Content-Type', 'image/jpeg')
    response.headers.set('Content-Disposition', 'attachment', filename=image.name)

    return response

@app.route('/images')
def get_images():
    session = Session()
    # images = session.query(Image).all() # get all images
    images = session.query(Image).filter(Image.deleted == False).all() # get all images that are not deleted
    return render_template('images.html', images=images)

# @app.route('/delete/<int:id>', methods=['DELETE'])
# def delete(id):
#     session = Session()
#     image = session.query(Image).filter_by(id=id).first()
#     if image:
#         session.delete(image)
#         session.commit()
#         return jsonify({'message': 'Image deleted successfully.'})
#     return jsonify({'error': 'Image not found.'}), 404

@app.route('/delete/<int:image_id>', methods=['GET', 'POST'])
def delete(image_id):
    session = Session()
    image = session.query(Image).get(image_id)

    if request.form.get('_method') == 'DELETE':
        if image:
            session.delete(image)
            session.commit()
            return jsonify({'message': 'Image deleted successfully.'})
        delete_form = DeleteForm()
        return render_template('delete.html', image=image, delete_form=delete_form)

    if image:
        image.deleted = True
        image.deleted_at = datetime.now()
        session.commit()

        return jsonify({'message': 'Image deleted successfully.'})
        
    return jsonify({'error': 'Image not found.'}), 404


@app.route('/restore/<int:image_id>', methods=['POST', 'PUT'])
def restore(image_id):
    session = Session()
    image = session.query(Image).get(image_id)

    if request.form.get('_method') == 'PUT':
        if image:
            image.deleted = False
            image.deleted_at = None
            session.commit()

            return jsonify({'message': 'Image restored successfully.'})
        
    if image:
        image.deleted = False
        image.deleted_at = None
        session.commit()

        return jsonify({'message': 'Image restored successfully.'})
        
    return jsonify({'error': 'Image not found.'}), 404


@app.route('/trash')
def trash():
    session = Session()
    images = session.query(Image).filter_by(deleted=True).all()

    return render_template('trash.html', images=images)


if __name__ == '__main__':
    app.run(debug=True)

