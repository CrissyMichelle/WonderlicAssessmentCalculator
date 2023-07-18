from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = "123-456"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

category = ["Weak", "Cautionary", "Moderate", "Strong"]
cogni_labels = ["Below Average", "Average", "Above Average"]

depend_questions = {'STRONG': ['Tell me about a time when you overworked your team. What did you learn?\n',
                               'Tell us about a time you came across as too confident. What did you learn?\n'],
                    'WEAK':['Tell me about a time your lack of preparation or focus led to a failure. What did you learn?\n',
                            'Describe the biggest work problem you have encountered. How did you solve it?\n',
                            'Tell me about a time you were proactive on a mission and it had a significant impact.\n']}
stress_questions = {'STRONG': ['Tell me about a time when your team was overly stressed and you were not. How did you lead your team to success?\n',
                               'Tell me about a time you had to complete a big task with inadequate resources. How did you complete it?\n'],
                    'WEAK': ['Tell me about a time you were overwhelmed with a project and reached out for help. What happened?\n',
                             'Tell me about a time you received difficult feedback. How did you utilize it?\n']}
cooperate_questions = {'STRONG': ["Tell me about a time you should have pushed back on a superior's tasking and didn't. How did it impact those working under you?\n",
                                  'Tell me about a time you gave a leader negative feedback.\n'],
                       'WEAK': ['Tell me about a time you disagreed with your supervisor. How did you resolve it?\n',
                                'Describe a time you came off as abrasive to others. How did that impact your ability to lead?\n']}
social_questions = {'STRONG': ['Tell me about a time you were a poor listener, and it impacted your team. How did you adjust course?\n',
                               'Describe a time you empathized with a Soldier and took their perspective into account.\n',
                               'Tell me about a time you spoke “too soon”. What was the result?\n'],
                    'WEAK': ['Describe a time you had to work with a difficult group of subordinates. How did you bring them together?\n',
                             'Share a time you had one particularly difficult subordinate. How did you motivate them?\n']}
openmind_questions = {'STRONG': ['Tell me about a time you came up with an initiative to change a process in your section. Did it work? How do you know others bought into your idea?\n',
                                 'How do you know if your subordinates are open to new initiatives or your solutions to problems?\n'],
                      'WEAK': ['Tell me about a time you lost sight of the big picture mission. What did you learn?\n',
                               'Give a specific example of how you have helped create an environment where differences are valued, encouraged, and supported.\n',
                               'Tell me about the most effective contribution you have made as part of a task group or special project.\n']}
question_bank = {'dep': depend_questions, 'sts': stress_questions, 'cop': cooperate_questions, 'soc': social_questions, 'opm': openmind_questions}


@app.route('/')
def index():
    """Show home page"""
    return render_template("base.html", question_bank_1S=depend_questions['STRONG'], question_bank_1W=depend_questions['WEAK'],
                            question_bank_2S=stress_questions['STRONG'], question_bank_2W=stress_questions['WEAK'],
                            question_bank_3S=cooperate_questions['STRONG'], question_bank_3W=cooperate_questions['WEAK'],
                            question_bank_4S=social_questions['STRONG'], question_bank_4W=social_questions['WEAK'],
                            question_bank_5S=openmind_questions['STRONG'], question_bank_5W=openmind_questions['WEAK'])


@app.route('/generated', methods=["POST"])
def handle_form():
    """Collect data from form"""
    fname = request.form['first']
    lname = request.form['last']
    full_name = lname + ', ' + fname

    cogni_score = request.form['cognitive']
    cog_label = cog_avg(cogni_score)

    moto_score = request.form["motivation"]
    overP_score = request.form["overallP"]
    depend_score = request.form["depend"]
    stress_score = request.form["stress"]
    coop_score = request.form["cooperate"]
    soci_score = request.form["social"]
    open_score = request.form["openmind"]

    """check for valid input and produce labels"""
    try:
        score_list= [moto_score, depend_score, stress_score, coop_score, soci_score, open_score];
        if valid_input(score_list) == True:

            moto_cat = label_score(moto_score)
            overP_cat = label_score(overP_score)
            dep_cat = label_score(depend_score)
            stress_cat = label_score(stress_score)
            coop_cat = label_score(coop_score)
            soci_cat = label_score(soci_score)
            open_cat = label_score(open_score)

            """Put categorical labels data into session storage"""
            session['labels'] = {'Cognitive': [cogni_score, cog_label], 'Motivation': [moto_cat, moto_score], 'Overall Personality': [overP_cat, overP_score], 'Dependability': [dep_cat, depend_score], 'Stress Tolerance': [stress_cat, stress_score],
                                 'Cooperation': [coop_cat, coop_score], 'Sociability': [soci_cat, soci_score], 'Open-Mindedness': [open_cat, open_score]}

            """Generate list of questions"""
            weakP = mins_ask_this([depend_score, stress_score, coop_score, soci_score, open_score])
            strongP = max_ask_this([depend_score, stress_score, coop_score, soci_score, open_score])

            flash(f"You entered {full_name} and the following scores:"
                  f"\nCognitive-{cogni_score},"
                  f"\nMotivation-{moto_score},"
                  f"\nOverall Personality-{overP_score},"
                  f"\nDependability-{depend_score},"
                  f"\nStress Tolerance-{stress_score},"
                  f"\nCooperation-{coop_score},"
                  f"\nSociability-{soci_score},"
                  f"\nOpen-Mindedness-{open_score}")

            return render_template("generated.html", name=full_name, cognitive=cog_label, moto=moto_cat, person=overP_cat, label_data=session['labels'], questionsW = weakP, questionsS = strongP,
                            question_bank_1S=depend_questions['STRONG'], question_bank_1W=depend_questions['WEAK'],
                            question_bank_2S=stress_questions['STRONG'], question_bank_2W=stress_questions['WEAK'],
                            question_bank_3S=cooperate_questions['STRONG'], question_bank_3W=cooperate_questions['WEAK'],
                            question_bank_4S=social_questions['STRONG'], question_bank_4W=social_questions['WEAK'],
                            question_bank_5S=openmind_questions['STRONG'], question_bank_5W=openmind_questions['WEAK'])
        else:
            return redirect('/')
    except:
        flash("UH-OH. What you typed caused an error. Please refresh the page and try again. Only numbers from 0 to 100 will work!!")
        return redirect('/')


def valid_input(vals):
    try:
        for val in vals:
            score = int(val)
            if score >= 0 and score <= 100:
                return True
            else:
                flash(f"You typed in {val}")
                flash("Please type in a valid number. Only values from 0 to 100 will work!")
                return False
    except:
        flash("oops. What you typed caused an error. Please refresh the page and try again. Only numbers from 0 to 100 will work!!")
        return redirect('/')

def cog_avg(val):
    try:
        score = float(val)
        if score <=94:
            return cogni_labels[0]
        elif score >=95 and score <= 113:
            return cogni_labels[1]
        else:
            return cogni_labels[2]
    except:
        flash(f"{val} is an invalid entry for cognitive score. Please type in a valid number.")
        return None

def label_score(val):
    try:
        score = float(val)
        if score <=25:
            return category[0]
        elif score >=26 and score <= 49:
            return category[1]
        elif score >=50 and score <= 74:
            return category[2]
        else:
            return category[3]
    except:
        flash("Please type in a valid number. Only values from 0 to 100 will work!")
        return None

def mins_ask_this(lst):
    personality = ['Dependability', 'Stress Tolerance', 'Cooperation', 'Sociability', 'Open-Mindedness']
    if len(lst) <= len(personality):
        try:
            key_val_pair = zip(personality, lst)
            quest_dict = dict(key_val_pair)
            min_trait = min_conditions(quest_dict)
            return weakP_questions(min_trait)
        except:
            return flash("Uh-oh. Did you forget to type a score into every Personality field?")
    else:
        flash("Please type in a valid number into each of the personality fields.  Thanks!")
        return None

def max_ask_this(lst):
    personality = ['Dependability', 'Stress Tolerance', 'Cooperation', 'Sociability', 'Open-Mindedness']
    if len(lst) <= len(personality):
        try:
            key_val_pair = zip(personality, lst)
            quest_dict = dict(key_val_pair)
            max_trait = max_conditions(quest_dict)
            return strongP_questions(max_trait)
        except:
            return flash("Uh-oh. Did you forget to type a score into every Personality field?")
    else:
        flash("Please type in a valid number into each of the personality fields.  Thanks!")
        return None

def min_conditions(dict):
    traits_list = []
    minimum = min(dict, key=dict.get)
    traits = dict.items()
    sorts = sorted(traits, key=value_getter)
    if int(dict[minimum]) <= 25 and int(sorts[1][1]) > 25:
        traits_list.append(minimum)
        return traits_list
    elif int(dict[minimum]) <= 25 and int(sorts[1][1]) <=25:
        traits_list.append(minimum)
        traits_list.append(sorts[1][0])
        return traits_list
    elif int(dict[minimum]) >= 25 and int(sorts[4][1]) < 75:
        traits_list.append(minimum)
        traits_list.append(sorts[1][0])
        return traits_list
    else:
        return ['Nothing recommended']

def value_getter(elm):
    """Enables sorting a dictionary based on 
    the value part of the key-value pair"""
    return elm[1]

def max_conditions(dict):
    traits_list = []
    maximum = max(dict, key=dict.get)
    traits = dict.items()
    sorts = sorted(traits, key=value_getter)
    if int(dict[maximum]) >= 75 and int(sorts[3][1]) < 75:
        traits_list.append(maximum)
        return traits_list
    elif int(dict[maximum]) >= 75 and int(sorts[3][1]) >= 75:
        traits_list.append(maximum)
        traits_list.append(sorts[3][0])
        return traits_list
    elif int(dict[maximum]) <= 75 and int(sorts[0][1]) > 25:
        traits_list.append(maximum)
        traits_list.append(sorts[3][0])
        return traits_list
    else:
        return ['Nothing recommended']

def weakP_questions(string_list):
    quest = []
    for arg in string_list:
        if arg == 'Dependability':
            quest.append(question_bank['dep']['WEAK'][0])
        elif arg == 'Stress Tolerance':
            quest.append(question_bank['sts']['WEAK'][0])
        elif arg == 'Cooperation':
            quest.append(question_bank['cop']['WEAK'][0])
        elif arg == 'Sociability':
            quest.append(question_bank['soc']['WEAK'][0])
        elif arg == 'Open-Mindedness':
            quest.append(question_bank['opm']['WEAK'][0])
        elif arg == 'Nothing recommended':
            quest.append("nothing to see here")

    return quest

def weakP_questions1(string_list):
    quest = []
    for arg in string_list:
        if arg == 'Dependability':
            quest.append(question_bank['dep']['WEAK'][1])
        elif arg == 'Stress Tolerance':
            quest.append(question_bank['sts']['WEAK'][1])
        elif arg == 'Cooperation':
            quest.append(question_bank['cop']['WEAK'][1])
        elif arg == 'Sociability':
            quest.append(question_bank['soc']['WEAK'][1])
        elif arg == 'Open-Mindedness':
            quest.append(question_bank['opm']['WEAK'][1])
        elif arg == 'Nothing recommended':
            quest.append("nothing to see here")

    return quest

def weakP_questions2(string_list):
    quest = []
    for arg in string_list:
        if arg == 'Dependability':
            quest.append(question_bank['dep']['WEAK'][2])
        elif arg == 'Open-Mindedness':
            quest.append(question_bank['opm']['WEAK'][2])
        elif arg == 'Nothing recommended':
            quest.append("nothing to see here")

    return quest

def strongP_questions(string_list):
    quest = []
    for arg in string_list:
        if arg == 'Dependability':
            quest.append(question_bank['dep']['STRONG'][0])
        elif arg == 'Stress Tolerance':
            quest.append(question_bank['sts']['STRONG'][0])
        elif arg == 'Cooperation':
            quest.append(question_bank['cop']['STRONG'][0])
        elif arg == 'Sociability':
            quest.append(question_bank['soc']['STRONG'][0])
        elif arg == 'Open-Mindedness':
            quest.append(question_bank['opm']['STRONG'][0])
        elif arg == 'Nothing recommended':
            quest.append("nothing to see here")

    return quest

def strongP_questions1(string_list):
    quest = []
    for arg in string_list:
        if arg == 'Dependability':
            quest.append(question_bank['dep']['STRONG'][1])
        elif arg == 'Stress Tolerance':
            quest.append(question_bank['sts']['STRONG'][1])
        elif arg == 'Cooperation':
            quest.append(question_bank['cop']['STRONG'][1])
        elif arg == 'Sociability':
            quest.append(question_bank['soc']['STRONG'][1])
        elif arg == 'Open-Mindedness':
            quest.append(question_bank['opm']['STRONG'][1])
        elif arg == 'Nothing recommended':
            quest.append("nothing to see here")

    return quest

def strongP_questions2(string_list):
    quest = []
    for arg in string_list:
        if arg == 'Sociability':
            quest.append(question_bank['soc']['STRONG'][2])
        elif arg == 'Nothing recommended':
            quest.append("nothing to see here")

    return quest


# 1a)If a score <=25  question only if no other scores are <= 25
# 1b) if a score is >=75  question, but only if no other scores are >= 75
# 1c) if score[i] <= 25 is min and score[j] >=75 is max  two questions

# 2)If a score is <= 25 and no other scores are >=75  question
# 3)If a score is >=75 and no other scores are <= 25  question
# 4)If score[i] != score[j] are both <= 25 and no other scores are >=75 or <= 25  two questions
# 5)If score[i] != score[j] are both >= 75 and no other scores are >=75 or <= 25  two questions

# 6)If 25<scores<75  new array of scores[min, max]
# diff_lo = min – 25 and diff_hi =75 – max
# if diff_lo < diff_hi  question(min), else  question(max)