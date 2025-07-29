import abc
import getpass
import io
import os
import pprint
import re
import sys
import textwrap
import time
import typing
import urllib.parse
import warnings
from abc import ABC
from datetime import datetime
from io import StringIO
from pathlib import Path
from textwrap import dedent

import edwh.tasks
import yaml
from edwh import task
from fabric import Connection, Result
from tabulate import tabulate
from termcolor import cprint
from yaml.loader import SafeLoader

DOT_XONSH = """
# XONSH WEBCONFIG START
$XONSH_COLOR_STYLE = 'monokai'
xontrib load distributed argcomplete vox vox_tabcomplete whole_word_jumping z pipeliner
# XONSH WEBCONFIG END
#
aliases['dc']='docker compose'
aliases['ll']='ls -al'
aliases['i']='invoke --echo'
aliases['flush_dns']='sudo systemd-resolve --flush-caches ; sudo systemctl restart systemd-resolved'
aliases['list_open_sockets']='sudo netstat -anlp'
aliases['port_search']='sudo netstat -anlp  | grep '
$UPDATE_OS_ENVIRON=True
$PATH.extend(':~/.local/bin/')
#$FLIT_USERNAME='...'
#$FLIT_PASSWORD='...'
$PROMPT_FIELDS['prompt_end'] = $PROMPT_FIELDS['prompt_end'].replace('$', '{WHITE}@')
$PROMPT = '{env_name}{BOLD_GREEN}{user}@{hostname}{BOLD_BLUE} {short_cwd}{branch_color}{curr_branch: {}}{NO_COLOR} {BOLD_BLUE}{prompt_end}{NO_COLOR} '
"""

JOPLIN_DOCKER_COMPOSE = """
version: '3.3'
services:
    proxy:
        image: "traefik:v2.5"
        container_name: "traefik"
        restart: unless-stopped
        command:
           #- --log.level=DEBUG
            - --api.insecure=false
            - --providers.docker=true
            - --providers.docker.exposedbydefault=false
            - --entrypoints.web.address=:80
            - --entrypoints.web-secured.address=:443
            - --entrypoints.web.http.redirections.entryPoint.to=web-secured
            - --entrypoints.web.http.redirections.entryPoint.scheme=https
            - --entrypoints.web.http.redirections.entrypoint.permanent=true
            - --certificatesResolvers.letsencrypt.acme.email=remco.b@educationwarehouse.nl
            - --certificatesResolvers.letsencrypt.acme.storage=/letsencrypt/production.json
            - --certificatesResolvers.letsencrypt.acme.httpChallenge=true
            - --certificatesResolvers.letsencrypt.acme.httpChallenge.entryPoint=web
            ## Staging Certificate Settings (Let's Encrypt) -  https://docs.traefik.io/https/acme/#configuration-examples ##
            - --certificatesResolvers.staging.acme.caServer=https://acme-staging-v02.api.letsencrypt.org/directory
            - --certificatesResolvers.staging.acme.email=remco.b@educationwarehouse.nl
            - --certificatesResolvers.staging.acme.storage=/letsencrypt/staging.json
            - --certificatesResolvers.staging.acme.httpChallenge=true
            - --certificatesResolvers.staging.acme.httpChallenge.entryPoint=web
        ports:
            - "80:80"
            - "443:443"
#            - "8080:8080"
        volumes:
            - "/var/run/docker.sock:/var/run/docker.sock:ro"
            - "./letsencrypt:/letsencrypt"
    joplin:
        environment:
            - APP_BASE_URL=https://joplin.edwh.nl
            - APP_PORT=22300
            - POSTGRES_PASSWORD=joplin
            - POSTGRES_DATABASE=joplin
            - POSTGRES_USER=joplin
            - POSTGRES_PORT=5432
            - POSTGRES_HOST=db
            - DB_CLIENT=pg
        restart: unless-stopped
        image: florider89/joplin-server:latest
        ports:
            - "22300:22300"
        labels:
            # Explicitly tell Traefik to expose this container
            - "traefik.enable=true"
            # The domain the service will respond to
            - "traefik.http.routers.joplin.rule=Host(`joplin.edwh.nl`)"
            # Allow request only from the predefined entry point named "web"
            - "traefik.http.routers.joplin.entrypoints=web-secured"
            - "traefik.http.routers.joplin.tls=true"
            - "traefik.http.routers.joplin.tls.certresolver=letsencrypt"

    db:
        restart: unless-stopped
        image: postgres:13.1
        #ports:
        #    - "5432:5432"
        volumes:
            - ./postgres-data:/var/lib/postgresql/data
        environment:
            - POSTGRES_PASSWORD=joplin
            - POSTGRES_USER=joplin
            - POSTGRES_DB=joplin

"""


# met irerable kan je meerdere cli keys in 1 regel meegeven.
@task(iterable=["command_line_key"])
# append key to remote is kort gezegd dat je via de YAML file de public key IN de opgegeven remote machine zet
def append_key_to_remote(c, command_line_key):
    """
    command-line-key is/zijn de key(s) die je toevoegd aan de remote machine.
    Je kan meerdere opgeven.

    Als er een key bij zit die NIET in de yaml file staat kan je die aanmaken door bij de input vraag 'y' mee te geven.
    LET OP: je moet dan wel een bericht mee geven, anders breekt het programma af.

    De private/public key staan in de ~/.managed_ssh_keys-{key_name}
    """
    # open de yaml file zodat die kan lezen welke head_keys er al zijn
    with open("key_holder.yaml", "r") as yaml_file:
        key_db: dict = yaml.load(yaml_file, Loader=SafeLoader)
        all_key_information = key_db.setdefault("sleutels")
        count_keys = 0
        # controleert of het aantal command_line_key's wel gelijk staan aan de keys die nodig zijn, zo niet gaat die je vragen in de cli of de onjuiste key wil veranderen
        for head_keys in all_key_information:
            if head_keys in command_line_key:
                count_keys += 1
        if count_keys == len(command_line_key):
            for which_key in command_line_key:
                for head_keys in all_key_information:
                    if which_key in head_keys:
                        for key, value in all_key_information[head_keys].items():
                            # gaat alleen de 'sleutel' toevoegen en niet de datetime enzovoort
                            if (
                                bool(key.find("datetime"))
                                and bool(key.find("wie@hostname"))
                                and bool(key.find("message")) is True
                            ):
                                c.run(f"echo {value} >> ~/.ssh/authorized_keys")
                                c.run("touch ~/.ssh/keys")
                                c.run("sort -u ~/.ssh/authorized_keys > ~/.ssh/keys")
                                time.sleep(1)
                                c.run("cp ~/.ssh/keys ~/.ssh/authorized_keys")
                                c.run("rm ~/.ssh/keys")
                                print(f"Het is gelukt! De \033[1m{which_key}\033[0m key is toegevoegd.")
        else:
            # verwijder alle keys die WEL in de yaml file staan
            not_in_yaml_keys = command_line_key
            for head_keys in all_key_information:
                not_in_yaml_keys = [which_key for which_key in not_in_yaml_keys if which_key not in head_keys]
            print(
                f"Verkeerde \033[1m{' '.join(not_in_yaml_keys)}\033[0m key, controleer eerst of je de juiste key hebt ingevuld. Of als die wel in de YAML file staat."
            )
            for which_key in not_in_yaml_keys:
                split_key = which_key.replace("-", " ")
                generate_doel = ""
                if len(split_key.split()) == 3:
                    generate_doel = split_key.split()[2]
                # maak de key aan die nog NIET in de yaml file stond
                if input(f"Wil je de {which_key} key aanmaken? [Yn]") in {"y", "Y", ""}:
                    if not (generate_message := input("Wat is het bericht dat je mee wilt geven? Deze MOET: ")):
                        print("Je moet een message invullen!")
                        exit(1)
                    # print('\n\nJe moet minimaal 2/3 invullen: Owner, Hostname en/of Doel!!\n\n')
                    # owner = str(input("Wie is de owner van de Private key?"'\n')) or ''
                    # hostname = str(input('Wie is de specifieke host? bvb: productie - testomgeving - naam van de stagiar''\n')) or ''
                    # doel = str(input('Waarom maak je deze key aan?''\n')) or ''
                    # generate(c, message, owner=owner.replace(" ", ""), hostname=hostname.replace(" ", ""), doel=doel.replace(" ", ""))
                    # voer dus de functie generate_keys uit om de key dus daadwerkelijk aan te maken
                    generate_key(
                        c,
                        generate_message,
                        owner=split_key.split()[0],
                        hostname=split_key.split()[1],
                        doel=generate_doel,
                    )
                    # bekijk of nu wel alle keys in de yaml file staan, zo ja, ga dan alsnog toevoegen
                    if head_keys in command_line_key:
                        count_keys += 1
                    if count_keys == len(command_line_key):
                        append_key_to_remote(c, command_line_key)


# met irerable kan je meerdere cli keys in 1 regel meegeven
@task(iterable=["command_line_key"])
# delete key from remote is kort gezegd dat je via de YAML file de public key UIT de opgegeven remote machine zet
def delete_key_from_remote(c, command_line_key):
    """
    command-line-key is/zijn de key(s) die je toevoegd aan de remote machine.
    Je kan meerdere opgeven.
    """
    with open("key_holder.yaml", "r") as yaml_file:
        key_db: dict = yaml.load(yaml_file, Loader=SafeLoader)
        all_key_information = key_db.setdefault("sleutels")
    for which_key in command_line_key:
        for head_keys in all_key_information:
            if which_key in head_keys:
                for key, value in all_key_information[head_keys].items():
                    # gaat alleen de 'sleutel' toevoegen en niet de datetime enzovoort
                    if (
                        bool(key.find("datetime"))
                        and bool(key.find("wie@hostname"))
                        and bool(key.find("message")) is True
                    ):
                        # pakt de juiste sleutel en 'verwijdert' die sleutel
                        c.run(f'grep -v "{value}" ~/.ssh/authorized_keys > ~/.ssh/keys')
                        c.run("mv ~/.ssh/keys ~/.ssh/authorized_keys")
                        print(f"Het is gelukt! De \033[1m{which_key}\033[0m key is verwijderd.")


@task
def generate_key(c, message, owner="", hostname="", doel=""):
    """
    message: Geef een verduidelijke bericht mee aan de key die gegenareerd wordt.
    owner: Wie heeft de private key..?
    hostname: Specifieke host, bvb: productie - testomgeving - naam van de stagiar
    doel: Waarom maak je deze key aan? bvb: Sandfly, SSH
    De private/public key staan in de ~/.managed_ssh_keys-{key_name}
    """
    # bekijk of de key_holder.yaml al bestaat, zo nee, maak die dan aan. zo ja, zorg er dan voor dat de sleutels
    # standaard wordt
    try:
        with open("key_holder.yaml", "r") as stream:
            key_db: dict = yaml.load(stream, Loader=SafeLoader)
            all_key_information = key_db.setdefault("sleutels")
    except FileNotFoundError:
        os.popen('touch key_holder.yaml | echo "sleutels" > key_holder.yaml')
        all_key_information = {}
    # hierbij wordt gekeken of er wel 2/3 argumenten zijn, zo ja wordt het dan ook meteen op de goeie volgorde gezet
    how_many_arguments_in_cli = bool(owner != ""), bool(hostname != ""), bool(doel != "")
    if sum(how_many_arguments_in_cli) < 2:
        print("Je moet minimaal twee van de drie argumenten meegeven: Owner, Hostname, Doel")
        exit(1)
    key_name = []
    if bool(owner) == True:
        key_name.append(owner)
    if bool(hostname) == True:
        key_name.append(hostname)
    if bool(doel) == True:
        key_name.append(doel)
    key_name = "-".join(key_name)
    if key_name in all_key_information:
        print(f"{key_name} bestaat al, toevoegen afgebroken.")
        exit(1)
    print("De key wordt aangemaakt...")
    # met ssh-keygen wordt de key pair dus aangemaakt en wordt de public key in de yaml file gezet
    os.popen(f'ssh-keygen -t rsa -b 4096 -f ~/.managed_ssh_keys-{key_name} -N "" -C "{message}"').close()
    whoami_local_handle = os.popen('echo "$(whoami)@$(hostname)"')
    time.sleep(4)
    whoami_local = whoami_local_handle.read().replace("\n", "")
    whoami_local_handle.close()
    cat_local_public_key_handle = os.popen(f"cat ~/.managed_ssh_keys-{key_name}.pub")
    cat_local_public_key = cat_local_public_key_handle.read().replace("\n", "")
    cat_local_public_key_handle.close()
    # zo komt het dus er uit te zien in de yaml file
    sleutel_dict = {
        "sleutels": {
            key_name: {
                "sleutel": cat_local_public_key,
                "datetime": datetime.today().strftime("Datum: %Y-%m-%d Tijdstip: %H:%M:%S"),
                "wie@hostname": whoami_local,
                "message": message,
            }
        }
    }
    # voor de eerste keer (wanneer het script dus nog niet bestond) wordt de hoofdkey sleutels nog aangemaakt en anders wordt het erin toegevoegd.
    with open("key_holder.yaml", "w") as stream:
        try:
            if key_db is not None:
                new_key_dict = sleutel_dict.pop("sleutels")
                all_key_information.update(new_key_dict)
                yaml.dump(key_db, stream, indent=4)
                pprint.pprint(new_key_dict)
                print(f"De private/public key staan in de ~/.managed_ssh_keys-{key_name}")
        except:
            yaml.dump(sleutel_dict, stream, indent=4)
            pprint.pprint(sleutel_dict)
            print(f"De private/public key staan in de ~/.managed_ssh_keys-{key_name}")


@task
def list_local_keys(c):
    """
    Hier komt de lijst te staan van alle sleutels die dus LOCAL in de yaml file staan.
    """
    with open("key_holder.yaml", "r") as yaml_file:
        key_db: dict = yaml.load(yaml_file, Loader=SafeLoader)
        all_key_information = key_db.setdefault("sleutels")
        print("\033[1mDe lijst van de local Keys:\033[0m")
    for which_key in all_key_information:
        print(which_key)
    # for keys in (k for k, v in all_keys.items() if v in output): print(keys)


@task
def list_remote_keys(c):
    """
    Hier komt de lijst te staan van alle sleutels die dus op de REMOTE machine staan.
    """
    with open("key_holder.yaml", "r") as yaml_file:
        key_db: dict = yaml.load(yaml_file, Loader=SafeLoader)
        all_key_information = key_db.setdefault("sleutels")
        print("\033[1mDe lijst van de remote Keys:\033[0m")
        cat = c.run("cat ~/.ssh/authorized_keys", hide=True)
        cat = cat.stdout
    for which_key in all_key_information:
        for key, value in all_key_information[which_key].items():
            if bool(key.find("datetime")) and bool(key.find("wie@hostname")) and bool(key.find("message")) is True:
                if value in cat:
                    print(which_key)


@task
def list_keys(c):
    """
    Je krijgt een overzicht te zien van alle keys
    Als er ook al keys remote staan dan worden er twee lijstjes gemaakt: local & remote :::: remote
    Als er nog keys staan in de remote file en die niet herkent worden, krijg je de output te zien van die keys
    """
    with open("key_holder.yaml", "r") as yaml_file:
        key_db: dict = yaml.load(yaml_file, Loader=SafeLoader)
        all_key_information = key_db.setdefault("sleutels")
    cat_remote_keys = c.run("cat ~/.ssh/authorized_keys", hide=True)
    cat_remote_keys = cat_remote_keys.stdout
    rows = []
    row_x = []
    row_y = []
    cat_list = []
    split_the_cat_list = r"\|"
    clolumn_names = ["\033[1mlocal & remote", "local\033[0m"]
    for head_keys in all_key_information:
        # all_key_information[head_keys].items() laat de keys en values zien die in de sleutel staan
        for key, value in all_key_information[head_keys].items():
            # verwijder de datetime, wie@hostname en message. zodat je alleen de sleutel te zien krijgt.
            if bool(key.find("datetime")) and bool(key.find("wie@hostname")) and bool(key.find("message")) is True:
                # als de key value in de cat (remote keys file) staan:
                if value in cat_remote_keys:
                    # voeg dan die sleutel toe aan de row_x
                    row_x.append(head_keys)
                    cat_list.append(value)
                # als de key value NIET in de cat staat:
                else:
                    # voeg dan de sleutel toe aan de row_y
                    row_y.append(head_keys)
    try:
        # kijk of er nog andere keys op de remote machine staan, zo ja, geef daar dan de output van
        grep_cat_list = c.run(f'grep -v "{split_the_cat_list.join(cat_list)}" ~/.ssh/authorized_keys', hide=True)
        print("LET OP!")
        print("Er staan nog andere keys op de remote, alleen kan die niet herkend worden door het yaml file:\n")
        print(grep_cat_list.stdout)
        print()
    except:
        pass
    # dit zorgt ervoor dat de keys in de goede column komt te staan
    for bron_index in range(max(len(row_x), len(row_y))):
        rows.append([])
    for bron_index in range(max(len(row_x), len(row_y))):
        if bron_index < len(row_x):
            rows[bron_index].append(row_x[bron_index])
        if bron_index < len(row_y):
            rows[bron_index].append(row_y[bron_index])
        if len(rows[bron_index]) == 1:
            if not bool("".join(rows[bron_index]) in row_x):
                rows[bron_index].insert(0, "")
                print(rows[bron_index][0])
    print("\033[1mDe lijst van de keys:\033[0m")
    if bool(row_x) == True:
        print(tabulate(rows, headers=clolumn_names))
    else:
        print("Er staan nog geen sleutels op deze remote machine die in de yaml file staan...")
        print("\033[1mlocal\033[0m")
        for head_keys in all_key_information:
            print(head_keys)


class RemoteWentWrong(Exception):
    pass


def failsafe(callable):
    """Executes the callable, and if not result.ok raises a RemoteWentWrong exception."""
    result: Result = callable()
    if not result.ok:
        raise RemoteWentWrong(result.stderr)
    return result


class TestOnce(ABC):
    tested = False

    @classmethod
    def test(cls, c: Connection):
        if not cls.tested:
            cls.evaluate(c)
            print(cls.__name__, "succesful")

        cls.tested = True

    @classmethod
    @abc.abstractmethod
    def evaluate(cls, c: Connection): ...


class Xonsh(TestOnce):
    @classmethod
    def evaluate(cls, c: Connection):
        if c.run("env | grep XONSH", hide=True, warn=True).stdout.strip():
            # xonsh is incompatbible met `cat filename` en dan de .ok uitlezen.
            # daarom gewoon niet toestaan.
            print(
                "ERROR: Do NOT use xonsh as the default shell for the given user. ",
                file=sys.stderr,
            )
            exit(1)


SUPPORTED_UBUNTU_VERSIONS = ("22.04", "24.04")


class OsVersionCheck(TestOnce):
    @classmethod
    def evaluate(cls, c: Connection):
        if (version := c.run("lsb_release -rs", hide=True, warn=True).stdout.strip()) not in SUPPORTED_UBUNTU_VERSIONS:
            print(
                f"ERROR: Ubuntu version {version} other than {SUPPORTED_UBUNTU_VERSIONS} is detected, aborting. ",
                file=sys.stderr,
            )
            exit(1)


def executes_correctly(c: Connection, argument: str) -> bool:
    """
    returns True if the execution was without error level
    """
    Xonsh.test(c)
    return c.run(argument, warn=True).ok


def execution_fails(c: Connection, argument: str) -> bool:
    """
    Returns true if the execution fails based on error level
    """
    return not executes_correctly(c, argument)


@task
def file_sizes(c, head: int = 20):
    """
    list the files from large to smallest
    :param head: amount of files to be listed by the large file search
    """
    print("searching for large files...(this can take a minute)")
    c.run(f"du -aBM 2>/dev/null | sort -nr | head -n {head}")


@task(pre=[edwh.tasks.require_sudo])
def apt_install(c, packages):
    if isinstance(packages, str):
        packages = [packages]

    failsafe(lambda: c.sudo("apt install -y " + " ".join(packages)))


@task(pre=[edwh.tasks.require_sudo])
def apt_upgrade(c, dist=False):
    failsafe(lambda: c.sudo("apt update -y"))
    if dist:
        failsafe(lambda: c.sudo("apt dist-upgrade -y"))
    else:
        failsafe(lambda: c.sudo("apt upgrade -y"))

    failsafe(lambda: c.sudo("apt autoremove -y "))


@task
def prepare_apt(c):
    apt_upgrade(c)
    # curl is nodig om externe gpg sleutels op te kunnen halen
    apt_install(
        c,
        [
            "apt-transport-https",
            "ca-certificates",
            "software-properties-common",
            "curl",
            "gnupg",
            "unzip",
        ],
    )


@task(pre=[edwh.tasks.require_sudo])
def add_apt_repository(c, gpg_url, repo_url):
    c.run(f"curl -fsSL {gpg_url} | sudo apt-key add -")
    c.sudo(f'add-apt-repository "deb [arch=amd64] {repo_url} $(lsb_release -cs) stable"')
    apt_upgrade(c)


@task(pre=[edwh.tasks.require_sudo])
def add_user_to_group(c, group):
    current_groups = c.run("groups").stdout
    if group not in current_groups:
        failsafe(lambda: c.sudo(f"gpasswd -a `whoami` {group} "))


@task(pre=[edwh.tasks.require_sudo])
def install_docker(c):
    if execution_fails(c, "docker compose version"):
        c.sudo("apt-get update")
        c.sudo("apt-get install ca-certificates curl -y")
        c.sudo("install -m 0755 -d /etc/apt/keyrings")
        c.sudo("sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc")
        c.sudo("chmod a+r /etc/apt/keyrings/docker.asc")
        c.sudo(
            'echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null'
        )
        c.sudo("apt update")
        apt_install(c, "docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin")

    if "microservices" not in c.run("groups").stdout:
        # maak een nieuwe microservices group met dit specifieke ID
        c.sudo("addgroup --gid 1050 microservices")
        # maak hier ook een nieuwe suer voor aan, met hetzelfde ID die niet mag inloggen
        c.sudo("adduser --uid 1050 --gid 1050 --disabled-password --disabled-login --system microservices")
        # voeg deze gebruiker toe aan die nieuwe groep
        c.sudo("usermod --groups microservices --append `whoami`")

    add_user_to_group(c, "docker")


@task
def show_user_groups(c):
    print(c.run("groups").stdout)


@task(pre=[edwh.tasks.require_sudo])
def install_python(c: Connection):
    if execution_fails(c, "python3 --version"):
        apt_install(c, ["python3"])
    if execution_fails(c, "pip3 -V"):
        apt_install(c, ["python3-pip"])
    # wonderbaarlijk genoeg schijnt virtualenv nu ook al geinstalleerd te zijn.
    # maar alsnog:
    c.sudo("apt install -y python3-venv")  # vereist voor pipx
    if execution_fails(c, "~/.local/bin/pipx --version"):
        c.run("pip install --user 'pipx<1.3'", env={"PIP_BREAK_SYSTEM_PACKAGES": "1"})

    if execution_fails(c, "~/.local/bin/uvenv --version"):
        c.run("pip install --user uvenv", env={"PIP_BREAK_SYSTEM_PACKAGES": "1"})


@task
def install_xonsh(c):
    c: Connection = c
    if execution_fails(c, ".local/bin/xonsh -V"):
        # cwd should be ~, but we cannot enforce this because ~ isn't understood by sftp
        c.put(StringIO(DOT_XONSH), remote=".xonshrc")
        c.run(
            "pip install --user xonsh vox xonsh-apt-tabcomplete xonsh-autoxsh xonsh-vox-tabcomplete xontrib-z pipeliner"
        )


@task
def set_noninteractive(c):
    c.run("export DEBIAN_FRONTEND=noninteractive")


@task
def prepare_git_client(
    c,
    username,
    email,
):
    c: Connection = c
    print(c.host)
    return
    # git config --global --add user.name spore
    c.run(f"git config --global --add user.name {username}")
    # git config --global --add user.email spore@edwh.nl
    c.run(f"git config --global --add user.email {email}")
    # git config --global core.editor "vim"
    c.run(f'git config --global core.editor "vim"')


@task
def clone_git_repo_with_new_key_file_for_edwh_repos(c, repo, rw, target_directory="", branch=None):
    c: Connection = c
    git_user, git_repo = repo.split("/")

    # first try: anonymous git
    if rw == "r" and executes_correctly(c, f"git clone https://github.com/{git_user}/{git_repo}"):
        # public read-only repo cloned fine
        return

    # alleen sleutels gebruiken voor edwh eigen repo's, voor de rest is anon access genoeg
    assert rw in {"r", "rw"}, "rw should be either r or rw"
    # ssh-keygen -t ed25519 -C "bla die pir" -f .ssh/bla_die_pir.key -N ""
    # -t == type : ecc type
    # -C == comment, geef naam op
    # -f == Destination file, neemt aan dat cwd == ~
    # -N == new passphrase. blanco dus.
    username = c.run("whoami").stdout.strip()
    host = c.host
    if host == "localhost":
        raise ValueError("Do not connect with localhost, use the hostname to avoid collisions in the keyfilename. ")
    filename = f"git-{git_user}-{git_repo}-{rw}".lower()
    if execution_fails(c, f"cat .ssh/{filename}.pub"):
        comment = f"{username}@{host} for {rw.lower()} on git:{git_user}/{git_repo} added {datetime.now().isoformat()}"
        failsafe(lambda: c.run(f'ssh-keygen -t ed25519 -C "{comment}" -f .ssh/{filename} -N ""'))
        key = c.run(f"cat .ssh/{filename}.pub").stdout
        url = f"https://github.com/{git_user}/{git_repo}/settings/keys/new"
        print(f"Post this key on the following page: {url}")
        print(key)
        input("\n\nPress enter when done.")

        # $ cat ~/.ssh/config
        if executes_correctly(c, f"cat .ssh/config"):
            config = c.run(f"cat .ssh/config").stdout
        else:
            config = ""
        config += dedent(
            f"""
        Host github.com-{git_repo}
             User git
             Hostname github.com 
             IdentityFile=/home/{username}/.ssh/{filename}
             StrictHostKeyChecking no
        """
        )
        # Host github.com-ontwikkelstraat
        #         Hostname github.com
        #         IdentityFile=/home/ubuntu/.ssh/git-ontwikkelstraat.id_rsa
        c.put(StringIO(config), ".ssh/config")

    # respond_to_security=Responder(r'Are you sure you want to continue connecting \(yes/no/\[fingerprint\]\)\?.*','yes\n')

    # check als machine correcte git ssh verbinding kan maken
    # fingerprint
    if (
        "Permission denied (publickey)"
        in c.run(
            "ssh-key -R github.com && ssh -tt -o StrictHostKeyChecking=accept-new git@github.com",
            hide=True,
            warn=True,
        ).stderr
    ):
        raise Exception(
            "github key klopt niet, CHECK ALS GITHUB_KNOWN_HOSTS KEY KLOPT IN DE server_provisioning_plugin.py"
        )

    # test if the repo exists:
    if "fatal:" in c.run(f"cd {target_directory or git_repo}; git status", warn=True, hide=True).stderr:
        failsafe(lambda: c.run(f"git clone github.com-{git_repo}:{git_user}/{git_repo} {target_directory}"))
    else:
        print(f"Repo {git_repo} already installed in {target_directory}, or a git repository exists higher-up")
    if branch:
        c.run(f"cd {target_directory}; git checkout {branch}")


class SecurityException(Exception):
    pass


@task(pre=[edwh.tasks.require_sudo])
def assert_root_disabled_on_ssh(c):
    print(f"Validating SSHd config file disallows root on {c.host}.")
    sshd_config_parts = (
        c.sudo("grep -i PermitRootLogin /etc/ssh/sshd_config", warn=True, hide=True).stdout.strip().split("\n")
    )
    if sshd_config_parts:
        enabled_linecount = sum(1 for line in sshd_config_parts if not line.startswith("#"))
        if enabled_linecount:
            print(
                """Invalid content in: \n\t""",
                "\t\n".join(sshd_config_parts),
                file=sys.stderr,
            )
            raise SecurityException(
                "PermitRootLogin found enabled in /etc/ssh/sshd_config on target host. Disable manually. "
            )
    authorized_keys = c.sudo("cat /root/.ssh/authorized_keys", warn=True, hide=True).stdout.strip().split("\n")
    if len(authorized_keys) > 1:
        raise SecurityException("There should only be one key in /root/.ssh/authorized_keys")
    if "command=" not in authorized_keys[0].lower():
        raise SecurityException("Missing a blocking command section in /root/.ssh/authorized_keys")
    print("Good, root seems unable to login.")


@task(pre=[edwh.tasks.require_sudo])
def assert_passwords_disabled_on_ssh(c):
    print(f"Validating SSHd config file disallows passwords on {c.host}.")
    sshd_config_parts = (
        c.sudo("grep -i PasswordAuthentication /etc/ssh/sshd_config", hide=True, warn=True).stdout.strip().split("\n")
    )
    if sshd_config_parts:
        for line in sshd_config_parts:
            line = line.strip()
            if line.startswith("#"):
                # ignore comments
                continue
            if line.startswith("PasswordAuthentication"):
                terms = re.split("[ \t]+", line)
                if terms[1].lower() == "yes":
                    print("From /etc/ssh/sshd_config:", "\n".join(sshd_config_parts))
                    raise SecurityException(
                        "PasswordAuthentication found enabled in /etc/ssh/sshd_config on target host. Disable manually. "
                    )
    print("Good, password authentication seems disabled")


@task(pre=[edwh.tasks.require_sudo])
def set_root_password(c, password=None, overwrite=False):
    """Sets remote root password to given password, or asks the user for one."""
    shadow = [line.strip().split(":") for line in c.sudo("cat /etc/shadow", hide=True).stdout.strip().split("\n")]
    for username, password_hash, *_ in shadow:
        if username == "root":
            if len(password_hash) > 1:
                # Some password exists for root
                if not overwrite:
                    print("Not overwriting existing root password.")
                    return
                else:
                    # password field contains a single character, denoting an invalid hash.
                    # mostly ! or *. Break the loop and continue overwriting the password.
                    break
    print(f"Changing password for root@{c.host} ...")
    if not password:
        p1 = getpass.getpass("Password for root: ")
        p2 = getpass.getpass("Password for root, again: ")
        if p1 != p2:
            print("ERROR: Password mismatch", file=sys.stderr)
            exit(254)
        password = p1
    c.sudo(
        "passwd root",
        hide=False,
        in_stream=StringIO(password + "\n" + password + "\n"),
    )


@task(pre=[edwh.tasks.require_sudo])
def enable_firewall(c, portmapping):
    """
    open ports with ufw, and docker-ufw.
    portmapping is a ';' seperated list of ':' seperated service_name:port tuples
    if no service_name is given, it will be applied just to UFW
    if a service_name is given, it will be aplied to ufw-docker as well.

    :param c: connection
    :param portmapping: portmapping to open up;
    :type portmapping: string
    :return:
    """
    assert_passwords_disabled_on_ssh(c)
    print("Current open ports:")
    get_open_ports(c)
    print("Setup up firewall on ", c.host)
    c.sudo(f"ufw disable")
    c.sudo(f"ufw reset")
    ports = [mapping.split(":")[1] for mapping in portmapping.split(";")]
    service_ports = dict(mapping.split(":") for mapping in portmapping.split(";") if not mapping.startswith(":"))
    ports = [int(_) for _ in ports.strip().split(",") if int(_)]
    if 22 not in ports:
        # niet jezelf uitsluiten
        ports.append(22)
    for port in ports:
        print("Allowing", port)
        c.sudo(f"ufw allow {port}", hide=True)
    print("drop by default")
    c.sudo(f"ufw default deny incoming")
    print("Enabling firewall on ", c.host)
    from invoke import Responder

    answer_yes = Responder(
        pattern=r"Command may disrupt existing ssh connections\. Proceed with operation \(y\|n\)\?.*",
        response="y\n",
    )
    c.sudo("ufw enable", hide=True, watchers=[answer_yes])
    c.sudo("ufw status verbose", hide="stderr")
    print("")
    if "fatal:" in c.run(f"cd ufw-docker; git status", warn=True, hide=True).stderr:
        failsafe(
            lambda: c.run(
                f"git clone https://github.com/chaifeng/ufw-docker.git; cd ufw-docker; ./ufw-docker install; systemctl restart ufw"
            )
        )
        for service, port in service_ports.items():
            failsafe(lambda: c.run(f""))


@task(pre=[edwh.tasks.require_sudo])
def get_open_ports(c):
    print("Checking", c.host)
    c.sudo("ufw status verbose")


@task()
def install_edwh(c):
    """
    Args:
        c (Connection)
    """
    if execution_fails(c, "~/.local/bin/uvenv install edwh[plugins]"):
        c.run("~/.local/bin/uvenv upgrade edwh")


@task()
def prepare_generic_server(
    c,
    silent: bool = False,
):
    """
    Updates apt and dist-upgrades the machine. Installs python, docker, docker compose, and xonsh.

    A default .xonshrc is added, as well as a microservices group and the current user is added to both
    the docker group as well as the microservices group.
    """
    OsVersionCheck.test(c)
    tasks = [
        set_noninteractive,
        prepare_apt,
        install_python,
        install_docker,
        install_edwh,
        # install_xonsh,
        assert_passwords_disabled_on_ssh,
        assert_root_disabled_on_ssh,
    ]

    if silent:
        errors = {}

        stderr = sys.stderr
        stdout = sys.stdout

        sys.stderr = open(os.devnull, "w")
        sys.stdout = open(os.devnull, "w")

        status = ["⚪️"] * len(tasks)

        for idx, task in enumerate(tasks):
            print("".join(status), end="\r", file=stderr, flush=True)
            try:
                task(c)
                status[idx] = "🟢"
            except Exception as e:
                errors[task.__name__] = e
                status[idx] = "🔴"

        sys.stderr = stderr
        sys.stdout = stdout

        for func, error in errors.items():
            cprint(f"--- {func} failed: ---", color="red", file=stderr)
            cprint(error, color="yellow", file=stderr)

        print("".join(status), file=stdout)

    else:
        for task in tasks:
            task(c)

        print("-------------------------------------------------------------------------------------", file=sys.stderr)
        print("--------------------------------------- Done! ---------------------------------------", file=sys.stderr)
        print("-------------------------------------------------------------------------------------", file=sys.stderr)


def _prepare_generic_server(c: Connection, silent: bool):
    warnings.warn(
        "'_prepare_generic_server' is deprecated. Please use 'prepare_generic_server' instead.",
        category=DeprecationWarning,
    )
    return prepare_generic_server(c, silent)


@task
def install_joplin(c):
    c: Connection = c
    c.run("mkdir services", warn=True)
    c.run("mkdir services/postgres-data", warn=True)
    c.run("mkdir services/letsencrypt", warn=True)
    c.put(StringIO(JOPLIN_DOCKER_COMPOSE), "services/docker-compose.yml")
    # home_folder = c.run('pwd').stdout
    c.run(
        "cd services; pwd; docker-compose stop proxy joplin; docker-compose up -d db ; docker-compose up -dV  proxy joplin"
    )
    # c.run(f'cd {home_folder}')


@task
def prepare_joplin_server(c):
    prepare_generic_server(c)
    install_joplin(c)


@task
def create_virtualenv(c, name):
    failsafe(lambda: c.run(f'virtualenv ".virtualenvs/{name}"  '))


# @task
# def install_ontwikkelstraat(c, is_production=False, dotenvpath=None):
#     clone_git_repo_with_new_key_file_for_edwh_repos(
#         c, "educationwarehouse/ontwikkelstraat", "r" if is_production else "rw"
#     )
#     # vox new ontwikkelstraa
#     # create_virtualenv(c, "ontwikkelstraat")
#     # def in_venv(arg):
#     #     return ".virtualenvs/ontwikkelstraat/bin/" + arg
#     if execution_fails(c, "python3 -c 'import redis'"):
#         c.run("pip install --user redis ")
#
#     ## begin met alles te resetten naar de standaard
#     # ubuntu:ubuntu als eigenaar van elk bestand en directory
#     c.sudo("chown ubuntu:ubuntu -R ontwikkelstraat ")
#     # vevolgens zetten we directories op rwxr-xr-x
#     c.sudo(r"find ontwikkelstraat -type d -exec chmod 755 {} \;")
#     # en files op rw-rw-r--
#     c.sudo(r"find ontwikkelstraat -type f -exec chmod 644 {} \;")
#     ## zet nu de eigenaar naar microservices voor alle apps van py4web
#     c.sudo("chown microservices:microservices -R ontwikkelstraat/apps")
#     ## zorg ervoor dat letsencrypt (en entuele .json files) de juiste rechten hebben.
#     c.sudo("chmod 600 -R ontwikkelstraat/letsencrypt/*.json")
#     c.sudo("chown root:root -R ontwikkelstraat/letsencrypt")
#     # tot hier ...
#     # .env file instellen/kopieren
#     # docker builden via `docker compose build`
#     # uitvoeren via `invoke up -d?`
#


def at_least(iterable: typing.Iterable, n: int):
    """
    Like 'all()' or 'any()' but for at least 'n'

    https://stackoverflow.com/questions/42514445/clever-any-like-function-to-check-if-at-least-n-elements-are-true
    """
    if n < 1:
        return True
    counter = 0
    for x in iterable:
        if x:
            counter += 1
            if counter == n:
                return True
    return False


@task(
    iterable=["omgeving"],
    help=dict(
        omgeving="Directory waarin opdrachten worden uitgevoerd, kan meerdere keren voorkomen.",
        cmd="Willekeurig welk shell commando.",
        invoke='argumenten aan invoke, denk eraan dat er 1 argument wordt opgegeven vanuit de cli, dus gebruik "" om meerdere mee te geven.',
    ),
)
def do(c, omgeving=None, cmd=None, invoke=None, edwh=None):
    """
    Voert remote commandos of invoke statements uit, binnen de opgegeven omgeving(en).

    cmd kan ook gebruikt worden voor troubleshooting/scripting.
    bijvoorbeeld:

      fab -H utils do --omgeving taiga --invoke "restart --quick" -e

    """
    current_user = c.user
    bin_path = f"/home/{current_user}/.local/bin"

    if not omgeving:
        omgeving = ["."]

    if at_least([cmd, invoke, edwh], 2):
        print("Gebruik slechts --invoke of --cmd, niet beide")
        exit(1)
    elif cmd:
        commando = cmd
    elif invoke:
        commando = f"{bin_path}/invoke {invoke}"
    elif edwh:
        commando = f"{bin_path}/edwh {edwh}"
    else:
        print("Gebruik ofwel cmd, edwh of invoke")
        exit(1)
    for directory in omgeving:
        print("Uitvoeren voor ", directory)
        # omgeving is een lijst van omgevingen
        c.run(f"cd {directory}; {commando}")


@task(
    help={
        "clone_source_url": '"educationwarehouse/repo" of andere toevoeging achter https://github.com/',
        "is_production": "in productie alleen lees rechten op de repo, anders lees en schrijf rechten.",
        "omgeving": "De target directory voor deze omgeving als subfolder in de home van de connectie.",
    }
)
def install_omgeving(c, clone_source_url, omgeving, is_production=False, branch=None):
    """
    Clone een git repository naar de directory `omgeving` in de homefolder, en voer `edwh setup` daar uit.
    """
    clone_git_repo_with_new_key_file_for_edwh_repos(
        c,
        clone_source_url,
        "r" if is_production else "rw",
        target_directory=omgeving,
        branch=branch,
    )
    do(c, omgeving=[omgeving], edwh="setup")


@task(
    help={
        "clone_source_url": '"educationwarehouse/generic-service" of andere toevoeging achter https://github.com/',
        "is_production": "in productie alleen lees rechten op de repo, anders lees en schrijf rechten.",
        "omgeving": "De target directory voor deze omgeving als subfolder in de home van de connectie.",
    }
)
def install_generic_service(
    c, omgeving, clone_source_url="educationwarehouse/generic-service", is_production=False, branch=None
):
    """
    Lijkt op install_omgeving maar dan voor een generic-service (die nog niet af is), dus zonder `edwh setup`
    """
    clone_git_repo_with_new_key_file_for_edwh_repos(
        c,
        clone_source_url,
        "r" if is_production else "rw",
        target_directory=omgeving,
        branch=branch,
    )

    # NO ew setup, since this service is (probably) not functional yet.


@task
def prepare_ontwikkelstraat_server(c, is_production=False):
    prepare_generic_server(c)
    # install_ontwikkelstraat(c)
    if is_production:
        subscription_key = input(
            "WithSecure linux server Subscription Key (https://elements.f-secure.com/apps/psb/c556915/subscription) [blank=ignore]: "
        )
        if subscription_key.strip():
            install_antivirus(c, subscription_key=subscription_key)
            print(r"/!\ Denk eraan, hier moet nog een profiel aan gekoppeld worden in de withsecure website! ")


@task(pre=[edwh.tasks.require_sudo])
def install_antivirus(c, subscription_key):
    c: Connection
    subscription_key: str
    c.run(
        "curl https://download.sp.f-secure.com/linuxsecurity64/f-secure-linuxsecurity.deb -o f-secure-linuxsecurity.deb"
    )
    c.sudo("dpkg -i f-secure-linuxsecurity.deb")
    # https://help.f-secure.com/product.html#business/linux-protection/latest/en/task_7C893CC525EF4BA5B7B4477FDE23E40F-latest-en
    c.sudo(f"/opt/f-secure/linuxsecurity/bin/activate --psb --subscription-key {subscription_key}")


# @task
# def new_proxy(c, docker_compose_path):
#     dc_path =


def read_dotenv_remote(c: Connection, path: Path):
    lines = c.run(f"cat {path}", hide=True).stdout.split("\n")

    # remove comments
    lines = [line.split("#", 1)[0] for line in lines]
    # remove redundant whitespace
    lines = [line.strip() for line in lines]
    # keep lines with values
    lines = [line for line in lines if line]
    # convert to tuples
    items = [line.split("=", 1) for line in lines]
    # clean the tuples
    items = [(key.strip(), value.strip()) for key, value in items]
    # convert to dict for quick lookup of keys
    return dict(items)


@task
def connect_postgres(c, omgeving=None, port=None, local_port=None):
    """
    Forward a remote port (--port or 5432) to the host machine (--local-port or 5432).
    If --omgeving is passed, the PG_PORT is used from the .env file (or 5432)
    """

    if omgeving and port:
        raise ValueError("Geef of --omgeving of --poort op, niet allebei.")
    elif omgeving:
        path = Path(omgeving) / ".env"
        vars = read_dotenv_remote(c, path)

        port = int(vars.get("PGPOOL_PORT", 5432))
    elif not port:
        port = 5432
    else:
        port = int(port)

    if local_port:
        local_port = int(local_port)
    else:
        local_port = 5432

    c: Connection
    import time

    with c.forward_local(local_port, port, "127.0.0.1", "127.0.0.1"):
        print(f"Connected remote :{port} to local :{local_port}, sleeping until Ctrl-C")
        while True:
            try:
                time.sleep(3)
            except KeyboardInterrupt:
                print("closing connection.")
                break


@task(pre=[edwh.tasks.require_sudo])
def require_npx(c):
    # npm installs npx
    c.sudo("npm --version > /dev/null || sudo apt install npm -y")


def background_run(c, command):
    # command = 'nohup %s &> /dev/null &' % command
    command = "nohup '%s' >& /dev/null < /dev/null &" % command
    c.run(command, pty=False)


@task(pre=[edwh.tasks.require_sudo])
def kill_ungit(c):
    c.sudo("ps aux | grep ungit | cut -d' ' -f5 | xargs kill", hide=True, warn=True)


@task(pre=[require_npx])
def ungit(c, omgeving="ontwikkelstraat", port=8111):
    """
    Open an 'ungit' session and forward to localhost so you can access it.
    """
    # make sure no old crap is running:
    kill_ungit(c)

    try:
        with c.forward_local(port, port, "127.0.0.1", "127.0.0.1"):
            print(f"Port {port} forwarded.")

            ungit_cmd = f"npx -y ungit@latest --port {port}"
            with c.cd(omgeving):
                c.run(ungit_cmd)
                print("If ungit is hanging, try `kill-ungit`")

            while True:
                time.sleep(3)

    except KeyboardInterrupt:
        print("closing connection and killing ungit processes.")
        kill_ungit(c)


@task()
def new_ghost(c, service, url, path, docker_compose_path, yes=False, also_www=True):
    """
    Creates a new ghost instance docker compose fragment.

    :type c: Connection
    :param service: Name of the service, used for `dc up <service>`, should be a valid python identifier
    :type service: str
    :param url: url (with protocol)
    :type url: str
    :param path: <path>_content is used for files
    :type path: str
    :param docker_compose_path: where is docker_compose located, based from the homefolder
    :param yes: do not prompt, force append
    :type yes: bool
    """
    if not service.isidentifier():
        raise ValueError(f"Service should be a pure alpha identifer, not `{service}`")
    # keep only the domain name
    url = urllib.parse.urlparse(url).netloc
    if not url:
        raise ValueError(f"Invalid URL: {url}")
    # test for the existence of the docker-compose file, alerting about a bad path when wrong
    if execution_fails(c, f"cat {docker_compose_path}/docker-compose.yaml"):
        raise ValueError(
            f"docker-compose-path argument is invalid. `{docker_compose_path}/docker-compose.yaml` does not exist"
        )
    also_www = f",`www.{url}`" if also_www else ""
    compose_fragment = textwrap.dedent(
        f"""
    ### {service} ######################################
    
      {service}:
        # https://hub.docker.com/_/ghost - official ghost image
        image: ghost:4.33.1
        restart: unless-stopped
        expose:
          - 2368
        environment:
          # see https://ghost.org/docs/config/#configuration-options
          url: https://{url} 
        volumes:
          - type: bind
            source: ./{path}_content # aanpassen per ghost instance
            target: /var/lib/ghost/content
        networks:
          - ghosts
        labels:
          - "traefik.enable=true"
          # http only
          - "traefik.http.routers.{service}.rule=Host(`{url}`{also_www})" # aanpassen per ghost instance
          # https only
          - "traefik.http.routers.{service}-secure.rule=Host(`{url}`{also_www})" # aanpassen per ghost instance
          - "traefik.http.routers.{service}-secure.tls=true" 
          - "traefik.http.routers.{service}-secure.tls.certresolver=letsencrypt" 
          # www to non-www
          - "traefik.http.routers.{service}-secure.middlewares=www-redirect"
          # http to https 
          - "traefik.http.middlewares.{service}-redirectscheme.redirectscheme.scheme=https"
          # gzip compress 
          - "traefik.http.middlewares.{service}-compress.compress=true"
    
    """
    )
    print("------- [new] ---------------------------------------------------- ")
    print(compose_fragment)
    if yes or input(f"append to {docker_compose_path}/docker-compose.yaml? [NO,yes] #").lower().strip() in {
        "y",
        "yes",
        "j",
        "ja",
        "1",
    }:
        print("Copying compose file to docker-compose.bak")
        c.run(
            f"cp {docker_compose_path}/docker-compose.yaml {docker_compose_path}/docker-compose.bak",
            hide=True,
        )
        # craft the directory if it doesn't exist already
        c.run(f"mkdir {docker_compose_path}/{path}_content", warn=True, hide=True)
        # create a new in memory file like object
        buffer = io.BytesIO()
        # read the remote file into the buffer
        print(c.get(f"{docker_compose_path}/docker-compose.yaml", buffer))
        # append a newline
        buffer.write(b"\n")
        # append the fragment (convert to bytes)
        buffer.write(compose_fragment.encode("utf-8"))
        # set the filepointer to the beginning of the file object
        # so following reads will read from the start of the file
        buffer.seek(0)
        # upload from the buffer, overwriting the original docker-compose.yaml
        print(c.put(buffer, f"{docker_compose_path}/docker-compose.yaml"))
    else:
        print("Nothing changed. ")
