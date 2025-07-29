# Changelog

<!--next-version-placeholder-->

## v0.4.13 (2025-07-04)

### Fix

* Use `edwh.task` instead of `fabric.task` ([`4121cf9`](https://github.com/educationwarehouse/server_provisioning/commit/4121cf9fe14dca16736ded818fa5439121b764b3))

## v0.4.12 (2025-02-20)

### Fix

* Added UBUNTU_CODENAME to one of the lines in install_docker to mimic more closely the manual install. ([`7002eb0`](https://github.com/educationwarehouse/server_provisioning/commit/7002eb0f325d920f0ad3a078229dbe532b7730a4))
* Changed gpg to files to asc files in the install_docker function so it can work with Linux Mint aswell as Ubuntu ([`c853c10`](https://github.com/educationwarehouse/server_provisioning/commit/c853c10e6af83544eae0fea3cda41337189fdc76))

## v0.4.11 (2024-09-03)

### Fix

* Use PIP_BREAK_SYSTEM_PACKAGES instead of --break-system-packages so it works on both 22.04 and 24.04 ([`1a08fc1`](https://github.com/educationwarehouse/server_provisioning/commit/1a08fc1110fe8d35b408f7a1371cc87a47d5a849))

## v0.4.10 (2024-07-29)

### Fix

* Add 'unzip' as apt dependency (for devdb) ([`d82c847`](https://github.com/educationwarehouse/server_provisioning/commit/d82c8470f9d2269c6efc15eae0f42a73407b5192))

## v0.4.9 (2024-07-29)

### Fix

* Make prepare-generic-server compatible with ubuntu 24.04 ([`853936e`](https://github.com/educationwarehouse/server_provisioning/commit/853936e77ba7dd7f4a5a7f22caa415315366825e))
* Don't warn about escape sequences on python 3.12+ ([`9606baf`](https://github.com/educationwarehouse/server_provisioning/commit/9606baff7665eedb4afb230d33c5f8f93b79dcce))

## v0.4.8 (2024-04-12)

### Fix

* Use require_sudo to improve password prompting ([`91694a4`](https://github.com/educationwarehouse/server_provisioning/commit/91694a464135a90fc5b93fa57051ab07e6ec6025))

## v0.4.7 (2024-03-15)
### Fix
* Deprecated '_prepare_generic_server' because it had no reason to exist ([`6d94f77`](https://github.com/educationwarehouse/server_provisioning/commit/6d94f7752cbe5248148e366d363483f9baec8501))

## v0.4.6 (2024-02-08)
### Fix
* Ubuntu verise Check gebeurt nu alleen bij server setup, niet bij repo install ([`05f943e`](https://github.com/educationwarehouse/server_provisioning/commit/05f943e93f6c20b919e9a67f286ffc7f0fa2db31))

## v0.4.5 (2023-12-15)
### Fix
* Add ' to < because bash ([`0cbed5b`](https://github.com/educationwarehouse/server_provisioning/commit/0cbed5bca684fa90ebdd1480bc24fc8af6edd060))

## v0.4.4 (2023-12-15)
### Fix
* Pipx 1.3 is broken, so pin to 1.2 for now ([`356c117`](https://github.com/educationwarehouse/server_provisioning/commit/356c1171cac3f3690f96f2bb7772499091a57a7e))

## v0.4.3 (2023-12-15)
### Fix
* Initial github connection asked for ssh key verification (y/n)- freezing the script ([`7fc402f`](https://github.com/educationwarehouse/server_provisioning/commit/7fc402f3e6af64805e3e207771f2c3ed9bff170c))

## v0.4.2 (2023-12-15)
### Fix
* Install-omgeving is now not hardcoded to educationwarehouse anymore ([`49a10e1`](https://github.com/educationwarehouse/server_provisioning/commit/49a10e17fc47babce3cc045f7444f139c3472ebc))

## v0.4.1 (2023-12-14)
### Fix
* Only print ---done--- if not silently ([`3ba5293`](https://github.com/educationwarehouse/server_provisioning/commit/3ba5293a9d55caacc72441d456165e6d4d3f0c60))

## v0.4.0 (2023-12-14)
### Feature
* Prepare-generic-omgeving --silent will suppress successful actions ([`918d3d3`](https://github.com/educationwarehouse/server_provisioning/commit/918d3d32a86c3ff20917f7f2dd93bae19f554e58))

## v0.3.2 (2023-12-14)
### Fix
* Minor tweaks: new docker compose, fix for edwh via pipx ([`842f0a8`](https://github.com/educationwarehouse/server_provisioning/commit/842f0a80f0d279e9073553c972be2dd6936dca5f))

## v0.3.1 (2023-06-09)
### Fix
* Added files_sizes which lists the file sizes from large to small with given head(amount of file to be listed) ([`d323b29`](https://github.com/educationwarehouse/server_provisioning/commit/d323b29f5a6ff9ed614f649ae82313846d6c7fd2))

## v0.3.0 (2023-05-01)
### Feature
* **server_provisioning_plugin.py:** Add `install_generic_service` function to clone a generic-service repository without running `edwh setup` ([`c01f928`](https://github.com/educationwarehouse/server_provisioning/commit/c01f928634deb656dd58260f79ded41882e84749))

## v0.2.1 (2023-05-01)
### Fix
* **do:** Use connection user instead of os user (for remote fab) ([`9b8de23`](https://github.com/educationwarehouse/server_provisioning/commit/9b8de238069c2f3f21097a608666788e67655b9a))

## v0.2.0 (2023-05-01)
### Feature
* **do:** Remote.do now supports --edwh flag which works similar to --invoke but for 'edwh' commands ([`6987fa8`](https://github.com/educationwarehouse/server_provisioning/commit/6987fa89741177de6e2046d1782fec860dc7d879))
* **postgres:** Connect-postgres now accepts --omgeving to select a directory to read postgres port from dc ([`4b2fcda`](https://github.com/educationwarehouse/server_provisioning/commit/4b2fcda3eaee7a2e9d4610a744c115a7633fcf45))
* Added auto edwh install when prepare_generic_server is called ([`f2e41df`](https://github.com/educationwarehouse/server_provisioning/commit/f2e41df419213924fd53e493fc8514d8dc78ea16))

### Fix
* **dev:** Additional dependencies for dev now exclude semantic-release, which conflicts with invoke 2.0 ([`6e98b1a`](https://github.com/educationwarehouse/server_provisioning/commit/6e98b1a905ab92ec2518a4018e95db6ac4edc096))

## v0.1.3 (2023-04-25)
### Fix
* Now removes github keys before reassigning using `ssh -o StricHostKeyChecking=accept-new` to flush the old one and insert a new one. Also adds a better warning when installing a repo inside a git-repo (which you can't). ([`5402e03`](https://github.com/educationwarehouse/server_provisioning/commit/5402e0322301380dbd9e9abcdfe99457c7b4d288))

## v0.1.3-beta.1 (2023-04-25)
### Fix
* `ssh -tt` instead of `ssh -t` to avoid `pseudo-terminal  will not be allocated because stdin is not a terminal` ([`fa18bd9`](https://github.com/educationwarehouse/server_provisioning/commit/fa18bd980763790df7ef3a34c4193d1b171189a2))

## v0.1.2 (2023-04-17)
### Documentation
* **versions:** Remove unsupported python versions + fix md badges ([`d696150`](https://github.com/educationwarehouse/server_provisioning/commit/d696150b974bb8e37faf08ebcbc9d524d3d29586))

## v0.1.1 (2023-04-17)
### Documentation
* **readme:** New plugin docs, keep old (Dutch) readme for reference ([`fe2e8da`](https://github.com/educationwarehouse/server_provisioning/commit/fe2e8daec6ca758cc3997fc5ce95de9f3735ad52))

## v0.1.0 (2023-04-17)
### Feature
* **server_provisioning:** Rewrote to edwh plugin structure ([`632a604`](https://github.com/educationwarehouse/server_provisioning/commit/632a604182aa35b06b1fbfdab1a5f9cf9766a1fe))
* **connect-postgres:** Allow selecting 'omgeving' from which to use postgres with the -o flag ([`ecdf807`](https://github.com/educationwarehouse/server_provisioning/commit/ecdf8078ab5f5192bd9d7056a7543c9514dc11a0))
* **ungit:** Finished ungit via npx + port forwarding ([`93b6972`](https://github.com/educationwarehouse/server_provisioning/commit/93b69726e74e125dc4c64b0fb706b7c06e1b8ff3))
* **ungit:** Ungit werkte maar nog niet goed in de achtergrond :( ([`fc85368`](https://github.com/educationwarehouse/server_provisioning/commit/fc8536836183efbde97745ec86cfc389949ad8fe))
* Setup.sh toegevoegd ([`948dd4c`](https://github.com/educationwarehouse/server_provisioning/commit/948dd4c237357d1dacdea189d862cda0c2f940fe))
* **multipass:** Past /etc/hosts aan voor een gegeven multipass vm. Toevoegen of updaten. ([`ac76d32`](https://github.com/educationwarehouse/server_provisioning/commit/ac76d32fcef4fcaaf17d7b4ddcff637216093e61))
* **virtualenv:**  gebruikt nu meer de  `--user` lib space van python ipv virtualenvs en `install_ontwikkelstraat` werkt al iets beter, maar is nog incompleet. ([`2f34774`](https://github.com/educationwarehouse/server_provisioning/commit/2f347746a6623370b3da1711b3f75e990234170d))
* Xonsh wordt niet ondersteund ([`2872716`](https://github.com/educationwarehouse/server_provisioning/commit/28727169e2aa365863308fbeb267031dfd414228))
* `fab -H host connect_postgres` toegevoegd ([`12e3237`](https://github.com/educationwarehouse/server_provisioning/commit/12e3237951e7f5fb38807130a383b0b99d3310b5))
* **antivirus:** Installatie afgemaakt. ([`bccd7a5`](https://github.com/educationwarehouse/server_provisioning/commit/bccd7a5a179c75492523b124acd0c1e9d4e45c5f))
* `do` en `install_omgeving` toegevoegd ([`bf508bc`](https://github.com/educationwarehouse/server_provisioning/commit/bf508bc0223462994cf7686f019ac282e04c1a41))
* **virtualenv:**  gebruikt nu meer de  `--user` lib space van python ipv virtualenvs en `install_ontwikkelstraat` werkt al iets beter, maar is nog incompleet. ([`8b2e356`](https://github.com/educationwarehouse/server_provisioning/commit/8b2e356c6b065d1b74c4c8bc7b179ec72afa8cdb))
* New_ghost toegevoegd ([`6d77639`](https://github.com/educationwarehouse/server_provisioning/commit/6d77639b6773c4369494bf4fe97330877bf00431))
* +enable-firewall, +set-root-password +assert-passwords-disabled-on-ssh +assert-root-disabled-on-ssh ([`4c2993a`](https://github.com/educationwarehouse/server_provisioning/commit/4c2993abcabd1efdf4ced195033dbf1d0a515a09))
* **fabfile:** Virtualenvs toegevoegd. ([`0790cd4`](https://github.com/educationwarehouse/server_provisioning/commit/0790cd491ce5cd14dd642c55a8bcf572b86a73e6))
* **tasks:** Tasks.py toegevoegd om multipass machines in te richten om ssh gereed te zijn. ([`f307d9a`](https://github.com/educationwarehouse/server_provisioning/commit/f307d9a7cd4320961d1e7de1da5fb277f044ed1d))
* Werkende prepare_joplin_server op basis van prepare_generic_server ([`0a3cc27`](https://github.com/educationwarehouse/server_provisioning/commit/0a3cc27e61e7e5fa8628f0dc22133c28e042a497))

### Fix
* **req:** Pyyaml was not a requirement ([`3ec29e7`](https://github.com/educationwarehouse/server_provisioning/commit/3ec29e76bbb27e77554aa48e289209f819d8ec05))
* `python3.10-pip` e.d. werkt niet meer, dus weer terug naar `python3-pip` ([`22dbf0d`](https://github.com/educationwarehouse/server_provisioning/commit/22dbf0da0437cfb1746a35bdb19958ddd62cb75d))
*  instaleert nu ook pyyaml, tabulate, humanize en httpx. probeert python3.11 ([`a533a7d`](https://github.com/educationwarehouse/server_provisioning/commit/a533a7d11eaa95e0949a6c35ad6d95a705206132))
* Reodering van imports ([`ee59f9a`](https://github.com/educationwarehouse/server_provisioning/commit/ee59f9af872ba0d15f07c4452b8df10e7f898420))
* Datetime.datetime ging stuk door een from datetime import datetime. ([`57e0c51`](https://github.com/educationwarehouse/server_provisioning/commit/57e0c51c4c5ac5e60441a2c2fcb7e9092a95a380))
* **git:** Right requirements and ignore some stuff ([`895f3ad`](https://github.com/educationwarehouse/server_provisioning/commit/895f3adca5683fd92986c4f4b22c3ac5f788defd))
* **OsVersionCheck:** Lsb_release -v werkt niet, maar met -a werkt wel ([`dd7c5b8`](https://github.com/educationwarehouse/server_provisioning/commit/dd7c5b871b49fe168fca0b0cef1ce199be5a74c3))
* Xonsh en OsVersionCheck op basis van ([`ad6e38f`](https://github.com/educationwarehouse/server_provisioning/commit/ad6e38f9d1201bf591a07b5b7ca3e0534bbf6435))
* Install_ontwikkelstraat uitgezet, dat gaat nu via omgevingen; branch toegevoegd aan install_omgeving als optie ([`381f7b5`](https://github.com/educationwarehouse/server_provisioning/commit/381f7b5a354b25e6f8be425a631c2e23540ae70f))
* **antivirus:** Extra waarschuwing dat er nog wat moet gebeuren ([`4f06abf`](https://github.com/educationwarehouse/server_provisioning/commit/4f06abf36102d71f82ac9a601fb168011a941d0c))
* **antivirus:** Url toegevoegd van withsecure ([`b504168`](https://github.com/educationwarehouse/server_provisioning/commit/b50416877659bbbe7834f0a6fec515a8bd6c5316))
* **ontwikkelstraat_server:** Antivirus wordt bij productie automatisch geinstalleerd ([`dafbf58`](https://github.com/educationwarehouse/server_provisioning/commit/dafbf58d632ae63eca668b2851ff89a994e2a290))
* Python user environment wordt meer gebruikt dan systemwide. voor xonsh en pipx in ieder geval. ([`75f10a2`](https://github.com/educationwarehouse/server_provisioning/commit/75f10a2c2e0c035c5f0140c358f6812fc68861db))
* **firewall:**  enable_firewall is uitgebreid ([`f6ecaca`](https://github.com/educationwarehouse/server_provisioning/commit/f6ecaca1fae779364bafe5aaeefffdd4399e634a))
* `python --version` ipv `python -v`, set_root_password werkt beter. ([`7f5dbbb`](https://github.com/educationwarehouse/server_provisioning/commit/7f5dbbbbab5e0c98af7a1eca3bab2a87b2f75af4))
* Betere foutafhandeling (stderr check ipv stdout) ([`7a6c196`](https://github.com/educationwarehouse/server_provisioning/commit/7a6c1966cb720d27e1d7b73a358a4a0a488b499a))
* Typo ([`6c10e10`](https://github.com/educationwarehouse/server_provisioning/commit/6c10e107619ac0b367f9f9dea8bf46e469823be8))
* Voorkomt verbinding met localhost als je een git key aanmaakt ivm verwarrende naamgeving ([`8a6602d`](https://github.com/educationwarehouse/server_provisioning/commit/8a6602d724cb09c28e9601a58fcc795751782583))

### Documentation
* **changelog:** First release ([`fd828f7`](https://github.com/educationwarehouse/server_provisioning/commit/fd828f722fb2c97c86d73209154c2ede24c92066))
* Toegevoegd ([`f596fde`](https://github.com/educationwarehouse/server_provisioning/commit/f596fde701ee02ec655c9edbd7287beabfead1c2))

## v0.1.0 (2023-04-17)
### Feature
* **connect-postgres:** Allow selecting 'omgeving' from which to use postgres with the -o flag ([`ecdf807`](https://github.com/educationwarehouse/server_provisioning/commit/ecdf8078ab5f5192bd9d7056a7543c9514dc11a0))
* **ungit:** Finished ungit via npx + port forwarding ([`93b6972`](https://github.com/educationwarehouse/server_provisioning/commit/93b69726e74e125dc4c64b0fb706b7c06e1b8ff3))
* **ungit:** Ungit werkte maar nog niet goed in de achtergrond :( ([`fc85368`](https://github.com/educationwarehouse/server_provisioning/commit/fc8536836183efbde97745ec86cfc389949ad8fe))
* Setup.sh toegevoegd ([`948dd4c`](https://github.com/educationwarehouse/server_provisioning/commit/948dd4c237357d1dacdea189d862cda0c2f940fe))
* **multipass:** Past /etc/hosts aan voor een gegeven multipass vm. Toevoegen of updaten. ([`ac76d32`](https://github.com/educationwarehouse/server_provisioning/commit/ac76d32fcef4fcaaf17d7b4ddcff637216093e61))
* **virtualenv:**  gebruikt nu meer de  `--user` lib space van python ipv virtualenvs en `install_ontwikkelstraat` werkt al iets beter, maar is nog incompleet. ([`2f34774`](https://github.com/educationwarehouse/server_provisioning/commit/2f347746a6623370b3da1711b3f75e990234170d))
* Xonsh wordt niet ondersteund ([`2872716`](https://github.com/educationwarehouse/server_provisioning/commit/28727169e2aa365863308fbeb267031dfd414228))
* `fab -H host connect_postgres` toegevoegd ([`12e3237`](https://github.com/educationwarehouse/server_provisioning/commit/12e3237951e7f5fb38807130a383b0b99d3310b5))
* **antivirus:** Installatie afgemaakt. ([`bccd7a5`](https://github.com/educationwarehouse/server_provisioning/commit/bccd7a5a179c75492523b124acd0c1e9d4e45c5f))
* `do` en `install_omgeving` toegevoegd ([`bf508bc`](https://github.com/educationwarehouse/server_provisioning/commit/bf508bc0223462994cf7686f019ac282e04c1a41))
* **virtualenv:**  gebruikt nu meer de  `--user` lib space van python ipv virtualenvs en `install_ontwikkelstraat` werkt al iets beter, maar is nog incompleet. ([`8b2e356`](https://github.com/educationwarehouse/server_provisioning/commit/8b2e356c6b065d1b74c4c8bc7b179ec72afa8cdb))
* New_ghost toegevoegd ([`6d77639`](https://github.com/educationwarehouse/server_provisioning/commit/6d77639b6773c4369494bf4fe97330877bf00431))
* +enable-firewall, +set-root-password +assert-passwords-disabled-on-ssh +assert-root-disabled-on-ssh ([`4c2993a`](https://github.com/educationwarehouse/server_provisioning/commit/4c2993abcabd1efdf4ced195033dbf1d0a515a09))
* **fabfile:** Virtualenvs toegevoegd. ([`0790cd4`](https://github.com/educationwarehouse/server_provisioning/commit/0790cd491ce5cd14dd642c55a8bcf572b86a73e6))
* **tasks:** Tasks.py toegevoegd om multipass machines in te richten om ssh gereed te zijn. ([`f307d9a`](https://github.com/educationwarehouse/server_provisioning/commit/f307d9a7cd4320961d1e7de1da5fb277f044ed1d))
* Werkende prepare_joplin_server op basis van prepare_generic_server ([`0a3cc27`](https://github.com/educationwarehouse/server_provisioning/commit/0a3cc27e61e7e5fa8628f0dc22133c28e042a497))

### Fix
* **req:** Pyyaml was not a requirement ([`3ec29e7`](https://github.com/educationwarehouse/server_provisioning/commit/3ec29e76bbb27e77554aa48e289209f819d8ec05))
* `python3.10-pip` e.d. werkt niet meer, dus weer terug naar `python3-pip` ([`22dbf0d`](https://github.com/educationwarehouse/server_provisioning/commit/22dbf0da0437cfb1746a35bdb19958ddd62cb75d))
*  instaleert nu ook pyyaml, tabulate, humanize en httpx. probeert python3.11 ([`a533a7d`](https://github.com/educationwarehouse/server_provisioning/commit/a533a7d11eaa95e0949a6c35ad6d95a705206132))
* Reodering van imports ([`ee59f9a`](https://github.com/educationwarehouse/server_provisioning/commit/ee59f9af872ba0d15f07c4452b8df10e7f898420))
* Datetime.datetime ging stuk door een from datetime import datetime. ([`57e0c51`](https://github.com/educationwarehouse/server_provisioning/commit/57e0c51c4c5ac5e60441a2c2fcb7e9092a95a380))
* **git:** Right requirements and ignore some stuff ([`895f3ad`](https://github.com/educationwarehouse/server_provisioning/commit/895f3adca5683fd92986c4f4b22c3ac5f788defd))
* **OsVersionCheck:** Lsb_release -v werkt niet, maar met -a werkt wel ([`dd7c5b8`](https://github.com/educationwarehouse/server_provisioning/commit/dd7c5b871b49fe168fca0b0cef1ce199be5a74c3))
* Xonsh en OsVersionCheck op basis van ([`ad6e38f`](https://github.com/educationwarehouse/server_provisioning/commit/ad6e38f9d1201bf591a07b5b7ca3e0534bbf6435))
* Install_ontwikkelstraat uitgezet, dat gaat nu via omgevingen; branch toegevoegd aan install_omgeving als optie ([`381f7b5`](https://github.com/educationwarehouse/server_provisioning/commit/381f7b5a354b25e6f8be425a631c2e23540ae70f))
* **antivirus:** Extra waarschuwing dat er nog wat moet gebeuren ([`4f06abf`](https://github.com/educationwarehouse/server_provisioning/commit/4f06abf36102d71f82ac9a601fb168011a941d0c))
* **antivirus:** Url toegevoegd van withsecure ([`b504168`](https://github.com/educationwarehouse/server_provisioning/commit/b50416877659bbbe7834f0a6fec515a8bd6c5316))
* **ontwikkelstraat_server:** Antivirus wordt bij productie automatisch geinstalleerd ([`dafbf58`](https://github.com/educationwarehouse/server_provisioning/commit/dafbf58d632ae63eca668b2851ff89a994e2a290))
* Python user environment wordt meer gebruikt dan systemwide. voor xonsh en pipx in ieder geval. ([`75f10a2`](https://github.com/educationwarehouse/server_provisioning/commit/75f10a2c2e0c035c5f0140c358f6812fc68861db))
* **firewall:**  enable_firewall is uitgebreid ([`f6ecaca`](https://github.com/educationwarehouse/server_provisioning/commit/f6ecaca1fae779364bafe5aaeefffdd4399e634a))
* `python --version` ipv `python -v`, set_root_password werkt beter. ([`7f5dbbb`](https://github.com/educationwarehouse/server_provisioning/commit/7f5dbbbbab5e0c98af7a1eca3bab2a87b2f75af4))
* Betere foutafhandeling (stderr check ipv stdout) ([`7a6c196`](https://github.com/educationwarehouse/server_provisioning/commit/7a6c1966cb720d27e1d7b73a358a4a0a488b499a))
* Typo ([`6c10e10`](https://github.com/educationwarehouse/server_provisioning/commit/6c10e107619ac0b367f9f9dea8bf46e469823be8))
* Voorkomt verbinding met localhost als je een git key aanmaakt ivm verwarrende naamgeving ([`8a6602d`](https://github.com/educationwarehouse/server_provisioning/commit/8a6602d724cb09c28e9601a58fcc795751782583))

### Documentation
* Toegevoegd ([`f596fde`](https://github.com/educationwarehouse/server_provisioning/commit/f596fde701ee02ec655c9edbd7287beabfead1c2))
