from os import system

start = "2022-09-25"
end = "2022-09-30"
newspaper = "workerdaily"
cmd = f"scrapy crawl {newspaper} -a start={start} -a end={end}"
system(cmd)

##