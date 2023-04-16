import pandas as pd 
from sklearn.cluster import KMeans 
import numpy as np
############    cleans up hh 
def PNind(df):
    df=df.loc[pd.isna(df.PN)==False]
    countPNyear=pd.DataFrame(df.groupby(['HHID','SUBHH','year'])\
        ['PN'].agg(['unique'])).reset_index()  ## gives PN list by year,HHID,SUBHH
    countPNyear.rename(columns={'unique':'PNlist'},inplace=True)
    countPNyear['countPN']=countPNyear.PNlist.apply(lambda x: len(x))

    countPNyear=countPNyear.loc[countPNyear.countPN==2]
    df=df.merge(countPNyear,how='left',on=['HHID','SUBHH','year']) ## gets PN list 
    df=df.loc[df.countPN==2]
    #countPNyear.PNlist=countPNyear.PNlist.map(tuple)  ## allows 2nd groupby
    #countPN=pd.DataFrame(countPNyear.groupby(['HHID','SUBHH','PNlist'])\
    #    ['year'].agg(['unique'])).reset_index()
    #countPN=countPN.rename(columns={'unique':'yearlist'})
    #countPN[['PNs0','PNs1']]=pd.DataFrame(countPN.PNlist.tolist(),columns=['PNs0','PNs1'])
    df[['PNs0','PNs1']]=df.PNlist.apply(pd.Series)
    #df[['PNs0','PNs1']]=pd.DataFrame(df.PNlist.tolist(),columns=['PNs0','PNs1'])
    #df=df.loc[pd.isna(df.PNs1)==False]  ##  hh must have two agents
    #df.drop(columns=['PNlist'],inplace=True)
    #df=df.merge(countPN[['HHID','SUBHH','PNs0','PNs1','']],how='left',on=['HHID','SUBHH','PNs0','PNs1'])
    return df

######################################################################
#####  PN to HH level (for time/hh)
def hhlevel(df,colnames):
    df['minPN']=df.groupby(['HHID','SUBHH','year'])['PN'].\
        transform('min')  ## turns out not all are  10 
    df.loc[df.PN==df['minPN'],'PN']='s0'
    df.loc[df.PN!='s0','PN']='s1'
    df=df.pivot(index=['HHID','SUBHH','year'],columns='PN',\
        values=colnames)
    df.columns=[''.join((j,k)) for j,k in df.columns]
    df=df.reset_index()
    return df
#######################################################################
######  CREATES TREATMENT INDICATOR/CONT (nbr of single parents)
def treatment(df):
    df['alives0'],df['alives1']=0,0
    for i in ['s0','s1']:
        df.loc[((df[f'lmomeventdate{i}']>0)&(df[f'ldadeventdate{i}']<0))|\
            ((df[f'lmomeventdate{i}']<0)&(df[f'ldadeventdate{i}']>0)),f'alive{i}']=1
    df['totalive']=df['alives0']+df['alives1']
    df['D']=0
    df.loc[df.totalive>0,'D']=1
    return df 
#######################################################################
######  TRANFORM DF TO BE MLE FORMAT (using julia so i can learn stuff)
def mle_df(df):
    '''
    a=(c,ch,hu,hc,Nw,Nh)
        c+savings (actually idk, maybe just part of consump?)=income+other inflow (assets) (if allie is ambitious) + ss 
    s_0=(w[1:2],y,i)  ## wages, income, investments/savings, using core hrs here
    -- thought for consump
        get inflow of cash, get outflow of savingsm assume diff is consump
    will also keep hhid, year
    Q: how to think of time? one day? idk all of this 
    '''
    Nh=['houseclean','washiron','yardwork','errands','mealprep']
    Nw=['workforpay']
    hu=['tv','readpaper','readbooks','sleep']
    hc=['volunteer','rel','meetings','concerts']  ## monthly 
    ###  rn using core to grab wage and ssi, using time to get Nw (i think this is ok?)
    # leaning towards using j to get wage (idk how else to know wage just income) and Q for ssi
    wage=['wage']
    ssi=['ssi']
    coldic={'Nh':(Nh,7),'hu':(hu,7),'hc':(hc,30)}  ## already have wage,ssi
    df=df.rename(columns={'wages0':'ws0','wages1':'ws1','workforpays0':'Nws0',\
        'workforpays1':'Nws1'})
    df.Nws0,df.Nws1=df.Nws0/7,df.Nws1/7
    ## time not sure how to think of time, everything in time is weekly or monthly, 
    ##      but when i think of this model in my head its daily, but is this complicated with work? 
    #######  rn going with daily and just divide by 7? (/30)
    for i in coldic.keys():
        for sp in ['s0','s1']:
            tempi=[x+sp for x in coldic[i][0]]  ## to get sp 
            ## normalize to day. feels weird.           
            df[f'{i}{sp}']=df[tempi].sum(axis=1)/coldic[i][1]  ## ignore na 
    ###   ideally add other assets 
    df['y']=df[['ssis0','ssis1']].sum(axis=1)  ##  cause consump/inflow is at hh 
    ######################################
    ###############    cluster into N groups 
    nclusters=10
    vars=['Nws0','Nws1','Nhs0','Nhs1','hus0','hus1','hcs0','hcs1','ws0','ws1','y']
    df[vars]=df[vars].fillna(0)
    ## if this is a valud IV right??
    #X0,X1=df.loc[df.D==0][vars],df.loc[df.D==1][vars]
    X=df[vars]
    ###  create groups 
    ##  non-treated pop
    kmeans=KMeans(n_clusters=nclusters,init='k-means++',max_iter=300,n_init=10,random_state=0)
    kmeans.fit(X)
    df['group']=kmeans.predict(X)
    ##  treated pop
    #kmeans1=KMeans(n_clusters=nclusters,init='k-means++',max_iter=300,n_init=10,random_state=0)
    #kmeans1.fit(X1)
    #df['group']=kmeans1.predict(X1)
    #########################################################
    ###  gets mean for group (how we are solving rn)
    for i in vars:
        df[f'g{i}']=df.groupby(['group','D'])[i].transform('mean')
    #df['c']=df['ssi']/365+df['ws0']*df['Nws0']+df['ws1']*df['Nws1']  ## for now..
    #df['work']=df['ws0']*df['Nws0']+df['ws1']*df['Nws1']
    df[['group','gws0','gws1','gy','gNws0','gNws1','gNhs0','gNhs1','ghcs0','ghcs1'\
        ,'D']].drop_duplicates('group').to_csv('group.csv')
    df[['Nws0','Nws1','Nhs0','Nhs1','hus0','hus1','hcs0','hcs1','ws0',\
        'ws1','y','alives0','alives1','totalive','D','group','gws0','gws1',\
        'gy']].to_csv('a.csv')  ## everything now contained within a 
    
##############################################################
#############################################     ESTIMATE TIME PARAMS :: \nu,tB,\delta
def shockparams(df): 
    ######  cleaning up the vars 
    vars=['helpmonth','helpweek','helpday']  #'hours',
    cleandic={'hours':(0,98),'helpmonth':(0,98),'helpweek':(0,8),'helpday':(0,8)}
    normdic={'helpmonth':1,'helpweek':4.35,'helpday':30.437}
    childlist=[3,5,6,8,np.nan]  ## son,son-in-law,daughter,daughter-in-law
    ######   only looks at single hh 
    df['pncount']=df.groupby(['HHID','SUBHH','year'])['PN'].transform('nunique')
    for i in cleandic.keys():
        df.loc[(df[i]<=cleandic[i][0])|(df[i]>=cleandic[i][1]),i]=np.nan
        
    for i in vars: 
        df[i]=df[i]*normdic[i]
    df['days']=df[vars].max(axis=1) 
    for i in ['days','hours']:
        df[i]=df[i].replace([98.,99.],np.nan)  
    ###   control for age here?
    for i in ['days']:  ## took out hours cause we want conditionall on 
            df[i]=df[i].replace(np.nan,0)

    #####   estimate the tB using hours 
    shockparams=pd.DataFrame(data={'tB':[0,0],'nu':[0,0]})
    for n in [1,2]:       ##  recording diff between single and couple mom and dads
        shockparams['nu'].loc[n-1]=np.mean(df.loc[(df.pncount==n)&(df.helprel.isin(childlist))].days)/30.437
        #df=df.loc[df.helprel.isin(childlist)]  ## must be a child.child spouse  (nan included )
        shockparams['tB'].loc[n-1]=np.mean(df.loc[(df.pncount==n)&(df.helprel.isin(childlist))].hours)  ## homogenous rn for hh 

    shockparams.to_csv("shockparams.csv")
#################################################################

#################################################################
############################################      ESTIMATE HH STATE 
############    estimate the state hh is in 
## rn super basic and will say if helpothers>tB=> loss of time tB and have shock 
def hhstate(df):
    shockparams=pd.read_csv("shockparams.csv")
    nu,tB=shockparams['nu'],shockparams['tB']
    df['state']=0 
    df.loc[(df.D==1)&(df.helpothers>tB),'state']=1  ## would like to turn this into a twfe thing 
    return df 
##################################################################
    