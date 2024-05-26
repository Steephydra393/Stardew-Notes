import html
from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid, re

app = Flask(__name__)
CORS(app)

# Heh

guildInfo = {"841474628614488086":{'year':'Year 1', 'season':'Summer'}}
# guildInfo = {}
notes = {}

@app.route('/notes', methods=['POST']) # Now Santizes Data
def create_note():
    try:
        note_data = request.get_json()
        guild_id = note_data.get('guild_id')
        text = note_data.get('text')
        category = note_data.get('category')
        author = note_data.get('author')

        try:
            s_guild_id = sanitizeData(guild_id)
            print("GI fine")
            s_category = sanitizeData(category)
            print("CAT fine")
            print(author)
            s_author = sanitizeData(author)
            print("AUTH fine")
        except Exception as E:
            print("Sani")
            print(E)
            return jsonify({'error': 'Sanitation process failed'}), 401
        
        if not s_guild_id or not text or not s_category:
            print("ISSUE")
            print(s_guild_id, text, s_category, s_author)
            return jsonify({'error': 'guild_id, text, category, and author are required'}), 400 

        message_id = str(uuid.uuid4()) # Create a uuid for the message
        
        note_data['message_id'] = message_id
        note_data['message_status'] = "none"

        if s_guild_id not in notes:
            notes[s_guild_id] = []
        print(note_data)
        notes[s_guild_id].append(note_data)
        
        print("Notes Data After POST request:")
        print(notes)
        
        return jsonify({'message': 'Note created successfully', 'message_id': message_id}), 201
    except:
        return jsonify({'error', 'Server error'}), 500

@app.route('/guilds/<guildId>')
def get_guild_info(guildId):
    if guildId in guildInfo:
        try:
            return jsonify(guildInfo[guildId])
        except Exception as E:
            return jsonify(['error', E]), 400
    else:
        return jsonify({'error': 'GuildID not found'}), 404

@app.route('/guilds', methods=['POST']) # Now Santizes Data
def create_guild_info():
    try:
        note_data = request.get_json()
        guild_id = note_data.get('guild_id')
        year = note_data.get('year')
        season = note_data.get('season')
        
        if not guild_id or not year or not season:
            print("ISSUE")
            print(guild_id, year, season)
            return jsonify({'error': 'guild_id, year, and season are required'}), 400 

        if guild_id not in guildInfo:
            guildInfo[guild_id] = []
        print(note_data)
        guildInfo[guild_id].append(note_data)
        
        print("guildInfo Data After POST request:")
        print(guildInfo)
        
        return jsonify({'message': 'Note created successfully'}), 201
    except:
        return jsonify({'error', 'Server error'}), 500

@app.route('/notes/<guild_id>/<filter>/')
def get_notes(guild_id, filter):
    print(guild_id, filter)
    # {'text': '<p>Test</p>', 'guild_id': '841474628614488086', 'category': '0', 'message_id': '54553afa-6c0f-4ceb-9f02-6cd9244d3fe5', 'message_status': None}
    filters = ['bundle', 'season', 'location']
    seasons = ['spring', 'summer', 'fall', 'winter']
    c2n = {"Spring Foraging Bundle" : 0, 
           "Summer Foraging Bundle" : 1, 
           "Fall Foraging Bundle" : 2, 
           "Winter Foraging Bundle" : 3, 
           "Construction Bundle" : 4, 
           "Exotic Foraging Bundle" : 5, 
           "Spring Crops Bundle" : 6, 
           "Summer Crops Bundle" : 7, 
           "Fall Crops Bundle" : 8, 
           "Quality Crops Bundle" : 9, 
           "Animal Bundle" : 10, 
           "Artisan Bundle" : 11, 
           "River Fish Bundle" : 12, 
           "Lake Fish Bundle" : 13, 
           "Ocean Fish Bundle" : 14, 
           "Night Fishing Bundle" : 15, 
           "Crab Pot Bundle" : 16, 
           "Specialty Fish Bundle" : 17, 
           "Blacksmith\'s Bundle" : 18, 
           "Geologist\'s Bundle" : 19, 
           "Adventurer\'s Bundle" : 20}
    categories = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    spring = [0, 2, 4, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    summer = [1, 4, 5, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    fall = [2, 4, 5, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    winter = [3, 4, 5, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

    if guild_id in notes:
        guildNotes = notes[guild_id]
    else:
        print("Error: guild not in file")
        return jsonify(['error', 'guild not in files OR season not valid']), 400

    if filter not in filters and filter != "status":
        print(f"Filter Issue, the filter at fault - {filter}")
        return jsonify(['error', 'Filters applied could not be verified']), 200

    elif filter == "status":
        return jsonify(['error', 'Filter Error, Not implemented']), 501
    
    if filter == 'bundle': # TODO fix.
        # Setup sending file
        preSend = {
            
        }
        for i in notes[guild_id]:
            category = i['category']

            if category in preSend:
                preSend[category].append(i)
            else:
                preSend[category] = [i]  # Create a new list
    else:
        return jsonify(['error', 'smth occured']), 400
    print(preSend)

    send = {
        'spring': [],
        'summer': [],
        'fall': [],
        'winter': []
    }

    for category in preSend:
        print(category)
        notes_list = preSend[category]
        if c2n[category] in spring: # Spring
            send['spring'].append(notes_list)
        if c2n[category] in summer: # Summer
            send['summer'].append(notes_list)
        if c2n[category] in fall: # Fall
            send['fall'].append(notes_list)
        if c2n[category] in winter: # Winter
            send['winter'].append(notes_list)
    print(send)
    print(notes)
    return jsonify(send)

@app.route('/notes/status/<guild_id>/<message_id>/', methods=['PUT']) 
def update_status(guild_id, message_id):
    try:
        new_status = request.get_json().get('status')
        print(new_status)

        if not re.match(r'^\d+$', guild_id) or not isinstance(message_id, str):
            return jsonify({'error': 'Invalid guild_id or message_id format'}), 400
       
        if guild_id in notes:
            for note in notes[guild_id]:
                if note['message_id'] == message_id:
                    note['message_status'] = new_status
                    print(notes)
                    return jsonify({'message': 'Message status updated successfully'}), 200  # Use 200 OK
            return jsonify({'error': 'Message not found in the guild'}), 404
        else:
            return jsonify({'error': 'Guild not found'}), 404 

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500 # Use str(e) for more details about the error.

@app.route('/notes/delete/<guild_id>/<message_id>', methods=['DELETE']) # Now Santizes Data
def delete_note(guild_id, message_id):
    try:
        s_guild_id = sanitizeData(guild_id)
        s_message_id = sanitizeData(message_id)
    except:
        return jsonify({'error': 'Sanitation process failed'}), 400

    if not s_guild_id or not s_message_id:
        return jsonify({'error': 'Both  guild_id and message_id are required'}), 400

    if s_guild_id in notes:
        notes[s_guild_id] = [note for note in notes[s_guild_id] if note['message_id'] != s_message_id]
        return jsonify({'message', 'Note deleted successfully'}), 200

    return jsonify({'error': 'Guild not found'}), 404

@app.route('/deleteAllNotes/<guild_id>')
def delete_notes(guild_id):
    if guild_id in notes:
         del notes[guild_id]
         return jsonify(['message', 'All notes deleted successfully']), 200
    return jsonify(['error', 'Guild not found']), 404

@app.route('/deleteBundle/<guildId>/<bundleName>')
def delete_bundle(guildId, bundleName):
    c2n = {"Spring Foraging Bundle" : 0, 
           "Summer Foraging Bundle" : 1, 
           "Fall Foraging Bundle" : 2, 
           "Winter Foraging Bundle" : 3, 
           "Construction Bundle" : 4, 
           "Exotic Foraging Bundle" : 5, 
           "Spring Crops Bundle" : 6, 
           "Summer Crops Bundle" : 7, 
           "Fall Crops Bundle" : 8, 
           "Quality Crops Bundle" : 9, 
           "Animal Bundle" : 10, 
           "Artisan Bundle" : 11, 
           "River Fish Bundle" : 12, 
           "Lake Fish Bundle" : 13, 
           "Ocean Fish Bundle" : 14, 
           "Night Fishing Bundle" : 15, 
           "Crab Pot Bundle" : 16, 
           "Specialty Fish Bundle" : 17, 
           "Blacksmith\'s Bundle" : 18, 
           "Geologist\'s Bundle" : 19, 
           "Adventurer\'s Bundle" : 20}
    spring = [0, 2, 4, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    summer = [1, 4, 5, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    fall = [2, 4, 5, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    winter = [3, 4, 5, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

    if not guildId or not bundleName:
        return jsonify({'error': 'Both  guild_id and message_id are required'}), 400

    notes[guildId] = [note for note in notes[guildId] if note['category'] != bundleName]

    if len(notes[guildId]) == 0: 
        del notes[guildId]  # Remove the guild entry if no notes remain
        return jsonify({'message': 'Notes deleted successfully, Guild deleted since no data is left'}), 200

    return jsonify({'message': 'Notes deleted successfully'}), 200

@app.route('/details/<guild_id>')
def get_details(guild_id):
    print(guild_id)
    return jsonify(['error'], ['Yo, whatcha doing? Did you forget to make the function?']), 403

def sanitizeData(note_data):
    if note_data == None:
        return(False)
    output = html.escape(note_data)
    return(output)

if __name__ == '__main__':
    app.run(debug=True, port=5173)
