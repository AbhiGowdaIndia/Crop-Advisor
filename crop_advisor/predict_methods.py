import pandas as pd
import numpy as np
from flask import Markup
import requests,json
import pickle
from requests.exceptions import ConnectionError
import torch
import io
from torchvision import transforms
from PIL import Image
from crop_advisor.model import ResNet9
from crop_advisor.details import fertilizer_dic,disease_dic,disease_classes

weather_api_key = "9d7cde1f6d07ec55650544be1631307e"

disease_model_path = 'crop_advisor/models/plant-disease-model.pth'
disease_model = ResNet9(3, len(disease_classes))
disease_model.load_state_dict(torch.load(
    disease_model_path, map_location=torch.device('cpu')))
disease_model.eval()

#weather_api_key='285965b62c3463979a712f6336ef9197'

def fert_recommend(N,P,K,crop_name):
    df = pd.read_csv('crop_advisor/data/fertilizer.csv')
    nr = df[df['Crop'] == crop_name]['N'].iloc[0]
    pr = df[df['Crop'] == crop_name]['P'].iloc[0]
    kr = df[df['Crop'] == crop_name]['K'].iloc[0]
    
    n = nr - N
    p = pr - P
    k = kr - K
    temp = {abs(n): "N", abs(p): "P", abs(k): "K"}
    max_value = temp[max(temp.keys())]
    if max_value == "N":
        if n < 0:
            key = 'NHigh'
        else:
            key = "Nlow"
    elif max_value == "P":
        if p < 0:
            key = 'PHigh'
        else:
            key = "Plow"
    else:
        if k < 0:
            key = 'KHigh'
        else:
            key = "Klow"
    
    response = Markup(str(fertilizer_dic[key]))
    return response  

def weather_fetch(city_name):
    """
    Fetch and returns the temperature and humidity of a city
    :params: city_name
    :return: temperature, humidity
    """
    x={}
    api_key = weather_api_key
    base_url = "http://api.openweathermap.org/data/2.5/weather?"

    complete_url = base_url + "appid=" + api_key + "&q=" + city_name
    
    try:
        response = requests.get(complete_url)
    except ConnectionError:
        x["cod"]="404"
    else:
        x=response.json()

    if x["cod"] != "404":
        y = x["main"]
        temperature = round((y["temp"] - 273.15), 2)
        humidity = y["humidity"]
        return temperature, humidity
    else:
        return None  

def  crop_recommendation_model(data):
    path = 'crop_advisor/models/RandomForest.pkl'
    model = pickle.load(open(path, 'rb'))
    prediction = model.predict(data)
    final_prediction = prediction[0]
    return final_prediction


def weather_predict(city):
    x={}
    weather_info={}
    api_key = weather_api_key
    base_url = "http://api.openweathermap.org/data/2.5/weather?"

    complete_url = base_url + "appid=" + api_key + "&q=" + city
    
    try:
        response = requests.get(complete_url)
    except ConnectionError:
        x["cod"]="404"
    else:
        x=response.json()
        
    if x["cod"] != "404":
        weather_info['city']=x['name']
        weather_info['long']=x['coord']['lon']
        weather_info['lat']=x['coord']['lat']
        weather_info['w_main']=x['weather'][0]['main']
        weather_info['description']=x['weather'][0]['description']
        weather_info['temp']=round((x['main']['temp']-273.15),2)
        weather_info['feels_like']=round((x['main']['feels_like']-273.15),2)
        weather_info['temp_min']=round((x['main']['temp_min']-273.15),2)
        weather_info['temp_max']=round((x['main']['temp_max']-273.15),2)
        weather_info['humidity']=x['main']['humidity']
        weather_info['wind_speed']=x['wind']['speed']
        weather_info['wind_dir']=x['wind']['deg']
        weather_info['clouds']=x['clouds']['all']
        return weather_info
        
    else:
        return None
        

def predict_image(img, model=disease_model):
    """
    Transforms image to tensor and predicts disease label
    :params: image
    :return: prediction (string)
    """
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.ToTensor(),
    ])
    image = Image.open(io.BytesIO(img))
    img_t = transform(image)
    img_u = torch.unsqueeze(img_t, 0)

    # Get predictions from model
    yb = model(img_u)
    # Pick index with highest probability
    _, preds = torch.max(yb, dim=1)
    prediction = disease_classes[preds[0].item()]
    # Retrieve the class label
    prediction = Markup(str(disease_dic[prediction]))
    return prediction


