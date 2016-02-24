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
    busyFarmer = Farmer()
    busyFarmer.write_json(troves, "1860wholeyear.json")





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