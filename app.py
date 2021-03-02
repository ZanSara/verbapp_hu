
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'avrq23n8rp2ru p lvskjnawlurcny ur01c3fakdsfw'

import os, json, random, requests, pathlib
from bs4 import BeautifulSoup


verbs_folder = (pathlib.Path(__file__).parent / "verbs_conj")

def verbs_list():
    return [v.decode('utf-8', 'surrogateescape') for v in os.listdir(verbs_folder)]


@app.route("/add-verb", methods=["GET", "POST"])
def add_verb():
    if request.method=="GET":
        return render_template('verbapp_add_verb.html', get=True, downloaded_verbs=verbs_list())
    
    # Load the new verb, if it does not exist already
    
    verb = request.form['verb']
    print("Requested verb: ", verb)

    if verb in os.listdir(verbs_folder):
        flash("This verb was already in the list.")
        return render_template('verbapp_add_verb.html', downloaded_verbs=verbs_list())
            
    conjugations = []

    verb = verb.strip().lower()
    print("Requested verb: " + verb)
    
    try:
    
        cooljugator = requests.get( 'https://cooljugator.com/hu/{}'.format(verb) ) 
        print("Fetching from "+cooljugator.url )
        
        cooljugator_soup = BeautifulSoup(cooljugator.content, "html.parser")

        title = cooljugator_soup.body.find('h1').text
        verb_translation = title.split("(")[1].split(")")[0]
        print("Verb translation: ", verb_translation)

        table_cells = cooljugator_soup.body.find_all('div', attrs={'class':'conjugation-cell'})
        last_tense_title = ""
        for cell in table_cells:

            if "tense-title" in cell['class']:

                tense = cell.find('span', attrs={'class':'tense-title-space'})
                if tense:
                    last_tense_title = tense.text
                    print("\n\n*** " + tense.text + " ***")

            else:
                conjugation_div = cell.find('div', attrs={'class':'forms-wrapper'})

                if conjugation_div:
                    conjugated_verb_div = conjugation_div.find('div', attrs={'class': 'meta-form'})
                    conjugated_verb = conjugated_verb_div.text

                    translation = cell.attrs.get('data-tooltip')

                    if conjugated_verb and translation:
                        print(f"{conjugated_verb} ({translation})")

                        conjugations.append( (
                                                verb,
                                                verb_translation,
                                                last_tense_title,
                                                conjugated_verb,
                                                translation
                                            ) )

        # save its verb file
        with open("{}/{}".format(verbs_folder, verb), 'w') as verbfile:
            json.dump(conjugations, verbfile)            
        
        return render_template('verbapp_add_verb.html', get=False, success=True, downloaded_verbs=verbs_list())

    except Exception as e:
        flash("Something went wrong fetching this verb! Is the spelling correct?")
        print(e)
        return redirect(url_for('add_verb'))


@app.route("/", methods=['GET'])
def home():
    return redirect(url_for('add_verb'))


@app.route("/words/<direction>", methods=['GET', 'POST'])
def words(direction):
    checked_tenses = list(request.form.keys())
    
    conjugations = []
    for filename in os.listdir(verbs_folder):
        with open("{}/{}".format(verbs_folder, filename), 'r') as verbfile:
            verbsconj = json.loads(verbfile.readlines()[0])
            conjugations += verbsconj
    
    if not conjugations:
        return redirect(url_for('add_verb'))

    available_tenses = [conj[2] for conj in conjugations]
    available_tenses = list(dict.fromkeys(available_tenses))  # Remove duplicates without shuffling
    
    while True:
        (selected_verb, verb_translation, tense, to_translate, solution) = random.choice(conjugations)
        if len(checked_tenses) == 0:
            break
        if tense in checked_tenses:
            break 

    return render_template(f'verbapp_{direction}.html',
                                to_translate=to_translate,
                                solution=solution,
                                tense=tense,
                                selected_verb=selected_verb,
                                verb_translation=verb_translation,
                                available_tenses=available_tenses,
                                checked_tenses=checked_tenses)

    
                                
