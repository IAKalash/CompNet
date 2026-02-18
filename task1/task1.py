import subprocess


def main():
    domains = ["google.com",
               "quad9.net",
               "yandex.ru", 
               "one.one.one.one", 
               "wikipedia.org", 
               "github.com",
               "adguard.com", 
               "resolver1.level3.net", 
               "recursorprimary.nsd.app", 
               "a.root-servers.net"]
    
    with open('table.csv', 'w') as out:
        print("Domain, TTL, Packet Loss, rtt min/avg/max/mdev", file=out)
        
        for domain in domains:
                output = subprocess.check_output(
                     f'ping -c 1 {domain} | grep -o -E "([0-9.]+/){{3}}[0-9.]+|ttl=[0-9]*|[0-9]*%"',
                     shell=True, universal_newlines=True).split('\n')
                
                print(f"{domain}, {output[0].replace('ttl=', '')}, {output[1]}, {output[2]}", file=out)

if __name__ == "__main__":
    main()