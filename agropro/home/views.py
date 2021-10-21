from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login as authlogin
from django.contrib.auth import logout as authlogout
from .models import Farmer, Wholesaler
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework import status


# Create your views here.
@api_view(['GET'])
def index(request):
    permission_classes = (IsAuthenticated,)
    try:
        utype=request.user.username
        utype=utype[utype.rfind('-')+1:]
        context={'utype':utype,'username':request.user.username[:request.user.username.rfind('-')]}
        return Response({"success": True, "data": context}, status=status.HTTP_200_OK)
    except:
        context={'utype':None,'username':None}
        return Response({"success": True, "data": context}, status=status.HTTP_200_OK)

def login(request):
    # print("Hemlo")
    # if request.method == 'POST':
    #     print("Hemlo2")
    #     password1= request.POST['password']
    #     utype = request.POST['usertype']
    #     username= request.POST['username']
    #     print("***",username,password1,utype,"***")
    #     return redirect('/')
    # else:    
    return render(request,'login.html')

@api_view(['POST'])
def signin(request):
        password1 = str(request.data.get('password'))
        utype = str(request.data.get('usertype'))
        username= str(request.data.get('username'))+"-"+utype
        print("***",username,password1,utype,"***")
        user=authenticate(username=username,password=password1)
        if user is not None:
            authlogin(request,user)
            print(user)
            return Response({"success": True}, status=status.HTTP_200_OK)
        else:
            return Response({"success": False}, status=status.HTTP_200_OK)
        # return redirect('/')

@api_view(['POST'])
def signup(request):
        name= request.data.get('fullname')
        phone= request.data.get('phone number')
        password1= request.data.get('password')
        #password2= request.POST['']
        utype = request.data.get('usertype')
        username= request.data.get('username')+"-"+utype
        fname,lname=name.split(' ')
        print("***",name,username,phone,password1,utype,"***")

       #Check the inputs
        if utype=='farmer':
            farmer=Farmer(username=username,phone=phone,name=name)
            farmer.save()
        if utype=='wholesaler':
            ws=Wholesaler(username=username,phone=phone,name=name)
            ws.save()

        # #Creating User
        user=User.objects.create_user(username,email=None,password=password1,first_name=fname,last_name=lname)
        return Response({"success": True}, status=status.HTTP_200_OK)
        # return redirect('/login')

@api_view(['POST'])
def logout(request):
        print("Chems bhai please kara hi do")
        authlogout(request)
        return Response({"success": True}, status=status.HTTP_200_OK)
        # return redirect('/login')
