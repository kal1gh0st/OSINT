import glob
import json
import shodan
import time

shodan_client = shodan.Shodan("YOURKEY")

file_list = glob.glob("/tmp/onionscan_results/*.json")

ssh_key_list = []
key_to_hosts = {}

for json_file in file_list:

    with open(json_file,"rb") as fd:

        scan_result = json.load(fd)

        if scan_result['sshKey']:
            print "%s => %s" % (scan_result['hiddenService'],scan_result['sshKey'])
            
            if key_to_hosts.has_key(scan_result['sshKey']):
                key_to_hosts[scan_result['sshKey']].append(scan_result['hiddenService'])
            else:
                key_to_hosts[scan_result['sshKey']] = [scan_result['hiddenService']]
            
for ssh_key in key_to_hosts:
    
    if len(key_to_hosts[ssh_key]) > 1:
        
        print "[!] SSH Key %s is used on multiple hidden services." % ssh_key
        
        for key in key_to_hosts[ssh_key]:
            
            print "\t%s" % key           
    
    while True:
    
        try:
            
            shodan_result = shodan_client.search(ssh_key)
            break
        except:
            time.sleep(5)
            pass
        
    if shodan_result['total'] > 0:
        
        for hit in shodan_result['matches']:
            print "[!] Hit for %s on %s for hidden services %s" % (ssh_key,hit['ip_str'],",".join(key_to_hosts[ssh_key]))

