#################################################################
###################################    CLEANS HRS AND TIME DATA - TIME BASE
#################################################################
#######  NOTES 
#  MAKES TIME THE BASE AND ONLY CHARS FROM CORE ARE FED INTO THE TIME 
#   MAIN TIME INVARIANT - DATE MOM/DAD DIED (O/W FE SHOULD TAKE CARE OF SHIT 
#       UNLESS I WANT TO LOOK AT HTE) + WAGE / EMP (FROM J_R) + AGE (A_RS)
#  NEED TWO AGENTS IN HH AND ONLY CONSIDER YEARS WHERE WE SEE TIME 
#   ALLOC FOR BOTH AGENTS 
#  WILL ADD / THINK MORE ABOUT CONSUMP IN TIME AND HRS (FOR FOOD DELIVERY)
#  WITH CURRENT SETUP ONLY TIME NEEDS TO HAVE BOTH RESPONDANTS IF SOME 
#    ASSPTNS ON WAGES ARE MADE, FOR NOW WE WILL KEEP IT RESTRICTIVE TO I==2
# DYNAMIC: WAGES, EMPLOYMENT, MARITIAL STATUS (BUT SUBHH SHOULD BE SUFFICIENT), 
#  ASSETS (Y), ALL TIME/CONSUMP
# STATIC: DATEMOMDIED
##################################################################
import pandas as pd 
import numpy as np 
####  gets dics for core vars 
from diccore import gendic 
from timedic import timedic,consumpdic
from hrsdic import genhrscols 
hrsdic=genhrscols()
from hrshelper import PNind,hhlevel,mle_df,treatment,shockparams

## fix the est_age, not super motivated rn
##  how to think of disability income?
###################################################################
###############   'CONFIG PART'   (both core and time)
start,end=2002,2018
t0,t1=2001,2017
end+=2
dfs=['F_R','A_R','J_R','PR_R','Q_H','G_HP']  ## keeping P_R for momprevalive as a bug check
###################################################################

###################################################################
####   DEFINES SOME OBJECTS BASED ON CONFIG (kindof)
dfsyears={'P_R':[2008,2010,2012,2014,2016,2018],'A_H':[],\
    'PR_R':[],'F_R':[],'A_R':[],'J_R':[],'Q_H':[],'G_HP':[]}   ##  years that do not work
dftype={'F_R':'S','P_R':'S','PR_R':'S','A_R':'D','A_H':'D',\
    'J_R':'D','P_R':'D','Q_H':'D','G_HP':'D'}   ##  if df is static or dynamic
typedic={'S':['SUBHH','HHID'],'D':['SUBHH','HHID','year'],'R':['PN'],\
    'H':[],'SR':['SUBHH','HHID','PN'],'DR':['SUBHH','HHID','PN','year'],\
    'DH':['SUBHH','HHID','year'],'DP':['SUBHH','PN','HHID','year']}  ## last should kinds actually be DHP, but this works:)  
### add dic for hh\implies [], _R \implies 'PN'
###  maps vars to years
years=[]
totyears=np.arange(start,end,2,dtype=int)
for x in totyears:
    if x==start: ## this is brute force 
        years+=[(x,'H')]
    else:
        years+=[(x,chr(ord('A')+int((x-1992)/2)+3))]
###  init object to store core dfs 
coredic={}
for i in dfs:
    coredic[i]={}
##  some init for time 
timeyears=list(np.arange(t0,t1+1,2))
timetemp={}
###################################################################

###################################################################
#################################################           CLEANS CORE 
###################################################################
###############  
##  renames to make one to one mapping THIS IS COMPLETE TRASH 
for df in dfs:
    #dfcols=[x[0] for x in gendic[df]]  ## need to add the proper char in front
    for i in years:   ### just initializing some shit 
        tempyr=i[0]-2000
        if tempyr<10:
            tempyr='0'+str(tempyr)
        else:
            tempyr=str(tempyr)
        coredic[df][i[0]]=pd.read_csv(f'H{tempyr}{df}.csv',)
        coredic[df][i[0]]['year']=i[0]
        for x in gendic[df]:
            x=list(x)
            if df=="PR_R" and i[0]>2002 and (x[1]=='momprevalive' or x[1]=='dadprevalive'):
                x[0]+='_R'
            coredic[df][i[0]]=coredic[df][i[0]].rename(columns={f'{i[1]}{x[0]}':x[1]})

##############################################################
###########   APPENDS FILE DFS TOGETHER
df2={key: pd.concat(value,axis=0,join='inner') for key,value in coredic.items()}  ## chatpt*=allie *9.99e^9999
##############################################################
########        CREATE STATIC AND DYNAMIC VARS 
###############        STATIC 
static=df2['F_R'].groupby(typedic['SR'],as_index=False)[['mommonthdied','momyeardied'\
    ,'dadmonthdied','dadyeardied','parmarried']].min()
static=static.merge(pd.DataFrame(df2['PR_R'].groupby(typedic['SR'],\
    as_index=False)[['momprevalive','dadprevalive']].min()),on=typedic['SR'],how='left')
########   clean up mommonthdied and create momdatedied 
for i in ['mom','dad']:
    static[f'{i}datedied']=static[f'{i}yeardied']*1000+static[f'{i}monthdied']   
################       DYNAMIC
dyndfslist=[x for x in dfs if dftype[x]=='D']

#dyndfs=pd.concat([df2[key].reset_index() for key in dyndfslist],axis=1)
for i in dyndfslist:
    if i==dyndfslist[0]:
        dyndfs=df2[i]
    else:
        dyndfs=pd.merge(dyndfs,df2[i],how='left',on=typedic[f'{dftype[i]}{i[-1]}'])  
####   creating a wage - hellish 
unitsdic={1:1,2:5*8,3:5*8*2,4:5*8*4,5:5*8*4*2,6:52*5*8,11:8,0:1}  ### not sure about this (weeks nbr)?
##  lazy and doing a dotproduct - filling nan with 0 
poswages=['hourly','salary','selfempwage','selfempplus']
dyndfs[[col for col in dyndfs if col.endswith('units')]]=dyndfs[[col for col in dyndfs if \
    col.endswith('units')]].fillna(0)
dyndfs[poswages]=dyndfs[poswages].fillna(0)
for i in poswages:
    dyndfs.loc[dyndfs[i]>=999998,i]=0
    dyndfs.loc[dyndfs[i]==-8,i]=0  ## web non-response
    if i!='hourly':
        dyndfs.loc[(dyndfs[f'{i}units'].isin([8,-8,7,97,99,98])),f'{i}units']=0
       
    ###  above should take care of 99% of cases, but.. 
dyndfs[f'wage']=dyndfs[f'hourly']+dyndfs[f'salary']/dyndfs\
    [f'salaryunits'].map(unitsdic)+dyndfs[f'selfempwage']/\
    dyndfs[f'selfempwageunits'].map(unitsdic)+dyndfs[\
    f'selfempplus']/dyndfs[f'selfempplusunits'].map(unitsdic)
dyndfs.loc[dyndfs[f'wrkhrswk']>995,f'wrkhrswk']=0
dyndfs.loc[dyndfs[f'wksworked']>95,f'wksworked']=0
 
dyndfs.loc[dyndfs[f'wage']<0,f'wage']=0  
###############       USES ASSETS FILE TO GET INCOME AND SSI (and ambitious allie gets other assets)
for i in ['income','ssi','selfincome']:
    dyndfs[i]=0
    dyndfs[i]=np.where(dyndfs['PN_FIN']==dyndfs['PN'],dyndfs[f'r{i}'],\
        dyndfs[f'sp{i}'])
    dyndfs.loc[(dyndfs[i]<0)|(dyndfs[i]>999997),i]=0

## wrkhrswk for 'effect wage', add vacation and others for more precise? 
###############      FIX ANY MISING AGES 
dyndfs['day']=1
dyndfs['date']=pd.to_datetime(dict(year=dyndfs.yearint,\
    month=dyndfs.month,day=dyndfs.day))
#grouped=dyndfs.groupby(typedic['SR'])
#first_values = [group[['age','date']].first_valid_index() for name, \
#    group in grouped]
#new_df=pd.DataFrame(list(tuple(grouped.groups.keys())),columns=['HHID', 'SUBHH','PN'])
#new_df['age_est']=dyndfs
#dyndfys=pd.merge(df, new_df, on=typedic['SR'])
###############################################################
#########      ESTIMATE PARAMS :: \nu, t, \delta
shockparams(df=dyndfs)
###############################################################
#########      ESTIMATE STATE  :: s==1 \implies shock, s==0 \implies (D==0 || (D==1 && s==0)
shockparams(df=dyndfs)
###############################################################
#########      FILTERS OUT YEARS AND HH WITHOUT 2 AGENTS 
###  take the unique PNs by HH and year and find the years that satisfy
dyndfs=PNind(df=dyndfs)

###############################################################
######     MERGE STATIC AND DYNAMIC TO TIME 
######     RELABEL TO *s0, *s1, note: each SUBHH is now a HH 

###############################################################
###############################################################
################################################        CLEANS TIME 
###############################################################
######    CLEANS 
for x in timeyears: ## pretty sure there are +3 lines needed 
    xyear=x-2000
    if xyear<10:
        xyear='0'+str(xyear)
    else:
        xyear=str(xyear)
    timetemp[x]=pd.read_csv(f'time{xyear}.csv')
    timetemp[x]['year']=int(x)-1  ## think i this more 
    timetemp[x].rename(columns=hrsdic[xyear],inplace=True)
    if x!=timeyears[0]:      
        df=pd.concat([df,timetemp[x]],join='outer')  ### note this allie - we are all good 
    else:
        df=timetemp[x]
######################################################################
#########     CLEAN BY HH PN 
#df=PNind(df=df)
######################################################################
#########     SOME RENAMING /CLEANING 
##  time 
colnames,keynames=[x[0] for x in timedic.values()],\
    [x for x in timedic.keys()]
time=df[keynames+typedic['DR']]  ##  only keeping a subset 
time=time.rename(columns=dict(zip(keynames,colnames)))  ## renames 
##  consump
consump=df[list(consumpdic.keys())+typedic['DR']]  ##  only keeping a subset 
consump=consump.rename(columns=consumpdic)
consump=pd.DataFrame(consump.groupby(['HHID','year','SUBHH'],\
    as_index=False)[list(consumpdic.values())].max())
monthlyconsumpmap={1:12,2:1,3:0}
weeklyconsumpmap={1:52,2:12,3:1,4:0} 
monthlyconsump=['housesupplies','yardsupplies','yardservices','hkservices']
weeklyconsump=['tickets','hobbieseqm','foodroc','dining','gas']  ##clothes
for i in consumpdic.keys():  ### should have just done two sep dics
    if 'per' in consumpdic[i]:
        if consumpdic[i][:-3] in weeklyconsump:
            consump[consumpdic[i][:-3]]=consump[consumpdic[i][:-3]]\
                *consump[consumpdic[i]].map(weeklyconsumpmap)
        elif consumpdic[i][:-3] in monthlyconsump:
            consump[consumpdic[i][:-3]]=consump[consumpdic[i][:-3]]\
                *consump[consumpdic[i]].map(monthlyconsumpmap)
######################################################################
################     MERGE TO CORE - making hh level the base and then agent
###  time invariant
time=time.merge(static,how='left',on=['HHID','SUBHH','PN'])
time['eventdate']=time.year*1000+10
#time['eventdate']=pd.to_datetime(f'{str(df.year)}-10-01')
##  make eventdate vars 
for i in ['mom','dad']:
    time.loc[(pd.isna(time[f'{i}datedied'])==True)&(time[f'{i}prevalive']==1),f'{i}datedied']=2030*1000 ## stillalive
    time.loc[(pd.isna(time[f'{i}datedied'])==True)&(time[f'{i}prevalive']==5),f'{i}datedied']=1990*1000 ## dead
    ### fix this, dont need eventdate,just using year for time (and consump outside of deliver food)
    time[f'l{i}eventdate']=(round((time.eventdate)/1000)-round(time[f'{i}datedied']/1000))*12+\
        (time.eventdate)%1000-(time[f'{i}datedied']%1000)  ###  gets the weekly l 
    time[f'l{i}eventdatemonth']=(round(time['eventdate']/1000)-round(time[f'{i}datedied']/1000))*12+\
        (time['eventdate']%1000-(time[f'{i}datedied']%1000))-1  ###  gets the monthly l (could get more fancy, rn just constant shift )
    time[f'l{i}eventdateyearly']=(round(time['eventdate']/1000)-round(time[f'{i}datedied']/1000))*12+\
        (time['eventdate']%1000-(time[f'{i}datedied']%1000))-12  ###  gets the weekly l 
###  time variant 
time=PNind(df=time)   ## checking PNlist to PNs0, PNs1 
time=time.merge(dyndfs,how='left',on=typedic['DR']+['PNs0','PNs1'])  
time=time.merge(consump,how='left',on=['HHID','SUBHH','year'])
######################################################################
###############      TRANFORM TO HH LEVEL 
time=hhlevel(df=time,colnames=list(set(time.columns)-set(['HHID',\
    'SUBHH','PNs1','PNs0','year','PN'])))  ## need to understand the form , idk whats going on with PN
#time.drop(columns='PN',inplace=True)  ### to allow later specification of PN for agent level
time['idhhid']=time.HHID*1000+time.SUBHH  ## gives unique id for hh level
###  SAVE TO FILE (TWFE FORMAT)
time.drop_duplicates(['year','HHID','SUBHH'],keep='first').to_csv('hhdf.csv')
#####################       CREATE TREATMENT DUMMY / CONT 
time=treatment(df=time)
#####################       CREATE MLE FORMAT 
mle_df(df=time)

####################################################################
####################################################################
#############################                        MAP TO AGENT LEVEL 
####################################################################
####################################################################ime2=time.copy(deep=True)  ### will use for 's1'
time2=df.copy(deep=True)
time['PN']=10

time2['PN']=20
#time.drop(columns='PNs0',inplace=True),time2.drop(columns='PNs1',inplace=True)  ### idt this the two lines above are really needed,bt rn have duplicates
time.columns=[x.replace('s0','') for x in time]
time2.columns=[x.replace('s1','') for x in time2]  ## makes 's1' the respondant 
time2.columns=[x.replace('s0','s1') for x in time2]  ## meakes 's0' 's1' or the spouse

time=pd.concat([time,time2])
time['id']=time.HHID*1000+time.SUBHH*100+time.PN
time.to_csv('agentdf.csv')

stop


