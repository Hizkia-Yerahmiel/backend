from flask import Flask, render_template, request, redirect, jsonify, session

app = Flask(__name__)
app.secret_key = 'lnadbvajd123'

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("kunci.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

daftar_mahasiswa = []

@app.route('/')
def index():
    if 'login' not in session:
        return redirect('/login')
    
    daftar_mahasiswa = []
    # -- stream artinya untuk mengambil semua
    docs = db.collection('mahasiswa').where("nilai", ">", 42).stream()
    for doc in docs:
        # -- to_dict artinya mengubah dictionary firebase ke dictionary python
        mhs = doc.to_dict()
        mhs['id'] = doc.id
        daftar_mahasiswa.append(mhs)
        print(f'{doc.id} => {doc.to_dict()["nama"]}')
    return render_template('index.html', mhs=daftar_mahasiswa)

@app.route('/detail/<uid>')
def detail(uid):
    mahasiswa = db.collection('mahasiswa').document(uid).get().to_dict()
    return render_template('detail.html', siswa=mahasiswa)
    

    # mahasiswa = daftar_mahasiswa[int(uid)-1]
    # return render_template('detail.html', siswa=mahasiswa)


@app.route('/updatedata/<uid>', methods=["POST"])
def updatedata(uid):
    nama = request.form.get("nama")
    nilai = request.form.get("nilai")

    # -- fungsi untuk update ke data firebase
    db.collection('mahasiswa').document(uid).update(
        {
            'nama' : nama,
            'nilai' : int(nilai)
        }
    )

    return redirect('/')



@app.route('/add', methods=["POST"])
def add_data():
    nama = request.form.get("nama")
    nilai = request.form.get("nilai")
    alamat = request.form.get("alamat")
    email = request.form.get("email")
    foto = request.form.get("foto")
    no_hp = request.form.get("no_hp")
    

    mahasiswa = {
        'alamat' : alamat,
        'email' : email,
        'nama' : nama,
        'nilai' : int(nilai),
        'foto' : foto,
        'no_hp' : no_hp
    }

    db.collection("mahasiswa").document().set(mahasiswa)

    daftar_mahasiswa = []
    docs = db.collection('mahasiswa').where("nilai", ">", 42).stream()
    for doc in docs:
        mhs = doc.to_dict()
        mhs['id'] = doc.id
        daftar_mahasiswa.append(mhs)
        print(f'{doc.id} => {doc.to_dict()["nama"]}')
    return render_template('index.html', mhs=daftar_mahasiswa)


# @app.route('/update/<uid>')
# def update(uid):
#     mahasiswa = db.collection('mahasiswa').document(uid).get().to_dict()
#     return render_template('update.html', mhs=mahasiswa)

@app.route('/update/<uid>')
def update(uid):
    mhs = db.collection('mahasiswa').document(uid).get()
    mahasiswa = mhs.to_dict()
    mahasiswa['id'] = mhs.id
    return render_template('update.html', mhs=mahasiswa)


@app.route('/delete/<uid>')
def delete(uid):
    # -- fungsi untuk delete data di firebase
    db.collection('mahasiswa').document(uid).delete()
    
    # -- ambil semua data mahasiswa lagi
    daftar_mahasiswa = []
    docs = db.collection('mahasiswa').stream()
    for doc in docs:
        mhs = doc.to_dict()
        mhs['id'] = doc.id
        daftar_mahasiswa.append(mhs)
        print(f'{doc.id} => {doc.to_dict()["nama"]}')
    return render_template('index.html', mhs=daftar_mahasiswa)


# -- ini adalah API
@app.route('/api/mahasiswa')
def api_mahasiswa():
    daftar_mahasiswa = []
    # -- stream artinya untuk mengambil semua
    docs = db.collection('mahasiswa').stream()
    for doc in docs:
        # -- to_dict artinya mengubah dictionary firebase ke dictionary python
        mhs = doc.to_dict()
        mhs['id'] = doc.id
        daftar_mahasiswa.append(mhs)
    return jsonify(daftar_mahasiswa)


# -- ini adalah API untuk per ID
@app.route('/api/mahasiswa/<uid>')
def api_detail(uid):
    mahasiswa = db.collection('mahasiswa').document(uid).get().to_dict()
    return jsonify(mahasiswa)


@app.route('/login')
def login():
    if 'login' in session:
        return redirect('/')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


@app.route('/proseslogin', methods=["POST"])
def proseslogin():
    username_form = request.form.get("username")
    password_form = request.form.get("password")

#-------------------------------------------------------------------------
    # admins = db.collection('admin').stream()
    # for u in admins:
    #     admin = u.to_dict()
    #     print(admin)
    #     if admin['username'] == username_form and admin['password'] == password_form:
    #         print('berhasil login')
    #         break
    #     else:
    #         print('gagal')
    # return render_template('login.html')
#-------------------------------------------------------------------------
    admins = db.collection('admin').where('username', '==', username_form).stream()
    for u in admins:
        admin = u.to_dict()
        print(admin)
        if admin['password'] == password_form:
            session['login']=True
            return redirect('/')
    return render_template('login.html')


if __name__ == "__main__":
    app.run(debug=True)

# biru = fungsi
# merah = parameter
# hijau = string
# ungu = bawaan pyhton
# putih = variabel 