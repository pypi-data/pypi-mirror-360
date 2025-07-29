# -*- coding: utf-8 -*-
# Quasarr
# Project by https://github.com/rix1337

import os
import sys

import requests
from bottle import Bottle, request

import quasarr
import quasarr.providers.sessions.al
import quasarr.providers.sessions.dd
import quasarr.providers.sessions.nx
from quasarr.providers.html_templates import render_button, render_form, render_success, render_fail
from quasarr.providers.log import info
from quasarr.providers.shared_state import extract_valid_hostname
from quasarr.providers.web_server import Server
from quasarr.storage.config import Config


def path_config(shared_state):
    app = Bottle()

    current_path = os.path.dirname(os.path.abspath(sys.argv[0]))

    @app.get('/')
    def config_form():
        config_form_html = f'''
            <form action="/api/config" method="post">
                <label for="config_path">Path</label>
                <input type="text" id="config_path" name="config_path" placeholder="{current_path}"><br>
                {render_button("Save", "primary", {"type": "submit"})}
            </form>
            '''
        return render_form("Press 'Save' to set desired path for configuration",
                           config_form_html)

    def set_config_path(config_path):
        config_path_file = "Quasarr.conf"

        if not config_path:
            config_path = current_path

        config_path = config_path.replace("\\", "/")
        config_path = config_path[:-1] if config_path.endswith('/') else config_path

        if not os.path.exists(config_path):
            os.makedirs(config_path)

        with open(config_path_file, "w") as f:
            f.write(config_path)

        return config_path

    @app.post("/api/config")
    def set_config():
        config_path = request.forms.get("config_path")
        config_path = set_config_path(config_path)
        quasarr.providers.web_server.temp_server_success = True
        return render_success(f'Config path set to: "{config_path}"',
                              5)

    info(f'Starting web server for config at: "{shared_state.values['internal_address']}".')
    info("Please set desired config path there!")
    return Server(app, listen='0.0.0.0', port=shared_state.values['port']).serve_temporarily()


def hostnames_config(shared_state):
    app = Bottle()

    @app.get('/')
    def hostname_form():
        hostname_fields = '''
        <label for="{id}">{label}</label>
        <input type="text" id="{id}" name="{id}" placeholder="example.com" autocorrect="off" autocomplete="off"><br>
        '''

        hostname_form_content = "".join(
            [hostname_fields.format(id=label.lower(), label=label) for label in shared_state.values["sites"]])

        hostname_form_html = f'''
        <p>
          If you're having trouble setting this up, take a closer look at 
          <a href="https://github.com/rix1337/Quasarr?tab=readme-ov-file#instructions" target="_blank" rel="noopener noreferrer">
            step one of the instructions.
          </a>
        </p>
        <form action="/api/hostnames" method="post">
            {hostname_form_content}
            {render_button("Save", "primary", {"type": "submit"})}
        </form>
        '''

        return render_form("Set at least one valid hostname", hostname_form_html)

    @app.post("/api/hostnames")
    def set_hostnames():
        hostnames = Config('Hostnames')

        hostname_set = False
        message = "No valid hostname provided!"

        for key in shared_state.values["sites"]:
            shorthand = key.lower()
            hostname = request.forms.get(shorthand)
            if shorthand and hostname:
                domain_check = extract_valid_hostname(hostname, shorthand)
                domain = domain_check.get('domain', None)
                message = domain_check.get('message', "Error checking the hostname you provided!")

                if domain:
                    hostnames.save(key, domain)
                    hostname_set = True

        if hostname_set:
            message = "At least one valid hostname set!"
            quasarr.providers.web_server.temp_server_success = True
            return render_success(message, 5)
        else:
            return render_fail(message)

    info(f'Hostnames not set. Starting web server for config at: "{shared_state.values['internal_address']}".')
    info("Please set at least one valid hostname there!")
    return Server(app, listen='0.0.0.0', port=shared_state.values['port']).serve_temporarily()


def hostname_credentials_config(shared_state, shorthand, domain):
    app = Bottle()

    shorthand = shorthand.upper()

    @app.get('/')
    def credentials_form():
        form_content = f'''
        <span>If required register account at: <a href="https://{domain}">{domain}</a>!</span><br><br>
        <label for="user">Username</label>
        <input type="text" id="user" name="user" placeholder="User" autocorrect="off"><br>

        <label for="password">Password</label>
        <input type="password" id="password" name="password" placeholder="Password"><br>
        '''

        form_html = f'''
        <form action="/api/credentials/{shorthand}" method="post">
            {form_content}
            {render_button("Save", "primary", {"type": "submit"})}
        </form>
        '''

        return render_form(f"Set User and Password for {shorthand}", form_html)

    @app.post("/api/credentials/<sh>")
    def set_credentials(sh):
        user = request.forms.get('user')
        password = request.forms.get('password')
        config = Config(shorthand)

        if user and password:
            config.save("user", user)
            config.save("password", password)

            if sh.lower() == "al":
                if quasarr.providers.sessions.al.create_and_persist_session(shared_state):
                    quasarr.providers.web_server.temp_server_success = True
                    return render_success(f"{sh} credentials set successfully", 5)
            if sh.lower() == "dd":
                if quasarr.providers.sessions.dd.create_and_persist_session(shared_state):
                    quasarr.providers.web_server.temp_server_success = True
                    return render_success(f"{sh} credentials set successfully", 5)
            if sh.lower() == "nx":
                if quasarr.providers.sessions.nx.create_and_persist_session(shared_state):
                    quasarr.providers.web_server.temp_server_success = True
                    return render_success(f"{sh} credentials set successfully", 5)

        config.save("user", "")
        config.save("password", "")
        return render_fail("User and Password wrong or empty!")

    info(
        f'"{shorthand.lower()}" credentials required to access download links. '
        f'Starting web server for config at: "{shared_state.values['internal_address']}".')
    info(f"If needed register here: 'https://{domain}'")
    info("Please set your credentials now, to allow Quasarr to launch!")
    return Server(app, listen='0.0.0.0', port=shared_state.values['port']).serve_temporarily()


def flaresolverr_config(shared_state):
    app = Bottle()

    @app.get('/')
    def url_form():
        form_content = '''
        <span><a href="https://github.com/FlareSolverr/FlareSolverr?tab=readme-ov-file#installation">A local instance</a>
        must be running and reachable to Quasarr!</span><br><br>
        <label for="url">FlareSolverr URL</label>
        <input type="text" id="url" name="url" placeholder="http://192.168.0.1:8191/v1"><br>
        '''
        form_html = f'''
        <form action="/api/flaresolverr" method="post">
            {form_content}
            {render_button("Save", "primary", {"type": "submit"})}
        </form>
        '''
        return render_form("Set FlareSolverr URL", form_html)

    @app.post('/api/flaresolverr')
    def set_flaresolverr_url():
        url = request.forms.get('url').strip()
        config = Config("FlareSolverr")

        if url:
            try:
                headers = {"Content-Type": "application/json"}
                data = {
                    "cmd": "request.get",
                    "url": "http://www.google.com/",
                    "maxTimeout": 30000
                }
                response = requests.post(url, headers=headers, json=data, timeout=30)
                if response.status_code == 200:
                    config.save("url", url)
                    print(f'Using Flaresolverr URL: "{url}"')
                    quasarr.providers.web_server.temp_server_success = True
                    return render_success("FlareSolverr URL saved successfully!", 5)
            except requests.RequestException:
                pass

        # on failure, clear any existing value and notify user
        config.save("url", "")
        return render_fail("Could not reach FlareSolverr at that URL (expected HTTP 200).")

    info(
        '"flaresolverr" URL is required for proper operation. '
        f'Starting web server for config at: "{shared_state.values["internal_address"]}".'
    )
    info("Please enter your FlareSolverr URL now.")
    return Server(app, listen='0.0.0.0', port=shared_state.values['port']).serve_temporarily()


def jdownloader_config(shared_state):
    app = Bottle()

    @app.get('/')
    def jd_form():
        verify_form_html = f'''
        <span>If required register account at: <a href="https://my.jdownloader.org/login.html#register">
        my.jdownloader.org</a>!</span><br>
        
        <p><strong>JDownloader must be running and connected to My JDownloader!</strong></p><br>
        
        <form id="verifyForm" action="/api/verify_jdownloader" method="post">
            <label for="user">E-Mail</label>
            <input type="text" id="user" name="user" placeholder="user@example.org" autocorrect="off"><br>
            <label for="pass">Password</label>
            <input type="password" id="pass" name="pass" placeholder="Password"><br>
            {render_button("Verify Credentials",
                           "secondary",
                           {"id": "verifyButton", "type": "button", "onclick": "verifyCredentials()"})}
        </form>
        
        <p>Some JDownloader settings will be enforced by Quasarr on startup.</p>
        
        <form action="/api/store_jdownloader" method="post" id="deviceForm" style="display: none;">
            <input type="hidden" id="hiddenUser" name="user">
            <input type="hidden" id="hiddenPass" name="pass">
            <label for="device">JDownloader</label>
            <select id="device" name="device"></select><br>
            {render_button("Save", "primary", {"type": "submit"})}
        </form>
        <p><strong>Saving may take a while!</strong></p><br>
        '''

        verify_script = '''
        <script>
        function verifyCredentials() {
            var user = document.getElementById('user').value;
            var pass = document.getElementById('pass').value;
            fetch('/api/verify_jdownloader', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({user: user, pass: pass}),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    var select = document.getElementById('device');
                    data.devices.forEach(device => {
                        var opt = document.createElement('option');
                        opt.value = device;
                        opt.innerHTML = device;
                        select.appendChild(opt);
                    });
                    document.getElementById('hiddenUser').value = document.getElementById('user').value;
                    document.getElementById('hiddenPass').value = document.getElementById('pass').value;
                    document.getElementById("verifyButton").style.display = "none";
                    document.getElementById('deviceForm').style.display = 'block';
                } else {
                    alert('Fehler! Bitte die Zugangsdaten überprüfen.');
                }
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        }
        </script>
        '''
        return render_form("Set your credentials for My JDownloader", verify_form_html, verify_script)

    @app.post("/api/verify_jdownloader")
    def verify_jdownloader():
        data = request.json
        username = data['user']
        password = data['pass']

        devices = shared_state.get_devices(username, password)
        device_names = []

        if devices:
            for device in devices:
                device_names.append(device['name'])

        if device_names:
            return {"success": True, "devices": device_names}
        else:
            return {"success": False}

    @app.post("/api/store_jdownloader")
    def store_jdownloader():
        username = request.forms.get('user')
        password = request.forms.get('pass')
        device = request.forms.get('device')

        config = Config('JDownloader')

        if username and password and device:
            config.save('user', username)
            config.save('password', password)
            config.save('device', device)

            if not shared_state.set_device_from_config():
                config.save('user', "")
                config.save('password', "")
                config.save('device', "")
            else:
                quasarr.providers.web_server.temp_server_success = True
                return render_success("Credentials set",
                                      15)

        return render_fail("Could not set credentials!")

    info(
        f'My-JDownloader-Credentials not set. '
        f'Starting web server for config at: "{shared_state.values['internal_address']}".')
    info("If needed register here: 'https://my.jdownloader.org/login.html#register'")
    info("Please set your credentials now, to allow Quasarr to launch!")
    return Server(app, listen='0.0.0.0', port=shared_state.values['port']).serve_temporarily()
