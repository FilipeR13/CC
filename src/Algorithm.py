weight_RTT = 0.6
weight_PacketLoss = 0.4

def calculate_load (RTT, PacketLoss):
    return (RTT * weight_RTT) + (PacketLoss * weight_PacketLoss)

# return best ip to send the chunk. If all ips are new, MSS_SEND = 0, return the first one
def best_ip (ips, info_nodes, max_rtt):
    best_ip = None
    best_load = 2
    for ip in ips:
        info_ip = info_nodes.get(ip)
        # If MSS_SEND is 0 dont send to this ip because it is already in the process of receiving a chunk
        if info_ip[1] != 0:
            load = calculate_load((info_ip[0] / info_ip[1]) / max_rtt,1 - info_ip[1] / info_ip[2])
            if load < best_load and load != 0:
                best_load = load
                best_ip = ip
    return best_ip if best_ip else ips[0]

# check for ips that its not being used by any other chunk
def check_repeated (result, ips):
    ips_not_used = []
    for ip in ips:
        if ip not in result:
            ips_not_used.append(ip)
    return ips_not_used 

def check_for_unknown (ips, info_nodes):
    for ip in ips:
        if info_nodes.get(ip) == None:
            return ip
    return None

def search_chunks (chunks_ips, info_nodes, max_rtt):
    # result is a dict (ips,[chunks])... each chunk appears only once
    result = {}
    for chunk, ips in chunks_ips.items():
        ip_unknown = check_for_unknown(ips, info_nodes)
        if ip_unknown:
            result[ip_unknown] = [chunk]
            info_nodes[ip_unknown] = (0,0,0)
        else:
            ips_not_used = check_repeated(result, ips)
            if ips_not_used:
                best_ip = best_ip(ips_not_used, info_nodes, max_rtt)
                result[best_ip] = [chunk]
            else:
                best_ip = best_ip(ips, info_nodes, max_rtt)
                result[best_ip].append(chunk)
    return result 