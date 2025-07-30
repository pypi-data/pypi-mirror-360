#!/usr/bin/python
# -*- coding: utf-8 -*-

from signate import info
import click
import warnings
import requests
import os
from signate import config
from tabulate import tabulate
from datetime import timedelta
import mimetypes
import base64

api_session = requests.Session()
api_session.headers.update({"User-Agent": config.USER_AGENT})

def success(message):
    click.echo(click.style(message, fg='green'))
    exit(0)

def warn(message):
    click.echo(click.style(message, fg='yellow'))

def error(message):
    click.echo(click.style(message, fg='red'))

def die(message):
    error(message)
    exit(1)

@click.group()
@click.version_option(version=info.VERSION)
def cli():
    pass

def main():
    warnings.filterwarnings(action='ignore')
    try:
        cli()
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)

@cli.command()
@click.option('-e', '--email', type=str, required=True, help='The email address to be registered')
def token(email):
    # パスワード入力
    password = click.prompt('Password', type=str, hide_input=True)

    # CSRFトークン取得
    getToken()
    userCsrf = getCookieTarget('_user_csrf_cloud')
    # ユーザーサインイン
    signIn(userCsrf, email, password)
    # 組織ログイン
    signInOrganization(userCsrf)
    jwt = getCookieTarget(config.JWT_COOKIE_KEY)
    # 保存
    setApiToken(jwt)
    success('The API Token has been downloaded successfully.')


@cli.command(name='competition-list')
def competition_list():
    try:
        api_session.cookies.set(config.JWT_COOKIE_KEY, getApiToken())
        response = api_session.get(
            config.COMPETITION_URL + '/competition/list?status=open',
            headers={
                "Content-Type": "application/json",
            }
        )
        response.raise_for_status()

        competition_list = response.json()['competition_list']
        for item in competition_list:
            item['remaining'] = format_remaining_time(item['remaining_second'])

        columns = ['public_key', 'title', 'remaining', 'reward', 'entry_count']
        filtered_data = [{key: item[key] for key in columns if key in item} for item in
                         competition_list]


        click.echo(tabulate(filtered_data, headers='keys', tablefmt='simple', stralign='left'))
    except requests.exceptions.HTTPError as http_err:
        try:
            error_detail = response.json()
        except ValueError:
            error_detail = response.text
        error(f"HTTP Error occurred: {http_err}")
        error(f"Response content: {error_detail}")
    except requests.exceptions.ConnectionError as conn_err:
        error(f"Connection Error occurred: {conn_err}")
        die("Failed to connect to the server. Please check your network connection.")
    except requests.exceptions.Timeout as timeout_err:
        error(f"Timeout Error occurred: {timeout_err}")
        die("No response from the server. Please try again later.")
    except requests.exceptions.RequestException as req_err:
        error(f"An unexpected error occurred: {req_err}")
        die("An error occurred during the organization sign-in process.")

@cli.command(name='task-list')
@click.option('--competition_key', type=str, required=True)
def task_list(competition_key):
    try:
        api_session.cookies.set(config.JWT_COOKIE_KEY, getApiToken())
        response = api_session.get(
            config.COMPETITION_URL + f"/task/{competition_key}/list",
            headers={
                "Content-Type": "application/json",
            }
        )
        response.raise_for_status()

        task_list = response.json()['task_list']
        columns = ['public_key', 'task_name']
        filtered_data = [{key: item[key] for key in columns if key in item} for item in
                         task_list]
        click.echo(tabulate(filtered_data, headers='keys', tablefmt='simple', stralign='left'))
    except requests.exceptions.HTTPError as http_err:
        try:
            error_detail = response.json()
        except ValueError:
            error_detail = response.text
        error(f"HTTP Error occurred: {http_err}")
        error(f"Response content: {error_detail}")
    except requests.exceptions.ConnectionError as conn_err:
        error(f"Connection Error occurred: {conn_err}")
        die("Failed to connect to the server. Please check your network connection.")
    except requests.exceptions.Timeout as timeout_err:
        error(f"Timeout Error occurred: {timeout_err}")
        die("No response from the server. Please try again later.")
    except requests.exceptions.RequestException as req_err:
        error(f"An unexpected error occurred: {req_err}")
        die("An error occurred during the organization sign-in process.")

@cli.command(name='file-list')
@click.option('--task_key', type=str, required=True)
def file_list(task_key):
    try:
        api_session.cookies.set(config.JWT_COOKIE_KEY, getApiToken())
        response = api_session.get(
            config.COMPETITION_URL + f"/dataset/{task_key}",
            headers={
                "Content-Type": "application/json",
            }
        )
        response.raise_for_status()

        public_file_list = response.json()['public_file_list']
        for item in public_file_list:
            item['file_size'] = format_file_size(item['file_size'])
        columns = ['public_key', 'file_name', 'title', 'file_size']
        filtered_data = [{key: item[key] for key in columns if key in item} for item in
                         public_file_list]
        click.echo(tabulate(filtered_data, headers='keys', tablefmt='simple', stralign='left'))
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 401:
            die('If your sign-in session has expired, please sign in again.')
        elif response.status_code == 404:
            die('If you haven’t joined the competition yet, please do so through your browser.')
        else:
            try:
                error_detail = response.json()
            except ValueError:
                error_detail = response.text
            error(f"HTTP Error occurred: {http_err}")
            error(f"Response content: {error_detail}")
    except requests.exceptions.ConnectionError as conn_err:
        error(f"Connection Error occurred: {conn_err}")
        die("Failed to connect to the server. Please check your network connection.")
    except requests.exceptions.Timeout as timeout_err:
        error(f"Timeout Error occurred: {timeout_err}")
        die("No response from the server. Please try again later.")
    except requests.exceptions.RequestException as req_err:
        error(f"An unexpected error occurred: {req_err}")
        die("An error occurred during the organization sign-in process.")

@cli.command()
@click.option('--task_key', type=str, required=True)
@click.option('--file_key', type=str, required=True)
@click.option('--path', type=str, required=False)
def download(task_key, file_key, path):
    try:
        api_session.cookies.set(config.JWT_COOKIE_KEY, getApiToken())
        # ファイル名取得
        response = api_session.get(
            config.COMPETITION_URL + f"/dataset/{task_key}",
            headers={
                "Content-Type": "application/json",
            }
        )
        response.raise_for_status()

        public_file_list = response.json()['public_file_list']
        file_data = next((item for item in public_file_list if item['public_key'] == file_key), None)
        file_name = file_data['file_name'] if file_data else None

        if file_name is None:
            die(f"File with key {file_key} not found.")

        response = api_session.get(
            config.COMPETITION_URL + f"/storage/{task_key}/public_file/{file_key}",
            headers={
                "Content-Type": "application/json",
            }
        )
        response.raise_for_status()

        file_path = path if path is not None else file_name

        with open(file_path, 'wb') as file:
            file.write(response.content)

    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 401:
            die('If your sign-in session has expired, please sign in again.')
        elif response.status_code == 404:
            die('If you haven’t joined the competition yet, please do so through your browser.')
        else:
            try:
                error_detail = response.json()
            except ValueError:
                error_detail = response.text
            error(f"HTTP Error occurred: {http_err}")
            error(f"Response content: {error_detail}")
    except requests.exceptions.ConnectionError as conn_err:
        error(f"Connection Error occurred: {conn_err}")
        die("Failed to connect to the server. Please check your network connection.")
    except requests.exceptions.Timeout as timeout_err:
        error(f"Timeout Error occurred: {timeout_err}")
        die("No response from the server. Please try again later.")
    except requests.exceptions.RequestException as req_err:
        error(f"An unexpected error occurred: {req_err}")
        die("An error occurred during the organization sign-in process.")

@cli.command()
@click.option('--task_key', type=str, required=True)
@click.option('--memo', type=str, required=False)
@click.argument('file_path', type=click.Path(exists=True))
def submit(task_key, memo, file_path):
    try:
        file_name = os.path.basename(file_path)

        # ファイルの読み込み（バイナリ）
        with open(file_path, 'rb') as f:
            raw = f.read()
            base64_body = base64.b64encode(raw).decode('utf-8')

        # 拡張子からMIMEタイプを推定（例: .csv → text/csv）
        mime_type, _ = mimetypes.guess_type(file_name)
        if not mime_type:
            mime_type = 'application/octet-stream'  # fallback

        # Data URI形式にする
        file_content = f"data:{mime_type};base64,{base64_body}"

        # メモがなければ空文字にする
        memo = memo if memo else ""

        payload = {
            "public_key": task_key,
            "file_content": file_content,
            "file_name": file_name,
            "memo": memo
        }
        api_session.cookies.set(config.JWT_COOKIE_KEY, getApiToken())
        response = api_session.post(
            config.COMPETITION_URL + f"/submission",
            headers={
                "Content-Type": "application/json",
            },
            json=payload
        )
        response.raise_for_status()
        success("Submission completed successfully.")

    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 401:
            die('If your sign-in session has expired, please sign in again.')
        elif response.status_code == 404:
            die('If you haven’t joined the competition yet, please do so through your browser.')
        else:
            try:
                error_detail = response.json()
            except ValueError:
                error_detail = response.text
            error(f"HTTP Error occurred: {http_err}")
            error(f"Response content: {error_detail}")
    except requests.exceptions.ConnectionError as conn_err:
        error(f"Connection Error occurred: {conn_err}")
        die("Failed to connect to the server. Please check your network connection.")
    except requests.exceptions.Timeout as timeout_err:
        error(f"Timeout Error occurred: {timeout_err}")
        die("No response from the server. Please try again later.")
    except requests.exceptions.RequestException as req_err:
        error(f"An unexpected error occurred: {req_err}")
        die("An error occurred during the organization sign-in process.")


def getToken():
    try:
        response = api_session.get(config.CLOUD_URL + '/v1/token')
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as errh:
        die(f"HTTP Error occurred: {errh}")
    except requests.exceptions.ConnectionError as errc:
        die(f"Connection Error occurred: {errc}")
    except requests.exceptions.Timeout as errt:
        die(f"Timeout Error occurred: {errt}")
    except requests.exceptions.RequestException as err:
        die(f"An unexpected error occurred: {err}")

def getCookieTarget(target):
    value = next((c.value for c in api_session.cookies if c.name == target), None)
    if not value:
        die(f"Could not retrieve the value for {target}.")
    return value


def signIn(userCsrf, email, password):
    try:
        response = api_session.post(
            config.CLOUD_URL + '/v1/sign_in',
            headers={
                "Content-Type": "application/json",
                "X-CSRF-Token": userCsrf
            },
            json={
                'email': email,
                'password': password,
                'individual': True
            }
        )
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as http_err:
        error(f"HTTP Error occurred: {http_err}")
        die("Failed to sign in. Please check your email and password.")
    except requests.exceptions.ConnectionError as conn_err:
        error(f"Connection Error occurred: {conn_err}")
        die("Failed to connect to the server. Please check your network connection.")
    except requests.exceptions.Timeout as timeout_err:
        error(f"Timeout Error occurred: {timeout_err}")
        die("No response from the server. Please try again later.")
    except requests.exceptions.RequestException as req_err:
        error(f"An unexpected error occurred: {req_err}")
        die("An error occurred during the sign-in process.")

def signInOrganization(csrf):
    try:
        response = api_session.post(
            config.CLOUD_URL + '/v1/organizations/sign_in',
            headers={
                "Content-Type": "application/json",
                "X-CSRF-Token": csrf
            },
            json={
                'id': config.DEFAULT_ORGANIZATION_ID
            }
        )
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as http_err:
        error(f"HTTP Error occurred: {http_err}")
        die("Failed to sign in to the organization.")
    except requests.exceptions.ConnectionError as conn_err:
        error(f"Connection Error occurred: {conn_err}")
        die("Failed to connect to the server. Please check your network connection.")
    except requests.exceptions.Timeout as timeout_err:
        error(f"Timeout Error occurred: {timeout_err}")
        die("No response from the server. Please try again later.")
    except requests.exceptions.RequestException as req_err:
        error(f"An unexpected error occurred: {req_err}")
        die("An error occurred during the organization sign-in process.")

def setApiToken(token):
    config_dir = os.path.expanduser(config.CONFIG_DIR)
    config_file_name = os.path.join(config_dir, config.CONFIG_FILE_NAME)
    if not os.path.isdir(config_dir):
        os.makedirs(config_dir)
    try:
        with open(config_file_name, 'w') as tokenFile:
            tokenFile.write(token)
    except IOError as e:
        die(f"I/O Error occurred: {e}")

def getApiToken():
    config_dir = os.path.expanduser(config.CONFIG_DIR)
    file_name = os.path.join(config_dir, config.CONFIG_FILE_NAME)
    if not os.path.isfile(file_name):
        die("Please sign in using the following token command:\nex) signate token -e xxxx@sample.com")
    try:
        with open(file_name, 'r') as tokenFile:
            api_token = tokenFile.read()
    except IOError as e:
        die(f"I/O Error occurred: {e}")
    return api_token

def format_remaining_time(remaining_second):
    if remaining_second is None:
        return "-"

    # 秒数を timedelta に変換
    remaining_time = timedelta(seconds=remaining_second)

    if remaining_time.days >= 1:
        # 日数が1日以上ある場合
        return f"{remaining_time.days} days"
    else:
        # 1日未満の場合は秒数表示
        return f"{remaining_time.seconds} seconds"

def format_file_size(size):
    # バイト数を適切な単位に変換する
    for unit in ['Byte', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"  # 1TB以上の場合
