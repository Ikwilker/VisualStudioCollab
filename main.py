import requests
import credentials

#Generates Important Session information.
loginPayload = {"email":credentials.Username,"password": credentials.Password}
s = requests.Session()
r = s.post(url="https://logicinfo.atlassian.net/jsd-login/v1/authentication/authenticate", json=loginPayload)

# --------------------------------------------------------
# Script below needs to log into a logic ticket and pull ticket header, comments, and status
# Prompt user for Logic ticket number when script is ran
# --------------------------------------------------------

false = False
TicketNum = input("Please enter the Logic ticket number you want to scrape: ").upper()
idPayload = {"options":{"portal":{"id":83,"expand":["kbs","reqTypes","reqGroups","orderMapping","analyticsContext"]},"user":{"fetchRequestCounts":false},"reqDetails":{"key":str(TicketNum),"portalId":83},"branding":{"id":83},"portalId":83},"models":["portal","xsrfToken","user","reqDetails","branding"]}
ticket = s.post(url="https://logicinfo.atlassian.net/rest/servicedesk/1/customer/models", json=idPayload)
jsonTicket = ticket.json()


print(jsonTicket)