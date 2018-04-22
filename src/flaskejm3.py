#Instalar opencv en el servidor que usemos
import os,json,requests
from flask import Flask, request, redirect, url_for, flash,send_from_directory
from werkzeug.utils import secure_filename
from watson_developer_cloud import VisualRecognitionV3
#asi se hace un post desde consola
#curl -F "file=@/home/mhincapie/Imágenes/oe.png" http://127.0.0.1:5000/
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = APP_ROOT + '/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
visual_recognition = VisualRecognitionV3(
	'2016-05-20',
	api_key="4893812447dc238483d5c01a41dfc798057baaeb")

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#Comprobar si el archivo tiene extencion valida
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#ruta para el inicio y para hacer el post con la imagen
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        if not os.path.isdir(UPLOAD_FOLDER):
            os.mkdir(UPLOAD_FOLDER)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #envio a IBM para clasifcar
            file_path = UPLOAD_FOLDER +'/'+ filename
            with open(file_path, 'rb') as images_file:
                classes = visual_recognition.classify(
			    images_file,
			    parameters=json.dumps({
				    'classifier_ids': ['DefaultCustomModel_914733598'],
				    'threshold': 0.6
			    }))
            predict = classes["images"][0]["classifiers"][0]["classes"][0]["class"]
            print(predict)
            #aca acaba el envio a IBM
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

if __name__== '__main__':
    app.run(debug=True)