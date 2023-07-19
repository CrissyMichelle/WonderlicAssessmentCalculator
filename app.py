from flask import Flask, request, render_template, redirect, flash, session
from markupsafe import Markup  # prevents HTML tags in string to not get autoescaped
from flask_debugtoolbar import DebugToolbarExtension
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = "123-456"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

category = ["Weak", "Cautionary", "Moderate", "Strong"]
cogni_labels = ["Below Average", "Average", "Above Average"]

# question banks
question_bank_dependability = {'STRONG': ["Strong Dependability: Tell me about a time when you overworked your team. What did you learn?\n"
                               "Strong Dependability: Tell us about a time you came across as too confident. What did you learn?"],
                    'WEAK': ["Weak Dependability: Tell me about a time your lack of preparation or focus led to a failure. What did you learn?\n"
                            "Weak Dependability: Describe the biggest work problem you have encountered. How did you solve it?\n"
                            "Weak Dependability: Tell me about a time you were proactive on a mission and it had a significant impact."]}

question_bank_stress_tolerance = {'STRONG': ["Strong Stress Tolerance: Tell me about a time when your team was overly stressed and you were not. How did you lead your team to success?\n"
                               "Strong Stress Tolerance: Tell me about a time you had to complete a big task with inadequate resources. How did you complete it?"],
                    'WEAK': ["Weak Stress Tolerance: Tell me about a time you were overwhelmed with a project and reached out for help. What happened?\n"
                             "Weak Stress Tolerance: Tell me about a time you received difficult feedback. How did you utilize it?"]}

question_bank_cooperation = {'STRONG': ["Strong Cooperation: Tell me about a time you should have pushed back on a superior's tasking and didn't. How did it impact those working under you?\n"
                                  "Strong Cooperation: Tell me about a time you gave a leader negative feedback."],
                       'WEAK': ["Weak Cooperation: Tell me about a time you disagreed with your supervisor. How did you resolve it?\n"
                                "Weak Cooperation: Describe a time you came off as abrasive to others. How did that impact your ability to lead?"]}

question_bank_sociability = {'STRONG': ["Strong Sociability: Tell me about a time you were a poor listener, and it impacted your team. How did you adjust course?\n"
                               "Strong Sociability: Describe a time you empathized with a Soldier and took their perspective into account.\n"
                               "Strong Sociability: Tell me about a time you spoke “too soon”. What was the result?"],
                    'WEAK': ["Weak Sociability: Describe a time you had to work with a difficult group of subordinates. How did you bring them together?\n"
                             "Weak Sociability: Share a time you had one particularly difficult subordinate. How did you motivate them?"]}

question_bank_open_mindedness = {'STRONG': ["Strong Open-Mindedness: Tell me about a time you came up with an initiative to change a process in your section. Did it work? How do you know others bought into your idea?\n"
                                 "Strong Open-Mindedness: How do you know if your subordinates are open to new initiatives or your solutions to problems?"],
                      'WEAK': ["Weak Open-Mindedness: Tell me about a time you lost sight of the big picture mission. What did you learn?\n"
                               "Weak Open-Mindedness: Give a specific example of how you have helped create an environment where differences are valued, encouraged, and supported.\n"
                               "Weak Open-Mindedness: Tell me about the most effective contribution you have made as part of a task group or special project."]}

question_bank_all = {'dep': question_bank_dependability, 'sts': question_bank_stress_tolerance, 'cop': question_bank_cooperation, 'soc': question_bank_sociability, 'opm': question_bank_open_mindedness}


@app.route('/')
def index():
    """Show home page"""
    return render_template("base.html", question_bank_1S=question_bank_dependability['STRONG'], question_bank_1W=question_bank_dependability['WEAK'],
                           question_bank_2S=question_bank_stress_tolerance['STRONG'], question_bank_2W=question_bank_stress_tolerance['WEAK'],
                           question_bank_3S=question_bank_cooperation['STRONG'], question_bank_3W=question_bank_cooperation['WEAK'],
                           question_bank_4S=question_bank_sociability['STRONG'], question_bank_4W=question_bank_sociability['WEAK'],
                           question_bank_5S=question_bank_open_mindedness['STRONG'], question_bank_5W=question_bank_open_mindedness['WEAK'])


@app.route('/generated', methods=["POST"])
def handle_form():
    """Collect data from form"""
    full_name = request.form['last'] + ', ' + request.form['first']

    score_cognitive = request.form['cognitive']
    cog_label = cog_avg(score_cognitive)

    score_motivation = request.form["motivation"]
    score_overall_personality = request.form["overallP"]
    score_dependability = request.form["depend"]
    score_stress_tolerance = request.form["stress"]
    score_cooperation = request.form["cooperate"]
    score_sociability = request.form["social"]
    score_open_mindedness = request.form["openmind"]

    """check for valid input and produce labels"""
    try:
        score_list = [score_motivation, score_dependability, score_stress_tolerance, score_cooperation, score_sociability, score_open_mindedness]
        if valid_input(score_list) == True:

            moto_cat = label_score(score_motivation)
            overP_cat = label_score(score_overall_personality)
            dep_cat = label_score(score_dependability)
            stress_cat = label_score(score_stress_tolerance)
            coop_cat = label_score(score_cooperation)
            soci_cat = label_score(score_sociability)
            open_cat = label_score(score_open_mindedness)

            """Put categorical labels data into session storage"""
            session['labels'] = {'Cognitive': [score_cognitive, cog_label], 'Motivation': [moto_cat, score_motivation], 'Overall Personality': [overP_cat, score_overall_personality], 'Dependability': [dep_cat, score_dependability], 'Stress Tolerance': [stress_cat, score_stress_tolerance],
                                 'Cooperation': [coop_cat, score_cooperation], 'Sociability': [soci_cat, score_sociability], 'Open-Mindedness': [open_cat, score_open_mindedness]}

            """Generate list of questions"""
            weakP = mins_ask_this([score_dependability, score_stress_tolerance, score_cooperation, score_sociability, score_open_mindedness])
            strongP = max_ask_this([score_dependability, score_stress_tolerance, score_cooperation, score_sociability, score_open_mindedness])

            flash(
                Markup(
                    f"Name: {full_name}<br>"
                    f"Cognitive: {score_cognitive}<br>"
                    f"Motivation: {score_motivation}<br>"
                    f"Overall Personality: {score_overall_personality}<br>"
                    f"Dependability: {score_dependability}<br>"
                    f"Stress Tolerance: {score_stress_tolerance}<br>"
                    f"Cooperation: {score_cooperation}<br>"
                    f"Sociability: {score_sociability}<br>"
                    f"Open-Mindedness: {score_open_mindedness}"
                )
            )

            return render_template("generated.html", name=full_name, cognitive=cog_label, moto=moto_cat, person=overP_cat, label_data=session['labels'], questionsW=weakP, questionsS=strongP,
                                   question_bank_1S=question_bank_dependability['STRONG'], question_bank_1W=question_bank_dependability['WEAK'],
                                   question_bank_2S=question_bank_stress_tolerance['STRONG'], question_bank_2W=question_bank_stress_tolerance['WEAK'],
                                   question_bank_3S=question_bank_cooperation['STRONG'], question_bank_3W=question_bank_cooperation['WEAK'],
                                   question_bank_4S=question_bank_sociability['STRONG'], question_bank_4W=question_bank_sociability['WEAK'],
                                   question_bank_5S=question_bank_open_mindedness['STRONG'], question_bank_5W=question_bank_open_mindedness['WEAK'])
        else:
            return redirect('/')
    except:
        flash("UH-OH. What you typed caused an error. Please refresh the page and try again. Only numbers from 0 to 100 will work!!")
        return redirect('/')


def valid_input(vals):
    try:
        for val in vals:
            score = int(val)
            if 0 <= score <= 100:
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
        if score <= 94:
            return cogni_labels[0]  # Below Average
        elif 95 <= score <= 113:
            return cogni_labels[1]  # Average
        else:
            return cogni_labels[2]  # Above Average
    except:
        flash(f"{val} is an invalid entry for cognitive score. Please type in a valid number.")
        return None


def label_score(val):
    try:
        score = float(val)
        if score <=25:
            return category[0]  # weak
        elif 26 <= score <= 49:
            return category[1]  # cautionary
        elif 50 <= score <= 74:
            return category[2]  # moderate
        else:
            return category[3]  # strong
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
            quest.append(question_bank_all['dep']['WEAK'][0])
        elif arg == 'Stress Tolerance':
            quest.append(question_bank_all['sts']['WEAK'][0])
        elif arg == 'Cooperation':
            quest.append(question_bank_all['cop']['WEAK'][0])
        elif arg == 'Sociability':
            quest.append(question_bank_all['soc']['WEAK'][0])
        elif arg == 'Open-Mindedness':
            quest.append(question_bank_all['opm']['WEAK'][0])
        elif arg == 'Nothing recommended':
            quest.append("nothing to see here")

    return quest


def strongP_questions(string_list):
    quest = []
    for arg in string_list:
        if arg == 'Dependability':
            quest.append(question_bank_all['dep']['STRONG'][0])
        elif arg == 'Stress Tolerance':
            quest.append(question_bank_all['sts']['STRONG'][0])
        elif arg == 'Cooperation':
            quest.append(question_bank_all['cop']['STRONG'][0])
        elif arg == 'Sociability':
            quest.append(question_bank_all['soc']['STRONG'][0])
        elif arg == 'Open-Mindedness':
            quest.append(question_bank_all['opm']['STRONG'][0])
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