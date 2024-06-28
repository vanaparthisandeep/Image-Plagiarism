from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
import pymysql
from django.http import HttpResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import matplotlib.pyplot as plt
import cv2
import numpy as np
import os


image_files = []
image_data = []

def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})

def Register(request):
    if request.method == 'GET':
       return render(request, 'Register.html', {})

def Login(request):
    if request.method == 'GET':
       return render(request, 'Login.html', {})




def UploadSuspiciousImage(request):
    if request.method == 'GET':
        return render(request, 'UploadSuspiciousImage.html', {})

def FMM(name):#five modulus algorithm
    img = cv2.imread(name)
    img = cv2.resize(img,(50,50))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rows,cols = img.shape
    for i in range(rows):
        for j in range(cols):
            k = img[i,j]
            if (k % 5) == 4:
                img[i,j] = k + 1
            elif (k % 5) == 3:
                img[i,j] = k + 2
            elif (k % 5) == 2:
                img[i,j] = k - 2
            elif (k % 5) == 1:
                img[i,j] = k - 1
    for i in range(rows):
        for j in range(cols):
            k = img[i,j]
            k = k / 5
            img[i,j] = k
    temp = img.ravel()
    temp = np.min(img)
    for i in range(rows):
        for j in range(cols):
            if img[i,j] > 0:
                img[i,j] = img[i,j] - temp
        
    hist = cv2.calcHist([img], [0], None, [256], [0, 256])
    return hist    


def UploadSuspiciousImageAction(request):
    if request.method == 'POST' and request.FILES['t1']:
        output = ''
        myfile = request.FILES['t1']
        fs = FileSystemStorage()
        name = str(myfile)
        filename = fs.save(name, myfile)
        hist = FMM(name)
        os.remove(name)
        similarity = 0
        file = 'No Match Found'
        hist1 = 0
        for i in range(len(image_files)):
            metric_val = cv2.compareHist(hist, image_data[i], cv2.HISTCMP_INTERSECT)
            if metric_val > similarity:
                similarity = metric_val
                file = image_files[i]
                hist1 = image_data[i]
        output = '<table border=1 align=center><tr><th>Source Original Image Name</th><th>Suspicious Image Name</th><th>Histogram Matching Score</th><th>Plagiarism Result</th></tr>'
        result = 'No Plagiarism Detected'
        print(str(name)+" "+str(similarity))
        if similarity >= 2000:
            result = 'Plagiarism Detected'
        output+='<tr><td><font size="" color="white">'+file+'</td><td><font size="" color="white">'+name+'</td>'
        output+='<td><font size="" color="white">'+str(similarity)+'</td><td><font size="" color="white">'+result+'</td></tr>'
        context= {'data':output}
        fig, ax = plt.subplots(2,1)
        ax[0].plot(hist1, color = 'b')
        ax[1].plot(hist, color = 'g')
        plt.xlim([0, 256])
        ax[0].set_title('Original image')
        ax[1].set_title('Suspicious image')
        plt.show()
        return render(request, 'SuspiciousImageResult.html', context)        
        


    

def UploadSourceImage(request):
    if request.method == 'GET':
        if len(image_files) == 0:
            for root, dirs, directory in os.walk('images'):
                for j in range(len(directory)):
                    hist = FMM(root+"/"+directory[j])
                    image_data.append(hist)
                    image_files.append(directory[j])
        output = '<table border=1 align=center><tr><th>Source Image File Name</th><th>Histogram Values</th></tr>'
        for i in range(len(image_files)):
            output+='<tr><td><font size="" color="white">'+image_files[i]+'</td><td><font size="" color="white">'+str(image_data[i])+"</td></tr>"
        context= {'data':output}
        return render(request, 'UploadSourceImage.html', context)




def UserLogin(request):
    if request.method == 'POST':
      username = request.POST.get('username', False)
      password = request.POST.get('password', False)
      index = 0
      con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'plagiarism',charset='utf8')
      with con:    
          cur = con.cursor()
          cur.execute("select * FROM users")
          rows = cur.fetchall()
          for row in rows: 
             if row[0] == username and password == row[1]:
                index = 1
                break		
      if index == 1:
       file = open('session.txt','w')
       file.write(username)
       file.close()   
       context= {'data':'welcome '+username}
       return render(request, 'UserScreen.html', context)
      else:
       context= {'data':'login failed'}
       return render(request, 'Login.html', context)

def Signup(request):
    if request.method == 'POST':
      username = request.POST.get('username', False)
      password = request.POST.get('password', False)
      contact = request.POST.get('contact', False)
      email = request.POST.get('email', False)
      address = request.POST.get('address', False)
      db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'plagiarism',charset='utf8')
      db_cursor = db_connection.cursor()
      student_sql_query = "INSERT INTO users(username,password,contact_no,email,address) VALUES('"+username+"','"+password+"','"+contact+"','"+email+"','"+address+"')"
      db_cursor.execute(student_sql_query)
      db_connection.commit()
      print(db_cursor.rowcount, "Record Inserted")
      if db_cursor.rowcount == 1:
       context= {'data':'Signup Process Completed'}
       return render(request, 'Register.html', context)
      else:
       context= {'data':'Error in signup process'}
       return render(request, 'Register.html', context)


