# Fabric 4 server provisioning
[Deze repo](https://github.com/educationwarehouse/server_provisioning) maakt gebruik van [fabric](https://www.fabfile.org/index.html) om servers in te richten.
Sommige commando's zijn ook "handig" om lokaal te gebruiken.

## Definities en aannames

Met de definitie dat een **omgeving** een subdirectory is in de home directory van de ubuntu gebruiker op een server waarin een clone staat van een **repository**.   
De **taken** kunnen per omgeving verschillend zijn, maar de api kan gelijk zijn. Bijvoorbeeld `backup` . 
De taken worden gescript en uitgevoerd middels **invoke.**


## Repository clonen

```shell
fab --prompt-for-login-password -H vortex  clone-git-repo-with-new-key-file-for-edwh-repos  educationwarehouse/server_provisioning rw
```
Hiermee wordt een github repo gecloned in `~/<reponame>` maar inclusief  
het aanmaken van sleutels en een eenvoudige manier van het opsturen ervan.

Voor het inrichten van een ontwikkelserver wordt dit gedaan om de
[ontwikkelstraat](https://github.com/educationwarehouse/ontwikkelstraat/) repository te clonen.

Inspiratie voor het clonen van een repository op een server:
```shell
fab -eH ubuntu@util.edwh.nl clone-git-repo-with-new-key-file-for-edwh-repos educationwarehouse/ontwikkelstraat r
```
Let op de `r` op het eind, die kan ook een `rw` zijn, en is bedoeld om de bedoeling van de sleutel aan te geven
waarmee deze ook op github gekoppeld wordt. Hierdoor is te zien of het om een ontwikkelmachine of een productie
machine gaat.


## fabfile gebruik

De code van deze user story maakt het mogelijk om eenvoudig op afstand (vanaf een development machine, of vanuit n8n) de taken uit  te voeren in 1 of meerdere omgevingen:  

```bash
fab -H server do --omgeving leiden --omgeving slimfit --omgeving taiga --invoke "backup"
```

Om eenvoudig beheer commando's uit te voeren kan het volgende nuttig zijn: 

```bash
fab -H server do --omgeving leiden --cmd "echo hoi; echo nog een hoi"
```

Als daarbij de `--omgeving` niet opgegeven wordt, is deze gelijk aan `.` wat effectief de home folder van ubuntu betekend. Hierdoor kan ook op 'host' niveau snel hetzelfde command uitgevoerd worden. 

Gebruik makend van fabric's `-H` optie, kun je dit ook doen op meerdere hosts: 

```bash
fab -H mike,robin,romy do --cmd "apt update; apt upgrade -y "
```

Ook kan dit wel met gebruik van een gedeelde repository: 

```bash
fab -H mike,robin,romy do --omgeving ontwikkelstraat --cmd "git pull"
```

Hoewel de laatste natuurlijk het mooiste is om te upgraden via een `tasks.py` invoke file, zodat de upgrade specifiek per omgeving bijgewerkt kan worden.

## Server inrichten
De basis van de meeste van onze servers is gelijk, vandaar dit script om
dat te automatiseren. Daarnast zijn er wel eens wijzigingen en het is heel
irritant om al die wijzigingen door te voeren op elke server.  
Je hebt al snel niet door dat je 1 vergeet, en als je die later moet bijwerken
dan is het een tijdrovende klus om na te gaan wat er allemaal moet gebeuren om het
systeem weer werkend te krijgen.

Vandaar de behoefte aan zo'n script als dit.

Voorbeeld van een `generic` inrichting van een server:

```shell
fab -eH ubuntu@<hotname> prepare-generic-server 
```

 > :warning: **SSH authenticatie vereist**
 > Er wordt vanuit gegaan dat je een ssh verbinding zonder problemen opgebouwd
 > kan worden. Meestal bij de uitrol van een machine op cloudvps wordt de
 > `ew-key` file meegenomen zodat er op afstand mee te verbinden is.

## Generic
Hieronder valt:
  *  `prepare_apt` - update en upgrade
  *  `install_python` - default via apt install, vereist voor het meeste, inclusief installatie van pip3
  *  `install_docker` - key en apt repository worden toegevoegd; de gebruiker wordt lid gemaakt van de `docker` group en er wordt een `microservices` group en user aangemaakt waaronder de dockers kunnen draaien.
  *  `install_xonsh` - std installatie met wat plugins via pip


## Joplin server
Joplin is geinstalleerd via het volgende commando, op een generic server:
```shell
fab -eH ubuntu@util.edwh.nl install-joplin
```
Bij een volledig kale machine, zou je voor een herinrichting het volgende
kunnen gebruiken:
```shell
fab -eH ubuntu@util.edwh.nl prepare-joplin-server 
```

# Interessante links
 * SPEC https://cloudinit.readthedocs.io/en/latest/topics/examples.html
 * FRAMEWORK [fabric](https://www.fabfile.org/index.html) - invoke over ssh (fabfile.py)
 * FRAMEWORK [invoke](https://www.pyinvoke.org/) - lokaal (tasks.py)
 * LIB [plumbum](https://plumbum.readthedocs.io/) - alternatief, itegreert shell met python
 * SHELL [xonsh](https://xon.sh/) - shell + python; vervanger van /bin/bash
