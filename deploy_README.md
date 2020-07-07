# RPL-2.0-runner deploy

- Me cree un host en Vultr
- Agrego user y lo agrego al grupo root 
    - useradd ale-vultr
    - usermod -aG sudo ale-vultr
- Descargo docker 
    - wget -qO- https://get.docker.io/ | sh
    - sudo gpasswd -a ale-vultr docker
- Creo ssh keys
    - ssh-keygen
- Copio las ssh keys y las pego en el repo de github en la parte de deploy keys
- Clono repo
    - git clone git@github.com:alelevinas/RPL-2.0-runner.git rpl_runner_receiver
- instalo dependencias
    - cd rpl_runner_receiver && pip install -r requirements.txt
- Buildeo imagen docker de corridas de submissions rpl
    - docker build -t rpl-2.0-runner ./rpl_runner

- Declaro service
    - sudo vim /etc/systemd/system/rpl_receiver.service
        ```
        Ver archivo deploy.service
        ```
    - Chequeo que exista `sudo systemctl list-unit-files  | grep rpl`

- Starteo service
    - sudo systemctl daemon-reload
    - sudo systemctl restart rpl_receiver.service

- Miro status
    - sudo systemctl status rpl_receiver.service

- Miro logs
    - journalctl -f --unit rpl_receiver.service 