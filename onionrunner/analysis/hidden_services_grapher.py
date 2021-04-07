import glob
import json
import networkx

file_list = glob.glob("/tmp/onionscan_results/*.json")

graph = networkx.DiGraph()

for json_file in file_list:

    with open(json_file,"rb") as fd:

        scan_result = json.load(fd)
        
        edges = []
        
        if scan_result['linkedSites'] is not None:
            
            edges.extend(scan_result['linkedSites'])
        
        if scan_result['relatedOnionDomains'] is not None:
            
            edges.extend(scan_result['relatedOnionDomains'])
        
        if scan_result['relatedOnionServices'] is not None:
            
            edges.extend(scan_result['relatedOnionServices'])
        
        if edges:
            
            graph.add_node(scan_result['hiddenService'],{"node_type":"Hidden Service"})
            
            for edge in edges:
                
                if edge.endswith(".onion"):
                    
                    graph.add_node(edge,{"node_type":"Hidden Service"})
                
                else:
                    
                    graph.add_node(edge,{"node_type":"Clearnet"})
            
                graph.add_edge(scan_result['hiddenService'],edge)
            
        if scan_result['ipAddresses'] is not None:
            
            for ip in scan_result['ipAddresses']:
                
                graph.add_node(ip,{"node_type":"IP"})
                
                graph.add_edge(scan_result['hiddenService'],ip)
                

networkx.write_gexf(graph, "onionscan-with-ips.gexf")