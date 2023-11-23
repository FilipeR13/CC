weight_RTT = 0.6
weight_PacketLoss = 0.4

# calculate load of an ip. Bigger means slower
def calculate_load (info_ip, max_rtt):
    RTT = (info_ip[0] / info_ip[1]) / max_rtt
    PacketLoss = 1 - info_ip[2] / info_ip[1]
    return (RTT * weight_RTT) + (PacketLoss * weight_PacketLoss)

# obtain rate between the slower and the faster node
def ratio_bettewen_nodes (load1, load2):
    slower = load1 if load1 > load2 else load2
    faster = load1 if load1 < load2 else load2
    return slower / faster

def best_chunk_distribution (result, ips, info_nodes, max_rtt):
    current_ip = ips[0]
    info_ip = info_nodes.get(current_ip)
    current_load = calculate_load(info_ip, max_rtt)
    for ip in ips[1:]:
        info_ip = info_nodes.get(ip)
        load = calculate_load(info_ip, max_rtt)
        print (f"load: {load} |||current_load: {current_load}")
        length_current_ip = len(result.get(current_ip))
        length_ip = len(result.get(ip))
        # if ip is slower than current and have more chunks, ignore it
        if load > current_load and length_ip > length_current_ip:
            continue
        # if ip is faster than current and have less chunks, send the chunk to it
        if load <= current_load and length_ip < length_current_ip:
            current_ip = ip
            current_load = load
        else:
            ratio = ratio_bettewen_nodes(load, current_load)

            ratio_chunk_fst_ip = length_current_ip + 1 / length_ip
            ratio_chunk_snd_ip = length_ip + 1 / length_current_ip
            # if the ration between length of adding a chunk to the ip is more closer to the ratio between the loads, send the chunk to it
            if abs (ratio_chunk_fst_ip - ratio) > abs (ratio_chunk_snd_ip - ratio):
                current_ip = ip
                current_load = load
    return current_ip
# return best ip to send the chunk. If all ips are new, MSS_SEND = 0, return the first one
def best_ip_not_used (ips, info_nodes, max_rtt):
    best_ip = ips[0]
    info_ip = info_nodes.get(best_ip)
    best_load = calculate_load(info_ip, max_rtt) if info_ip[1] != 0 else 2
    for ip in ips[1:]:
        info_ip = info_nodes.get(ip)
        # If MSS_SEND is 0 dont send to this ip because it is already in the process of receiving a chunk
        if info_ip[1] != 0:
            load = calculate_load(info_ip, max_rtt)
            if load < best_load and load != 0:
                best_load = load
                best_ip = ip
    return best_ip

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

def get_ip_with_less_chunks (result, ips, info_nodes):  
    best_ip = ips[0]
    best_chunks = len(result.get(best_ip))
    for ip in ips[1:]:
        chunks = len(result.get(ip))
        if chunks < best_chunks:
            best_chunks = chunks
            best_ip = ip
    return best_ip

def choose_ip (result, ips, info_nodes, max_rtt):
    ip = None
    ips_not_used = check_repeated(result, ips)
    # if there is an ip not used, send the chunk to it
    if ips_not_used:
        ip = best_ip_not_used(ips_not_used, info_nodes, max_rtt)
        result[ip] = []
    else:
        ips_not_new = [ip for ip in ips if info_nodes.get(ip)[1] != 0]
        if ips_not_new:
            ip = best_chunk_distribution(result,ips_not_new, info_nodes, max_rtt)
        # if all ips are new, send the chunk to the one with less chunks
        else:
            ip = get_ip_with_less_chunks(result, ips, info_nodes)
    return ip

def search_chunks (chunks_ips, info_nodes, max_rtt):
    # result is a dict (ips,[chunks])... each chunk appears only once
    result = {}
    for chunk, ips in chunks_ips.items():
        # if exists an ip unknown, send the chunk to it and create a new entry in info_nodes
        ip_unknown = check_for_unknown(ips, info_nodes)
        if ip_unknown:
            result[ip_unknown] = [chunk]
            info_nodes[ip_unknown] = [0,0,0]
        else:
            ip = choose_ip(result, ips, info_nodes, max_rtt)
            result[ip].append(chunk)
    return result 
