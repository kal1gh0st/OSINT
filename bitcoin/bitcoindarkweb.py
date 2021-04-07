import argparse
import requests
import networkx

webhose_access_token = ""

blacklist = ["4a6kzlzytb4ksafk.onion","blockchainbdgpzk.onion"]

webhose_base_url    = "http://webhose.io"
webhose_darkweb_url = "/darkFilter?token=%s&format=json&q=" % webhose_access_token

block_explorer_url  = "https://blockexplorer.com/api/addrs/"
#?from=0&to=50

parser = argparse.ArgumentParser(description='Collect and visualize Bitcoin transactions and any related hidden services.')

parser.add_argument("--graph",help="Output filename of the graph file. Example: bitcoin.gexf",default="bitcoingraph.gexf")
parser.add_argument("--address", help="A bitcoin address to begin the search on.",)


args = parser.parse_args()

bitcoin_address = args.address
graph_file      = args.graph

# 
# Retrieve all bitcoin transactions for a Bitcoin address
#
def get_all_transactions(bitcoin_address):
    
    transactions = []
    from_number  = 0
    to_number    = 50
    
    block_explorer_url_full = block_explorer_url + bitcoin_address + "/txs?from=%d&to=%d" % (from_number,to_number)
    
    response = requests.get(block_explorer_url_full)
    
    try:
        results  = response.json()
    except:
        print "[!] Error retrieving bitcoin transactions. Please re-run this script."
        return transactions

    if results['totalItems'] == 0:
        print "[*] No transactions for %s" % bitcoin_address
        return transactions

    transactions.extend(results['items'])
    
    while len(transactions) < results['totalItems']:
        
        from_number += 50
        to_number   += 50
    
        block_explorer_url_full = block_explorer_url + bitcoin_address + "/txs?from=%d&to=%d" % (from_number,to_number)
        
        response = requests.get(block_explorer_url_full)
            
        results  = response.json()        
    
        transactions.extend(results['items'])
    
    print "[*] Retrieved %d bitcoin transactions." % len(transactions)
    
    return transactions

#
# Simple function to return a list of all unique
# bitcoin addresses from a transaction list
#
def get_unique_bitcoin_addresses(transaction_list):
    
    bitcoin_addresses = []
    
    for transaction in transaction_list:
        
        # check the sending address
        if transaction['vin'][0]['addr'] not in bitcoin_addresses:
            bitcoin_addresses.append(transaction['vin'][0]['addr'])
        
        # walk through all recipients and check each address
        for receiving_side in transaction['vout']:
            
            if receiving_side['scriptPubKey'].has_key("addresses"):
                
                for address in receiving_side['scriptPubKey']['addresses']:
                    
                    if address not in bitcoin_addresses:
                        
                        bitcoin_addresses.append(address)
    
    print "[*] Identified %d unique bitcoin addresses." % len(bitcoin_addresses)
    
    return bitcoin_addresses


#
# Search Webhose.io for each bitcoin address
#
def search_webhose(bitcoin_addresses):
    
    bitcoin_to_hidden_services = {}
    count = 1
    
    for bitcoin_address in bitcoin_addresses:
        
        print "[*] Searching %d of %d bitcoin addresses." % (count,len(bitcoin_addresses))
        
        # search for the bitcoin address
        search_url = webhose_base_url + webhose_darkweb_url + bitcoin_address
        
        response   = requests.get(search_url)
        
        result     = response.json()
       
        # loop continually until we have retrieved all results at Webhose
        while result['totalResults'] > 0:
            
            # now walk each search result and map out the unique hidden services
            for search_result in result['darkposts']:
                
                if not bitcoin_to_hidden_services.has_key(bitcoin_address):
                    bitcoin_to_hidden_services[bitcoin_address] = []
                
                if search_result['source']['site'] not in bitcoin_to_hidden_services[bitcoin_address]:
                    
                    bitcoin_to_hidden_services[bitcoin_address].append(search_result['source']['site'])
            
            # if we have 10 or less results no need to ding the API again
            if result['totalResults'] <= 10:
                break
            
            # build a filtering keyword string
            query = "%s" % bitcoin_address
            
            for hidden_service in bitcoin_to_hidden_services[bitcoin_address]:
                query += " -site:%s" % hidden_service
            
            # use the blacklisted onions as filters
            for hidden_service in blacklist:
                query += " -site:%s" % hidden_service
            
            search_url = webhose_base_url + webhose_darkweb_url + query
            
            response     = requests.get(search_url)
            
            result     = response.json()
        
        if bitcoin_to_hidden_services.has_key(bitcoin_address):        
            print "[*] Discovered %d hidden services connected to %s" % (len(bitcoin_to_hidden_services[bitcoin_address]),bitcoin_address)
        
        count += 1
    
    return bitcoin_to_hidden_services

#
# Graph all of the Bitcoin transactions
#
def build_graph(source_bitcoin_address,transaction_list,hidden_services):
    
    graph = networkx.DiGraph()
    
    # graph the transactions by address
    for transaction in transaction_list:
        
        # check the sending address
        sender = transaction['vin'][0]['addr']
    
        if sender == source_bitcoin_address:
            graph.add_node(sender,{"type":"Target Bitcoin Address"})
        else:
            graph.add_node(sender,{"type":"Bitcoin Address"})
        
      
        # walk through all recipients and check each address
        for receiving_side in transaction['vout']:
    
            if receiving_side['scriptPubKey'].has_key("addresses"):
                for address in receiving_side['scriptPubKey']['addresses']:
                    
                    if address == source_bitcoin_address:
                        graph.add_node(address,{"type":"Target Bitcoin Wallet"})
                    else:
                        graph.add_node(address,{"type":"Bitcoin Wallet"})
                    
                    graph.add_edge(sender,address)
        
    for bitcoin_address in hidden_services:
        
        for hidden_service in hidden_services[bitcoin_address]:
            
            if hidden_service not in blacklist:
                graph.add_node(hidden_service,{"type":"Hidden Service"})
                graph.add_edge(bitcoin_address,hidden_service)
    
    
    # write out the graph
    networkx.write_gexf(graph,graph_file)
    
    return


# get all of the bitcoin transactions  
print "[*] Retrieving all transactions from the blockchain for %s" % bitcoin_address

transaction_list = get_all_transactions(bitcoin_address)

if len(transaction_list) > 0:
    
    # get all of the unique bitcoin addresses
    bitcoin_addresses = get_unique_bitcoin_addresses(transaction_list)
    
    # now search Webhose for all addresses looking
    # for hidden services
    hidden_services   = search_webhose(bitcoin_addresses)

    # graph the bitcoin transactions
    build_graph(bitcoin_address,transaction_list, hidden_services)
    
    print "[*] Done! Open the graph file and happy hunting!"
