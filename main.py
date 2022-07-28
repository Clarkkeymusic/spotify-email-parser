#
#       CLARK KEY'S SPOTIFY PLAYLIST EMAIL PARSER
#
#       FOLLOW CLARK KEY   @CLARKKEYMUSIC
#       SOUNDCLOUD: https://soundcloud.com/clarkkeymusic
#       INSTAGRAM: https://www.instagram.com/clarkkeymusic/
#       TWITTER: https://twitter.com/clarkkeymusic
#

from bs4 import BeautifulSoup
import requests
import re
import csv
import time

token = ""  # Paste your Spotify Auth Token Here
keyword = input("Please enter a Genre:\n")
fieldnames = ['Name', 'Likes', 'Email', 'Creator', 'URL']
fileNames = []  # These Values are previously used keywords to prevent duplicate emails
playlistIds = []
scrapedEmails = []


def parseData(response):
    if response.get('description'):
        if response['description'].find("@") != -1:
            email = extractEmail(response['description'])
            if email is not None:
                row = {
                    'Name': response['name'],
                    'Likes': getLikeCount(response['id']),
                    'Email': email,
                    'Creator': response['owner']['display_name'],
                    'URL': response['external_urls']['spotify']
                }
                return row
    return None


def extractEmail(descripton):
    emails = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", descripton.lower())
    if len(emails) > 0:
        if emails[0] not in scrapedEmails:
            return emails[0]
    return None


def buildEndpoint(offset):
    endpoint = "https://api.spotify.com/v1/search?q= " + keyword.replace(" ",
                                                                         "%20") + "&type=playlist&limit=50&offset=" + str(
        offset)
    return endpoint


def spotifyGetPlaylist():
    totalEmails = 0
    offset = 0
    headers = {
        "Authorization": "Bearer " + token
    }
    print("Looking for all " + keyword + " playlist emails")
    with open('Emails/' + keyword + '.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        while offset <= 950:
            response = requests.get(buildEndpoint(offset), headers=headers)
            response_json = response.json()
            for playlist in response_json['playlists']['items']:
                row = parseData(playlist)
                if row is not None:
                    writer.writerow(row)
                    print("---PLAYLIST ADDED ---")
                    print(row['Name'])
                    print("--------------------")
                    totalEmails += 1
            offset += 50
    print("Total New Emails Added: " + str(totalEmails))


def getEmails():
    for fileName in fileNames:
        with open("Emails/" + fileName + ".csv", 'r') as file:
            csvreader = csv.reader(file)
            next(csvreader)
            for row in csvreader:
                if len(row[2]) != 0:
                    scrapedEmails.append(row[2])


def getLikeCount(playlistId):
    headers = {
        "Authorization": "Bearer " + token
    }
    response = requests.get("https://api.spotify.com/v1/playlists/" + str(playlistId), headers=headers)
    response_json = response.json()
    return response_json['followers']['total']


def compressFiles():
    with open('SpotifyEmails.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for fileName in fileNames:
            row = {
                'Name': "Genre: " + fileName,
            }
            writer.writerow(row)
            with open("Emails/" + fileName + ".csv", 'r') as file:
                csvreader = csv.reader(file)
                next(csvreader)
                for row in csvreader:
                    row = {
                        'Name': row[0],
                        'Likes': row[1],
                        'Email': row[2],
                        'Creator': row[3],
                        'URL': row[4]
                    }
                    writer.writerow(row)


getEmails()
spotifyGetPlaylist()
# compressFiles() Use this function if you want to compress all emails into one file,
# you have to comment out getEmails as well as spotifyGetPlaylist
