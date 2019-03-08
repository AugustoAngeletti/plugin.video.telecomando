# -*- coding: utf-8 -*-
import urllib2
import json
from resources.lib.channel import Channel
from resources.lib.utils import utils
utils       = utils()

class Skytg24:
    # Raiplay android app
    UserAgent = "Dalvik/1.6.0 (Linux; U; Android 4.2.2; GT-I9105P Build/JDQ39)"
    MediapolisUserAgent = "Android 4.2.2 (smart) / RaiPlay 2.1.3 / WiFi"
    
    noThumbUrl = "http://www.rai.it/dl/components/img/imgPlaceholder.png"

    baseUrl = "https://www.raiplay.it/"

    
    def __init__(self):
        opener = urllib2.build_opener()
        # Set User-Agent
        opener.addheaders = [('User-Agent', self.UserAgent)]
        urllib2.install_opener(opener)

    def getChannels(self, _url, channel_url, fetched_channels):
        data = json.load(urllib2.urlopen(channel_url))
        channels = []
        if 'streaming_url' in data:
            if any(d.get('title', None) == 'Sky TG24' for d in fetched_channels):
                fetched_channel = next((x for x in fetched_channels if x.get('title', None) == 'Sky TG24'), None)
                title = 'Sky TG24'
                icon = self.noThumbUrl
                url = utils.get_url(_url, action='play', type='live', channel=self.__class__.__name__,  callSign = data["streaming_url"])
                epg = fetched_channel.get('epg', None)
                lcn = fetched_channel.get('lcn', None)
                channel = Channel(icon, title, url, lcn, epg)
                channels.append(channel)
        return channels

    def getLiveChannelUrl(self, _callSign):

        return _callSign
    
    def getUrl(self, pathId):
        pathId = pathId.replace(" ", "%20")
        if pathId[0:2] == "//":
            url = "http:" + pathId
        elif pathId[0] == "/":
            url = self.baseUrl[:-1] + pathId
        else:
            url = pathId
        return url
      
    def getThumbnailUrl(self, pathId):
        if pathId == "":
            url = self.noThumbUrl
        else:
            url = self.getUrl(pathId)
            url = url.replace("[RESOLUTION]", "256x-")
        return url
 