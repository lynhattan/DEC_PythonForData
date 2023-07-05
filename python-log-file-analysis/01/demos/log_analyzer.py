from parsers import *
from collections import Counter
from operator import itemgetter
from difflib import SequenceMatcher
import matplotlib.pyplot as plt
# from pymongo import MongoClient
# from elasticsearch import Elasticsearch

def openLogFile(path):
    with open(path) as log_file:
        for log_entry in log_file:
            yield log_entry

def openEvtxFile(path):
    with evtx.Evtx(path) as log_file:
        for log_entry in log_file.records():
            yield log_entry.lxml()

def detectRundll32(path):
    log_file = openEvtxFile(path)
    for log_entry in log_file:
        try:
            log_data = parseEvtx(log_entry)
            if log_data["eid"] == "4688" and log_data["CommandLine"]:
                if "rundll32" in log_data["NewProcessName"] and re.search("powershell|cmd", log_data["ParentProcessName"]):
                    print(log_data["CommandLine"])
        except:
            pass

def getHttpByUid(path):
    r = Counter()
    log_file = openLogFile(path)
    for log_entry in log_file:
        try:
            log_data = parseZeekHttp(log_entry)
            r.update([log_data['uid']])
        except:
            pass
    return r

def detectBeacons(conn_path, http_path):
    req = getHttpByUid(http_path)
    conn_log = openLogFile(conn_path)
    beacons = []
    for log_entry in conn_log:
        try:
            log_data = parseZeekConn(log_entry)
            if log_data['service'] == "http":
                log_data['requests'] = req[log_data['uid']]
                beacons.append(log_data)
        except:
            pass

    # sort descending based on the number of requests
    beacons.sort(key=itemgetter("requests"), reverse=True)

    # display the top beacons
    header = "{:20}\t{:5}\t{:5}".format("Dst. IP", "Duration", "Requests")
    print(header)
    print("-" * len(header))
    for entry in beacons[:8]:
        print("{:20}\t{:5}\t{:5}".format(entry['dst_ip'], entry['duration'], entry['requests']))

def getDnsAnomalies(path, similar_domain="globomantics.com"):
    log_file = openLogFile(path)
    domains = Counter()
    for log_entry in log_file:
        try:
            log_data = parseZeekDns(log_entry)
            dns_query = ".".join(log_data['query'].split(".")[-2:])
            domains.update([dns_query])
        except:
            pass

    least_common = domains.most_common()[-10:]
    domain_anomalies = []
    for domain in least_common:
        anomaly = {
            "domain": domain[0],
            "occurence": domain[1],
            "similarity" : round(SequenceMatcher(None, domain[0], similar_domain).ratio() * 100)
        }
        domain_anomalies.append(anomaly)

    domain_anomalies.sort(key=itemgetter("similarity"), reverse=True)
    return domain_anomalies

def printDnsAnomalies(path):
    domains = getDnsAnomalies(path)
    print("{:20}\t{}\t{}".format("Domain", "Occurence", "Similarity"))
    print("-" * 60)
    for domain in domains:
        print("{:20}\t{}\t{}".format(domain['domain'], domain['occurence'], domain['similarity']))

def printDnsQueries(path, domain):
    log_file = openLogFile(path)
    for log_entry in log_file:
        try:
            log_data = parseZeekDns(log_entry)
            if domain in log_data['query']:
                print("{}\t{}".format(log_data["query"], log_data["answers"]))
        except:
            pass

def plotBarChart(events, users):
    plt.subplot(211)
    plt.bar(range(len(events)), list(events.values()), align="center")
    plt.xticks(range(len(events)), list(events.keys()))
    plt.subplot(212)
    plt.bar(range(len(users)), list(users.values()), align="center")
    plt.xticks(range(len(users)), list(users.keys()))
    plt.show()

def getBaseTs(ts, interval):
    # divide an hour into the interval number of sections
    interval = int(60 / interval)

    hours = ts.time().hour
    minutes = ts.time().minute

    base_minutes = int(minutes / interval) * interval
    return "{}:{}".format(hours,base_minutes)

def plotSmbActivity(path):
    log_file = openLogFile(path)
    users = Counter()
    events = Counter()
    for log_entry in log_file:
        try:
            log_data = parseSmb(log_entry)
            users.update([log_data['client_hostname']])
            ts = getBaseTs(log_data['ts'], 4)
            events.update([ts])
        except:
            pass
    plotBarChart(events, users)

def ransomwareAlert(path="logs/smb.log"):
    client = MongoClient("mongodb://localhost")
    db = client['alerts']
    col = db['smb']

    # pattern to detect common ransomware extensions in file paths
    ext_re = r"\.encrypted|\.locked|\.wncry"

    smb_log = openLogFile(path)
    for log_entry in smb_log:
        try:
            log_data = parseSmb(log_entry)
            if re.search(ext_re, log_data['path']):
                log_data['ts_added'] = dt.utcnow()
                col.insert_one(log_data)
        except:
            pass

def exportSshActivity(path="logs/auth.log"):
    es = Elasticsearch("http://localhost:9200")
    log_file = openLogFile(path)
    for log_entry in log_file:
        try:
            log_data = parseAuth(log_entry)
            es.index(index="auth", document=log_data)
        except:
            pass