#!/usr/bin/python
# -*- coding: utf-8 -*-

from future.standard_library import install_aliases
install_aliases()

import datetime
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

import CommonFunctions as common
import simplejson as json
try:
   import StorageServer
except ImportError:
   import storageserverdummy as StorageServer
import xbmcvfs

from resources.lib.helpers import *
from .base import *
from .Scraper import *

class htmlScraper(Scraper):

	__urlBase	   = 'http://tvthek.orf.at'
	__urlLive	   = __urlBase + '/live'
	__urlMostViewed = __urlBase + '/most-viewed'
	__urlNewest	 = __urlBase + '/newest'
	__urlSchedule   = __urlBase + '/schedule'
	__urlSearch	 = __urlBase + '/search'
	__urlShows	  = __urlBase + '/profiles'
	__urlTips	   = __urlBase + '/tips'
	__urlTopics	 = __urlBase + '/topics'
	__urlArchive	= __urlBase + '/history'


	def __init__(self, xbmc, settings, pluginhandle, quality, protocol, delivery, defaultbanner, defaultbackdrop):
		self.translation = settings.getLocalizedString
		self.xbmc = xbmc
		self.videoQuality = quality
		self.videoDelivery = delivery
		self.videoProtocol = protocol
		self.pluginhandle = pluginhandle
		self.defaultbanner = defaultbanner
		self.defaultbackdrop = defaultbackdrop
		self.enableBlacklist = settings.getSetting("enableBlacklist") == "true"
		debugLog('HTML Scraper - Init done','Info')


	def getMostViewed(self):
		self.getTeaserList(self.__urlMostViewed)


	def getNewest(self):
		self.getTeaserList(self.__urlNewest)


	def getTips(self):
		self.getTeaserList(self.__urlTips)
		
	# Parses the Frontpage Carousel
	def getHighlights(self):
		self.getTeaserSlideshow(self.__urlBase)

	# Extracts VideoURL from JSON String
	def getVideoUrl(self,sources):
		for source in sources:
			if source["protocol"].lower() == self.videoProtocol.lower():
				if source["delivery"].lower() == self.videoDelivery.lower():
					if source["quality"].lower() == self.videoQuality.lower():
						return generateAddonVideoUrl(source["src"])
		return False

	# Converts Page URL to Title
	def programUrlTitle(self,url):
		title = url.replace(self.__urlBase,"").split("/")
		if title[1] == 'index.php':
			return title[3].replace("-"," ")
		else:
			return title[2].replace("-"," ")

	# Parses Result Layout Page
	def getResultList(self,url):
		url = urllib.parse.unquote(url)
		html = common.fetchPage({'link': url})
		container = common.parseDOM(html.get("content"),name='main',attrs={'class': "main"},ret=False)
		teasers = common.parseDOM(container,name='section',attrs={'class': "b-search-results"},ret=False)
		teasers = common.parseDOM(container,name='section',attrs={'class': "b-search-results"},ret=False)
		items = common.parseDOM(teasers,name='article',attrs={'class': "b-teaser"},ret=False)
		print(url)
		print(len(items))
		for item in items:
			subtitle = common.parseDOM(item,name='h4',attrs={'class': "profile"},ret=False)
			subtitle = common.replaceHTMLCodes(subtitle[0]).encode('UTF-8')			
			
			title = common.parseDOM(item,name='h5',attrs={'class': "teaser-title.*?"},ret=False)
			title = common.replaceHTMLCodes(title[0]).encode('UTF-8')
			
			desc = common.parseDOM(item,name='p',attrs={'class': "description.*?"},ret=False)
			if len(desc):
				desc = common.replaceHTMLCodes(desc[0]).encode('UTF-8')
			else:
				desc = ""
			
			channel = common.parseDOM(item,name='p',attrs={'class': "channel"},ret=False)
			if len(channel):
				channel = common.replaceHTMLCodes(channel[0]).encode('UTF-8')
			else:
				channel = ""
			date = common.parseDOM(item,name='span',attrs={'class':'date'},ret=False)
			date = date[0].encode('UTF-8')
			
			time = common.parseDOM(item,name='span',attrs={'class':'time'},ret=False)
			time = time[0].encode('UTF-8')

			figure = common.parseDOM(item,name='figure',attrs={'class':'teaser-img'},ret=False)
			image = common.parseDOM(figure,name='img',attrs={},ret='src')
			image = common.replaceHTMLCodes(image[0]).encode('UTF-8')
			
			link = common.parseDOM(item,name='a',attrs={'class':'teaser-link.*?'},ret='href')
			link = link[0].encode('UTF-8')

			desc = self.formatDescription(title,channel,subtitle,desc,date,time)
			
			parameters = {"link" : link, "banner" : image, "mode" : "openSeries"}

			url = sys.argv[0] + '?' + urllib.parse.urlencode(parameters)
			self.html2ListItem(title,image,"",desc,"","","",url,None,True, False);
			
	# Parses teaser lists
	def getTeaserList(self,url):
		url = urllib.parse.unquote(url)
		html = common.fetchPage({'link': url})
		container = common.parseDOM(html.get("content"),name='main',attrs={'class': "main"},ret=False)
		teasers = common.parseDOM(container,name='ul',attrs={'class': "b-teasers-list"},ret=False)
		items = common.parseDOM(teasers,name='article',attrs={'class': "b-teaser"},ret=False)

		for item in items:
			subtitle = common.parseDOM(item,name='h4',attrs={'class': "profile"},ret=False)
			subtitle = common.replaceHTMLCodes(subtitle[0]).encode('UTF-8')			
			
			title = common.parseDOM(item,name='h5',attrs={'class': "teaser-title.*?"},ret=False)
			title = common.replaceHTMLCodes(title[0]).encode('UTF-8')
			
			desc = common.parseDOM(item,name='p',attrs={'class': "description.*?"},ret=False)
			if len(desc):
				desc = common.replaceHTMLCodes(desc[0]).encode('UTF-8')
			else:
				desc = ""
			
			channel = common.parseDOM(item,name='p',attrs={'class': "channel"},ret=False)
			if len(channel):
				channel = common.replaceHTMLCodes(channel[0]).encode('UTF-8')
			else:
				channel = ""
			date = common.parseDOM(item,name='span',attrs={'class':'date'},ret=False)
			date = date[0].encode('UTF-8')
			
			time = common.parseDOM(item,name='span',attrs={'class':'time'},ret=False)
			time = time[0].encode('UTF-8')

			figure = common.parseDOM(item,name='figure',attrs={'class':'teaser-img'},ret=False)
			image = common.parseDOM(figure,name='img',attrs={},ret='src')
			image = common.replaceHTMLCodes(image[0]).encode('UTF-8')
			
			link = common.parseDOM(item,name='a',attrs={'class':'teaser-link.*?'},ret='href')
			link = link[0].encode('UTF-8')

			desc = self.formatDescription(title,channel,subtitle,desc,date,time)
			
			parameters = {"link" : link, "banner" : image, "mode" : "openSeries"}

			url = sys.argv[0] + '?' + urllib.parse.urlencode(parameters)
			self.html2ListItem(title,image,"",desc,"","","",url,None,True, False)
	

	def formatDescription(self,title,channel,subtitle,desc,date,time):
		date_prefix = self.translation(30009).encode("utf-8")
		
		#Reformat Title
		if subtitle != title:
			if len(subtitle):
				title = "%s | %s" % (title,subtitle)
		if date != "":
			title = "%s - %s" % (title,date)
		
		#Reformat
		if len(subtitle):
			if subtitle == title:
				subtitle = ""
			else:
				if len(channel):
					subtitle = " | [LIGHT]%s[/LIGHT]" % subtitle
				else:
					subtitle = "[LIGHT]%s[/LIGHT]" % subtitle
		else:
			subtitle = ""
			
		if len(desc):
			desc = "[CR]%s" % desc
		else:
			desc = ""
			
		if len(channel):
			channel = "[B]%s[/B]" % channel
		else:
			channel = ""
			
		if len(date):
			return "%s%s[CR]%s[CR][I]%s %s - %s[/I]" % (channel,subtitle,desc,date_prefix,date,time)
		else:
			return "%s%s[CR]%s" % (channel,subtitle,desc)
	
	# Parses a teaser slideshow
	def getTeaserSlideshow(self,url):
		url = urllib.parse.unquote(url)
		html = common.fetchPage({'link': url})
		container = common.parseDOM(html.get("content"),name='main',attrs={'class': "main"},ret=False)
		teasers = common.parseDOM(container,name='ul',attrs={'class': "stage-item-list.*?"},ret=False)
		items = common.parseDOM(teasers,name='li',attrs={'class': "stage-item.*?"},ret=False)

		for item in items:
			subtitle = common.parseDOM(item,name='h2',attrs={'class': "stage-item-profile-title"},ret=False)
			subtitle = common.replaceHTMLCodes(subtitle[0]).encode('UTF-8')			
			
			title = common.parseDOM(item,name='h3',attrs={'class': "stage-item-teaser-title"},ret=False)
			title = common.replaceHTMLCodes(title[0]).encode('UTF-8')
			
			figure = common.parseDOM(item,name='figure',attrs={'class':'stage-item-img'},ret=False)
			image = common.parseDOM(figure,name='img',attrs={},ret='src')
			image = common.replaceHTMLCodes(image[0]).encode('UTF-8')
			
			link = common.parseDOM(item,name='a',attrs={},ret='href')
			link = link[0].encode('UTF-8')
			
			#Reformat Title
			if subtitle != title:
				title = "%s | %s" % (subtitle,title)

			parameters = {"link" : link, "banner" : image, "mode" : "openSeries"}

			url = sys.argv[0] + '?' + urllib.parse.urlencode(parameters)
			self.html2ListItem(title,image,"","","","","",url,None,True, False);


	def openArchiv(self,url):
		url = urllib.parse.unquote(url)
		html = common.fetchPage({'link': url})
		container = common.parseDOM(html.get("content"),name='main',attrs={'class': "main"},ret=False)
		teasers = common.parseDOM(container,name='div',attrs={'class': "b-schedule-list"},ret=False)
		items = common.parseDOM(teasers,name='article',attrs={'class': "b-schedule-episode.*?"},ret=False)
		
		date = common.parseDOM(teasers,name='h2',attrs={'class':'day-title.*?'},ret=False)
		if len(date):
			date = date[0].encode('UTF-8')
		else:
			date = ""

		for item in items:	
			title = common.parseDOM(item,name='h4',attrs={'class': "item-title.*?"},ret=False)
			title = common.replaceHTMLCodes(title[0]).encode('UTF-8')
			
			desc = common.parseDOM(item,name='div',attrs={'class': "item-description.*?"},ret=False)
			if len(desc):
				desc = common.replaceHTMLCodes(desc[0]).encode('UTF-8')
				desc = common.stripTags(desc)
			else:
				desc = ""
			
			channel = common.parseDOM(item,name='span',attrs={'class': "small-information.meta.meta-channel-name"},ret=False)
			if len(channel):
				channel = common.replaceHTMLCodes(channel[0]).encode('UTF-8')
			else:
				channel = ""
			
			time = common.parseDOM(item,name='span',attrs={'class':'meta.meta-time'},ret=False)
			time = time[0].encode('UTF-8')
			
			title = "[%s] %s" % (time,title)
			
			subtitle = time

			figure = common.parseDOM(item,name='figure',attrs={'class':'episode-image'},ret=False)
			image = common.parseDOM(figure,name='img',attrs={},ret='src')
			image = common.replaceHTMLCodes(image[0]).encode('UTF-8')
			
			link = common.parseDOM(item,name='a',attrs={'class':'episode-content'},ret='href')
			link = link[0].encode('UTF-8')

			desc = self.formatDescription(title,channel,subtitle,desc,date,time)
			
			parameters = {"link" : link, "banner" : image, "mode" : "openSeries"}

			url = sys.argv[0] + '?' + urllib.parse.urlencode(parameters)
			self.html2ListItem(title,image,"",desc,"","","",url,None,True, False);

	# Parses the Frontpage Show Overview Carousel
	def getCategories(self):
		html = common.fetchPage({'link': self.__urlShows})
		container = common.parseDOM(html.get("content"),name='main',attrs={'class': "main"},ret=False)
		teasers = common.parseDOM(container,name='div',attrs={'class': "b-profile-results-container.*?"},ret=False)
		items = common.parseDOM(teasers,name='article',attrs={'class': "b-teaser"},ret=False)

		for item in items:
			subtitle = common.parseDOM(item,name='h4',attrs={'class': "profile"},ret=False)
			subtitle = common.replaceHTMLCodes(subtitle[0]).encode('UTF-8')			
			
			title = common.parseDOM(item,name='h5',attrs={'class': "teaser-title.*?"},ret=False)
			title = common.replaceHTMLCodes(title[0]).encode('UTF-8')
			
			desc = common.parseDOM(item,name='p',attrs={'class': "description.*?"},ret=False)
			if len(desc):
				desc = common.replaceHTMLCodes(desc[0]).encode('UTF-8')
			else:
				desc = ""
			
			channel = common.parseDOM(item,name='p',attrs={'class': "channel"},ret=False)
			if len(channel):
				channel = common.replaceHTMLCodes(channel[0]).encode('UTF-8')
			else:
				channel = ""
			date = common.parseDOM(item,name='span',attrs={'class':'date'},ret=False)
			date = date[0].encode('UTF-8')
			
			time = common.parseDOM(item,name='span',attrs={'class':'time'},ret=False)
			time = time[0].encode('UTF-8')

			figure = common.parseDOM(item,name='figure',attrs={'class':'teaser-img'},ret=False)
			image = common.parseDOM(figure,name='img',attrs={},ret='src')
			image = common.replaceHTMLCodes(image[0]).encode('UTF-8')
			
			link = common.parseDOM(item,name='a',attrs={'class':'teaser-link.*?'},ret='href')
			link = link[0].encode('UTF-8')
			
			desc = self.formatDescription(title,channel,subtitle,desc,date,time)

			parameters = {"link" : link, "banner" : image, "mode" : "getSendungenDetail"}
			url = sys.argv[0] + '?' + urllib.parse.urlencode(parameters)
			self.html2ListItem(title,image,"", desc,"","","",url,None,True, False);

	# Parses Details for the selected Show
	def getCategoriesDetail(self,category,banner):
		url =  urllib.parse.unquote(category)
		banner =  urllib.parse.unquote(banner)
		html = common.fetchPage({'link': url})
		container = common.parseDOM(html.get("content"),name='main',attrs={'class': "main"},ret=False)
		
		#Main Episode
		main_episode_container = common.parseDOM(container,name='section',attrs={'class': "b-video-details.*?"},ret=False)
			
		title = common.parseDOM(main_episode_container,name='h2',attrs={'class': "description-title.*?"},ret=False)
		title = common.replaceHTMLCodes(title[0]).encode('UTF-8')
		
		subtitle = common.parseDOM(main_episode_container,name='span',attrs={'class': "js-subheadline"},ret=False)
		if len(subtitle):
			subtitle = common.replaceHTMLCodes(subtitle[0]).encode('UTF-8')		
		else:
			subtitle = ""
		
				
		desc = common.parseDOM(main_episode_container,name='p',attrs={'class': "description-text.*?"},ret=False)
		if len(desc):
			desc = common.replaceHTMLCodes(desc[0]).encode('UTF-8')
		else:
			desc = ""
				
		channel = common.parseDOM(main_episode_container,name='span',attrs={'class': "channel.*?"},ret="aria-label")
		if len(channel):
			channel = common.replaceHTMLCodes(channel[0]).encode('UTF-8')
		else:
			channel = ""
			
		date = common.parseDOM(main_episode_container,name='span',attrs={'class':'date'},ret=False)
		date = date[0].encode('UTF-8')
				
		time = common.parseDOM(main_episode_container,name='span',attrs={'class':'time'},ret=False)
		time = time[0].encode('UTF-8')

		image = banner
		
		if date != "":
			title = "%s - %s" % (title,date)
				
		desc = self.formatDescription(title,channel,subtitle,desc,date,time)

		parameters = {"link" : url, "banner" : image, "mode" : "openSeries"}
		url = sys.argv[0] + '?' + urllib.parse.urlencode(parameters)
		self.html2ListItem(title,image,"", desc,"","","",url,None,True, False);
		
		
		#More Episodes
		more_episode_container = common.parseDOM(container,name='section',attrs={'class': "related-videos"},ret=False)
		more_episode_json = common.parseDOM(more_episode_container,name="div",attrs={'class':'more-episodes.*?'},ret='data-jsb')
		if len(more_episode_json):
			more_episode_json_raw = common.replaceHTMLCodes(more_episode_json[0]).encode('UTF-8')
			more_episode_json_data = json.loads(more_episode_json_raw)
			more_episodes_url = "%s%s" % (self.__urlBase,more_episode_json_data.get('url'))
			
			additional_html = common.fetchPage({'link': more_episodes_url})

			items = common.parseDOM(additional_html.get("content"),name='article',attrs={'class': "b-teaser"},ret=False)

			#print(len(items))
			for item in items:
				subtitle = common.parseDOM(item,name='h4',attrs={'class': "profile"},ret=False)
				subtitle = common.replaceHTMLCodes(subtitle[0]).encode('UTF-8')			
				
				title = common.parseDOM(item,name='h5',attrs={'class': "teaser-title.*?"},ret=False)
				title = common.replaceHTMLCodes(title[0]).encode('UTF-8')
				
				desc = common.parseDOM(item,name='p',attrs={'class': "description.*?"},ret=False)
				if len(desc):
					desc = common.replaceHTMLCodes(desc[0]).encode('UTF-8')
				else:
					desc = ""
				
				channel = common.parseDOM(item,name='p',attrs={'class': "channel"},ret=False)
				if len(channel):
					channel = common.replaceHTMLCodes(channel[0]).encode('UTF-8')
				else:
					channel = ""
				date = common.parseDOM(item,name='span',attrs={'class':'date'},ret=False)
				date = date[0].encode('UTF-8')
				
				time = common.parseDOM(item,name='span',attrs={'class':'time'},ret=False)
				time = time[0].encode('UTF-8')

				figure = common.parseDOM(item,name='figure',attrs={'class':'teaser-img'},ret=False)
				image = common.parseDOM(figure,name='img',attrs={},ret='src')
				image = common.replaceHTMLCodes(image[0]).encode('UTF-8')
				
				link = common.parseDOM(item,name='a',attrs={'class':'teaser-link.*?'},ret='href')
				link = link[0].encode('UTF-8')
				
				date_prefix = self.translation(30009).encode("utf-8")
				
				if date != "":
					title = "%s - %s" % (title,date)
				
				desc = self.formatDescription(title,channel,subtitle,desc,date,time)

				parameters = {"link" : link, "banner" : image, "mode" : "openSeries"}
				url = sys.argv[0] + '?' + urllib.parse.urlencode(parameters)
				self.html2ListItem(title,image,"", desc,"","","",url,None,True, False);
		
		

	# Parses "Sendung verpasst?" Date Listing
	def getSchedule(self):
		html = common.fetchPage({'link': self.__urlSchedule})
		container = common.parseDOM(html.get("content"),name='div',attrs={'class': 'b-select-box.*?'})
		list_container = common.parseDOM(container,name='select',attrs={'class': 'select-box-list.*?'})
		items = common.parseDOM(list_container,name='option',attrs={'class': 'select-box-item.*?'})
		data_items = common.parseDOM(list_container,name='option',attrs={'class': 'select-box-item.*?'},ret="data-custom-properties")
		i = 0
		for item in items:
			title = common.replaceHTMLCodes(item).encode('UTF-8')
			link = common.replaceHTMLCodes(data_items[i]).encode('UTF-8')
			link = "%s%s" % (self.__urlBase,link)

			print("Titel: %s" % title)
			print("Link: %s" % link)

			parameters = {"link" : link, "mode" : "getScheduleDetail"}
			url = sys.argv[0] + '?' + urllib.parse.urlencode(parameters)
			self.html2ListItem(title,"","","","","","",url,None,True, False);
			i = i+1

	def getArchiv(self):
		html = common.fetchPage({'link': self.__urlArchive})
		html_content = html.get("content")

		wrapper = common.parseDOM(html_content,name='main',attrs={'class':'main'})
		items = common.parseDOM(wrapper,name='article',attrs={'class':'b-topic-teaser.*?'})

		for item in items:
			subtitle = common.parseDOM(item,name='h4',attrs={'class': "sub-headline"},ret=False)
			subtitle = common.replaceHTMLCodes(subtitle[0]).encode('UTF-8')			
			
			title = common.parseDOM(item,name='h5',attrs={'class': "teaser-title.*?"},ret=False)
			title = common.replaceHTMLCodes(title[0]).encode('UTF-8')		
			
			video_count = common.parseDOM(item,name='p',attrs={'class': "topic-video-count"},ret=False)
			desc = common.replaceHTMLCodes(video_count[0]).encode('UTF-8')

			figure = common.parseDOM(item,name='figure',attrs={'class':'teaser-img'},ret=False)
			image = common.parseDOM(figure,name='img',attrs={},ret='src')
			image = common.replaceHTMLCodes(image[0]).encode('UTF-8')
			
			link = common.parseDOM(item,name='a',ret='href')
			link = link[0].encode('UTF-8')

			desc = self.formatDescription(title,"",subtitle,desc,"","")
			
			parameters = {"link" : link, "banner" : image, "mode" : "getArchiveDetail"}

			url = sys.argv[0] + '?' + urllib.parse.urlencode(parameters)
			self.html2ListItem(title,image,"",desc,"","","",url,None,True, False);

	# Creates a XBMC List Item
	def html2ListItem(self,title,banner,backdrop,description,duration,date,channel,videourl,subtitles=None,folder=True,playable = False,contextMenuItems = None):
		if banner == '':
			banner = self.defaultbanner
		if backdrop == '':
			backdrop = self.defaultbackdrop
		params = parameters_string_to_dict(videourl)
		mode = params.get('mode')
		if not mode:
			mode = "player"

		blacklist = False
		if self.enableBlacklist:
			if mode == 'openSeries' or mode == 'getSendungenDetail':
				blacklist = True
		debugLog("Adding List Item","Info")
		debugLog("Mode: %s" % mode,"Info")
		debugLog("Videourl: %s" % videourl,"Info")
		debugLog("Duration: %s" % duration,"Info")

		return createListItem(title,banner,description,duration,date,channel,videourl,playable,folder, backdrop,self.pluginhandle,subtitles,blacklist,contextMenuItems)

	# Parses a Video Page and extracts the Playlist/Description/...
	def getLinks(self,url,banner,playlist):
		url = str(urllib.parse.unquote(url))
		debugLog("Loading Videos from %s" % url,'Info')
		if banner != None:
			banner = urllib.parse.unquote(banner)

		html = common.fetchPage({'link': url})
		data = common.parseDOM(html.get("content"),name='div',attrs={'class': "jsb_ jsb_VideoPlaylist"},ret='data-jsb')
		if len(data):
			try:
				data = data[0]
				data = common.replaceHTMLCodes(data)
				data = json.loads(data)
				current_preview_img = data.get("selected_video")["preview_image_url"]
				video_items = data.get("playlist")["videos"]
				current_title = data.get("selected_video")["title"]
				if data.get("selected_video")["description"]:
					current_desc = data.get("selected_video")["description"].encode('UTF-8')
				else:
					current_desc = ""

				if data.get("selected_video")["duration"]:
					current_duration = float(data.get("selected_video")["duration"])
					current_duration = int(current_duration / 1000)
				else:
					current_duration = 0

				
				if "subtitles" in data.get("selected_video"):
					current_subtitles = []
					for sub in data.get("selected_video")["subtitles"]:
						current_subtitles.append(sub.get(u'src'))
				else:
					current_subtitles = None
				current_videourl = self.getVideoUrl(data.get("selected_video")["sources"]);
			except Exception as e:
				debugLog("Error Loading Episode from %s" % url,'Exception')
				notifyUser((self.translation(30052)).encode("utf-8"))
				current_subtitles = None

			if len(video_items) > 1:
				play_all_name = "[ "+(self.translation(30015)).encode("utf-8")+" ]"
				debugLog("Found Video Playlist with %d Items" % len(video_items),'Info')
				createPlayAllItem(play_all_name,self.pluginhandle)						   
				for video_item in video_items:
					try:
						title = video_item["title"].encode('UTF-8')
						if video_item["description"]:
							desc = video_item["description"].encode('UTF-8')
						else:
							debugLog("No Video Description for %s" % title,'Info')
							desc = ""

						if video_item["duration"]:
							duration = float(video_item["duration"])
							duration = int(duration / 1000)
						else:
							duration = 0

						preview_img = video_item["preview_image_url"]
						sources = video_item["sources"]
						if "subtitles" in video_item:
							debugLog("Found Subtitles for %s" % title,'Info')
							subtitles = []
							for sub in video_item["subtitles"]:
								subtitles.append(sub.get(u'src'))
						else:
							subtitles = None
						videourl = self.getVideoUrl(sources);

						liz = self.html2ListItem(title,preview_img,"",desc,duration,'','',videourl, subtitles,False, True)
						playlist.add(videourl,liz)
					except Exception as e:
						debugLog(str(e),'Error')
						continue
				return playlist
			else:
				debugLog("No Playlist Items found for %s. Setting up single video view." % current_title.encode('UTF-8'),'Info')
				liz = self.html2ListItem(current_title,current_preview_img,"",current_desc,current_duration,'','',current_videourl, current_subtitles,False, True)
				playlist.add(current_videourl,liz)
				return playlist
		else:
			notifyUser((self.translation(30052)).encode("utf-8"))
			sys.exit()


	# Returns Live Stream Listing
	def getLiveStreams(self):
		html = common.fetchPage({'link': self.__urlBase})
		wrapper = common.parseDOM(html.get("content"),name='main',attrs={'class': 'main'})
		section = common.parseDOM(wrapper,name='section',attrs={'class': 'b-live-program.*?'})
		items = common.parseDOM(section,name='li',attrs={'class': 'channel orf.*?'})

		for item in items:		
			channel = common.parseDOM(item,name='img',attrs={'class': 'channel-logo'},ret="alt")
			channel = common.replaceHTMLCodes(channel[0]).encode('UTF-8')
			
			article = common.parseDOM(item,name='article',attrs={'class': 'b-livestream-teaser.*?'})
			if len(article):
				figure = common.parseDOM(article,name='figure',attrs={'class':'teaser-img'},ret=False)
				image = common.parseDOM(figure,name='img',attrs={},ret='data-src')
				image = common.replaceHTMLCodes(image[0]).encode('UTF-8')

				time = common.parseDOM(article,name='h4',attrs={'class': 'time'},ret=False)
				time = common.replaceHTMLCodes(time[0]).encode('UTF-8').replace("Uhr","").replace(".",":").strip()
				time = common.stripTags(time).encode('UTF-8')
				
				title = common.parseDOM(article,name='h4',attrs={'class': 'livestream-title.*?'})
				title = common.replaceHTMLCodes(title[0]).encode('UTF-8')

				link = common.parseDOM(item,name='a',attrs={'class': 'js-link-box'},ret="href")
				link = common.replaceHTMLCodes(link[0]).encode('UTF-8')
				
				data = common.parseDOM(item,name='a',attrs={'class': 'js-link-box'},ret="data-jsb")
				data = common.replaceHTMLCodes(data[0]).encode('UTF-8')
				data = json.loads(data)
				
				online = common.parseDOM(article,name='span',attrs={'class': 'status-online'})
				if len(online):
					online = True
				else:
					online = False		
					
				restart = common.parseDOM(article,name='span',attrs={'class': 'is-restartable'})
				if len(restart):
					restart = True
				else:
					restart = False
				
				self.buildLivestream(title,link,time,restart,channel,image,online)
				
	def buildLivestream(self,title,link,time,restart,channel,banner,online):
		html = common.fetchPage({'link': link})
		container = common.parseDOM(html.get("content"),name='div',attrs={'class': "player_viewport.*?"})
		data = common.parseDOM(container[0],name='div',attrs={},ret="data-jsb")

		if online:
			state = (self.translation(30019)).encode("utf-8")
		else:
			state = (self.translation(30020)).encode("utf-8")
		
		if time:
			time_str = " (%s)" % time
		else:
			time_str = ""
		
		try:
			xbmcaddon.Addon('inputstream.adaptive')
			inputstreamAdaptive = True
		except RuntimeError:
			inputstreamAdaptive = False
		
		if channel:
			channel = "[%s]" % channel
		else:
			channel = "LIVE"

		
		uhd_streaming_url = self.getLivestreamUrl(data,'uhdbrowser')
		if uhd_streaming_url:
			debugLog("Adding UHD Livestream","Info")
			uhdContextMenuItems = []
			if inputstreamAdaptive and restart:
				uhdContextMenuItems.append(('Restart', 'RunPlugin(plugin://%s/?mode=liveStreamRestart&link=%s)' % (xbmcaddon.Addon().getAddonInfo('id'), link)))
				uhd_final_title = "[Restart]%s[UHD] - %s%s" % (channel,title,time_str)
			else:
				uhd_final_title = "%s[UHD] - %s%s" % (channel,title,time_str)
			self.html2ListItem(uhd_final_title ,banner,"",state,time,channel,channel, generateAddonVideoUrl(uhd_streaming_url),None,False, True, uhdContextMenuItems)
						
		streaming_url = self.getLivestreamUrl(data,self.videoQuality)
		contextMenuItems = []
		if inputstreamAdaptive and restart:
			contextMenuItems.append(('Restart', 'RunPlugin(plugin://%s/?mode=liveStreamRestart&link=%s)' % (xbmcaddon.Addon().getAddonInfo('id'), link)))
			final_title = "[Restart]%s - %s%s" % (channel,title,time_str)
		else:
			final_title = "%s - %s%s" % (channel,title,time_str)
		self.html2ListItem(final_title,banner,"",state,time,channel,channel, generateAddonVideoUrl(streaming_url),None,False, True,contextMenuItems)
					
	def liveStreamRestart(self, link):
		try:
			xbmcaddon.Addon('inputstream.adaptive')
		except RuntimeError:
			return

		livestream_id = link.rpartition('/')[-1]
		html = common.fetchPage({'link': link})
		bitmovinStreamId = self.getLivestreamBitmovinID(html)
		stream_info = self.getLivestreamInformation(html)

		if bitmovinStreamId:
			title	   = stream_info['title']
			image	   = stream_info['image']
			description = stream_info['description']
			duration	= stream_info['duration']
			date		= stream_info['date']
			channel	 = stream_info['channel']

			ApiKey = '2e9f11608ede41f1826488f1e23c4a8d'
			response = urllib.request.urlopen('https://playerapi-restarttv.ors.at/livestreams/%s/sections/?state=active&X-Api-Key=%s' % (bitmovinStreamId, ApiKey)) 
			response_raw = response.read().decode(response.headers.get_content_charset())
			
			section = json.loads(response_raw)
			if len(section):
				section = section[0]
				streamingURL = 'https://playerapi-restarttv.ors.at/livestreams/%s/sections/%s/manifests/hls/?startTime=%s&X-Api-Key=%s' % (bitmovinStreamId, section.get('id'), section.get('metaData').get('timestamp'), ApiKey)

				listItem = createListItem(title, image, description, duration, date, channel , streamingURL, True, False, self.defaultbackdrop, self.pluginhandle)
				listItem.setProperty('inputstreamaddon', 'inputstream.adaptive')
				listItem.setProperty('inputstream.adaptive.manifest_type', 'hls')
				self.xbmc.Player().play(streamingURL, listItem)

	@staticmethod
	def getLivestreamUrl(data_sets,quality):
		for data in data_sets:
			try:
				data = common.replaceHTMLCodes(data)
				data = json.loads(data)
				if 'playlist' in data:
					if 'videos' in data['playlist']:
						for video_items in data['playlist']['videos']:
							for video_sources in video_items['sources']:
								if video_sources['quality'].lower() == quality.lower() and video_sources['protocol'].lower() == "http" and video_sources['delivery'].lower() == 'hls':
									return video_sources['src']
			except:
				debugLog("Error getting Livestream","Info")

	@staticmethod
	def getLivestreamBitmovinID(html):
		container = common.parseDOM(html.get("content"),name='div',attrs={'class': "player_viewport.*?"})
		if len(container):
			data_sets = common.parseDOM(container[0],name='div',attrs={},ret="data-jsb")
			if len(data_sets):
				for data in data_sets:
					try:
						data = common.replaceHTMLCodes(data)
						data = json.loads(data)
						
						if 'restart_url' in data:
							print(data)
							bitmovin_id = data['restart_url'].replace("https://playerapi-restarttv.ors.at/livestreams/","").replace("/sections/","")
							return bitmovin_id.split("?")[0]
					except:
						debugLog("Error getting Livestream Bitmovin ID","Info")
						return False
		return False

	@staticmethod
	def getLivestreamInformation(html):
		container = common.parseDOM(html.get("content"),name='div',attrs={'class': "player_viewport.*?"})
		data_sets = common.parseDOM(container[0],name='div',attrs={},ret="data-jsb")
		title	   = "Titel"
		image	   = ""
		description = "Beschreibung"
		duration	= ""
		date		= ""
		channel	 = ""
		time_str	= ""


		for data in data_sets:
			try:
				data = common.replaceHTMLCodes(data)
				data = json.loads(data)

				if 'playlist' in data:
					if 'title' in data['playlist']:
						title = data['playlist']['title'].encode('UTF-8')
					if 'preview_image_url' in data['playlist']:
						image = data['playlist']['preview_image_url']
					if 'livestream_start' in data['playlist']:
						date = data['playlist']['livestream_start']
						time_str = datetime.datetime.fromtimestamp(int(date)).strftime('%H:%M')
					if 'livestream_end' in data['playlist']:
						date = data['playlist']['livestream_end']
						time_str_end = datetime.datetime.fromtimestamp(int(date)).strftime('%H:%M')
					if 'videos' in data['playlist']:
						if 'description' in data['playlist']['videos']:
							description = data['playlist']['videos']['description']

					return {"title" : "%s (%s - %s)" % (title,time_str,time_str_end),"image" : image,"description" : description, "date" : date, "duration" : duration, "channel" : channel}
			except:
				debugLog("Error getting Livestream Infos","Info")

	# Helper for Livestream Listing - Returns if Stream is currently running
	@staticmethod
	def getBroadcastState(time):
		time_probe = time.split(":")

		current_hour = datetime.datetime.now().strftime('%H')
		current_min = datetime.datetime.now().strftime('%M')
		if time_probe[0] == current_hour and time_probe[1] >= current_min:
			return False
		elif time_probe[0] > current_hour:
			return False
		else:
			return True

	# Parses the Topic Overview Page
	def getThemen(self):
		html = common.fetchPage({'link': self.__urlTopics})
		html_content = html.get("content")

		content = common.parseDOM(html_content,name='section',attrs={})
		#topics = common.parseDOM(content,name='section',attrs={'class':'item_wrapper'})

		for topic in content:
			title = common.parseDOM(topic,name='h3',attrs={'class':'item_wrapper_headline.subheadline'})
			if title:
				title = common.replaceHTMLCodes(title[0]).encode('UTF-8')

				link = common.parseDOM(topic,name='a',attrs={'class':'more.service_link.service_link_more'},ret="href")
				link = common.replaceHTMLCodes(link[0]).encode('UTF-8')

				image = common.parseDOM(topic,name='img',ret="src")
				image = common.replaceHTMLCodes(image[0]).replace("width=395","width=500").replace("height=209.07070707071","height=265").encode('UTF-8')

				descs = common.parseDOM(topic,name='h4',attrs={'class':'item_title'})
				description = ""
				for desc in descs:
					description += "* "+common.replaceHTMLCodes(desc).encode('UTF-8') + "\n"

				parameters = {"link" : link, "mode" : "getThemenDetail"}
				url = sys.argv[0] + '?' + urllib.parse.urlencode(parameters)
				self.html2ListItem(title,image,"",description,"","","",url,None,True, False);

	# Parses the Archive Detail Page
	def getArchiveDetail(self,url):
		url = urllib.parse.unquote(url)
		html = common.fetchPage({'link': url})
		html_content = html.get("content")

		wrapper = common.parseDOM(html_content,name='main',attrs={'class':'main'})
		items = common.parseDOM(wrapper,name='article',attrs={'class':'b-teaser.*?'})

		for item in items:
			subtitle = common.parseDOM(item,name='h4',attrs={'class': "profile"},ret=False)
			subtitle = common.replaceHTMLCodes(subtitle[0]).encode('UTF-8')			
			
			title = common.parseDOM(item,name='h5',attrs={'class': "teaser-title.*?"},ret=False)
			title = common.replaceHTMLCodes(title[0]).encode('UTF-8')		
			
			desc = common.parseDOM(item,name='p',attrs={'class': "description.*?"},ret=False)
			desc = common.replaceHTMLCodes(desc[0]).encode('UTF-8')
			
			figure = common.parseDOM(item,name='figure',attrs={'class':'teaser-img'},ret=False)
			image = common.parseDOM(figure,name='img',attrs={},ret='src')
			image = common.replaceHTMLCodes(image[0]).encode('UTF-8')
			
			link = common.parseDOM(item,name='a',ret='href')
			link = link[0].encode('UTF-8')
			
			channel = common.parseDOM(item,name='p',attrs={'class': "channel"},ret=False)
			if len(channel):
				channel = common.replaceHTMLCodes(channel[0]).encode('UTF-8')
			else:
				channel = ""
				
			date = common.parseDOM(item,name='span',attrs={'class':'date'},ret=False)
			date = date[0].encode('UTF-8')
				
			time = common.parseDOM(item,name='span',attrs={'class':'time'},ret=False)
			time = time[0].encode('UTF-8')

			desc = self.formatDescription(title,channel,subtitle,desc,date,time)
			
			parameters = {"link" : link, "banner" : image, "mode" : "openSeries"}
			url = sys.argv[0] + '?' + urllib.parse.urlencode(parameters)
			self.html2ListItem(title,image,"",desc,"","","",url,None,True, False);

	def getSearchHistory(self):
		parameters = {'mode' : 'getSearchResults'}
		u = sys.argv[0] + '?' + urllib.parse.urlencode(parameters)
		createListItem((self.translation(30007)).encode("utf-8")+" ...", self.defaultbanner, "", "", "", '', u, False, True, self.defaultbackdrop,self.pluginhandle,None)

		cache = StorageServer.StorageServer("plugin.video.orftvthek", 999999)
		cache.table_name = "searchhistory"
		some_dict = cache.get("searches").split("|")
		for str_val in reversed(some_dict):
			if str_val.strip() != '':
				parameters = {'mode' : 'getSearchResults','link' : str_val.replace(" ","+")}
				u = sys.argv[0] + '?' + urllib.parse.urlencode(parameters)
				createListItem(str_val.encode('UTF-8'), self.defaultbanner, "", "", "", '', u, False, True, self.defaultbackdrop,self.pluginhandle,None)

	@staticmethod
	def removeUmlauts(str_val):
		return str_val.replace("Ö","O").replace("ö","o").replace("Ü","U").replace("ü","u").replace("Ä","A").replace("ä","a")

	def getSearchResults(self,link):
		keyboard = self.xbmc.Keyboard(link)
		keyboard.doModal()
		if (keyboard.isConfirmed()):
			cache = StorageServer.StorageServer("plugin.video.orftvthek", 999999)
			cache.table_name = "searchhistory"
			keyboard_in = self.removeUmlauts(keyboard.getText())
			if keyboard_in != link:
				some_dict = cache.get("searches") + "|"+keyboard_in
				cache.set("searches",some_dict);
			searchurl = "%s?q=%s"%(self.__urlSearch,keyboard_in.replace(" ","+"))
			self.getResultList(searchurl)
		else:
			parameters = {'mode' : 'getSearchHistory'}
			u = sys.argv[0] + '?' + urllib.parse.urlencode(parameters)
			createListItem((self.translation(30014)).encode("utf-8")+" ...", self.defaultbanner, "", "", "", '', u, False, True, self.defaultbackdrop,self.pluginhandle,None)
