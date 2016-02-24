__author__ = 'user'

#a topic that has been found in the text.
class DetectedTopic:

    def __init__(self, topicTitle):
        self.topicTitle = topicTitle
        self.labels = {}
        self.occurencesCount = 0

    #we add all of the labels used to find this topic title in the text to a map that is labelText --> label found count
    def addLabel(self, labelText):
        #if this label was already detected, just add 1 to its count
        if labelText in self.labels:
            self.labels[labelText] = self.labels[labelText] + 1
            self.occurencesCount += 1
        #if this is the first time that this label was detected, add it to the map
        else:
            self.labels[labelText] = 1
            self.occurencesCount += 1



