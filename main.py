# -*- coding: utf-8 -*-

import sys

import xbmcaddon
import xbmcplugin
import xbmcgui
import xbmc
import json
import urllib2
import os.path
#import StorageServer

from resources.lib.mediaset import Mediaset
from resources.lib.rai import Rai
from resources.lib.canale8 import Canale8
from resources.lib.canale9 import Canale9
from resources.lib.cielo import Cielo
from resources.lib.skytg24 import Skytg24
from resources.lib.dmax import Dmax
from resources.lib.utils import utils
from urllib import urlencode
from urlparse import parse_qsl
import xml.etree.ElementTree as ET

addon       = xbmcaddon.Addon()
addonname   = addon.getAddonInfo('name')
utils       = utils()
#mediaset    = Mediaset()
#rai    = Rai()

# Cache channels for 1 hour
#cache = StorageServer.StorageServer("plugin.video.telecomando", 1) # (Your plugin name, Cache time in hours)
#tv_stations = cache.cacheFunction(raiplay.getChannels)

PLUGIN_NAME = "telecomando"
__settings__ = xbmcaddon.Addon(id="plugin.video."+PLUGIN_NAME)

def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.
    :param kwargs: "argument=value" pairs
    :type kwargs: dict
    :return: plugin call URL
    :rtype: str
    """
    return '{0}?{1}'.format(_url, urlencode(kwargs))
 
def router(paramstring):
    xbmc.log(paramstring,2)
    """
    Router function that calls other functions
    depending on the provided paramstring
    :param paramstring: URL encoded plugin paramstring
    :type paramstring: str
    """
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring))
    # Check the parameters passed to the plugin
    if params:
        
        if params['action'] == 'play':     
            version = xbmc.getInfoLabel('System.BuildVersion').split('.')[0]
        
            if params['type'] == 'live':
                class_name = eval(params['channel'])
                
                params['url'] = class_name().getLiveChannelUrl(params['callSign'])
        
            if (xbmc.getCondVisibility('system.platform.linux') and xbmc.getCondVisibility('system.platform.android')) and params['type'] != 'live':
                # solves final url to grab mpd file
                req = urllib2.build_opener()
                req.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:64.0) Gecko/20100101 Firefox/64.0')]
                response = req.open(params['url'])
                params['url'] = response.geturl()
                
                liz = xbmcgui.ListItem(path = params['url'])
                # To use inputstream.adaptive
                liz.setProperty('inputstreamaddon', 'inputstream.adaptive')
                liz.setProperty('inputstream.adaptive.manifest_type', 'mpd')
                liz.setMimeType('application/dash+xml')
                liz.setContentLookup(False)
            else:
                liz = xbmcgui.ListItem(path = params['url'])
                
            xbmcplugin.setResolvedUrl(_handle, True, liz)

        else:
            # If the provided paramstring does not contain a supported action
            # we raise an exception. This helps to catch coding errors,
            # e.g. typos in action names.
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        if 1:

            channels = fetch_channels_from_xml(addon.getSetting('xml_filename'))

            listing = []
            for channel in channels:
                channel_name = channel.get('name')
                channel_url = channel.get('url')
                fetched_channels = fetch_channels_from_xml(addon.getSetting('xml_filename'), channel_name)
                print(fetched_channels)
                print(channel_name, channel_url)
                channel_class = eval(channel_name)
                channels = channel_class().getChannels(_url, channel_url, fetched_channels)
                listing.extend(channels)
                
            newlist = sorted(listing, key=lambda x: int(x.lcn), reverse=False)
            
            for channel in newlist: 
                print(channel.title)
                list_item = xbmcgui.ListItem(channel.title)
                list_item.setInfo('video', {
                                'title': channel.title,
                    })
                list_item.setArt({'thumb': channel.icon, 'icon': channel.icon, 'fanart': channel.icon})
                list_item.setProperty('IsPlayable', 'true')
                is_folder = False
            
            
                xbmcplugin.addDirectoryItem(_handle, channel.url, list_item, is_folder)
            
            # Add a sort method for the virtual folder items (alphabetically, ignore articles)
            xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_UNSORTED)
            # Finish creating a virtual folder.
            xbmcplugin.endOfDirectory(_handle)
        
#parsing xml channels list
def get_xml_file_path():
    """ Return (path, filename) """
    # .kodi/userdata/addon_data/[addon name]
    path = xbmc.translatePath(
        addon.getAddonInfo('profile')).decode("utf-8")
    name = addon.getSetting('xml_filename')
    print(path)
    print(name)
    return (path, name)


def copy_default_xml_file(target_file_name):
    try:
        
        path = addon.getAddonInfo('path').decode('utf-8')
        path = xbmc.translatePath( __settings__.getAddonInfo('Path') )
        print(path)
        print(os.path.join(path, "channels.xml"))
        fin = open(os.path.join(path, "channels.xml"), "r")
        fout = file(target_file_name, "w")
        fout.write(fin.read(-1))  # .encode('utf-8'))
        fout.close()
        fin.close()
    except IOError as e:
        raise e


def make_addon_data_dir():
    import os
    (xml_path, xml_name) = get_xml_file_path()
    try:
        if not os.path.isdir(xml_path):
            os.mkdir(xml_path)
    except OSError:
        addon_name = addon.getAddonInfo("name")
        err = 'Can\'t create folder for addon data.'
        xbmcgui.Dialog().notification(addon_name, err,
                                      xbmcgui.NOTIFICATION_ERROR, 5000)


# For xml update over gui
def update_xml_file():

    import requests

    class FetchError(Exception):
        pass

    # addon = xbmcaddon.Addon()
    addon_name = addon.getAddonInfo("name")
    source_url = addon.getSetting('xml_update_url')
    (xml_path, xml_name) = get_xml_file_path()

    make_addon_data_dir()

    try:
        r = requests.get(source_url)
        if r.status_code != 200:
            raise requests.RequestException(response=r)

        o = file(xml_path+xml_name, "w")
        o.write(r.text.encode(r.encoding))
        # o.write(r.text.encode('utf-8')) # Seems wrong for iso*-input
        o.close()

        info = "File %s updated" % (xml_name,)
        xbmcgui.Dialog().ok(addon_name, info)
    except requests.RequestException as e:
        err = 'Can\'t fetch %s: %s' % (xml_name, e)
        xbmcgui.Dialog().notification(addon_name, err,
                                      xbmcgui.NOTIFICATION_ERROR, 5000)
        # raise FetchError(e)
    except IOError as e:
        err = 'Can\'t create file %s%s: %s' % (xml_path,
                                               xml_name, e)
        xbmcgui.Dialog().notification(addon_name, err,
                                      xbmcgui.NOTIFICATION_ERROR, 5000)
        # raise FetchError(e)


def fetch_channels_from_xml(xml_file, channel_name=None):

    # addon = xbmcaddon.Addon()
    xml_file = "".join(get_xml_file_path())
    if not os.path.isfile(xml_file):
        # 0. Create dir, if ness.
        make_addon_data_dir()

        # 1. Use default file
        copy_default_xml_file(xml_file)

        # 2. Toggle update
        update_xml_file()
    #parser = ET.XMLParser(recover=True)
    #elems = ET.fromstring(open(xml_file, "r"), parser=parser).getroot()
    #file = open(xml_file, "r")
    #print(file)
    elems = ET.parse(open(xml_file, "r")).getroot()
    
    if channel_name is None:
        # Return list of channels
        channels = elems.findall("channel")
        ret = []
        for channel in channels:
            ret.append({
                'name': channel.findtext("name"),
                'url':  channel.findtext("url"),
                # 'thumbnail': item.findtext("thumbnail"),
                # 'fanart': item.findtext("fanart"),
            })
        return ret
    else:
        # Return list of items for channel
        ret = []
        channels = elems.findall("channel")
        for channel in channels:
            if channel.findtext("name") == channel_name:
                items = channel.find("items").findall("item")
                for item in items:
                    it = {}
                    for child in item:
                        it[child.tag] = child.text
                    ret.append(it)
                break
        return ret
    


def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle
if sys.argv[1] == 'update_xml_file':
    update_xml_file()
else:
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    _handle = int(sys.argv[1])



if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    if sys.argv[1] != 'update_xml_file':
        router(sys.argv[2][1:])
    

