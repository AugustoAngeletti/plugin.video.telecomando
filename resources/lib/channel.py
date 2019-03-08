# -*- coding: utf-8 -*-

class Channel(object):
    icon = ""
    title = ""
    url=""
    lcn=""
    epg=""

    # The class "constructor" - It's actually an initializer 
    def __init__(self, icon, title, url, lcn=None, epg=None):
        self.icon = icon
        self.title = title
        self.url = url
        self.lcn = lcn
        self.epg = epg