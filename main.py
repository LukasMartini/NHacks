# main.py
import asyncio
import discord
import ast

import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/classroom.student-submissions.me.readonly', 'https://www.googleapis.com/auth/classroom.announcements.readonly', 'https://www.googleapis.com/auth/classroom.courses.readonly']


TOKEN = 'ODU1NTU3MjIwMDYyNTkzMDM0.YM0NwA.yzJ44_KwVMWltw27o_Kt9PK7QY0' #discord token (replace with your own if you make your own bot)
GUILD = 'Classroom Updates Server' #server name

client = discord.Client()



def getstream():
    """Shows basic usage of the Classroom API.
    Prints the names of the first 10 courses the user has access to.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.

    course = ''
    title = ''
    description = ''
    link = ''
    type = ''
    coursename = ''

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            jsonLocation = os.path.abspath('client_secret_303424121251-hh9kpkeuihncd9ruj2tc68vp98mcv2hl.apps.googleusercontent.com.json')
            flow = InstalledAppFlow.from_client_secrets_file(jsonLocation, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('classroom', 'v1', credentials=creds)

    # Call the Classroom API
    results = service.courses().list().execute()
    courses = results.get('courses', [])

    currNewAssignments = {}
    currNewAnnouncements = {}

    currNewAssignmentsSansEmoji = {}
    currNewAnnouncementsSansEmoji = {}

    for each in courses:
        eatChit = each.get('id')
        resultsAssignments = service.courses().courseWork().list(courseId=str(eatChit)).execute()
        resultsAssignments = resultsAssignments.get('courseWork', [])

        #we still need title, description, and access link

        try:
            currNewAssignments[each.get('name')] = [resultsAssignments[0].get('id'), resultsAssignments[0].get('title'), resultsAssignments[0].get('description'), resultsAssignments[0].get('alternateLink')]
            currNewAssignmentsSansEmoji[each.get('name')] = [resultsAssignments[0].get('id')]
        except IndexError:
            pass


        resultsAnnouncements = service.courses().announcements().list(courseId=str(eatChit)).execute()
        resultsAnnouncements = resultsAnnouncements.get('announcements', [])

        try:
            currNewAnnouncements[each.get('name')] = [resultsAnnouncements[0].get('id'), resultsAnnouncements[0].get('text')]
            currNewAnnouncementsSansEmoji[each.get('name')] = [resultsAnnouncements[0].get('id')]
        except IndexError:
            pass

    print(currNewAssignments)
    print(currNewAnnouncements)
    if os.path.exists('PrevA&A.txt'):
        with open('PrevA&A.txt', 'r') as paa:
            information = paa.read()
            information = information.split('}')
            currOldAssignments = information[0] + '}'
            currOldAnnouncements = information[1] + '}'

            currOldAssignments = ast.literal_eval(currOldAssignments)
            currOldAnnouncements = ast.literal_eval(currOldAnnouncements)

            for each in currNewAssignments.keys():
                if currOldAssignments.get(each)[0] != currNewAssignments.get(each)[0]:
                    course = currNewAssignments.get(each)[0]
                    title = currNewAssignments.get(each)[1]
                    description = currNewAssignments.get(each)[2]
                    link = currNewAssignments.get(each)[3]
                    type = 'ass'
                    coursename = each

            for each in currNewAnnouncements.keys():
                if currOldAnnouncements.get(each)[0] != currNewAnnouncements.get(each)[0]:
                    course = currNewAnnouncements.get(each)[0]
                    title = currNewAnnouncements.get(each)[1]
                    type = 'ann'
                    coursename = each

            paa.close()

        with open('PrevA&A.txt', 'w') as paa:
            paa.truncate(0)
            try:
                paa.write(str(currNewAssignments))
            except UnicodeEncodeError:
                paa.write(str(currNewAssignmentsSansEmoji))

            try:
                paa.write(str(currNewAnnouncements))
            except UnicodeEncodeError:
                paa.write(str(currNewAnnouncementsSansEmoji))

    else:
        with open('PrevA&A.txt', 'w') as paa:
            try:
                paa.write(str(currNewAssignments))
            except UnicodeEncodeError:
                paa.write(str(currNewAssignmentsSansEmoji))

            try:
                paa.write(str(currNewAnnouncements))
            except UnicodeEncodeError:
                paa.write(str(currNewAnnouncementsSansEmoji))

    #if you want to adjust formating you can do it here

    if type == 'ass':
        return ['***' + str(title) + '***\n\n' + str(description) + '\n\n' + str(link), course, coursename]
    elif type == 'ann':
        return ['***' + str(title) + '***', course, coursename]
    else: return ['', '', '']



@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})\n'
    )
    print(guild.text_channels)
    print(guild.roles)

while True:
    async def timer():

        await client.wait_until_ready()
        previous_message = ''
        science = client.get_channel(855600297980329994) #replace these with whatever channel id's you need; the program automatically prints off the channel ids to the server it connects to
        history = client.get_channel(855600430247575602)
        general = client.get_channel(855558887611695127)
        messagesend = ''
        coursename = ''
        while True:

            messagecourse = getstream()
            message = messagecourse[0]
            coursename = messagecourse[2]

            if previous_message != message and message != '':
                messagesend = message
                messagesend = str(coursename) + '\n\n' + messagesend
                if coursename == 'IB Physics SL': #replace with the course name of the specific ones
                    messagesend = messagesend + '\n<@&855602710714515486>' #replace with the role id (if you want that) (itll print those as well)
                    await science.send(messagesend) #change to whichever channel you want it to send to
                elif coursename == 'HZT4U7a Theory Of Knowledge':
                    messagesend = messagesend + '\n<@&855602278794395668>'#replace with the role id (if you want that)
                    await history.send(messagesend)#change to whichever channel you want it to send to
                else:
                    await general.send(messagesend)#change to whichever channel you want it to send to
            previous_message = message
            subject = ''
            await asyncio.sleep(100) #timer inbetween checks (in seconds)

    client.loop.create_task(timer())
    client.run(TOKEN)
