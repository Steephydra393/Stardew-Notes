import html
from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid, re
import json
import time, os
from html import unescape  # For HTML entity decoding

guildFilename = 'files\\guilddata.json'
notesFilename = 'files\\notesdata.json'

app = Flask(__name__)
CORS(app)

guildInfo = {"841474628614488086":{'year':'Year 1', 'season':'Summer'}}
# guildInfo = {}
notes = {}

def get_data():
    global notes, guildInfo
    try:
        with open(notesFilename, 'r') as f:
            try:
                notes = json.load(f)
            except:
                notes = {}
                save_notes({}, "Glob", True)
    except FileNotFoundError:
        notes = {}
    
    try:
        with open(guildFilename, 'r') as f:
            try:
                guildInfo = json.load(f)
            except:
                guildInfo = {}
                save_guild({}, "Glob", True)
    except FileNotFoundError:
        guildInfo = {}
        save_guild({}, "Glob", True)
    return notes, guildInfo

def save_guild(data, guildID, sign=False):
    if sign == False: # Fixes RecursionError by accidental loop creation
        get_data()

    global guildInfo  # Ensure guildInfo is defined globally

    try:
        sanitized_data = {}  # Create a new dictionary for the sanitized guild data

        # Sanitize each item within the guild data individually
        for key, value in data.items():
            sanitized_data[key] = json.loads(sanitize_json_string(json.dumps(value)))

        # Update the global guildInfo dictionary with the sanitized data
        if guildID.upper() != "GLOB":
            guildInfo[guildID] = sanitized_data 
        else:
            guildInfo = sanitized_data

        with open(guildFilename, 'w') as f:
            # Write the sanitized data to the file
            json.dump(sanitized_data, f, indent=6)

        # Fetch and log the cleaned data (optional for debugging)
        finalnote, finalguild = get_data()
        print(f"NoteData = {finalnote}\n\n GuildData = {finalguild}")

        return True

    except (json.JSONDecodeError, KeyError) as e:
        # Handle potential errors (e.g., invalid JSON, missing key) gracefully
        print(f"Error saving guild data: {e}")
        return False 

def save_notes(data, guildID, sign=False):
    if sign == False:
        get_data()

    global notes

    try:
        sanitized_data = []

        # Sanitize and update notes
        if guildID.upper() != "GLOB":
            # If guildID is not "GLOB", update just that guild's data
            # Fetch the existing notes for this guild, or initialize an empty list
            existing_notes = notes.get(guildID, [])

            # Assuming `data` is now a list of dictionaries, directly sanitize each
            for note_content in data:
                sanitized_note = json.loads(
                    sanitize_json_string(json.dumps(note_content))
                )
                sanitized_data.append(sanitized_note) # Append sanitized note to list

            # Append new notes to the existing notes
            updated_notes = existing_notes + sanitized_data
            notes[guildID] = updated_notes
        else:
            # If guildID is "GLOB", update all notes across guilds
            for guild_id, guild_notes in data.items(): # Data is a dictionary of lists
                sanitized_guild_notes = []
                for note_content in guild_notes: # Iterate over the list of notes
                    sanitized_note = json.loads(
                        sanitize_json_string(json.dumps(note_content))
                    )
                    sanitized_guild_notes.append(sanitized_note) # Add as a dictionary
                notes[guild_id] = sanitized_guild_notes

        # Save the entire 'notes' dictionary to the file
        with open(notesFilename, 'w') as f:
            json.dump(notes, f, indent=6)

        # Optional logging for debugging
        # finalnote, finalguild = get_data()
        # print(f"NoteData = {finalnote}\n\n GuildData = {finalguild}")

        return True

    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error saving notes: {e}")
        return False

@app.route('/notes', methods=['POST']) # Now Santizes Data
def create_note():
    get_data()

    try:
        note_data = request.get_json() # Retreve the data payload from the website
        guild_id = note_data.get('guild_id') # Get and Save the user's guild_id
        text = note_data.get('text') # Get and Save the note's text
        category = note_data.get('category') # Get and save the category the user has given
        author = note_data.get('author') # Save the user that submited it

        try: # Try to Sanitize the data
            s_guild_id = sanitizeData(guild_id)
            print("GI fine")
            s_category = sanitizeData(category)
            print("CAT fine")
            print(author)
            s_author = sanitizeData(author)
            print("AUTH fine")
        except Exception as E: # Else, if fails, report it to the user's console
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
        
        print(f"(localized) Notes Data After POST request: \n|\n|   {note_data}\n^Saving...\n")

        result = save_notes(note_data, s_guild_id)
        if result != True:
            return jsonify({'error', 'Unable to save data'}), 500
        
        return jsonify({'message': 'Note created successfully', 'message_id': message_id}), 201
    except:
        return jsonify({'error', 'Server error'}), 500

@app.route('/guilds/<guildId>')
def get_guild_info(guildId):
    get_data()
    
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
            print(notes[guild_id])
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
    print("WARNING: USING DEPRECATED SANITIZATION METHOD!")
    if note_data == None:
        return(False)
    output = html.escape(note_data)
    return(output)

def sanitize_json_string(json_string):
    try:
        # 1. Parse JSON, handling potential decoding issues
        data = json.loads(json_string, strict=False)  # Allow for some flexibility

        # 2. Recursive Sanitization
        def sanitize_recursively(data):
            if isinstance(data, dict):
                return {k: sanitize_recursively(v) for k, v in data.items() if v is not None}
            elif isinstance(data, list):
                return [sanitize_recursively(v) for v in data if v is not None]
            elif isinstance(data, str):
                return sanitize_string(data)
            else:
                return data

        return json.dumps(sanitize_recursively(data))
    except json.JSONDecodeError as e:
        # Handle parsing failure gracefully, return the original string, or log an error.
        return json_string  
        
def sanitize_string(text):
    # 3. String-Specific Cleaning
    text = unescape(text)  # Decode HTML entities like &amp;
    text = text.replace("\u0000", "")  # Remove null bytes
    # Optionally: Add custom sanitization rules for your specific needs

    return text

def save_note_data(data):
    with open(notesFilename, 'w') as f:
        json.dump(data, f, indent=4)

def save_guild_data(data):
    with open(guildFilename, 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == '__main__':
    try: 
        with open(guildFilename, 'x') as file: 
            file.write("") 
    except FileExistsError: 
        print(f"The file '{guildFilename}' already exists.") 
    try: 
        with open(notesFilename, 'x') as file: 
            file.write("") 
    except FileExistsError: 
        print(f"The file '{notesFilename}' already exists.") 

    app.run(debug=True, port=5173)