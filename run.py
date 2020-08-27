from flask import Flask, flash, redirect, render_template, url_for, request
from flask_cors import CORS
import ibm_watson
from gtts import gTTS
import os
import re
import webbrowser
import smtplib
import requests,json
import urllib
import boto3
import os
import subprocess
import cv2
import googlemaps
from datetime import datetime
import analyze as az
from opencage.geocoder import OpenCageGeocode
import nexmo
from pprint import pprint
from ibm_watson import AssistantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator






#import assistant


app = Flask(__name__)

CORS(app)# to let the webapp know that this backend is ready to accept stuff.

@app.route('/')
def home():
    return render_template ('index.html')
@app.route('/useme.html')
def useme():
    return render_template ('useme.html')
@app.route('/map.html')
def map():
    return render_template ('map.html', value=value,loc=loc)
@app.route('/print/name', methods=['POST', 'GET'])
def get_names():

    if request.method == 'POST':
        resp_json = request.get_json()
        command = resp_json['text']
        if 'villa' in command or 'billa' in command:
            command= 'okay iWheel-inator'
        else:
            command= command
        authenticator = IAMAuthenticator('u1N9ThXmpZUk_-1_F1AaAw-11BbBXFtCbonmmerHbnFI')
    assistant = AssistantV1(
        version='2019-02-28',
        authenticator = authenticator
    )

    assistant.set_service_url('https://gateway-wdc.watsonplatform.net/assistant/api')

    response = assistant.message(
        workspace_id='97afbe1c-dd6b-4d91-8022-8d483eae2174',
        input={
            'text': command
        }
    ).get_result()


    a=response
    b=a['intents']
    if b==[]:
        intent= 'nothing'
    else:
        intent = b[0]['intent']
    print('the intent is:' , intent)
    def currentad():
        send_url = "http://api.ipstack.com/check?access_key=9a86bc5e18df530bd1ded7ff6620187d"
        geo_req = requests.get(send_url)
        geo_json = json.loads(geo_req.text)
        latitude = geo_json['latitude']
        longitude = geo_json['longitude']
        return [latitude,longitude]
        
    if intent=='weather':
        latt,long = currentad()
        endpoint = 'http://api.openweathermap.org/data/2.5/forecast?'
        api_key = 'e33c84cc9eb1157c533611a494f638a3'

        nav_request = 'lat={}&lon={}&APPID={}'.format(latt, long, api_key)
        reequest = endpoint + nav_request
        # Sends the request and reads the response.
        response = urllib.request.urlopen(reequest).read().decode('utf-8')
            # Loads response as JSON
        weather = json.loads(response)
        current_temp = weather['list'][0]['main']['temp']
        temp_c = current_temp - 273.15
        temp_c_str = str(int(temp_c)) + ' degree Celsius '
        descript_place = weather['list'][0]['weather'][0]['main']
        #print(descript_place + ' ' + temp_c_str)
        if descript_place == 'Clouds':
            descript_place = 'overcast'
        print('It is a little '+descript_place + ' and temperature outside is, ' + temp_c_str)
        
       #response = assistant.assistant(resp_json["test"])
        global call_trigger
        call_trigger =0
        return json.dumps({"response": 'It is a little '+descript_place + ' and temperature outside is, ' + temp_c_str}), 200
    elif intent == 'call':
        
        call_trigger = 1
        return json.dumps({"response": "Can I know the message you wish to convey?"}), 200

    elif intent=='maps':
        #webbrowser.open('http:127.0.0.1:5000/map.html')
        #print('Done!')
        gmaps = googlemaps.Client(key='AIzaSyAMP6SIK4ruB5Tsl5qR6h54XDcl4FDl3HQ')
        SUBSCRIPTION_KEY_ENV_NAME = "bc20ced3c3014badbf34d1799e28f2a2"
        now = datetime.now()
        x = az.entity_extraction(SUBSCRIPTION_KEY_ENV_NAME,command)
        if x[1]=='Location' or x[1]=='Organization':
            c = x[0]
        else:
            return json.dumps({"response": 'Give me a specific destination'}), 200



        send_url = "http://api.ipstack.com/check?access_key=9a86bc5e18df530bd1ded7ff6620187d"
        geo_req = requests.get(send_url)
        geo_json = json.loads(geo_req.text)
        lat = geo_json['latitude']
        lon = geo_json['longitude']
        results = geocoder.reverse_geocode(lat, lon)
        print(lat+0.4,lon+0.4)
        #pprint(results[0]['formatted'])
        our_loc = str(results[0]['formatted'])
        print(our_loc)
        
        '''directions_result = gmaps.directions(our_loc,
                                     c,
                                     mode="walking",
                                     departure_time=now)'''
        directions_result = gmaps.directions('Hodson Hall, Baltimore, MD',
                                     c,
                                     mode="walking",
                                     departure_time=now)
        time = directions_result[0]['legs'][0]['duration']['text']
        dis = directions_result[0]['legs'][0]['distance']['text']
        start_loc_lat = dis = directions_result[0]['legs'][0]['start_location']['lat']
        start_loc_lng = dis = directions_result[0]['legs'][0]['start_location']['lng']
        end_loc_lat = dis = directions_result[0]['legs'][0]['end_location']['lat']
        end_loc_lng = dis = directions_result[0]['legs'][0]['end_location']['lng']
        

        instru = []
        for i in directions_result[0]['legs'][0]['steps']:
            instru.append(i['html_instructions']+" "+i['distance']['text'] + ' ' + i['duration']['text'] + " Moving from lat : " + str(i['start_location']['lat']) +" , lon : "+str(i['start_location']['lng']) + " to lat : " + str(i['end_location']['lat']) +" , lon : "+str(i['end_location']['lng']))
        webbrowser.open('http:127.0.0.1:5000/map.html')
        #print("distance isssshabdgyjasvkd", dis)
        global value
        value = 'ETA '+ str(time)+' :)'
        global loc
        loc= [start_loc_lat,start_loc_lng,end_loc_lat,end_loc_lng] 
        mytext = 'Opened in a new tab.'
        language = 'en'
        myobj = gTTS(text=mytext, lang=language, slow=False)  
        myobj.save("welcome.mp3") 
        subprocess.call(['afplay','welcome.mp3'])
        call_trigger =0
        return render_template('map.html'), json.dumps({"response": 'It openend on a new Tab'}), 200
        
    elif intent=='person':
        thisdict={
        1:"Akshat.jpeg",
        2:"anand.jpeg",
        3:"David_Troy.jpeg",
        4:"Gorkem_Sevinc.jpeg",
        5:"Joshua_Reiter.jpeg",
        6:"Kevin_Carter.jpeg",
        7:"Edward_Shiang.jpeg",
        8:"Andrew_Wiles.jpeg",
        9:"goldy.jpeg",
        10:"sandeep.jpeg"

            }
        n=5
        f=0

        ch='y'
        while(ch=='y'):

            camera = cv2.VideoCapture(0)
            return_value, image = camera.read()
            cv2.imwrite('test.jpeg', image)
            del(camera)


            sourceFile='test.jpeg'#from camera
            for i in range(1,n+1):
# targetFile='anand.jpeg'
                targetFile= thisdict[i]
                client=boto3.client('rekognition')

                imageSource=open(sourceFile,'rb')
                imageTarget=open(targetFile,'rb')

                response=client.compare_faces(SimilarityThreshold=70,SourceImage={'Bytes': imageSource.read()},TargetImage={'Bytes': imageTarget.read()})
                f=2
                for faceMatch in response['FaceMatches']:
                    f=1
                    nameee=''
                    for i in targetFile:
                        if i != '.':
                            nameee+=i
                        else:
                            break
                    
                    os.remove("test.jpeg")
                    return json.dumps({"response": 'This is' + ' ' + nameee + ', '+ ' who\'s come to visit you! '
                            }), 200
                imageSource.close()
                imageTarget.close()               
            if(f!=1):
                call_trigger =0
                return json.dumps({"response": 'This person doesn\'t exist in our database. Would you like to add him? '
                            }), 200

    elif 'add' in command:
        camera = cv2.VideoCapture(0)
        return_value, image = camera.read()
        cv2.imwrite('new.jpeg', image)
        del(camera)
        namee= command[4::1]
        namee= namee+ ".jpeg"
        os.rename("new.jpeg", namee)
        d1={n:namee}
        thisdict.update(d1)

    elif intent=='text':
        new=[]
        camera = cv2.VideoCapture(0)
        return_value, image = camera.read()
        cv2.imwrite('test1.jpeg', image)
        del(camera)
    
        s3 = boto3.resource('s3')
        images=[('test1.jpeg','test'),]

        for image in images:
            file = open(image[0],'rb')
            object = s3.Object('aags-wheeler1',image[0])
            ret = object.put(Body=file,
                                Metadata={'Name':image[1]}
                                )



        bucket='aags-wheeler1'
        photo='test1.jpeg'
        client=boto3.client('rekognition')
        response=client.detect_text(Image={'S3Object':{'Bucket':bucket,'Name':photo}})
        textDetections=response['TextDetections']

        stuff=' '
        for text in textDetections:
            if(' ' in text['DetectedText']):
                stuff+= text['DetectedText'] +'\n'
            
        print(stuff)
        call_trigger =0
        return json.dumps({"response": stuff}), 200
        #talkToMe(str(text['DetectedText']))



        s3.Object('aags-wheeler1', 'test1.jpeg').delete()

    elif intent=='news':
        def NewsFromBBC():
            global new
            new=[] 
            main_url = "https://newsapi.org/v1/articles?source=bbc-news&sortBy=top&apiKey=e4313a22f54042c9aba095ce5354be51"
            open_bbc_page = requests.get(main_url).json() 
            article = open_bbc_page["articles"] 
            results = []
            for ar in article:
                results.append(ar["title"]) 
                
            for i in range(0,3):
                stuff= str(str((i+1)) +'. '+ results[i])
                new.append(stuff)
            return new
                #return json.dumps({"response": str(stuff)})
                #talkToMe(stuff)
        new = NewsFromBBC()
        news=' '
        for i in new:
            news+=i+',\n'+'\n'
            call_trigger =0
        return json.dumps({"response": news})
    else:
        if call_trigger==1:
            #call_text = command
            client = nexmo.Client(
            application_id='bfc1264a-8021-4576-bd74-bf9dd9c04222',
            private_key='./private.key',
            )
        
            ncco = [
                {
                    'action': 'talk',
                    'voiceName': 'Brian',
                    'text': '! ! ! ! !hey!'+command
                }
                ]
            response = client.create_call({
            'to': [{
                'type': 'phone',
                'number': '12132103009'
            }],
            'from': {
                'type': 'phone',
                'number': '12132103009'
            },
            'ncco': ncco
            })

            pprint(response)
            call_trigger=0
            mytext = 'call has been initiated!.'
            language = 'en'
            myobj = gTTS(text=mytext, lang=language, slow=False)  
            myobj.save("call.mp3") 
            subprocess.call(['afplay','call.mp3'])
            return json.dumps({"Call excuted succesfully!"}), 200
        
        else:    #make call here
            return json.dumps({"response":'wanna know what i can do? check your top-left.'}), 200
if __name__=='__main__':
            #from pprint import pprint

    key = '9ceed27ef0e646188df1656457bdffa6'
    geocoder = OpenCageGeocode(key)
    
    webbrowser.open('http://127.0.0.1:5000/')
    app.run(debug=False)
