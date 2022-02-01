import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.db import IntegrityError
from django.http.response import StreamingHttpResponse
from django.shortcuts import render, redirect
from smart_lock.camera import VideoCamera, IPWebCam
from smart_lock.decorators import unauthenticated_user, allowed_users, admin_only
from smart_lock.models import logs
from datetime import date
from django.http import JsonResponse
from smart_lock.recognizer import FaceRecognizer
import time
from django.http import HttpResponse
from smart_lock.trainer import FaceTrainer

@login_required(login_url='login')
def restricted(request):
    return render(request, "smart_lock/restricted.html")


@login_required(login_url='login')
def dashboard(request):
    request.session['lock'] = "LOCKED"
    log = logs.objects.filter(VISIT_TIME__date=date.today()).order_by('-VISIT_TIME')[:5]
    return render(request, "smart_lock/dashboard.html", {'log': log})


# CAMERA SETUP
def gen(request,camera):
    timeout = time.time() + 10   # 10 seconds from now
    while True:
        frame = camera.get_frame(request.session['regname'])
        if time.time() > timeout:
            break
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    train = FaceTrainer()
    train.trainer()
    # train.del_data()

def gen1(camera):
    while True:
        frame = camera.recognizer()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def recognizer_feed(request):
    return StreamingHttpResponse(gen1(FaceRecognizer()),
                                 content_type='multipart/x-mixed-replace; boundary=frame')


# REGISTRATION
@login_required(login_url='login')
@admin_only
def registerPage(request):
    if request.method == 'POST':
        user_reg = User.objects.create_user(first_name=request.POST.get('first_name'),
                        password=request.POST.get('password1'),
                        username=request.POST.get('username'))
        try:
            user_reg.save()
            groups = Group.objects.get(name=request.POST.get('access_level'))
            groups.user_set.add(user_reg)
            request.session['regname'] = request.POST.get('first_name')
            context = {'folder_name': request.POST.get('first_name')}
            return render(request, "smart_lock/dataset.html", context)
        except IntegrityError:
            messages.info(request, "Username already present!!")
    return render(request, 'smart_lock/form.html')


def video_feed(request):
    return StreamingHttpResponse(gen(request,VideoCamera()),
                                 content_type='multipart/x-mixed-replace; boundary=frame')


# LOGIN
@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.info(request, 'Username or Password is incorrect')
    return render(request, 'smart_lock/login.html')


# LOGOUT
@login_required(login_url='login')
def logoutUser(request):
    logout(request)
    return redirect('login')


# TABLE DATA
@login_required(login_url='login')
@admin_only
def table_data(request):
    records = logs.objects.all().order_by('-VISIT_TIME')
    count = logs.objects.count()
    lock_status = request.session['lock']
    return render(request, 'smart_lock/logs.html', {'records': records, 'count': count, 'lock_status':lock_status})


# SEND OTP
@login_required(login_url='login')
def send_otp(request):
    url = "http://2factor.in/API/V1/0b8f5ce5-400e-11eb-83d4-0200cd936042/SMS/9326747347/AUTOGEN"
    payload = ""
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.request("GET", url, data=payload, headers=headers)
    data = response.json()
    request.session['otp_session_data'] = data['Details']
    return JsonResponse({'data':data})


# VERIFY OTP
@login_required(login_url='login')
@allowed_users(allowed_roles=['ADMIN', 'VIEW_UNLOCK'])
def verify_otp(request):
    if request.method == 'POST':
        user_otp = request.POST.get('votp')
        session_id= request.session['otp_session_data']
        url = "http://2factor.in/API/V1/0b8f5ce5-400e-11eb-83d4-0200cd936042/SMS/VERIFY/"+session_id+"/"+str(user_otp)
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        response = requests.request("GET", url, data="", headers=headers)
        data = response.json()
        if data['Status'] == "Success":
            print("Success")
            records = logs.objects.all().order_by('-VISIT_TIME')
            count = logs.objects.count()
            request.session['lock'] = "UNLOCKED"
            lock_status = request.session['lock']
            return render(request, 'smart_lock/logs.html', {'records': records, 'count': count, 'lock_status':lock_status})
        else:
            messages.info(request, 'Wrong OTP')
    return render(request, "smart_lock/unlock.html")