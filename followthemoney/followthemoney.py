import requests
import json
import argparse
import csv
import urllib
import os

ap = argparse.ArgumentParser()
ap.add_argument("-c","--company",    required=True,help="Pass in the exact corporate name to search for.")
ap.add_argument("-j","--jurisdiction", required=True,help="Pass in a two character jurisdiction code.")
ap.add_argument("-t","--timeline",     required=True,help="Timeline file, will create if doesn't exist or add to existing spreadsheet.")


args = vars(ap.parse_args())

company       = args['company']
jurisdiction  = args['jurisdiction']
timeline_file = args['timeline']

#
# Do an initial corporate search
#
def corporation_search(corporation,jurisdiction):
    
    url  = "https://api.opencorporates.com/v0.4/companies/search?q=%s" % urllib.quote(corporation)
    url += "&jurisdiction_code=%s" % jurisdiction
            
    response = requests.get(url)
    
    if response.status_code == 200:
        
        result = json.loads(response.content)
        
        for company in result['results']['companies']:
            
            if corporation.lower() == company['company']['name'].lower():
                
                return company['company']['company_number'], company['company']['name']
                
   
    return None,None   

#
# Retrieve corporate filings
#
def corporate_filings(corporation_id,jurisdiction):
    
    api_url = "https://api.opencorporates.com/v0.4/companies/%s/%s/filings" % (jurisdiction,corporation_id)
    
    response = requests.get(api_url)
    
    filings = []
    
    if response.status_code == 200:
        
        result = json.loads(response.content)

        filings.extend(result['results']['filings'])

        # iterate over all filings
        total_pages = result['results']['total_pages']
        count       = 2
        
        while count <= total_pages:
            
            url = api_url + "?page=%d" % count
            
            response = requests.get(url)
            
            if response.status_code == 200:
                
                result = json.loads(response.content)
                
                filings.extend(result['results']['filings'])
                
            count += 1
            
        print "[*] Retrieved %d filing records." % len(filings)
        
        return filings

    return None

#
# Build a timeline using the TimelineJS template
# 
def build_timeline(filings,corporate_name):
    
    fields = [
        'Year', 'Month', 'Day', 'Time', 'End Year', 
        'End Month', 'End Day', 'End Time', 'Display Date', 
        'Headline', 'Text', 'Media', 'Media Credit', 'Media Caption', 
        'Media Thumbnail', 'Type', 'Group', 'Background'] 
    
    if not os.path.exists(timeline_file):
        write_header = True
    else:
        write_header = False
    
    with open(timeline_file,"ab") as output:
        
        writer = csv.DictWriter(output,fieldnames=fields)
        
        if write_header is True:
            writer.writeheader()
        
        
        # add each corporate filing to the spreadsheet
        for filing in filings:
            
            year,month,day = filing['filing']['date'].split("-")
            
            record = {}
            record['Year']  = year
            record['Month'] = month
            record['Day']   = day
            
            record['Display Date'] = filing['filing']['date']
            record['Headline']     = "%s - %s" % (corporate_name,filing['filing']['title'])
            record['Text']         = "View record <a href='%s'>here</a>" % filing['filing']['opencorporates_url']
            record['Group']        = corporate_name
            
            writer.writerow(record)
            
        
        print "[*] Added records to spreadsheet: %s" % timeline_file


        return
    
# find the company
corporate_id,corporate_name = corporation_search(company,jurisdiction)

if corporate_id is not None:

    # extract all filings
    filings = corporate_filings(corporate_id,jurisdiction)

    # build a timeline
    build_timeline(filings,corporate_name)
else:
    print "[!!!] Failed to retrieve corporation. Please check the name."