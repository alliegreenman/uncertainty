#####    TIME DICS 
consumpdic={
    'TRIPS AND VACATIONS':'tripspend','HOME REPAIRS/MAINTENANCE DIY':'homerepairsdiy',\
    'HOME REPAIRS/MAINTENANCE SERVICES':'homerepairservice','HOUSEHOLD FURNISHINGS AND EQUIPMENT':\
    'homeconsump','CONTRIBUTIONS':'donations','GIFTS':'gifts','HOUSE/YARD SUPPLIES':'housesupplies',\
    'HOUSE/YARD - PER':'housesuppliesper','GARDENING/YARD SUPPLIES':'yardsupplies',\
    'GARDEN/YARD SUPPLIES - PER':'yardsuppliesper','GARDEN/YARD SERVICES':'yardservice',\
    'GARDEN/YARD SERVICES - PER':'yardserviceper','PERSONAL CARE PRODUCTS/SERVICES':'pc'\
    ,'PERSONAL CARE PROD/SERVICES - PER':'pcper',\
    'TICKETS':'tickets','TICKETS - PER':'ticketsper','SPORTS EQUIPMENT':'sportseqm','SPORTS EQUIPMENT - PER':\
    'sportseqmper','HOBBIES/LEISURE EQUIPMENT':'hobbyeqm','HOBBIES/LEISURE EQUIPMENT - PER':\
    'hobbyeqmper','FOOD/DRINK GROCERY':'foodgroc','FOOD/DRINK GROC - PER':'foodgrocper',\
    'DINING OUT':'dining','DINING OUT - PER':'diningper','GASOLINE':'gas','GASOLINE - PER':\
    'gasper','HH SPENT':'hhspent','HOUSEKEEPING SERVICES':'hkservices','HOUSEKEEPING SERVICES - PER':\
    'hkservicesper'
    }  #  ,'CLOTHING AND APPAREL':'clothes','CLOTHING AND APPAREL - PER':'clothesper'

#############################################################
w,m=0,1
timedic={
    ######################   weekly \
    "WATCH TV":('tv',w),"READ PAPERS/MAGS":('readpaper',w),"READ BOOKS":('readbooks',w),
    "LISTEN MUSIC":('music',w),"SLEEP/NAP":('sleep',w),"WALK":('walk',w),"SPORTS/EXERCISE":('sport',w),\
    "VISIT IN PERSON":('visit',w),"PHONE/LETTERS/EMAIL":('comm',w),"WORK FOR PAY":('workforpay',w),\
    "USE COMPUTER":('computer',w),"PRAY/MEDITATE":('pray',w),"HOUSE CLEANING":('houseclean',w),\
    "WASH/IRON/MEND":('washiron',w),"YARD WORK/GARDEN":('yardwork',w),"SHOP/RUN ERRANDS":('errands',w),\
    "MEALS PREP/CLEAN-UP":('mealprep',w),"PERSONAL GROOMING":('personalgrooming',w),"PET CARE":(\
    'petcare',w),"SHOW AFFECTION":('showaffection',w),"TIME SPENT ON EATING MEALS LAST WK":('eating',w),\
    ######################   monthly     
    "HELP OTHERS":('helpothers',m),"VOLUNTEER WORK":('volunteer',m),"RELIGIOUS ATTENDANCE":('rel',m),\
    "ATTEND MEETINGS":('meetings',m),"MONEY MANAGEMENT":('moneymanagement',m),"MANAGING MEDICAL CONDITION":\
    ('managemedicalcondition',m),"PLAY CARDS/GAMES/PUZZLES":('playcards',m),"CONCERTS/MOVIES/LECTURES":\
    ('concerts',m),"SING/PLAY INSTRUMENT":('playinstrument',m),"ARTS AND CRAFTS":('artscrafts',m),\
    "HOME IMPROVEMENTS":('homeimprovement',m),"VEHICLE MAINTENANCE/CLEANING":('vehiclemaintain',m),\
    "LEISURE DINING/EATING OUT":('leisdining',m)
    }

