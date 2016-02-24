__author__ = 'user'

from melon import Farmer
from DetectedTopic import DetectedTopic
import os
import time

#a text processor that creates and maintains DetectedTopics as it goes
class WordBagger:

    def __init__(self, labelToTitlesAUS, labelToTitlesNZ, verbose=True):
        self.processedTroves = []
        self.labelToTitlesAUS = labelToTitlesAUS
        self.labelToTitlesNZ = labelToTitlesNZ
        self.verbose = verbose
        self.farmer = Farmer()



    #traverse all of our .json articles and give the text from each one to the examineText method
    #add processed troves to our list as we go
    def processFiles(self, filePathString):
        for root, dirs, files in os.walk(filePathString):
            for eachFile in files:
                if eachFile.endswith(".json"):
                    start = time.clock()#TODO: remove this
                    if self.verbose:
                        print("-----------------EXAMINING FILE: " + eachFile.title())
                    #articleDict = self.farmer.read_json(os.path.join(root, eachFile)) #TODO: once other stuff is done, change this so that it works on the og trove files.
                    for articleDict in self.farmer.readTrove(os.path.join(root, eachFile)):
                        if not articleDict["category"] == "Advertising": #TODO: swap this out for checking a blacklist settings item against the title
                            print("about to examine the following article (will look for aus stuff first): " + articleDict["heading"])#TODO: delete this debug stuff
                            #get this article's topics
                            detectedTopicsAUS = self.examineText(articleDict["fulltext"], self.labelToTitlesAUS)
                            detectedTopicsNZ = self.examineText(articleDict["fulltext"], self.labelToTitlesNZ)#TODO: should really just make one call and pass both dctionaries as it is more efficient that way
                            #count total occurences of all of the nz and aus topic labels. also fill in lists of the detected topic names to be outputted in json
                            topicsAUS = []
                            AUSTopicOccurences = 0
                            for eachTopic in detectedTopicsAUS.values():
                                topicsAUS.append({eachTopic.topicTitle:eachTopic.occurencesCount})
                                AUSTopicOccurences += eachTopic.occurencesCount
                            topicsNZ = []
                            NZTopicOccurences = 0
                            for eachTopic in detectedTopicsNZ.values():
                                topicsNZ.append({eachTopic.topicTitle:eachTopic.occurencesCount})
                                NZTopicOccurences += eachTopic.occurencesCount
                            #fill out some other information for the json output
                            issue = eachFile.title()
                            heading = articleDict["heading"]
                            articleID = articleDict["id"]
                            wordCount = articleDict["wordCount"]
                            #calculate some nzness measure
                            if AUSTopicOccurences == 0:
                                nzness = NZTopicOccurences
                            else:
                                nzness = (NZTopicOccurences - AUSTopicOccurences)
                            self.processedTroves.append({"issue":issue, "heading":heading,  "articleID":articleID, "topicsNZ":topicsNZ, "topicsAUS":topicsAUS, "wordCount":wordCount, "nzness":nzness})
                    end = time.clock() - start #TODO: remove this
                    print("took the following secs to process that file: " + str(end))#TODO: remove this
        return self.processedTroves



    #takes some text and updates the detectedTopics dict when it finds labels in the text
    def examineText(self, fulltext, labelToTitles):
        start = time.clock()#TODO: remove this
        detectedTopics = {}
        for eachLabel in labelToTitles:#TODO: should actually check for collisions
            for eachInstanceFound in range(fulltext.lower().count(eachLabel.lower())): #we should mark the label as detected one time for each time we count that label in the article's body text
                if self.verbose:
                    print("found the label: " + eachLabel)
                    print("which pertains to the topic titles: " + str(labelToTitles.get(eachLabel)))
                #if this topic has not been detected, we should add it to the map
                topicTitles = labelToTitles.get(eachLabel)
                for eachTopicTitle in topicTitles:
                    if eachTopicTitle not in detectedTopics:
                        detectedTopics[eachTopicTitle] = DetectedTopic(eachTopicTitle)
                    detectedTopics[eachTopicTitle].addLabel(eachLabel)
        end = time.clock() - start #TODO: remove this
        print("took the following secs to process that text: " + str(end))#TODO: remove this
        return detectedTopics




