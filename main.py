import requests
import credentials
import os.path
import json

#Generates Important Session information.
loginPayload = {"email":credentials.Username,"password":credentials.Password}
print("Logging in...")
s = requests.Session()
r = s.post(url="https://logicinfo.atlassian.net/jsd-login/v1/authentication/authenticate", json=loginPayload)
print(f"Logged in. {r.status_code}")

dbFile = r'storage.json'

# ------------------------------------------------------------------------------------------------------------------------------------------
# TODO: Check if Logic Portal has Updated from last check (Backend DB/file maybe?)
# TODO: IF logic ticket has been updated, Update Jira ticket.
# TODO: Ignore System Messages (Ticket update comments.)
# TODO: Possibly add parameters for script to do multiple things. (IE. Count, Only check for updates, full auto, print specific ticket.)
# ------------------------------------------------------------------------------------------------------------------------------------------
# URL to hit most things, if not everything. 
logicAPIUrl ="https://logicinfo.atlassian.net/rest/servicedesk/1/customer/models"


#Known useful ID's = 6/Closed, 10403/Waiting for Logic, 10404/Waiting for Customer
# Things to update in this payload for the script. selectedPage, statusFilters.
logicRequestPayload = {"options":{"allReqFilter":{"selectedPage":1,"filter":"","reporter":"all","status":"","statusFilters":[],"statuses":["open"],"requestTypeFilters":[]}},"models":["xsrfToken","allReqFilter"]}
refinedStatusPayload = {"options":{"allReqFilter":{"selectedPage":1,"filter":"","reporter":"all","status":"","statusFilters":[{"portalId":"83","statusInfo":[{"statusId":"10404"}]}],"statuses":[],"requestTypeFilters":[]}},"models":["allReqFilter","xsrfToken"]}
detailedTicketPayload = {"options":{"reqDetails":{"portalId":83,"key":"GEN-133"},"portalId":83},"models":["reqDetails"]}

# Logic Count Function, Used to count how many tickets per status there are.
def logicCount():
    idList = (10404, 10403, 6)
    for i in range(len(idList)):
        currentId = idList[i]
        refinedPayload = {"options":{"allReqFilter":{"selectedPage":1,"filter":"","reporter":"all","status":"","statusFilters":[{"portalId":"83","statusInfo":[{"statusId":str(currentId)}]}],"statuses":[],"requestTypeFilters":[]}},"models":["allReqFilter","xsrfToken"]}
        ticket = s.post(url = logicAPIUrl, json = refinedPayload)
        jsonTicket = ticket.json()

        if currentId == 6:
            ticketType = "Closed"
        elif currentId == 10403:
            ticketType = "Waiting for Logic"
        elif currentId == 10404:
            ticketType = "Waiting for Customer"
        totalTickets = jsonTicket["allReqFilter"]["totalResults"]
        print(f"{totalTickets} ticket(s) are {ticketType}")

def getBaseLogicTicket():
    ticket = s.post(url=logicAPIUrl, json=logicRequestPayload)
    jsonTicket = ticket.json()["allReqFilter"]

    # for i in range(1, int(jsonTicket["allReqFilter"]["totalPages"] + 1)):
    #     selectedPage = i
    #     logicPageRequest = {"options":{"allReqFilter":{"selectedPage":selectedPage,"filter":"","reporter":"all","status":"","statusFilters":[],"statuses":["open"],"requestTypeFilters":[]}},"models":["xsrfToken","allReqFilter"]}
    #     newTicket = s.post(url=logicAPIUrl, json=logicPageRequest)
    #     print(len(newTicket.json()["allReqFilter"]["requestList"]))

    dbExists = os.path.exists(dbFile)
    if dbExists == True:
        with open(dbFile, "r", encoding= "utf-8") as jsonFile:
            info = json.load(jsonFile)
            for i in range(len(jsonTicket["requestList"])):
                refinedTicketJson = jsonTicket["requestList"][i]
                print(refinedTicketJson["key"])
                ticketId = refinedTicketJson["key"]
                ticketStatus = refinedTicketJson["status"]
                ticketSummary = refinedTicketJson["summary"] 
                if jsonTicket["requestList"][i]["key"] not in info:
                    updateBackendStorage(ticketId, ticketStatus, ticketSummary)
    else:
        createBackendStorage(jsonTicket["requestList"][1]["key"],jsonTicket["requestList"][1]["status"],jsonTicket["requestList"][1]["summary"])

#Updates Backend File with new information
def updateBackendStorage(id, status, summary):
    jsonFile = open(dbFile, "r")
    currentFile = json.load(jsonFile)
    jsonFile.close()
    currentFile[id] = {
                "JiraTicketID": "",
        "LogicTicketID": id,
        "Status": status,
        "Summary": summary,
        "Comments": []
    }
    currentJson = open(dbFile, "w")
    json.dump(currentFile, currentJson, indent=4, separators= (", ", ": "))
    currentJson.close() 

#Creates if no file found.
def createBackendStorage(id, status, summary):
    backendOutput = {
        id: {
            "JiraTicketID": "",
            "LogicTicketID": id,
            "Status": status,
            "Summary": summary,
            "Comments": [

            ]
        }
    }
    formatted_json = json.dumps(
        backendOutput,
        indent=4,
        separators= (", ", ": "),
    )
    print(formatted_json)
    with open(dbFile, "w+", encoding= 'utf-8') as file:
        file.write(formatted_json)

#logicCount()
getBaseLogicTicket()
#ticket = s.post(url=logicAPIUrl, json=detailedTicketPayload)
#print(ticket.json())
