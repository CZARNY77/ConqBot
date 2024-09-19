from flask import Flask, render_template_string, render_template, jsonify, request
from flask_cors import CORS
import json
from dotenv import load_dotenv
import os
import mysql.connector
import requests
from aiohttp import web

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
API_URL = 'https://discord.com/api/v10'
GUILD_ID = '1232957904597024882'
role_id = '1236647699831586838'
headers = {'Authorization': f'Bot {TOKEN}'}
BOT_KEY = f"{os.getenv('BOT_KEY')}"

template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Discord/HTML/templates')
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Discord/HTML/static')
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
CORS(app)
mydb = None
cursor = None

@app.route('/')
def hello_world():
    global mydb
    global cursor
    headers = {
        'Authorization': f'Bot {TOKEN}'
    }
    mydb = connect_with_db()
    cursor.execute(f"SELECT id_player, nick, signup_points, TW_points FROM Players WHERE discord_server_id = %s", (1232957904597024882, ))
    dane = cursor.fetchall()
    cursor.execute(f"SELECT COUNT(*) FROM TW WHERE discord_server_id = %s", (1232957904597024882, ))
    count_TW = cursor.fetchall()
    count_TW = count_TW[0][0] - 1
    data = []
    not_verified_data = []
    others_data = []
    if cursor:
        cursor.close()
    if mydb:
        mydb.close()
    if dane:
        response = requests.get(f'{API_URL}/guilds/{GUILD_ID}/members', headers=headers, params={'limit': 1000})
        members  = response.json()
        members_with_role = [member for member in members if role_id in member['roles']]
        members_with_role_dict = {member['user']['id']: member for member in members_with_role}
        for user_id, name, points, tw_points in dane:
            if str(user_id) in members_with_role_dict:
                tw_points = tw_points*100/count_TW
                roles = members_with_role_dict[str(user_id)]['roles']
                role_lineup = "brak"
                if "1247648190757343396" in roles:
                    role_lineup = "Friendship is Magic"
                elif "1251117068829331516" in roles:
                    role_lineup = "Kings Order"
                elif "1247648341861466215" in roles:
                    role_lineup = "Królewska Tarcza"
                elif "1247648550716833832" in roles:
                    role_lineup = "Czerwona Flota"
                elif "1247648446635053096" in roles:
                    role_lineup = "Zielona Piechota"
                data.append([user_id, name, points, tw_points, role_lineup])
                del members_with_role_dict[str(user_id)]
            else:
                others_data.append([user_id, name])
        for member_data in members_with_role_dict.items():
            member = member_data[1]
            not_verified_data.append([member['user']['id'], member['user']['username']])
         
    data = sorted(data, key=lambda user: user[2])
    return render_template('index.html', users=data, count=len(data), not_verified=not_verified_data, not_verified_count=len(not_verified_data), others_player=others_data, others_count=len(others_data))

@app.route('/index')
def index():
    global mydb
    global cursor
    headers = {
        'Authorization': f'Bot {TOKEN}'
    }
    mydb = connect_with_db()
    cursor.execute(f"SELECT id_player, nick, signup_points, TW_points FROM Players WHERE discord_server_id = %s", (1232957904597024882, ))
    dane = cursor.fetchall()
    cursor.execute(f"SELECT COUNT(*) FROM TW WHERE discord_server_id = %s", (1232957904597024882, ))
    count_TW = cursor.fetchall()
    count_TW = count_TW[0][0] - 1
    data = []
    not_verified_data = []
    others_data = []
    if cursor:
        cursor.close()
    if mydb:
        mydb.close()
    if dane:
        response = requests.get(f'{API_URL}/guilds/{GUILD_ID}/members', headers=headers, params={'limit': 1000})
        members  = response.json()
        members_with_role = [member for member in members if role_id in member['roles']]
        members_with_role_dict = {member['user']['id']: member for member in members_with_role}
        for user_id, name, points, tw_points in dane:
            if str(user_id) in members_with_role_dict:
                tw_points = tw_points*100/count_TW
                roles = members_with_role_dict[str(user_id)]['roles']
                role_lineup = "brak"
                role_house = "brak"
                if "1247648190757343396" in roles:
                    role_lineup = "Friendship is Magic"
                elif "1251117068829331516" in roles:
                    role_lineup = "Kings Order"
                elif "1247648341861466215" in roles:
                    role_lineup = "Królewska Tarcza"
                elif "1247648550716833832" in roles:
                    role_lineup = "Czerwona Flota"
                elif "1247648446635053096" in roles:
                    role_lineup = "Zielona Piechota"
                if "1243575612552122468" in roles:
                    role_house = "Gwardia"
                elif "1232957904621932557" in roles:
                    role_house = "Wielka"
                elif "1250205692871180431" in roles:
                    role_house = "Ostrze"
                data.append([user_id, name, points, tw_points, role_lineup, role_house])
                del members_with_role_dict[str(user_id)]
            else:
                others_data.append([user_id, name])
        for member_data in members_with_role_dict.items():
            member = member_data[1]
            not_verified_data.append([member['user']['id'], member['user']['username']])
         
    data = sorted(data, key=lambda user: user[2])
    return render_template('index.html', users=data, count=len(data), not_verified=not_verified_data, not_verified_count=len(not_verified_data), others_player=others_data, others_count=len(others_data))

@app.route('/TW')
def tw():
    global mydb
    global cursor
    mydb = connect_with_db()
    cursor.execute(f"SELECT date, player_list FROM TW WHERE discord_server_id = %s", (1232957904597024882, ))
    dane = cursor.fetchall()
    data = {}
    if cursor:
        cursor.close()
    if mydb:
        mydb.close()
    if dane:
        for day, players in dane:
            if players and type(players) == str:
                players = json.loads(players)
            data[day] = len(players)
    return render_template('tw.html', tw=data)

@app.route('/tw_points')
def tw_points():
    global mydb
    global cursor
    mydb = connect_with_db()
    cursor.execute(f"SELECT id_player, nick, TW_points  FROM Players WHERE discord_server_id = %s", (1232957904597024882, ))
    dane = cursor.fetchall()
    data = dane if dane else {}
    data = sorted(data, key=lambda user: user[2])
    if cursor:
        cursor.close()
    if mydb:
        mydb.close()
    return render_template('tw_points.html', users=data)

def connect_with_db():#łączy się z bazą danych
    global cursor
    try:
      with open('Discord/Keys/config.json', 'r') as file:
        config = json.load(file)
      mydb = mysql.connector.connect(
        host=config["host"],
        user=config["user"],
        password=config["password"],
        database=config["database"]
      )
      cursor = mydb.cursor()
      return mydb
    except Exception as e:
      print(e)
  

def authorization_header(request):
    auth_header = request.headers.get('Authorization')
    # Jeśli nagłówka brakuje lub jego wartość jest niepoprawna, zwróć błąd 401 Unauthorized
    if not auth_header or auth_header != BOT_KEY:
        return jsonify({"status": "Unauthorized!"}), 401
        #return web.Response(status=401, text="Unauthorized!")
    return False

@app.route('/info', methods=['GET'])
def get_info():
    return jsonify({"info": "",})
#---------------testy na pokaz-----------------
@app.route('/user', methods=['GET'])
def get_user():
    guild_id = request.args.get('guild_id', type=int)
    user_id = request.args.get('id', type=int)
    if guild_id and user_id:
        response = requests.get(f'{API_URL}/guilds/{guild_id}/members/{user_id}', headers=headers, params={'limit': 1})
        member  = response.json()
        if member:
            return jsonify({"id": user_id, "name": member.name})
        else:
            return jsonify({"status": "User not found"}), 404
    else:
        return jsonify({"status": "Invalid or missing guild_id or user_id parameter"}), 400
    
@app.route('/guilds/<int:guild_id>/members/<int:user_id>', methods=['GET'])
def get_user_v2(guild_id, user_id):
    response = requests.get(f'{API_URL}/guilds/{guild_id}/members/{user_id}', headers=headers, params={'limit': 1})
    member  = response.json()
    if member:
        return jsonify({"guild_id": guild_id, "user_id": user_id, "name": member.name})
    else:
        return jsonify({"status": "User not found"}), 404
#----------------------------------------------------
@app.route('/api/attendance/<int:guild_id>')
def get_attendance(guild_id):
    #auth_header = authorization_header(request)
    #if auth_header != False:
    #    return auth_header
    response = requests.get(f'http://localhost:8080/api/attendance/{guild_id}')
    return jsonify(response.json())

@app.route('/api/server_verification', methods=['GET'])
def server_verification():
    guild_id = request.args.get('guild_id', type=int)
    member_id = request.args.get('member_id', type=int)
    member_role_id = request.args.get('member', type=int)
    logs_channel_id = request.args.get('logs', type=int)
    attendance_channel_id = request.args.get('attendance', type=int)
    tw_server_id = request.args.get('tw_server', type=int)
    tw_role_id = request.args.get('tw_member', type=int)

    if not all([guild_id, member_id, member_role_id, logs_channel_id, attendance_channel_id, tw_server_id, tw_role_id]):
        return web.json_response({"status": "error: missing required parameters"}, status=400)

    if guild_id and member_id:
        params = {
        'guild_id': guild_id,
        'member_id': member_id,
        'member': member_role_id,
        'logs': logs_channel_id,
        'attendance': attendance_channel_id,
        'tw_server': tw_server_id,
        'tw_member': tw_role_id
        }

        response = requests.get(f'http://localhost:8080/api/server_verification', params=params)     
        return jsonify(response.json())
    else:
        return jsonify({"status": "error: Invalid or missing guild_id or member_id parameter"}), 400

@app.route('/api/roles', methods=['GET'])
def get_roles():
    guild_id = request.args.get('guild_id', type=int)
    if guild_id:
        response = requests.get(f'{API_URL}/guilds/{guild_id}/roles', headers=headers, params={'limit': 1})
        temp = response.json()
        #print(temp)
        print(temp[0])
        return jsonify(response.json())
    else:
        return jsonify({"status": "error: Invalid or missing guild_id parameter"}), 400