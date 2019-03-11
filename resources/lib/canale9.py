# -*- coding: utf-8 -*-
import urllib2
import json
from resources.lib.channel import Channel
from resources.lib.utils import utils
utils       = utils()

class Canale9:
    UserAgent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
    
    noThumbUrl = "http://www.rai.it/dl/components/img/imgPlaceholder.png"

    baseUrl = "https://www.raiplay.it/"

    
    def __init__(self):
        opener = urllib2.build_opener()
        # Set User-Agent
        opener.addheaders = [('User-Agent', self.UserAgent)]
        urllib2.install_opener(opener)

    def getChannels(self, _url, channel_url, fetched_channels):
        
        channels = []
        
        fetched_channel = next((x for x in fetched_channels if x.get('title', None) == 'Nove'), None)
        title = 'Nove'
        icon = self.noThumbUrl
        url = utils.get_url(_url, action='play', type='live', channel=self.__class__.__name__,  callSign = channel_url)
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
 