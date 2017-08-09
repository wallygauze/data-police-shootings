# Basic code for the app. Functionality and fast availability of the app
# was the focus for the prototype rather than anything else,
# it will be improved upon.

from flask import Flask, render_template
import pandas as pd
from scipy.stats import chisquare

app = Flask(__name__)

df_whole = pd.read_csv('../../fatal-police-shootings-data.csv')
df_whole.race.fillna(value='?', inplace=True)
# proxy column for counting with pivot_table
df_whole['#'] = 1

# : Race profile for top 3 racial groups

df_whole = df_whole[
    (df_whole["race"] == "W")
    | (df_whole["race"] == "B")
    | (df_whole["race"] == "H")].copy()

# :: Variables for the subsequent Chi-Square tests

t3_prop = df_whole.pivot_table(
    index='race',
    values='#',
    aggfunc=lambda x: float(sum(x)) / float(len(df_whole.race))).to_dict()['#']
t3_count = df_whole.pivot_table(
    index='race',
    values='#',
    aggfunc=sum).to_dict()['#']

t3_group_proportions = [t3_prop['W'], t3_prop['B'], t3_prop['H']]
# frequencies of unarmed deceased by racial group
f_obs_2t3 = [t3_count['W'], t3_count['B'], t3_count['H']]


@app.route("/unarmed")
def show_tables():

    total_positives = df_whole[
        (df_whole["armed"] == "unarmed")].shape[0]

    line1 = "count of people shot by the police that were unarmed: {}".format(
        df_whole[(df_whole["armed"] == "unarmed")].shape[0])
    line2 = "prop. of total count that were unarmed: {0:.2f}".format(
        float(df_whole[(df_whole["armed"] == "unarmed")].shape[0])
        / float(df_whole.shape[0]))


    data = df_whole[(df_whole["armed"] == "unarmed")]


    table1 = pd.DataFrame(
        data.pivot_table(
            index='race',
            values='#',
            aggfunc=[sum, lambda x:float(sum(x))/float(len(data.race))]
            )
        )
    table1.rename(columns={"sum": "count", "<lambda>": "proportion"},
                  inplace=True)
    table2_title = "Proportion of whole respective racial group in dataset"
    table2 = (df_whole[(df_whole["armed"] == "unarmed")]
              .race.fillna(value="?").value_counts()
              / df_whole.race.fillna(value="?")
              .value_counts().sort_values(ascending=False))
    table2 = pd.DataFrame(table2)
    table2 = pd.DataFrame(table2.race.rename('_'))

    # :: Chi-Square test
    chisquare_result_ = chisquare(
        f_obs_2t3,
        f_exp=([x * total_positives for x in t3_group_proportions])
        )
    if chisquare_result_[1] < 0.01:
        chisquare_result = """Chi-Square test of independence:
        Significant at alpha = 1%"""
    elif chisquare_result_[1] < 0.05:
        chisquare_result = """Chi-Square test of independence:
        Significant at alpha = 5%"""
    elif chisquare_result_[1] < 0.1:
        chisquare_result = """Chi-Square test of independence:
        Significant at alpha = 10%"""
    else:
        chisquare_result = """Chi-Square test of independence:
        Not significant at even alpha = 10%"""

    pvalue_interpretation = """(This percentage can be broadly interpreted as
    showing the probability such a result would have been found if there was
    actually no correlation between race and the proportion of the whole
    respective racial group in the dataset that falls in the \'unarmed\'
    group.)"""

    return render_template('view.html',
                           lines=[line1, line2],
                           table=table1.to_html(),
                           table2_title=table2_title,
                           table2=table2.to_html(),
                           x_result=chisquare_result,
                           pvalue_interpretation=pvalue_interpretation)


if __name__ == "__main__":
    app.run(port=8080, debug=True)
