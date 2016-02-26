__author__ = 'user'

from melon import Farmer
from DetectedTopic import DetectedTopic
import os
import time

#a text processor that creates and maintains DetectedTopics as it goes
class WordBagger:

    def __init__(self, labelToTitlesAUS, labelToTitlesNZ, verbose=True):
        self.processedTroves = []
        self.verbose = verbose
        self.farmer = Farmer()
        #these are for seeing which detected topic to increment the count of when labels detected in the text
        self.labelToTitlesAUS = labelToTitlesAUS
        self.labelToTitlesNZ = labelToTitlesNZ
        #these are the labels sorted by length in chars (descending order). These are to help us avoid collisions.
        #E.g. we search for "Islands" before we search for "Island". Once we have counted all occurences of "Islands"
        #we replace all of those occurences with a blocking character "|" so that when we search for "Island", we don't
        #count occurences of the string "Islands"
        labelsListAUS = list(labelToTitlesAUS.keys())
        labelsListAUS.sort(key=len, reverse=True)
        self.allLabelsAUS = labelsListAUS
        labelsListNZ = list(labelToTitlesNZ.keys())
        labelsListNZ.sort(key=len, reverse=True)
        self.allLabelsNZ = labelsListNZ






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
                            detectedTopicsAUS = self.examineText(articleDict["fulltext"], self.labelToTitlesAUS, self.allLabelsAUS)
                            detectedTopicsNZ = self.examineText(articleDict["fulltext"], self.labelToTitlesNZ, self.allLabelsNZ)#TODO: should really just make one call and pass both dctionaries as it is more efficient that way
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
                            nztotal = NZTopicOccurences
                            #calculate some nzness measure #TODO: this is kinda experimental. this should be externalised to another method when i figure out what relatedness is
                            if AUSTopicOccurences == 0:  #at the moment an article loses relatedness if there are lots of australian topics present and if it is very long. But it doesn't lose much.
                                nzness = NZTopicOccurences
                            else:
                                nzness = (NZTopicOccurences - (AUSTopicOccurences / 4) - (len(articleDict["fulltext"])/ 1000))
                            self.processedTroves.append({"issue":issue, "heading":heading,  "articleID":articleID, "topicsNZ":topicsNZ, "topicsAUS":topicsAUS, "wordCount":wordCount, "nzness":nzness, "nztotal":nztotal})
                    end = time.clock() - start #TODO: remove this
                    print("took the following secs to process that file: " + str(end))#TODO: remove this
        return self.processedTroves



    #takes some text and updates the detectedTopics dict when it finds labels in the text
    def examineText(self, fulltext, labelToTitles, allLabels):
        start = time.clock()#TODO: remove this
        fulltextLowered = fulltext.lower()
        detectedTopics = {}
        for eachLabel in allLabels:
            labelOccurencesCount = fulltextLowered.count(eachLabel.lower())
            for eachInstanceFound in range(labelOccurencesCount): #we should mark the label as detected one time for each time we count that label in the article's body text#TODO: consider passing count of detections as an arg to the addLabel method or something rather than just looping over add behaviour. maybe not tho, would need to add if block to check whether count > 0 for purposes of calling remove() etc so watev
                if self.verbose:
                    print("found the label: " + eachLabel)
                    print("which pertains to the topic titles: " + str(labelToTitles.get(eachLabel)))
                #if this topic has not been detected, we should add it to the map
                #NOTE: that at the moment this accomodates each label mapping to an arbitrary amount of topics.
                topicTitles = labelToTitles.get(eachLabel)
                for eachTopicTitle in topicTitles:
                    if eachTopicTitle not in detectedTopics:
                        detectedTopics[eachTopicTitle] = DetectedTopic(eachTopicTitle)
                    detectedTopics[eachTopicTitle].addLabel(eachLabel)
            #if we found the label at least once, we should remove all of its occurences to stop collisions with shorter labels
            fulltextLowered = fulltextLowered.replace(eachLabel.lower(), "|", labelOccurencesCount)



        end = time.clock() - start #TODO: remove this
        print("took the following secs to process that text: " + str(end))#TODO: remove this
        return detectedTopics




