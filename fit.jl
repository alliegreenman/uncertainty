##################################################
##################################################
######################################    GETS FIT OF ESTIMATES
##################################################
function estfit(res)
    function statefit(s)
        filedic=Dict(1=>"Uastar.csv",2=>"Castar.csv")
        ################################## 
        #########    read in opts 
        Nw,Nh,hc,w=zeros(2),zeros(2),zeros(2),zeros(2)
        if c==1
            hc=zeros(4)
        end 
        astar=CSV.read(filedic[s],header=false)
        if c==1 
            Nw[1],Nw[2],Nh[1],Nh[2],hc[1],hc[2],hc[3],hc[4]=res
        end 

    β,θ,σ=zeros(6),zeros(6),zeros(2)

    #a=a[1,:]  ##for debugging
    ###################################
    ##  unpacking  (generalize this with no magic numbers)
    β,θ,σ,tB,κ,η,δ,ν=res[1:4],res[5:8],res[9:12], res[13],res[14],res[15],res[16],res[17]
    ####  init for groups 
    groups,G=unique(a[:,12]),length(unique(a[:,12]))  ##list of groups, nbr of unique groups 
    Uupper,Ulower=[24.,24.,24.,24.,24.,24.,24.,24.,24.,24.],fill(.001,CVuncertain)  #CVuncertain=10
    Cupper,Clower=[24.,24.,24.,24.,24.,24.],fill(.001,CVcertain)  ##VCceraint=6
    ####  iterate over groups
    for g in groups
        Cc0=initguess(a[a[:,12].==g,:],CVcertain)
        Uc0=initguess(a[a[:,12].==g,:],CVuncertain)
        ###############################################      ASSIGN STATE VARS FOR GROUP
        state=a[a[:,12].==g,:][1,13:15]  ## arbitraly taking first row (all are the same)
        condition=a[:,12].==g
        ###############################################      ESTIMATE AND POPULATE CV FOR UNCERTAINTY
        ######    estimate cv
        Ures=optimize(cvars->uncertainU(cvars,res,state),Ulower,Uupper,Uc0,
            Fminbox(NelderMead()),Optim.Options(show_trace=false, #show_every=5000, 
            iterations=50)) #x_tol=1e-5,f_tol=1e-5,))
        Ures=Optim.minimizer(Ures)
        ######     populate cv 
        for (i,y) in enumerate(Ures)  ##Nw, Nh, hc*2 , hct
            if i in (9,10)  ##these are hct
                nothing 
            elseif i<9  ## how to think of hct?
                ####   a[:,aoldind+9+1]-> Nw1, +2-> Nw2, +3->Nh1, +4->Nh2, +5 ->hc11, +6-> hc21, +7->hc21,+8->hc22,+9->hct1,+10->hct2
                a[:,base+i].=condition.*y.*a[:,17].+(1 .- condition).*a[:,base+i].*a[:,17]
            end 
        end 
        ################################################     ESTIMATE CV FOR CERTAINTY
        #####    estimate cv 
        Cres=optimize(cvars->certainU(cvars,res,state),Clower,Cupper,Cc0,
            Fminbox(NelderMead()),Optim.Options(show_trace=false, #show_every=5000, 
            iterations=50)) #x_tol=1e-5,f_tol=1e-5,))
        Cres=Optim.minimizer(Cres)
        ######    populate cv 
        for (i,y) in enumerate(Cres)  ##Nw, Nh, hc
            ####   a[:,aoldind+9+1]-> Nw1, +2-> Nw2, +3->Nh1, +4->Nh2, +5 ->hc11, +6-> hc21, +7->hc21,+8->hc22,+9->hct1,+10->hct2
            a[:,base+i].=condition.*y.*a[:,17].+(1 .- condition).*a[:,base+i].*a[:,17]
        end 
    end 
    return astar
end 