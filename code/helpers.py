# source: https://github.com/Aveek-Saha/Movie-Script-Database/blob/master/sources/utilities.py

from bs4 import BeautifulSoup
import urllib.request
import string
import os
import textract
import re
import pandas as pd

from fuzzywuzzy import fuzz
from os import listdir, makedirs
from os.path import isfile, join, sep, getsize, exists
from tqdm import tqdm
import itertools
from unidecode import unidecode
import json
import warnings


def format_filename(s):
    valid_chars = "-() %s%s%s" % (string.ascii_letters, string.digits, "%")
    filename = ''.join(c for c in s if c in valid_chars)
    filename = filename.replace('%20', ' ')
    filename = filename.replace('%27', '')
    filename = filename.replace(' ', '-')
    filename = re.sub(r'-+', '-', filename).strip()
    return filename


def get_soup(url):
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            page = urllib.request.Request(
                url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)'})
            result = urllib.request.urlopen(page)
            resulttext = result.read()

        soup = BeautifulSoup(resulttext, 'html.parser')

    except Exception as err:
        # print(err)
        soup = None
    return soup


def get_pdf_text(url, name):
    doc = os.path.join("scripts", "temp", name + ".pdf")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = urllib.request.urlopen(url)
    f = open(doc, 'wb')
    f.write(result.read())
    f.close()
    try:
        text = textract.process(doc, encoding='utf-8').decode('utf-8')
    except Exception as err:
        # print(err)
        text = ""
    return text


def get_doc_text(url, name):
    doc = os.path.join("scripts", "temp", name + ".doc")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = urllib.request.urlopen(url)
    f = open(doc, 'wb')
    f.write(result.read())
    f.close()
    try:
        text = textract.process(doc, encoding='utf-8').decode('utf-8')
    except Exception as err:
        # print(err)
        text = ""
    return text


# source: https://github.com/AdeboyeML/Film_Script_Analysis
def extract_scene_characters(fname):
    with open(fname, "r", encoding='utf-8', errors='ignore') as f:
        data = [row for row in f]
    
    dat = []
    for x in data:
        x = re.sub(r'\(.*\)', '', x)
        x = re.sub(r'\-|\#\d+', '', x)
        #x = re.sub(r"[^a-zA-Z0-9.,?'\n ]+", '', x)
        x = re.sub(r"POINT OF VIEW", 'Point of view', x)
        x = re.sub(r"TEXT", 'Text', x)
        x = re.sub(r"NEXT", 'Next', x)
        dat.append(x.replace('\t', ' ').lstrip(" "))
    
    scenes = []
    for l in dat:
        match = re.search(r'(((INT\.|EXT\.)\s[A-Z]+.*)|((INT\.|EXT\.)\s+[A-Z]+.*)|((INT\.|EXT\.)\s[A-Z]+)|((INT\.|EXT\.)\s[0-9]+.*)|\
        ((INT\./EXT\.|EXT\./INT\.)\s[A-Z]+.*)|((INT\.|EXT\.)\s[0-9]+)|((INT\./EXT\.|EXT\./INT\.)\s[0-9]+.*)|(INT\.\s+.*|EXT\.\s+.*)\
        |((INT\.|EXT\.)\s[A-Z]+\W+.+)|((INT|EXT)\s[A-Z]+.*)|((INT|EXT)\s+[A-Z]+.*)|((INT|EXT)\s[A-Z]+)|((INT|EXT)\s[0-9]+.*)\
        |((INT/EXT|EXT/INT)\s[A-Z]+.*)|((INT|EXT)\s[0-9]+)|((INT/EXT|EXT/INT)\s[0-9]+.*)|((I/E\.|E/I\.)\s+[A-Z].*)\
        |((INT|EXT)\s[A-Z]+\W+.+)|((I/E\.|E/I\.)\s+.*))\n', l)
        if match:
            scenes.append(match.group(1))
    #scenes = [x.strip(" ") for x in scenes]
        
    characters = []
    for x in dat:
        xters = re.findall(r'(^[A-Z]+[A-Z]+\n)|(^[A-Z]+[A-Z]+\s+\n)|(^[A-Z]+\.\s+[A-Z]+\n)|(^[A-Z]+[A-Z]+\s+[A-Z]+[A-Z]+\s\n)\
        |(^[A-Z]+[A-Z]+\s+[A-Z]+[A-Z]+\s+[A-Z]+[A-Z]+\n)|(^[A-Z]+[A-Z]+\s+[A-Z]+[A-Z]+\n)|(^[A-Z]+[A-Z]+\'S\s+[A-Z]+[A-Z]+\s+[A-Z]+[A-Z]+\n)\
        |(^[A-Z]+[A-Z]+\'S\s+[A-Z]+[A-Z]+\n)|(^[A-Z]+[A-Z]+\'S\s+[A-Z]+[A-Z]+\s+\n)|(^MR\s+[A-Z]+[A-Z]+|MRS\s+[A-Z]+[A-Z]+\n)\
        |(^[A-Z]+[A-Z]+\s+\&\s+[A-Z]+[A-Z]+\n)|(^MR\s+[A-Z]+[A-Z]+|MRS\s+[A-Z]+[A-Z]+\s+\n)', x)
        characters.append(xters)
        
    characters = [x for x in characters if x != []]
    refined_characters = []
    for c in characters:
        cc = [tuple(filter(None, i)) for i in c]
        refined_characters.append(cc)
    refined_xters = [x[0][0] for x in refined_characters]
    
    best_ = ['BEST DIRECTOR', 'BEST ADAPTED SCREENPLAY', 'BROADCASTING STATUS', 'BEST COSTUME DESIGN', 'TWENTIETH CENTURY FOX', 'BEST ORIGINAL SCORE', 'BEST ACTOR', 'BEST SUPPORTING ACTOR', 'BEST CINEMATOGRAPHY', 'BEST PRODUCTION DESIGN', 'BEST FILM EDITING', 'BEST SOUND MIXING', 'BEST SOUND EDITING', 'BEST VISUAL EFFECTS']
    transitions = ['RAPID CUT TO:', 'TITLE CARD', 'FINAL SHOOTING SCRIPT', 'CUT TO BLACK', 'CUT TO:', 'SUBTITLE:', 'SMASH TO:', 'BACK TO:', 'FADE OUT:', 'END', 'CUT BACK:', 'CUT BACK', 'DISSOLVE TO:', 'CONTINUED', 'RAPID CUT', 'RAPID CUT TO', 'FADE TO:', \
                   'FADE IN:', 'FADE OUT:', 'FADES TO BLACK', 'FADE TO', 'CUT TO', 'FADE TO BLACK', 'FADE UP:', 'BEAT', 'CONTINUED:', 'FADE IN', \
                   'TO:', 'CLOSE-UP','WIDE ANGLE', 'WIDE ON LANDING', 'THE END', 'FADE OUT','CONTINUED:', 'TITLE:', 'FADE IN','DISSOLVE TO','CUT-TO','CUT TO', 'CUT TO BLACK',\
                   'INTERCUT', 'INSERT','CLOSE UP', 'CLOSE', 'ON THE ROOF', 'BLACK', 'BACK IN SILENCE', 'TIMECUT', 'BACK TO SCENE',\
                   'REVISED', 'PERIOD', 'PROLOGUE', 'TITLE', 'SPLITSCREEN.', 'BLACK.',\
                   'FADE OUT', 'CUT HARD TO:', 'OMITTED', 'DISSOLVE', 'WIDE SHOT', 'NEW ANGLE']
    movie_characters = []
    for x in refined_xters:
        x = re.sub(r'INT\..*|EXT\..*', '', x)
        x = re.sub(r'ANGLE.*', '', x)
        trans = re.compile("({})+".format("|".join(re.escape(c) for c in transitions)))
        x = trans.sub(r'', x)
        best = re.compile("({})+".format("|".join(re.escape(c) for c in best_)))
        x = best.sub(r'', x)
        movie_characters.append(x.replace('\n', '').strip())
    movie_characters = [x.strip() for x in movie_characters if x]
    
    return scenes, movie_characters


# source: https://github.com/Aveek-Saha/Movie-Script-Database/blob/master/clean_files.py
def clean_script(text):
    text = text.encode('utf-8', 'ignore').decode('utf-8').strip()
    text = text.replace("", "")
    text = text.replace("•", "")
    text = text.replace("·", "")

    whitespace = re.compile(r'^[\s]+')
    scenenumber = re.compile(r'^\d+\s+.*\s+\d+$')
    pagenumber = re.compile(
        r'^[(]?\d{1,3}[)]?[\.]?$|^.[(]?\d{1,3}[)]?[\.]?$|^[(]?\d{1,3}[)]?.?[(]?\d{1,3}[)]?[\.]?$')
    cont = re.compile(r'^\(continued\)$|^continued:$|^continued: \(\d+\)$')
    allspecialchars = re.compile(r'^[^\w\s ]*$')

    lines = []

    for line in text.split('\n'):
        copy = line
        line = line.lower().strip()
        # skip lines with one char since they're likely typos
        if len(line) == 1:
            if line.lower() != 'a' or line.lower() != 'i':
                continue
        # skip lines containing page numbers
        if pagenumber.match(line):
            continue
        # Lines which just say continued
        if cont.match(line):
            continue
        # skip lines containing just special characters
        if line != '' and allspecialchars.match(line):
            continue
        # Filter lines with numbers before and after scene details
        if scenenumber.match(line):
            numbers = copy.split()
            if numbers[0] == numbers[-1]:
                copy = " ".join(numbers[1:-1]).strip()
                line = copy.lower().strip()
        # Lines which just say continued
        if cont.match(line):
            continue
        if line == "omitted":
            continue
        lines.append(copy.strip())

    final_data = '\n'.join(lines)
    final_data = re.sub(r'\n\n+', '\n\n', final_data).strip()
    return final_data


# source: https://github.com/AdeboyeML/Film_Script_Analysis
def clean_text(fname):
    """
    Applies some pre-processing on the given text.
    """
    with open(fname, "r", encoding='utf-8', errors='ignore') as r:
        text = [row for row in r]


    #REMOVE TRANSITIONS OR CAMERA ANGLES
    transitions = ['SMASH CUT TO:', 'FINAL SHOOTING SCRIPT', 'CUT TO BLACK', 'SMASH TO:', 'RAPID CUT TO:', 'BACK TO:', 'BLACK SCREEN', 'FADE OUT TO WHITE LIGHT', 'CUT TO:', 'CUT BACK:', 'CUT BACK', 'DISSOLVE TO:', 'CONTINUED', 'RAPID CUT', 'RAPID CUT TO', 'FADE TO:', \
                   'FADE IN:', 'FADES TO BLACK', 'FADE TO', 'CUT TO', 'FADE UP:', 'BEAT', 'AFTERNOON', 'EVENING', 'CONTINUED:', 'FADE IN', \
                   'TO:', 'CLOSE-UP','WIDE ANGLE','CONTINUED:', 'TITLE:', 'FADE IN','DISSOLVE TO','CUT-TO','CUT TO', 'CUT TO BLACK',\
                   'INTERCUT', 'INSERT', 'CLOSE UP', 'TITLE CARD', 'PAUSE', 'SOUND', 'SONG CONTINUES OVER', 'BACK TO SCENE',\
                   'CUT', 'WATCH', 'CU WATCH', 'BLACK', 'BACK IN SILENCE', 'SUBTITLE:', 'CLOSE', 'ON THE ROOF','CUT HARD TO:',\
                   'THE SCREEN', 'TITLE', 'PROLOGUE', 'SPLITSCREEN.', 'OMITTED', 'BLACK.',\
                   'FADE OUT:', 'FADE OUT.', 'FADE OUT', 'DISSOLVE', 'NEW ANGLE', 'WIDE SHOT']
    # remove directors or the film production company
    best_ = ['BEST DIRECTOR', 'BEST ADAPTED SCREENPLAY', 'SENTENCE', 'BROADCASTING STATUS', 'BEST COSTUME DESIGN', 'TWENTIETH CENTURY FOX', 'BEST ORIGINAL SCORE', 'BEST ACTOR', 'BEST SUPPORTING ACTOR', 'BEST CINEMATOGRAPHY', 'BEST PRODUCTION DESIGN', 'BEST FILM EDITING', 'BEST SOUND MIXING', 'BEST SOUND EDITING', 'BEST VISUAL EFFECTS']
    #text = re.sub('\d+', '', text)
    tex = []
    for x in text:
        tx = x.replace('\t', ' ').lstrip(" ")
        tx = re.sub(r'^\d+\n', r'', tx)
        tx = re.sub(r'\(.*\)', r'', tx)
        tx = re.sub(r'\#\d+', r'', tx)
        #tx = tx.replace('\n', '')
        #tx = re.sub(r'\d+', r'', tx)
        tx = re.sub(r'(((INT\.|EXT\.)\s[A-Z]+.*)|((INT\.|EXT\.)\s+[A-Z]+.*)|((INT\.|EXT\.)\s[A-Z]+)|((INT\.|EXT\.)\s[0-9]+.*)|\
        ((INT\./EXT\.|EXT\./INT\.)\s[A-Z]+.*)|((INT\.|EXT\.)\s[0-9]+)|((INT\./EXT\.|EXT\./INT\.)\s[0-9]+.*)|(INT\.\s+.*|EXT\.\s+.*)\
        |((INT\.|EXT\.)\s+[A-Z]+\W+.+)|((INT|EXT)\s+[A-Z]+.*)|((INT|EXT)\s+[A-Z]+.*)|((INT|EXT)\s[A-Z]+)|((INT|EXT)\s[0-9]+.*)|\
        ((INT/EXT|EXT/INT)\s+[A-Z]+.*)|((INT|EXT)\s+[0-9]+)|((INT/EXT|EXT/INT)\s+[0-9]+.*)|((I/E\.|E/I\.)\s+[A-Z].*)\
        |((INT|EXT)\s+[A-Z]+\W+.+)|((I/E\.|E/I\.)\s+.*))', 'SCC', tx)
        tx = re.sub(r'(^\d+\w+\.\s\n)|(^\d+\.\s\n)|(^\d+\.\n)', r'', tx)
        tx = re.sub(r'^\W+', r'', tx)
        tx = re.sub(r'^\d+\.', r'', tx)
        tx = re.sub(r'^\d+/\d+/\d+', r'', tx)
        tx = re.sub(r'ANGLE.*', '', tx)
        tx = re.sub(r'(\'m|\’m)', r' am', tx)
        tx = re.sub(r'(\'ll|\’l)', r' will', tx)
        tx = re.sub(r'(\'re|\’re)', r' are', tx)
        tx = re.sub(r'(\'d|\’d)', r' had', tx)
        tx = re.sub(r'(\'ve|\’ve)', r' have', tx)
        tx = re.sub(r'SEQ\.\s+\d+', r'', tx)
        #tx = re.sub(r'Final\s+\d+\.', r'', tx)
        tx = re.sub(r'Goldenrod\s+\-\s+\d+\.\d+\.\d+\s+\d+\.', r'', tx)
        tx = re.sub(r'(^\d+\s+\d+\s+\d+\s+\-\sRev\.\s\d+/\d+/\d+\s+\d+[A-Z])|(^\d+\s+\d+\s+\d+\s+\-\sRev\.\s\d+/\d+/\d+\s+\d+)', '', tx)
        tx = re.sub(r'([A-Z]+[A-Z]+\sREV\s\d+\-\d+\-\d+\s\d+\.)|([A-Z]+[A-Z]+\sREV\s\d+\-\d+\-\d+\s\d+[A-Z]\.)|(DBL\.\s[A-Z]+[A-Z]+\sREV\s\d+\-\d+\-\d+\s\d+\.)', '', tx)
        #tx = re.sub(r'^TITLE:\n', '', tx)
        #end = re.compile(r'THE END.*|FADE OUT.*', re.MULTILINE)
        #tx = end.sub(r'', tx)
        trans = re.compile("({})+".format("|".join(re.escape(c) for c in transitions)))
        tx = trans.sub(r'', tx)
        #tx = re.sub(r'[A-Z]+\'S', '', tx)
        #tx = tx.replace('[^a-zA-Z]', '')
        #tx = tx.replace('', '')
        #tx = tx.strip()
        #tx = re.sub(r'\d+', r'', tx)
        tx = re.sub(r"[^a-zA-Z0-9.,?'&\n ]+", '', tx)
        #tx = re.sub(r'\W+', ' ', tx)
        tex.append(tx)
    txt = "".join([s for s in tex if s.strip()])
    txt = re.sub(r'\nTHE END\n(.|\n)*', '', txt)
    
    return txt


# source: https://github.com/AdeboyeML/Film_Script_Analysis
def characters_dialogue_action(text, scenes, movie_characters):    
    scene_action = []
    scene_xters = []
    scene_dialogue = []
    xters_list = []
    xters_dialogue = []
    
    scene_data = text.split('SCC')[1:]
        
    #     scs = re.compile("({})+".format("|".join(re.escape(c) for c in scenes))).split(text)[1:]
    #     scene_data = [x for x in scs if x not in scenes]

    
    for x in scene_data:
        scene_text = re.compile('(\n[A-Z]+[A-Z]+\n)|(\n[A-Z]+[A-Z]+\s+\n)|(\n[A-Z]+\.\s+[A-Z]+\n)|(\n[A-Z]+[A-Z]+\s+[A-Z]+[A-Z]+\s+\n)\
        |(\n[A-Z]+[A-Z]+\s+[A-Z]+[A-Z]+\s+[A-Z]+[A-Z]+\n)|(\n[A-Z]+[A-Z]+\s+[A-Z]+[A-Z]+\n)|(\nMR\s+[A-Z]+[A-Z]+|MRS\s+[A-Z]+[A-Z]+\n)\
        |(\n[A-Z]+[A-Z]+\'S\s+[A-Z]+[A-Z]+\n)|(\n[A-Z]+[A-Z]+\'S\s+[A-Z]+[A-Z]+\s+\n)|(\nMR\s+[A-Z]+[A-Z]+|MRS\s+[A-Z]+[A-Z]+\s+\n)\
        |(\n[A-Z]+[A-Z]+\s+\&\s+[A-Z]+[A-Z]+\n)').split(x)
        scene_text = [x for x in scene_text if x != None]
        xter_split = re.findall('(\n[A-Z]+[A-Z]+\n)|(\n[A-Z]+[A-Z]+\s+\n)|(\n[A-Z]+\.\s+[A-Z]+\n)|(\n[A-Z]+[A-Z]+\s+[A-Z]+[A-Z]+\s+\n)\
        |(\n[A-Z]+[A-Z]+\s+[A-Z]+[A-Z]+\s+[A-Z]+[A-Z]+\n)|(\n[A-Z]+[A-Z]+\s+[A-Z]+[A-Z]+\n)|(\n[A-Z]+[A-Z]+\'S\s+[A-Z]+[A-Z]+\s+[A-Z]+[A-Z]+\n)\
        |(\n[A-Z]+[A-Z]+\'S\s+[A-Z]+[A-Z]+\n)|(\n[A-Z]+[A-Z]+\'S\s+[A-Z]+[A-Z]+\s+\n)|(\nMR\s+[A-Z]+[A-Z]+|MRS\s+[A-Z]+[A-Z]+\s+\n)\
        |(\n[A-Z]+[A-Z]+\s+\&\s+[A-Z]+[A-Z]+\n)|(\nMR\s+[A-Z]+[A-Z]+|MRS\s+[A-Z]+[A-Z]+\n)', x)
        split_ = []
        for c in xter_split:
            cc = tuple(filter(None, c))
            split_.append(cc)
        xters_ = [x[0] for x in split_]
        sc_xters = []
        for r in xters_:
            tr = r.replace('\n', '').strip()
            if tr in movie_characters:
                sc_xters.append(r)
        if scene_text[0] not in sc_xters:
            scene_action.append(scene_text[0])
        else:
            scene_action.append(None)
        if len(sc_xters) >= 1:
            dialogue = []
            xhrs = []
            for z in range(0, len(scene_text),1):
                if scene_text[z] in sc_xters:
                    xters_list.append(scene_text[z])
                    xhrs.append(scene_text[z])
                    xters_dialogue.append(scene_text[z+1])
                    dialogue.append(scene_text[z+1])
                    xters_list = [re.sub(r'\n', r' ', y).strip() for y in xters_list]
                    xhrs = [re.sub(r'\n', r' ', y).strip() for y in xhrs]
                    xters_dialogue = [re.sub(r'\n', r' ', y) for y in xters_dialogue]
                    dialogue = [re.sub(r'\n', r' ', y) for y in dialogue]
            scene_dialogue.append(dialogue)
            scene_xters.append(xhrs)
        else:
            scene_dialogue.append(None)
            scene_xters.append(None)
    
    scene_data = [re.sub(r'\n', r' ', x) for x in scene_data]
    scene_action = [re.sub(r'\n', r' ', x).strip() for x in scene_action]
        
    data_tuples = list(zip(scenes, scene_action, scene_xters, scene_dialogue, scene_data))
    df_scene = pd.DataFrame(data_tuples, columns=['Scene_Names','Scene_action', 'Scene_Characters', 'Scene_Dialogue', 'Contents'])
    
    data_tuples2 = list(zip(xters_list, xters_dialogue))
    df_dialogue = pd.DataFrame(data_tuples2, columns=['characters','Character_dialogue'])
    df_xters = pd.DataFrame(movie_characters, columns = ['characters'])
    
    return df_scene, df_xters, df_dialogue


def get_dialogue(fname):
    scenes, characters = extract_scene_characters(fname)
    if len(scenes) >= 1:
        text = clean_text(fname)
        _, _, dialogue_df = characters_dialogue_action(text, scenes, characters)
        return dialogue_df