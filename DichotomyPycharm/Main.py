__author__ = 'user'
import csv
from collections import defaultdict
from melon import Farmer
import yaml
from WordBagger import WordBagger
import re


PATH_TO_CSVAUS = "C:\\gitRepos\\TopicLabelsGit\\onlyTitlesAus23rd.csv"
PATH_TO_CSVNZ = "C:\\gitRepos\\TopicLabelsGit\\onlyTitles19th.csv"
PATH_TO_TROVE_JSON = "I:\\TAS\\10\\1860\\"
PATH_TO_SETTINGS_YML = "settings.yml"
OUTPUT_NAME = "graph.csv"#needs ".json"
CSV_OUTPUT_NODES_NAME = "nodes1860.csv"
CSV_OUTPUT_EDGES_NAME = "edges1860.csv"


def main():
    #read the csv from file
    rowsAUS = loadCSV(PATH_TO_CSVAUS)
    rowsNZ = loadCSV(PATH_TO_CSVNZ)
    #create the dict
    with open(PATH_TO_SETTINGS_YML, "r", encoding="utf-8") as fileStream:
        settings = yaml.load(fileStream)
    labelToTitlesAUS = generateDict(rowsAUS, settings)
    labelToTitlesNZ = generateDict(rowsNZ, settings)
    #create the word bagger and set it off
    wordBagger = WordBagger(labelToTitlesAUS, labelToTitlesNZ, verbose=False)
    troves = wordBagger.processFiles(PATH_TO_TROVE_JSON)
    #let's sort it so that really relevant articles are at the top...
    troves.sort(key=lambda x: x["nzness"], reverse=True)
    #write our result back to file
    outputAsCSV(troves, labelToTitlesAUS, labelToTitlesNZ, OUTPUT_NAME)


#used to output as csv for gephi rather than in the standard, json form
def outputAsCSV(troves, labelToTitlesAUS, labelToTitlesNZ, outputName):
    #for the csv outputs, we need to convert the list of dicts into a list of lists where each element in list 1 is a Trove article and each element in list 2 is info on that article
    farmer = Farmer()

    #form the nodes csv
    nodes = []
    for eachTrove in troves:
        nodeID = eachTrove["articleID"]
        title =  eachTrove["heading"]
        nodetype = "trove"
        nodes.append([nodeID, title, nodetype])
    # for eachTopic in labelToTitlesAUS.keys():
    #     nodeID = int.from_bytes(eachTopic.encode("utf-8"), "little")#TODO: just using int version of title as node id. POTENTIAL collision with trove id nodes
    #     title =  eachTopic
    #     nodetype = "topic1"
    #     nodes.append([nodeID, title, nodetype])
    for eachTopic in labelToTitlesNZ.keys():
        nodeID = int.from_bytes(eachTopic.encode("utf-8"), "little")#TODO: just using int version of title as node id. POTENTIAL collision with trove id nodes
        title =  eachTopic
        nodetype = "topic2"
        nodes.append([nodeID, title, nodetype])

    #form the edges csv
    #note that building the edges is a little ugly because we are just using the information which
    #was structured to be written as json.
    edges = []
    edgeIDIndex = 0
    for eachTrove in troves:
        # for eachTopic1RelationDict in eachTrove["topicsAUS"]:
        #    for eachRelation in eachTopic1RelationDict.keys(): #NOTE: there is only ONE entry per dict. Should consider storing these internally as tuples and then just converting that to a dict if/when writing as json.
        #        edgeIDIndex += 1
        #        source = eachTrove["articleID"]
        #        target = int.from_bytes(eachRelation.encode("utf-8"), "little")
        #        weight = eachTopic1RelationDict[eachRelation]
        #        edges.append([edgeIDIndex, source, target, weight])
        for eachTopic2RelationDict in eachTrove["topicsNZ"]:
           for eachRelation in eachTopic2RelationDict.keys():
               edgeIDIndex += 1
               source = eachTrove["articleID"]
               target = int.from_bytes(eachRelation.encode("utf-8"), "little")
               weight = eachTopic2RelationDict[eachRelation]
               edges.append([edgeIDIndex, source, target, weight])

    #write the nodes and edges to file
    farmer.list_to_csv(nodes, CSV_OUTPUT_NODES_NAME)
    farmer.list_to_csv(edges, CSV_OUTPUT_EDGES_NAME)


def outputAsJSON(troves, outputName):
    farmer = Farmer()
    farmer.write_json(troves, outputName)

## v v v SOME FUNCTIONS TO CREATE THE DICT WE NEED FOR THE WordBagger FROM OUR JAVA GENERATED CSV

#takes a path to a csv file and returns a list of dicts (one for each row)
def loadCSV(filePath):
    with open(filePath, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="|")
        rows = [row for row in reader]
    return rows


#takes a list of dicts and returns a defaultdict that is labelText --> set of possible topic titles
def generateDict(csvRows, settings):
    labelToTitles = defaultdict(list)
    for eachRow in csvRows:
        # in here you should use a yml file of regex rules to filter out e.g. labels that are 1 char long, labels that are just a year e.g. 1960 etc. MAYBE FILTER OUT THE LABELS THAT MAP TO A HUGE AMOUNT OF TOPICS OR ELSE KEEP THEM.
        if not any(re.match(eachRegex, eachRow["label"]) for eachRegex in settings["blacklistLabels"]):
            labelToTitles[eachRow["label"]].append(eachRow["topic"])
    return labelToTitles



if __name__ == "__main__":
    main()
   #this readTrove call needs to return an iterable of all of the dicts
    # farmer = Farmer()
    # dicts = farmer.readTrove("I:\\TAS\\10\\1920\\04\\03\\issue-103169.json")
    # for each in dicts:
    #     print(each)
    #     print(each["heading"])