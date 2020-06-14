from flask import Flask , redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from werkzeug.utils import secure_filename
import os
from flask import send_from_directory
import numpy as np
import pandas as pd
import operator
import functools


UPLOAD_FOLDER = '.'
ALLOWED_EXTENSIONS = {'txt', 'csv'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "hehehe"
app.permanent_session_lifetime = timedelta(minutes=5)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower()in ALLOWED_EXTENSIONS

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    array = np.loadtxt(r"" + filename, delimiter=' ',)
    max_y = np.max(array[:,1], axis=0)
    row_max_y = array[array[:,1] == max_y]
    row_num_max_y = np.where(array[:,1] == max_y)
    int_row_max = functools.reduce(lambda sub, ele: sub *10 + ele, row_num_max_y[0])

    x_all = np.array([array[:,0]])
    y_all = np.array([array[:,1]])

    x_flat_all = x_all.flatten()
    y_flat_all = y_all.flatten()
    sec_1 = array[int_row_max: int_row_max + 800, 0:2]
    x_1 = np.array([sec_1[:,0]])
    y_1 = np.array([sec_1[:,1]])
    x_flat_1 = x_1.flatten()
    y_flat_1 = y_1.flatten()

    z_1 = np.polyfit(x_flat_1, y_flat_1, 4)
    p = np.poly1d(z_1)

    nest = []
    for i in x_flat_1[:]:
        nest.append(p(i))
    new_y = np.array(nest)
    new_y_flat = new_y.flatten()

    dy = np.diff(new_y_flat) / np.diff(x_flat_1)

    x_flat_dx = x_flat_1[:-1]

    ddy = np.diff(dy) / np.diff(x_flat_dx)

    x_flat_ddx = x_flat_dx[:-1]

    array_2nd = np.stack((x_flat_ddx, ddy), axis=1)

    highest = -10
    for i in array_2nd[:, 1]:
                if i > highest:
                    highest = i

                    if i > 0:
                        break
    
    imp_val = np.where(array_2nd[:,1] == highest)
    int_imp_val = functools.reduce(lambda sub, ele: sub *10 + ele, imp_val[0])

    array_1st = np.stack((x_flat_dx, dy), axis=1)
    x_val_imp_val = array_2nd[int_imp_val, 0]

    imp_val = np.where(array_2nd[:,1] == highest)
    int_imp_val = functools.reduce(lambda sub, ele: sub *10 + ele, imp_val[0])

    deriv_slope = np.where(array_1st[:,0] == x_val_imp_val)
    x_int_imp_val = functools.reduce(lambda sub, ele: sub *10 + ele, deriv_slope[0])


    slope = array_1st[x_int_imp_val,1]

    b_val = np.where(array[:,0] == x_val_imp_val)
    int_b_val = functools.reduce(lambda sub, ele: sub *10 + ele, b_val[0])

    b_line = array[int_b_val,1]

    ys = []
    for i in sec_1[:,0]:
        ys.append(slope*i + b_line)


    ys_final = np.array(ys)
    ys_final_flat = new_y.flatten()

    line_stacked = np.stack((x_flat_1, ys_final_flat), axis=1)

    low = 10
    for i in line_stacked[:, 1]:
            if i < low:
                low = i

                if i < 0:
                    break
    
    final_x_value = (low - b_line)/(slope) + x_val_imp_val

    return render_template("final_x.html", final_x_value = final_x_value)


if __name__ == "__main__":
    app.run(debug=True)