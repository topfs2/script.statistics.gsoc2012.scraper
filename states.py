import xbmc, xbmcgui
from xbmcjsonrpc import getSources
import extraction
import string
import urllib2
import json

server_base_address = "http://127.0.0.1:8000"

def post(address, d):
	h = {
		"Content-Type": "application/json",

		# Some extra headers for fun
		"Accept": "*/*",   # curl does this
		"User-Agent": "xbmc-gsoc2012-statistics", # otherwise it uses "Python-urllib/..."
	}

	req = urllib2.Request(address, headers = h, data = d)

	f = urllib2.urlopen(req)

class SubmitState(object):
	def __init__(self, episodes, movies, videoFiles):
		self.episodes = episodes
		self.movies = movies
		self.videoFiles = videoFiles

	def doModal(self):
		dialog = xbmcgui.Dialog()
		ret = dialog.yesno('Submit?', '{0} episodes'.format(len(self.episodes)), '{0} movies'.format(len(self.movies)), '{0} video files'.format(len(self.videoFiles)))

		if ret:
			progress = xbmcgui.DialogProgress()
			ret = progress.create('GSoC 2012', 'Initializing upload...', "")

			progress.update(1, "Uploading episodes")
			post(server_base_address + "/episodes", json.dumps(self.episodes))
			if progress.iscanceled():
				return

			progress.update(34, "Uploading movies")
			post(server_base_address + "/movies", json.dumps(self.movies))
			if progress.iscanceled():
				return

			progress.update(67, "Uploading unscraped video files")
			post(server_base_address + "/videofiles", json.dumps(self.videoFiles))

			progress.update(100)
			progress.close()

	def close(self):
		pass

class GatherState(object):
	def __init__(self, extractionSteps):
		self.gatherDialog = xbmcgui.DialogProgress()
		self.extractionSteps = extractionSteps

	def doModal(self):
		ret = self.gatherDialog.create('GSoC 2012', 'Initializing extractors...', "")

		try:
			self.steps = len(self.extractionSteps)
			files = set()

			episodes = list()
			if "episodes" in self.extractionSteps:
				def episodeProgress(percentage):
					self.gatherDialog.update(percentage / self.steps, "Extracting episodes", "", "")
				episodes = extraction.extractEpisodes(files, episodeProgress, self.gatherDialog.iscanceled)

			movies = list()
			if "movies" in self.extractionSteps:
				def movieProgress(percentage):
					self.gatherDialog.update((100 + percentage) / self.steps, "Extracting movies", "", "")
				movies = extraction.extractMovies(files, movieProgress, self.gatherDialog.iscanceled)

			videoFiles = list()
			sources = [s for s in getSources() if s["file"] in self.extractionSteps]
			nbrSources = len(sources)

			for i in range(nbrSources):
				source = sources[i]
				source["tick"] = 0
				source["percentage"] = 0

				def unscrapedIsCanceled():
					source["tick"] = source["tick"] + 1 if source["tick"] < 5 else 0
					s = string.join(['.' for s in range(source["tick"])])
					offset = 200 + i * nbrSources

					self.gatherDialog.update((offset + source["percentage"]) / self.steps, "Extracting unscraped videos " + s, source["label"], "")

					return self.gatherDialog.iscanceled()

				def midProgress(i):
					source["percentage"] = i / nbrSources
					unscrapedIsCanceled()

				extraction.extractVideoFilesFromDirectory(files, videoFiles, source["file"], unscrapedIsCanceled, midProgress)

		except:
			raise
		finally:
			self.gatherDialog.close()

		self.sm.switchTo(SubmitState(episodes, movies, videoFiles))

	def close(self):
		pass

class InitialWindow(xbmcgui.Window):
	def __init__(self):
		self.strActionInfo = xbmcgui.ControlLabel(0, 0, 300, 200, 'Push BACK to cancel', 'font13', '0xFFFFFFFF')
		self.addControl(self.strActionInfo)

		self.choiceButton = list()
		self.choiceID = list()

		self.gather = xbmcgui.ControlButton(800, 50, 200, 100, "Next!")
		self.addControl(self.gather)

		self.addChoice("Submit scraped movies", "movies")
		self.addChoice("Submit scraped episodes", "episodes")
		self.addChoice("Submit scraped music videos", "musicvideos")

		for source in getSources():
			self.addChoice(u'Submit unscraped videos from "' + source["label"] + u'"', source["file"])

		self.setFocus(self.choiceButton[0])
		self.gather.controlLeft(self.choiceButton[0])

	def addChoice(self, label, ID):
		button = xbmcgui.ControlRadioButton(50, 50 + 50 * len(self.choiceButton), 600, 40, label)
		self.addControl(button)
		button.setSelected(True)

		if len(self.choiceButton) > 0:
			last = self.choiceButton[-1]
			last.controlDown(button)
			button.controlUp(last)

		button.controlRight(self.gather)

		self.choiceID.append(ID)
		self.choiceButton.append(button)
 
	def onControl(self, control):
		if control is self.gather:
			steps = [self.choiceID[self.choiceButton.index(b)] for b in self.choiceButton if b.isSelected()]
			self.sm.switchTo(GatherState(steps))
