from django.shortcuts import render, redirect
from django.apps import apps
from django.http import JsonResponse
import pandas as pd
import os
import json
from .extras.modelClass import CropPredict,CNN2
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from farmer.serializers import CropSerializer, FarmerSerializer


Farmer = apps.get_model('home', 'Farmer')
Wholesaler = apps.get_model('home', 'Wholesaler')
Crop = apps.get_model('home', 'Crop')
Notification = apps.get_model('home', 'Notification')

CNN_obj_3D = CNN2()
# Crop_obj = CropPredict()

soilDict = {
    'Black':['Cotton(lint)','Groundnut','Wheat','Jowar','Tobacco'],
    'Red':['Rice','Niger seed','Groundnut','other oilseeds','Coriander'],
    'Alluvial':['Rice','Wheat','Sugarcane','Cotton(lint)','Maize'],
    'Clay':['Onion','Peas & beans (Pulses)','Soyabean','Sugarcane','Cabbage','Barley']
}

 
base_dir = os.path.dirname(__file__)
print(base_dir)
df = pd.read_csv(base_dir+'/uploads/datafile.csv')
df1 = pd.read_csv(base_dir+'/uploads/Data Yield_hect - Sheet1.csv')
print(df[:3])
print(df1[:3])

def findPrice(data):
    print(data)
    print('Checking information:',df.loc[(df['state'] == data['state']) & (df['commodity'] == data['crop'])])
    newPd = df.loc[(df['state'] == data['state']) & (df['commodity'] == data['crop'])]
    print("Checking for new PD:",newPd)
    if(len(newPd)):
        print("Checking for main Info:",newPd['modal_price'].iloc[0])
        return newPd['modal_price'].iloc[0]*data['production']
    else:
        return 0

def findYield(data):
    print(data)
    print('Checking information:',df1.loc[(df1['State'] == data['state']) & (df1['Crop'] == data['crop'])])
    newPd = df1.loc[(df1['State'] == data['state']) & (df1['Crop'] == data['crop'])]
    print("Checking for new PD:",newPd)
    if len(newPd):
        return newPd['Yield (Quintal/ Hectare)'].iloc[0]*data['area']
    else:
        return 0


newData = {
    'area':1,
    'crop':'Soyabean',
    'state':'Maharashtra',
    'season':'Kharif'    
}

print("Checking for Peas and Beans:",findYield(newData))


# Create your views here.
@api_view(['POST'])
def prediction(request):
    permission_classes = (IsAuthenticated,)
    try:
        username=request.user.username
        username=username[:username.rfind('-')]
        # context={'username':request.user.username[:request.user.username.rfind('-')]}
        print(username,"Ho raha hai")
        instance = Farmer.objects.filter(username = request.user.username).values()[0]

        # if request.method == 'POST' :
            # print('the user name is: ',request.POST.get('season'))
            # print('The file upoaded is: ',request.FILES['file'])
        print('yes value found')
            # body_unicode = request.body.decode('utf-8')
            # body = json.loads(body_unicode)
        # print(request.POST['season'])
        # print(request.FILES['file'])
            
        imageFile = request.data['file']
        # imageFile = request.FILES['file']
        # print("The image is:",imageFile)
        # answer = CNN_obj.prediction(imageFile)
        answer = CNN_obj_3D.prediction(imageFile)
        # answer = {'output':'Alluvial','percent':90}
        print("Got the answer:",answer)
        finalArray = []

        for crop in soilDict[answer['output']]:
            data = {
                    'area':instance['area'],
                    'crop':crop,
                    'state':instance['state'],
                    'season':request.data.get('season')    
            }
            # production = Crop_obj.prediction(data) // Approach 1
            production = findYield(data) # Approach 2
            data['production'] = production
            priceAssumption = findPrice(data)
            print("Checking for prices:",priceAssumption)
            if(priceAssumption != 0):
                    # data['price'] = priceAssumption[0]*10 // Approach 1
                    data['price'] = priceAssumption  # Approach 2
            else:
                    data['price'] = 0
            print("Checking for production:",data['production'])
            # data['production'] = data['production'][0]*10 // Approach 1
            data['production'] = data['production']  # Approach 2
            finalArray.append(data)
            
        print(finalArray)
        return Response({"success": True, 'data':finalArray}, status=status.HTTP_200_OK)

        # return JsonResponse({'result':finalArray})

        # elif(instance['state'] is None or instance['area'] is None or instance['email'] is None or instance['address'] is None):
        #     print('Checking for instance in prediction:',instance)
        #     return redirect('/farmer/profile')
        # else:
        #     return render(request,'predic.html',context)
        # print("The instance is:",instance)
    except:
        # return redirect('/login')
        return Response({"success": False}, status=status.HTTP_200_OK)


@api_view(['POST'])
def acceptNotif(request):
    permission_classes = (IsAuthenticated,)
    try:
        utype=request.user.username
        utype=utype[utype.rfind('-')+1:]
        not_id=request.data.get('id')
        notif_obj=list(Notification.objects.filter(id=not_id))[0]
        notif_obj.accepted=True
        notif_obj.save()
        return Response({"success": True}, status=status.HTTP_200_OK)
    except:
        return Response({"success": False}, status=status.HTTP_200_OK)

@api_view(['GET'])
def notification(request):
    permission_classes = (IsAuthenticated,)
    try:
        utype=request.user.username
        utype=utype[utype.rfind('-')+1:]
        f_obj=list(Farmer.objects.filter(username=request.user.username))[0]
        notif_final=[]
        notif_temp=list(Notification.objects.all())
        for i in notif_temp:
            if i.crop.farmer.id == f_obj.id:
                notif_final.append([])
                notif_final[-1].append(i.crop.name)
                notif_final[-1].append(i.wholesaler.name)
                notif_final[-1].append(i.crop.price)
                notif_final[-1].append(i.accepted)
                notif_final[-1].append("91"+i.wholesaler.phone)
                notif_final[-1].append(i.id)
        

        # Order By
        ob=request.data.get('orderby')
        print("*******************************")
        print(ob)
        if ob=="Pending":
            print("Pending")
            notif_final=sorted(notif_final, key=lambda x: x[3])
        if ob=="Accepted":
            print("Accepted")
            notif_final=sorted(notif_final, key=lambda x: x[3], reverse=True)
        print(notif_final)   
        context={'utype':utype,'username':request.user.username[:request.user.username.rfind('-')],"notif":notif_final,"n":3}
        return Response({"success": True, "data": context}, status=status.HTTP_200_OK)
        # return render(request,'notif.html',context)
    except:
        return Response({"success": False}, status=status.HTTP_200_OK)
        # return redirect('/login')
    
@api_view(['GET'])
def profile(request):
    permission_classes = (IsAuthenticated,)
    try:
        username=request.user.username
        username=username[:username.rfind('-')]
        # context={'username':request.user.username[:request.user.username.rfind('-')]}
        # print("$$$$$$$$$$$$$$$",context,"Ho raha hai")
        instance = Farmer.objects.get(username = request.user.username)
        # .values()[0]
        print("Checking for instance: ",instance)
        crops = Crop.objects.filter(farmer = instance.id,available = True)
        # .values()
        
        print("The instance is:",instance)
        print("The crop instance  is:",crops)

        context = {
            'instance':FarmerSerializer(instance).data,
            'crops':(CropSerializer(crops,many=True)).data,
            'username':username
        }
        return Response({"success": True, "data": context}, status=status.HTTP_200_OK)
        # return render(request,'profile.html',context)
    except:
        return Response({"success": False}, status=status.HTTP_200_OK)
        # return redirect('/')

@api_view(['PATCH'])
def editProfile(request):
    permission_classes = (IsAuthenticated,)
    try:
        username=request.user.username
        username=username[:username.rfind('-')]
        # context={'utype':utype,'username':request.user.username[:request.user.username.rfind('-')+1]}
        print(username,"Ho raha hai")
        instance = Farmer.objects.filter(username = request.user.username).update(name = request.data.get('name'),state = request.data.get('state'),area = request.data.get('area'),email = request.data.get('email'),address = request.data.get('address'),phone = request.data.get('phone'))
        
        print("The instance is:",instance)
        # print("The new changes are:",request.POST['state'],request.POST['name'],request.POST['phone'],request.POST['area'],request.POST['email'],request.POST['address'])

        # instance['name'] = request.POST['name']
        # instance['phone'] = request.POST['phone']
        # instance['area'] = request.POST['area']
        # instance['state'] = request.POST['state']
        # instance['address'] = request.POST['address']
        # instance['email'] = request.POST['email']
        # instance.save()
        # context = instance

        return Response({"success": True}, status=status.HTTP_200_OK)
        # return redirect('/farmer/profile')
    except:
        return Response({"success": False}, status=status.HTTP_200_OK)

@api_view(['POST'])
def setCrop(request):
    permission_classes = (IsAuthenticated,)
    try:
        # print(request.POST['name'],request.POST['quantity'],request.POST['price'],request.POST['tsp'])
        
        username=request.user.username
        username=username[:username.rfind('-')]
        # context={'utype':utype,'username':request.user.username[:request.user.username.rfind('-')+1]}
        print(username,"Ho raha hai")
        instance = Farmer.objects.filter(username = request.user.username).values()[0]
        
        print("The instance is:",instance)
        
        newCrop = Crop.objects.create(farmer=Farmer(id=instance['id']), name = request.data.get('name'),quantity = request.data.get('quantity'),price = request.data.get('price'),available = True)
        print('The new crop is:',newCrop)

        return Response({"success": True}, status=status.HTTP_200_OK)
        # return redirect('/farmer/profile?newCrop=True')
    except:
        return Response({"success": False}, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def removeCrop(request,crop_id):
    permission_classes = (IsAuthenticated,)
    try:
        print("Yes reached here:",crop_id)
        instance = Crop.objects.filter(id = crop_id).delete()
        print("Checking for deletion:",instance)
        return Response({"success": True}, status=status.HTTP_200_OK)
        # return redirect('/farmer/profile?itemDel=True')
    except:
        return Response({"success": False}, status=status.HTTP_200_OK)
        # return redirect('/farmer/profile')
