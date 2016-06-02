#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Easy to use downloader library based on urllib/urllib2
by Bystroushaak (bystrousak@kitakitsune.org)

This work is licensed under a Creative Commons Licence
(http://creativecommons.org/licenses/by/3.0/cz/).
"""
# Imports =====================================================================
import urllib
import urllib2


# Variables ===================================================================
# IE 7/Windows XP headers.
IEHeaders = {
    "User-Agent": "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
    "Accept": "text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain",
    "Accept-Language": "cs,en-us;q=0.7,en;q=0.3",
    "Accept-Charset": "utf-8",
    "Keep-Alive": "300",
    "Connection": "keep-alive",
}
# Linux ubuntu x86_64 Firefox 23 headers
LFFHeaders = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:23.0) Gecko/20100101 Firefox/23.0",
    "Accept": "text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain",
    "Accept-Language": "cs,en-us;q=0.7,en;q=0.3",
    "Accept-Charset": "utf-8",
    "Keep-Alive": "300",
    "Connection": "keep-alive",
}


#= Functions & objects ========================================================
class NoRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        infourl = urllib.addinfourl(fp, headers, req.get_full_url())
        infourl.status = code
        infourl.code = code
        return infourl
    http_error_300 = http_error_302
    http_error_301 = http_error_302
    http_error_303 = http_error_302
    http_error_307 = http_error_302


class Downloader():
    """
    Lightweight class utilizing downloads from internet.

    Main method: .download()

    Important properties:
        .headers
        .response_headers
        .cookies
        .handle_cookies
    """

    def __init__(self,
                 headers=None,
                 handle_cookies=True,
                 http_proxy=None,
                 disable_redirect=False):
        """
        You can set:

        headers -- default IEHeaders, but there is also LFFHeaders
        handle_cookies -- set to false if you don't wish to automatically
                          handle cookies
        http_proxy -- 'url:port' describing HTTP proxy
        disable_redirect -- dont follow 300/301/302/307 redirects
        """
        self.headers = headers if headers is not None else IEHeaders
        self.response_headers = None

        self.cookies = {}
        self.handle_cookies = True
        self.disable_redirect = disable_redirect

        self.http_proxy = None
        if http_proxy is not None:
            self.http_proxy = {'http': http_proxy}

    def download(self, url, get=None, post=None, head=None):
        """
        Parameters:
        url -- set url to download, automatically adds htt:// if not present
        get -- dict with GET parameters
        post -- dict with POST parameters
        head -- set to True if you wish to use HEAD request. Returns headers
                from server.
        """
        # POST params
        if post is not None:
            if type(post) not in [dict, str]:
                raise TypeError("Unknown type of post paramters.")
            if type(post) == dict:
                post = urllib.urlencode(post)

        # append GET params to url
        if get is not None:
            if type(get) != dict:
                raise TypeError("Unknown type of get paramters.")
            get = urllib.urlencode(get)
            if "?" in url:
                if url[-1] == "&":
                    url += get
                else:
                    url += "&" + get
            else:
                url += "?" + get

            get = None

        # check if protocol is specified in |url|
        if not "://" in url:
            url = "http://" + url

        if self.handle_cookies:
            self.__setCookies(url)

        # HEAD request support
        url_req = urllib2.Request(url, post, self.headers)
        if head is not None:
            url_req.get_method = lambda: "HEAD"

        # redirect disabling support
        if self.disable_redirect:
            urllib2.install_opener(urllib2.build_opener(NoRedirectHandler))
        else:
            urllib2.install_opener(
                urllib2.build_opener(urllib2.HTTPRedirectHandler)
            )

        # http proxy support
        opener = None
        if self.http_proxy is not None:
            opener = urllib2.build_opener(
                urllib2.ProxyHandler(self.http_proxy)
            )
            urllib2.install_opener(opener)

        # download page and save headers from server
        f = urllib2.urlopen(url_req)
        data = f.read()
        self.response_headers = f.info().items()
        f.close()

        if self.handle_cookies:
            self.__readCookies(url)

        # i suppose I could fix __readCookies() to use dict, but .. meh
        self.response_headers = dict(self.response_headers)

        # head doesn't have content, so return just response headers
        if head is not None:
            return self.response_headers

        return data

    def __setCookies(self, url):
        # add cokies into headers
        domain = self.__getDomain(url)
        if domain in self.cookies.keys():
            cookie_string = ""
            for key in self.cookies[domain].keys():
                cookie_string += key + "=" + str(self.cookies[domain][key]) + "; "

            self.headers["Cookie"] = cookie_string.strip()

    def __readCookies(self, url):
        # simple (and lame) cookie handling
        # parse "set-cookie" string
        cookie_string = ""
        for c in self.response_headers:
            if c[0].lower() == "set-cookie":
                cookie_string = c[1]

        # parse keyword:values
        tmp_cookies = {}
        for c in cookie_string.split(","):
            cookie = c
            if ";" in c:
                cookie = c.split(";")[0]
            cookie = cookie.strip()

            cookie = cookie.split("=")
            keyword = cookie[0]
            value = "=".join(cookie[1:])

            tmp_cookies[keyword] = value

        # append global variable cookies with new cookies
        if len(tmp_cookies) > 0:
            domain = self.__getDomain(url)

            if domain in self.cookies.keys():
                for key in tmp_cookies.keys():
                    self.cookies[domain][key] = tmp_cookies[key]
            else:
                self.cookies[domain] = tmp_cookies

        # check for blank cookies
        if len(self.cookies) > 0:
            for domain in self.cookies.keys():
                for key in self.cookies[domain].keys():
                    if self.cookies[domain][key].strip() == "":
                        del self.cookies[domain][key]

                if len(self.cookies[domain]) == 0:
                    del self.cookies[domain]

    def __getDomain(self, url):
        """
        Parse domain from url.
        """
        if "://" in url:
            url = url.split("://")[1]

        if "/" in url:
            url = url.split("/")[0]

        return url
