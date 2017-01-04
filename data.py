import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sb
import numpy as np

def data():
    # returns left outer joined table containing all emails with columns for sent, clicked and read indications
    emails = pd.read_csv('email_table.csv').sort_values(by='email_id')
    emails['sent'] = 1

    opened_id = pd.read_csv('email_opened_table.csv').sort_values(by='email_id')

    clicked_id = pd.read_csv('link_clicked_table.csv').sort_values(by='email_id')

    opened_id['opened'] = 1
    clicked_id['clicked'] = 1

    op = pd.merge(emails, opened_id, how='left', on='email_id')

    cl = pd.merge(op, clicked_id, how='left', on='email_id')
    cl.fillna(0, inplace=True)

    cl['time'] = np.where((cl['hour'] == 6) & (cl['hour'] <= 12), 'Morning', np.where((cl.hour > 12) & (cl.hour < 18),
                                                                                   'Afternoon', np.where(
            (cl.hour >= 18) & (cl.hour <= 24), 'Night', 'Early Morning')))
    cl['prior_purchases'] = np.where(cl['user_past_purchases'] == 0, '0 prior purchase',
                              np.where(cl['user_past_purchases'].isin([1, 2]), '1-2 prior',
                                       np.where(cl.user_past_purchases.isin([3, 4, 5, 6]), '3-6 prior', '6+ prior'))
                              )
    cl['day_type']=np.where(cl.weekday.isin(['Saturday','Sunday']),'Weekend','Weekday')


    #                           np.where((d.user_past_purchases in (1,2),
    # '1-2', np.where(d.user_past_purchases in (3,4,5,6), '3-6', np.where(d.user_past_purchases>6,'6+','NA')))))
    #
    cl['email_type'] = np.where((cl.email_version == 'personalized') & (cl.email_text == 'short_email'), 'personal_short',
                               'other')


    return cl


def eda(graph=True):
    # if raw_input()=='s':
    #     graph=True
    cl = data()

    open_rate = cl['opened'].sum() / 1. / len(cl)
    click_rate = cl['clicked'].sum() / 1. / cl['opened'].sum()
    click_sent_rate = open_rate * click_rate

    # print 'open rate {0:.2f}%'.format(open_rate * 100)
    # print 'click rate {0:.2f}%'.format(click_rate * 100)
    # print 'click sent rate {0:.2f}%'.format(click_sent_rate * 100)

    hours_clicked = cl.groupby('hour')['clicked'].sum()
    hours_sent = cl.groupby('hour')['sent'].sum()
    percent_hours_clicked = hours_clicked.div(hours_sent)
    percent_hours_clicked.name = 'percent_hours_clicked'
    hours_clicked = pd.concat([hours_clicked, hours_sent, percent_hours_clicked], axis=1)

    country_clicked = cl.groupby('user_country')['clicked'].sum()
    country_sent = cl.groupby('user_country')['sent'].sum()
    percent_country_clicked = country_clicked.div(country_sent)
    percent_country_clicked.name = 'percent'
    country = pd.concat([country_clicked, country_sent, percent_country_clicked], axis=1)
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    day_no = cl['weekday'].apply(lambda x: weekdays.index(x))

    cl['day_no'] = day_no

    days = cl.groupby('day_no')['clicked'].sum()
    days_sent = cl.groupby('day_no')['sent'].sum()
    percent_days = days.div(days_sent)
    percent_days.name = 'percent_days'

    days_vs_clicks = pd.concat([days, days_sent, percent_days], axis=1)

    email_type_clicked = cl.groupby(cl['email_version'] + '-' + cl['email_text'])['clicked'].sum()
    email_type_sent = cl.groupby(cl['email_version'] + '-' + cl['email_text'])['sent'].sum()
    percent_email_type_clicked = email_type_clicked.div(email_type_sent)
    percent_email_type_clicked.name = 'percent'

    email_types = pd.concat([email_type_clicked, email_type_sent, percent_email_type_clicked], axis=1)

    purchases_clicked = cl.groupby(cl['user_past_purchases'])['clicked'].sum()
    purchases_sent = cl.groupby(cl['user_past_purchases'])['sent'].sum()

    percent = purchases_clicked.div(purchases_sent)
    percent.name = 'percent'
    purchases = pd.concat([purchases_clicked, purchases_sent, percent], axis=1)
    #print purchases

    fig = plt.figure(1, figsize=(24, 14))

    ax = fig.add_subplot(2, 3, 1)

    plt.suptitle('Email Campaign EDA', fontsize=20)
    ax.bar(hours_clicked.index, hours_clicked['percent_hours_clicked'], color='Green')
    ax.legend(loc=0)
    plt.ylabel('percent clicked')
    ax2 = ax.twinx()

    ax2.plot(hours_clicked.index, hours_clicked['sent'], label='sent')
    ax2.legend(loc=0)
    plt.title('Clicks vs Hour email sent')
    ax = fig.add_subplot(2, 3, 2)

    xticks = weekdays

    sb.barplot(xticks, days_vs_clicks['percent_days'].values)
    plt.title('Clicks vs Day email sent')

    fig.add_subplot(2, 3, 3)

    sb.barplot(email_types.index, email_types['percent'].values)
    plt.title('Clicks vs Email Type')
    plt.xticks(rotation=45)

    ax = fig.add_subplot(2, 3, 4)

    ax.plot(purchases.index, purchases['sent'].values, color='blue', label='sent')
    ax.legend(loc=0)
    ax2 = ax.twinx()
    ax2.bar(purchases.index, purchases['percent'].values, color='green', label='click percent')
    # ax2.legend(loc=0)
    ax2.set_ylim(0, .2)
    ax.set_xlim(0, 15)
    plt.title('Clicks vs Purchases')

    ax = fig.add_subplot(2, 3, 5)

    ax.bar([1, 2, 3, 4], country['percent'].values, color='blue', label='percent of sent clicked')
    plt.xticks([1, 2, 3, 4], country.index)
    ax.legend(loc=0)
    # ax2 = ax.twinx()
    # ax2.plot(country.index, country['percent'].values, color='green', label='click percent')
    # ax2.legend(loc=0)
    plt.title('Clicks vs Country')

    if graph:
        plt.show()



if __name__=='__main__':

    eda()