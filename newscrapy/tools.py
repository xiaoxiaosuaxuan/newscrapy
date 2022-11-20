from datetime import datetime, timedelta 

def dateGen(start, end, format):
    start = datetime.strptime(start,"%Y-%m-%d")
    end = datetime.strptime(end, "%Y-%m-%d")
    d = end - start 
    for i in range(d.days+1):
        date = start + timedelta(days=i)
        date = date.strftime(format)
        yield date