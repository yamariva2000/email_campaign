from data import data
from numpy.random import choice
from itertools import combinations,product
import numpy as np
from random import shuffle
from numpy.random import beta
import matplotlib.pyplot as plt
import seaborn as sb
import pandas as pd
def NB_sim(conv,sent,n=1000):

    # if sent<n:
    #     raw_input('sent is only ' + str(sent))
    #
    n=min(sent,n)


    return  n,beta(1+conv,1+sent-conv,n)



#print [i for i in productde(['generic','personalized'],['short_email','long_email'],['US','UK','ES','FR'])]


def run_sim():

    d=data()

    fig = plt.figure(1, figsize=(30, 15))
    fig.suptitle('NB simulations of Click Rate',fontsize=25)
    for j,i in enumerate(['prior_purchases','user_country','email_version','email_text','time','day_type']):
        p = d.query("user_country in ('US','FR')")
        p= pd.pivot_table(p,index=[i],
                             values=['sent','clicked'],aggfunc='sum')#.unstack()
        p['ctr']=p.clicked/p.sent


        ax=fig.add_subplot(3,2,j+1)
        plt.subplots_adjust(left=.125,right=.9,top=.9,bottom=.1,wspace=.2,hspace=.9)
        for z in xrange(len(p.index)):
            n,email_sim=NB_sim(p.values[z,0],p.values[z,1])
            m=np.mean(email_sim)

            ax.text(m,-50,p.index[z],fontsize=20,fontweight='bold',rotation=45,color='orange')

            ax.hist(email_sim,label="{} n={}".format(p.index[z],n))

        ax.set_title('{} vs. click rate'.format(i),fontsize=16)
        ax.set_xlabel('Click Rate',fontsize=16)
        plt.xticks(fontsize=16)

        ax.legend(loc=0,fontsize=14)
        ax.set_ylabel('Frequency',fontsize=14)
    plt.show()

def run_sim2():

    d=data()

    fig = plt.figure(2, figsize=(30, 15))
    fig.suptitle('NB optimized click rates',fontsize=25)
    for j,i in enumerate([['prior_purchases','user_country','email_version','email_text','day_type']]):
        #print d.head()


        p = d.query("user_country in ('US','FR') & prior_purchases in ['0 prior purchase','6+ prior'] & email_version=='personalized' "
                    "& email_text=='short_email' & "
                     "day_type=='Weekday'")

        p= pd.pivot_table(p,index=i,
                             values=['sent','clicked'],aggfunc='sum')#.unstack()

        p['ctr']=p.clicked/p.sent


        ax=fig.add_subplot(1,1,j+1)
        plt.subplots_adjust(left=.125,right=.9,top=.9,bottom=.1,wspace=.2,hspace=.9)
        for z in xrange(len(p.index)):
            n,email_sim=NB_sim(p.values[z,0],p.values[z,1])
            m=np.mean(email_sim)
            #print m
            ax.text(m,160,p.index[z],fontsize=20,fontweight='bold',rotation=45,color='orange')

            ax.hist(email_sim,label="{} n={}".format(p.index[z],n))

        ax.set_title('{} vs. click rate'.format(i),fontsize=16)
        ax.set_xlabel('Click Rate',fontsize=16)
        plt.xticks(fontsize=16)

        ax.legend(loc=0,fontsize=14)
        ax.set_ylabel('Frequency',fontsize=14)
    plt.show()


if __name__=='__main__':

    run_sim()
    run_sim2()