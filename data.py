import matplotlib.pyplot as plt
from matplotlib.pyplot import subplot
import pandas as pd
import seaborn as sb
import numpy as np
import matplotlib.ticker as mtick

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
                                       np.where(cl.user_past_purchases.isin([3, 4, 5, 6]), '3-6 prior', '6+ prior')))

    cl['purchases_cat'] = np.where(cl['user_past_purchases'] > 0, '1+ purchases','0 purchases' )

    cl['country']=np.where(cl.user_country.isin(['US','UK']),'US_UK','FR_ES')


    cl['day_type']=np.where(cl.weekday.isin(['Saturday','Sunday']),'Weekend','Weekday')



    return cl


def rates_by_type(df, groups):
    group=df.groupby(groups)[['clicked','opened','sent']].sum()
    group['ctr']=group.clicked/group.opened*100
    group['opr']=group.opened/group.sent*100
    group['conv']=group.clicked/group.sent*100
    return group

def eda(graph=True):
    cl = data()

    open_rate = cl['opened'].sum() / 1. / len(cl)
    click_rate = cl['clicked'].sum() / 1. / cl['opened'].sum()
    click_sent_rate = open_rate * click_rate

    print 'open rate {0:.2f}%'.format(open_rate * 100)
    print 'click rate {0:.2f}%'.format(click_rate * 100)
    print 'click sent rate {0:.2f}%'.format(click_sent_rate * 100)


    hours = rates_by_type(cl[cl.hour<=20],['hour'])
    
    country=rates_by_type(cl,['user_country'])
    days=rates_by_type(cl,['day_type'])
    email_type = rates_by_type(cl, ['email_version'])
    email_text = rates_by_type(cl, ['email_text'])
    purchases=rates_by_type(cl,['prior_purchases'])
    time=rates_by_type(cl,['time'])

    plot=[country,purchases, email_type, email_text, days, time]
    fig = plt.figure(1, figsize=(24, 14))
    plt.suptitle('Figure 1: Email Campaign EDA', fontsize=25)
    import sampling

    for i,j in enumerate(plot):
        ax=fig.add_subplot(2,3,i+1)

        plt.title('Plot {}: Response vs. {}'.format(i+1,j.index.name),fontsize=20)


        # for h in range(len(j)):
        #     print j.iloc[h].name,j.iloc[h]['conv']
        #
        #     n,sims=sampling.NB_sim(j.iloc[h]['clicked'],j.iloc[h]['sent'],n=1000)
        #
        #     ax.hist(sims,label=j.iloc[h].name)


        sb.barplot(j.index,j['conv'],label='conversion')
        plt.plot(range(len(j.index)),j['opr'],label='open rate')
        ax.legend(loc=0,fontsize=20)

        fmt = '%.2f%%'
        yticks = mtick.FormatStrFormatter(fmt)
        ax.yaxis.set_major_formatter(yticks)

        plt.ylabel('percent',fontsize=16)

        plt.xticks(fontsize=16)
    if graph:
        plt.show()



def tsne():
    d=data()

    pd.set_option('display.width', 1000)

    dum=d[['email_text', 'email_version','time','day_type','prior_purchases']]

    x=pd.get_dummies(dum)


    y=d.clicked

    x_train, x_test, y_test,y_test =train_test_split(x,y,test_size=.02,random_state=0)
    from sklearn.manifold import TSNE
    tsne=TSNE(n_components=2,random_state=0)

    x_2d=tsne.fit_transform(x_test)

    markers=['s','o']
    colors=['green','blue']

    for i,label in enumerate(np.unique(y_test)):
        plt.scatter(x_2d[y_test==label,0],y=x_2d[y_test==label,1],c=colors[i],marker=markers[i],label=label)

    plt.show()

if __name__=='__main__':

    eda()
    #tsne()