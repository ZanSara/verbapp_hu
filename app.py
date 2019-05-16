
from flask import Flask, render_template, request

app = Flask(__name__)

import os, json, random, requests
from bs4 import BeautifulSoup


verbs_filename = "verbs"
verbs_folder = "verbs_conj/"


def load_verbs():
    conjugations = []
    for filename in os.listdir(verbs_folder):
        with open("{}{}".format(verbs_folder, filename), 'r') as verbfile:
            verbsconj = json.loads(verbfile.readlines()[0])
            conjugations += verbsconj
        
    print(len(conjugations))
    return conjugations
        



@app.route("/add-verb", methods=["GET", "POST"])
def add_verb():
    if request.method=="GET":
        return render_template('verbapp_add_verb.html', get=True)
    
    # Load the new verb, if it does not exist already
    
    verb = request.form['verb']
    with open(verbs_filename, 'r') as verbsfile:
        for existing_verb in verbsfile.readlines():
            if existing_verb == verb:
                return render_template('verbapp_add_verb.html', get=False, success=True)
            
    conjugations = []
    #try:
    verb = verb.strip().lower()
    
    cooljugator = requests.get( 'https://cooljugator.com/hu/{}'.format(verb) ) 
    verbix = requests.get( 'https://api.verbix.com//conjugator/jsonp/ab8e7bb5-9ac6-11e7-ab6a-00089be4dcbc/1/121/221/{}?getVerbixHtml=getVerbixHtml&_=1522874032369'.format(verb) ) 
    print("Fetching from "+cooljugator.url +" and "+verbix.url)  
    
    verbix_content = str(verbix.content).replace('\\n', '').replace('\\r', '').replace('\\', '')[30:-200].encode()
    print(type(verbix_content))
    print(verbix_content)
    
    cooljugator_soup = BeautifulSoup(cooljugator.content, "html.parser")
    verbix_soup = BeautifulSoup(verbix_content, "html.parser")

    title = cooljugator_soup.body.find('h1').text
    verb_translation = title.split("(")[1].split(")")[0];
    print(verb_translation)
    
    # Parsing hierarchy-wise
    try:
        for mode_div in verbix_soup.body.find_all('div', attrs={'class':'pure-u-1-1'}):
            mode_name = verbix_soup.body.find('h2').text
            print(mode_name)
            
            for tense_div in mode_div.find_all('div', attrs={'class':'pure-u-1-2'}):
                tense_name = tense_div.find('h3').text
                print(tense_name)
                
                for conj_span in tense_div.find_all('span', attrs={'class':'normal'}):
                    conj_name = conj_span.text
                    
                    translation = cooljugator_soup.body.find('div', attrs={'data-default':conj_name}).find('div', attrs={'class':'meta-translation'}).text
                    
                    conjugations.append( (
                                        verb,
                                        verb_translation,
                                        mode_name+' '+tense_name,
                                        conj_name,
                                        translation
                                   ) )
    except AttributeError as ae:
            print(ae) # we got a 404 with no such cells
            
    #for match in cooljugator_soup.body.find_all('div', attrs={'class': 'conjugation-cell'}):
    #    try:
    #        conjugations.append( (  
    #                                verb,
    #                                verb_translation,
    #                                match.find('div', attrs={'class': 'meta-form'}).text,
    #                                match.find('div', attrs={'class': 'meta-translation'}).text) 
    #                           )
    #    except AttributeError:
    #        continue # we got a 404 with no such cells
    
    # save its verb file
    with open("{}{}".format(verbs_folder, verb), 'w') as verbfile:
        json.dump(conjugations, verbfile)
            
        # add to the verbs index
        #with open(verbs_filename, 'a') as verbsfile:
        #    verbsfile.write(verb+'\n')
            
    #except Exception as e:
    #    print(" ===========> Exception! Reload pls")
    #    print('https://cooljugator.com/hu/' + verb)
    #    return render_template('verbapp_add_verb.html', success=False, msg=e)
        
    return render_template('verbapp_add_verb.html', get=False, success=True)
    
    


@app.route("/")
@app.route("/words")
def home():
    
    conjugations = load_verbs()
    
    (selected_verb, verb_translation, tense, to_translate, solution) = random.choice(conjugations)
    
    return render_template('verbapp_words.html', 
                                to_translate=to_translate,
                                solution=solution,
                                tense = tense,
                                selected_verb=selected_verb,
                                verb_translation=verb_translation)
                                
                                
                                
