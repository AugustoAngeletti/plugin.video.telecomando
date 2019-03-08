# -*- coding: utf-8 -*-
import xbmcaddon
import xbmcplugin
import xbmcgui
import xbmc
import os
import urllib2
import json
import requests
import uuid
import ssl
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

from resources.lib.channel import Channel

from resources.lib.utils import utils
utils       = utils()

class Mediaset():

    def getMainMenu(self):
        menu = []
        
        menu.append({"label": "Canali Live", 'url': {'action':'list', 'type': 'live'}})
        
        return menu
        
    def getChannels(self, _url, channel_url, fetched_channels):
        
        response = urllib2.urlopen(channel_url)
        data = json.load(response) 
        channels = [] 
        if 'entries' in data:
            for entry in data['entries']:
                if any(d.get('title', None) == entry['title'] for d in fetched_channels):
                    #fetched_channel = [item for item in fetched_channels if item.get('title', None) == entry['title']]
                    fetched_channel = next((x for x in fetched_channels if x.get('title', None) == entry['title']), None)
                    if 'channel_logo-100x100' in entry['thumbnails']:
                        icon = entry['thumbnails']['channel_logo-100x100']['url']
                    else:
                        icon = 'DefaultVideo.png'
                
                    title = entry['title']
                    
                    url = utils.get_url(_url, action='play', type='live', channel=self.__class__.__name__,  callSign = entry['callSign'])

                    epg = fetched_channel.get('epg', None)
                    lcn = fetched_channel.get('lcn', None)

                    channel = Channel(icon, title, url, lcn, epg)
                    channels.append(channel)

        return channels
    
    def getLiveChannelUrl(self, _callSign):

        apiData = self.getApiData()
        
        apiUrl = "https://api-ott-prod-fe.mediaset.net/PROD/play/alive/nownext/v1.0?channelId=%callSign%".replace('%callSign%', _callSign)
         
        # To Fix SSL: CERTIFICATE_VERIFY_FAILED on Kodi 17.6
        ssl._create_default_https_context = ssl._create_unverified_context
         
        headers = {
            't-apigw': apiData['t-apigw'],
            't-cts': apiData['t-cts'],
            'Accept': 'application/json'
        }
        response = requests.get(apiUrl, False, headers=headers)
        
        data = json.loads(response.content)
        
        if 'isOk' in data and data['isOk']:
            for entry in data['response']['tuningInstruction']['urn:theplatform:tv:location:any']:
                if entry['format'] == 'application/x-mpegURL':
                    return entry['publicUrls'][0]
        
        dialog = xbmcgui.Dialog()
        ok = dialog.ok('Errore!', 'Impossibile risolvere correttamente l\'URL del live streaming')
     
    def getApiData(self):     
        try:
            with open(os.path.join(PROFILE, 'apiLogin.txt'), "r") as read_file:
                apiData = json.load(read_file)
        except:
            apiData = self.apiLogin()
            
        if 'expire' not in apiData or not apiData or apiData['expire'] < datetime.now().strftime('%Y-%m-%d %H:%M:%S') or 'traceCid' not in apiData or 'cwId' not in apiData:
            apiData = self.apiLogin()
            
        return apiData

    def apiLogin(self):
        url = "https://api-ott-prod-fe.mediaset.net/PROD/play/idm/anonymous/login/v1.0"
        data = {
            'cid': str(uuid.uuid4()),
            "platform":"pc",
            "appName":"web/mediasetplay-web/2e96f80"
        }
        
        headers = {'Content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(data), headers=headers)
        
        data = json.loads(response.content)
        
        if 'isOk' in data and data['isOk']:
            apiData = {
                    "t-apigw": response.headers.get('t-apigw'),
                    "t-cts": response.headers.get('t-cts'),
                    "expire": datetime.now() + timedelta(hours=6),
                    "traceCid": data['response']['traceCid'],
                    "cwId": data['response']['cwId']
            }
            apiData['expire'] = apiData['expire'].strftime('%Y-%m-%d %H:%M:%S')
            
            with open(os.path.join(PROFILE, 'apiLogin.txt'), "w") as write_file:
                json.dump(apiData, write_file)
                
            return apiData
        else:
            dialog = xbmcgui.Dialog()
            ok = dialog.ok('Errore!', 'Impossibile eseguire il login sul sito Mediaset Play, contattare gli sviluppatori se il problema persiste')
            
