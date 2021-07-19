from flask import render_template, url_for, flash, redirect,request
from crop_advisor import app , db, bcrypt,func
from crop_advisor.forms import UserLoginForm , RegistrationForm,ChangePassword,FertilizerPredict,CropPredict,UpdateAccountForm
from crop_advisor.models import Approval, User, Admin,CropPrice,Messages
from crop_advisor.predict_methods import fert_recommend,crop_recommendation_model,weather_fetch,predict_image,weather_predict
from flask_login import login_user, current_user, logout_user, login_required
import numpy as np
import secrets
import os
from PIL import Image

#from flask_login import login_user, current_user, logout_user, login_required
    
@app.route("/")
@app.route("/home")
def home():
    if not Admin.query.all():
        pwd='Admin@Advisor'
        pswrd=bcrypt.generate_password_hash(pwd).decode('utf-8')
        user = Admin(email='admin@advisor.com',password=pswrd)
        db.session.add(user)
        db.session.commit()
    return render_template('home.html', title='Home')

@app.route("/adminhome")
def adminhome():
    return render_template('adminhome.html', title='Home')

@app.route("/userhome")
def userhome():
    return render_template('userhome.html', title='Home')

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/adminabout")
def adminabout():
    return render_template('adminabout.html', title='About')

@app.route("/userabout")
def userabout():
    return render_template('userabout.html', title='About')

@app.route("/fertilizerpredict",methods=['GET','POST'])
def fertilizerpredict():
    form= FertilizerPredict()
    if request.method=='POST':
        N = int(request.form['nitrogen'])
        P = int(request.form['phosphorous'])
        K = int(request.form['pottasium'])
        crop = request.form.get("crop")
        response=fert_recommend(N,P,K,crop)
        return render_template('fertilizerresult.html', recommendation=response, title='Fertlilizer-Suggestion')
    return render_template('fertilizerpredict.html', title='Fertilizer-Suggestion',form=form)
    

@app.route("/croppredict",methods=['GET','POST'])
def croppredict():
    form= CropPredict()
    if request.method=='POST':
        N = int(request.form['nitrogen'])
        P = int(request.form['phosphorous'])
        K = int(request.form['pottasium'])
        ph = float(request.form['ph'])
        rainfall = float(request.form['rainfall'])
        soiltype=request.form.get("soiltype")
        city = request.form.get("city")
        if weather_fetch(city) != None:
            temperature, humidity = weather_fetch(city)
            data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
            prediction = crop_recommendation_model(data)
            return render_template('cropresult.html', recommendation=prediction, title='Crop Recommendation')
        else:
            flash("Sorry we couldn't process your request currently.Please check your internet connection and try again",'danger')
            return redirect(url_for('croppredict'))
    return render_template('croppredict.html', title='Crop Recommendation',form=form)

@app.route("/diseasepredict",methods=['GET','POST'])
def diseasepredict():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Please upload an Image of crop leave..','danger')
            return redirect(url_for('diseasepredict'))
        file = request.files.get('file')
        if not file:
            flash('Please upload an Image of crop leave..','danger')
            return redirect(url_for('diseasepredict'))
        try:
            img = file.read()

            prediction = predict_image(img)

            return render_template('diseaseresult.html', prediction=prediction, title='Disease Prediction')
        except:
            flash('Please upload an Image of crop leave..','danger')
            pass    
    
    return render_template('diseasepredict.html', title='Disease Prediction')

@app.route("/userlogin", methods=['GET', 'POST'])
def userlogin():
    if current_user.is_authenticated:
        return redirect(url_for('userhome'))
    form = UserLoginForm()
    if form.validate_on_submit():
        userrequest = Approval.query.filter_by(email=form.email.data).first()
        user=User.query.filter_by(email=form.email.data).first()
        if userrequest:
            flash('Your request for membership is pending, please try after sometimes..', 'info')
            return redirect(url_for('userlogin'))
        elif not user:
            flash('You are not a member, please sign up..','info')
            return redirect(url_for('userlogin'))
        elif user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Logged in successfully..!','success')
            return redirect(url_for('userhome'))
        else:
            flash('Please check your password..','danger')
            return redirect(url_for('userlogin'))
    return render_template('userlogin.html',title='Login',form=form)
    
    
            

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = Approval(username=form.username.data, email=form.email.data, phone=form.phone.data,
                        city=form.city.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your request for the registration will be processed with in 24 hours!', 'success')
        return redirect(url_for('userlogin'))
    return render_template('register.html', title='Registration Form', form=form)
 

@app.route("/adminlogin", methods=['GET', 'POST'])
def adminlogin():
    form = UserLoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@advisor.com' and form.password.data == 'Admin@Advisor':
            flash('hello Admin... \n You have been logged in!', 'success')
            return redirect(url_for('adminhome'))
        else:
            flash('Login Unsuccessful. Please check Email address and password', 'danger')
    return render_template('adminlogin.html', title='Login', form=form)

@app.route("/memberrequests")
def memberrequests():
    result=Approval.query.all()
    return render_template('memberrequests.html', title='Member Requests',result=result)

@app.route("/approved/<int:id>")
def approved(id):
    user1=Approval.query.get_or_404(id)
    db.session.delete(user1)
    user2 = User(username=user1.username, email=user1.email, phone=user1.phone,
                        city=user1.city, image_file=user1.image_file, password=user1.password)
    db.session.add(user2)
    db.session.commit()
    return redirect(url_for('memberrequests'))

@app.route("/deleterequest/<int:id>")
def deleterequest(id):
    user1=Approval.query.get_or_404(id)
    db.session.delete(user1)
    db.session.commit()
    return redirect(url_for('memberrequests'))

@app.route("/usersdetails")
def usersdetails():
    result=User.query.all()
    return render_template('usersdetails.html', title='Users list',result=result)

@app.route("/changepswrd",methods=['GET','POST'])
def changepassword():
    form=ChangePassword()
    if form.validate_on_submit():
        record=Admin.query.all()[0]
        if bcrypt.check_password_hash(record.password,form.current_password.data):
            record.password=bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            db.session.commit()
            flash('Password changed successfully..!', 'success')
            return redirect(url_for('adminhome'))
        else:
            flash('Please enter correct current password', 'danger')
    return render_template('changepswrd.html', title='Change Password',form=form)
            

@app.route("/deletemember/<int:id>")
def deletemember(id):
    user1=User.query.get_or_404(id)
    db.session.delete(user1)
    db.session.commit()
    return redirect(url_for('usersdetails'))

@app.route("/cropprice",methods=['GET','POST'])
def cropprice():
    crops=[(croprecords.crop) for croprecords in CropPrice.query.all()]
    if request.method=='POST':
        cropname=request.form["crop2"]
        rate=float(request.form['price2'])
        record =CropPrice.query.filter(func.lower(CropPrice.crop) == func.lower(cropname)).first()
        if record:
            flash('This crop is already added..','info')
        else:
            record=CropPrice(crop=cropname,price=rate)
            db.session.add(record)
            db.session.commit()
            flash('crop added successfully..!','success')
            return redirect(url_for('cropprice'))
    return render_template('cropprice.html', title="Crop price",names=crops)
    
@app.route("/croppriceedit",methods=['POST'])
def croppriceedit():
    if request.method=='POST':
        cropname=request.form.get("crop1")
        rate=float(request.form['price1'])
        entry=CropPrice.query.filter_by(crop=cropname).first()
        entry.price=rate
        db.session.commit()
        flash('crop price updated successfully..!','success')
        return redirect(url_for('cropprice'))
    
@app.route("/admincropview")
def admincropview():
    result=CropPrice.query.all()
    return render_template('admincropview.html', title='Crop price list',result=result)

@app.route("/usercropview")
def usercropview():
    result=CropPrice.query.all()
    return render_template('usercropview.html', title='Crop price list',result=result)
    

@app.route("/deletecropprice/<int:id>")
def deletecropprice(id):
    crop=CropPrice.query.get_or_404(id)
    db.session.delete(crop)
    db.session.commit()
    flash("Deleted successfully...!",'success')
    return redirect(url_for('admincropview'))

@app.route("/contactus",methods=['GET','POST'])
def contactus():
    if request.method=='POST':
        useremail=current_user.email
        sub=request.form['subject']
        msg=request.form['message']
        record=Messages(email=useremail,subject=sub,message=msg)
        db.session.add(record)
        db.session.commit()
        flash('your message sent successfully..!','success')
    return render_template('contactus.html', title='Contact us')

@app.route("/messageview")
def messageview():
    result=Messages.query.all()
    return render_template('messageview.html', title='Users Messages',result=result)

@app.route("/messagedelete/<int:id>")
def messagedelete(id):
    msg=Messages.query.get_or_404(id)
    db.session.delete(msg)
    db.session.commit()
    flash("Message deleted duccessfully...!",'success')
    return redirect(url_for('messageview'))

@app.route("/userprofile")
def userprofile(): 
    image_file = url_for('static', filename='profile/' + current_user.image_file)
    return render_template('userprofile.html', title='Profile',image=image_file)

@app.route("/userlogout")
def userlogout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/adminlogout")
def adminlogout():
    return redirect(url_for('home'))

@app.route("/weatherinformation",methods=['GET','POST'])
def weatherinformation():
    if request.method=="POST":
        city=request.form.get("city")
        weather=weather_predict(city)
        if weather != None:
            return render_template('weatherinforesult.html',dic=weather,title="Weather Information")
        else:
            flash("Sorry we couldn't process your request currently.Please check your internet connection..",'info')
            return redirect(url_for('weatherinformation'))     
    return render_template('weatherinfo.html',title="Weather Information")


@app.route("/editprofile",methods=['GET','POST'])
@login_required
def editprofile():
    form=UpdateAccountForm()
    if form.validate_on_submit():
        current_user.email=form.email.data
        current_user.username= form.username.data
        current_user.phone = form.phone.data
        current_user.city= form.city.data
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('userprofile'))
    if request.method=='GET':
        form.username.data=current_user.username
        form.email.data=current_user.email
        form.phone.data=current_user.phone
        form.city.data=current_user.city
        return render_template('editprofile.html', title='Profile',form=form)

@app.route("/userchangepassword",methods=['GET','POST'])
def userchangepassword():
    form=ChangePassword()
    if form.validate_on_submit():
        if bcrypt.check_password_hash(current_user.password,form.current_password.data):
            current_user.password=bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            db.session.commit()
            flash('Password changed successfully..!', 'success')
            return redirect(url_for('userhome'))
        else:
            flash('Please enter correct current password', 'danger')
    return render_template('userchangepassword.html', title='Change Password',form=form)


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static\profile', picture_fn)
    output_size = (175, 175)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn




