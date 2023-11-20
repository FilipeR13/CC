def search_chunks (ips, chunks):
    result = []
    for ip, chunk in zip(ips, chunks):
        result.append((ip, chunk))
    return result 