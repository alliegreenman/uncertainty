######################################################
#########################################   SOLVES TIME ALLOCATION MODEL 
######################################################
using Optim, NLSolversBase, Random,Symbolics,CSV,DataFrames,Distributions, 
    Parameters,ModelingToolkit,ForwardDiff,CategoricalArrays,StatsBase,Tables
using LinearAlgebra: diag
##  may need to make the focs 2 again
include("helperfct.jl")
N,a=dfobs()
global CVuncertain=2*2+4+2  ## counterfactuals plus hct
global CVcertain=2+2+2  #Nw,Nh,hc
a=hcat(a,zeros(size(a,1),CVuncertain))
a=hcat(a,zeros(size(a,1),CVuncertain-2))  ## pop diff - no hct
global base,base2=17,27
#####   import the estimated shock params ::  ν, tB
shockdf=CSV.read("shockparams.csv",DataFrame)  ## may need header=false
global tB,ν=shockdf[1,1],shockdf[1,2]
# next: demean lc,lu idk about consump? cause idk how to think about this
## problems: not usine hu but i feel like i should, just even as a gut check/robusteness
###########################################################
###########################################################
## a[:,16]->totalive, 17->D

include("uncertainU.jl"),include("certainU.jl"),include("EM.jl") #,include("fit.jl")

###########################################################
######################################     DEFINING LOG-LIKELIHOOD
###########################################################
function loglik(γ,a,ν,tB)
    ###################################
    ####  init for groups 
    groups,G=unique(a[:,12]),length(unique(a[:,12]))  ##list of groups, nbr of unique groups 
    ## initiate vectors 
    β,θ,σ=zeros(4),zeros(4),zeros(4,2)
    Ures,Cres=Vector{Vector{Float64}}(undef, G),Vector{Vector{Float64}}(undef, G) #zeros(G),zeros(G)
    #a=a[1,:]  ##for debugging
    ###################################
    ##  unpacking  (generalize this with no magic numbers)
    β,θ,σ[:,1],σ[:,2],κ,η,δ=γ[1:4],γ[5:8],γ[9:12],γ[13:16], γ[17],γ[18],γ[19]

    Uupper,Ulower=[24.,24.,24.,24.,24.,24.,24.,24.,24.,24.],fill(.001,CVuncertain)  #CVuncertain=10
    Cupper,Clower=[24.,24.,24.,24.,24.,24.],fill(.001,CVcertain)  ##VCceraint=6
    ####  iterate over groups
    for g in groups
        g=Int(g)
        Cc0=initguess(a[a[:,12].==g,:],CVcertain)
        Uc0=initguess(a[a[:,12].==g,:],CVuncertain)
        ###############################################      ASSIGN STATE VARS FOR GROUP
        @show g,a[a[:,12] .==g,:],groups

        state=a[a[:,12].==g,:][13:15]  ## arbitraly taking first row (all are the same)
        condition=a[:,12].==g
        ###############################################      ESTIMATE AND POPULATE CV FOR UNCERTAINTY
        ######    estimate cv
        temp=Optim.minimizer(optimize(cvars->uncertainU(cvars,γ,state),Ulower,Uupper,Uc0,
            Fminbox(NelderMead()),Optim.Options(show_trace=false, #show_every=5000, 
            iterations=50))) #x_tol=1e-5,f_tol=1e-5,))
        @show temp,groups,Int(g),g,groups
        Ures[Int(g)+1]=temp
        #Ures[Int(g)]=Optim.minimizer(Ures[Int(g)])
        @show Ures[Int(g)+1]
        ######     populate cv 
        for (i,y) in enumerate(Ures[Int(g)+1])  ##Nw, Nh, hc*2 , hct
            if i in (9,10)  ##these are hct
                nothing 
            elseif i<9  ## how to think of hct?
                ####   a[:,aoldind+9+1]-> Nw1, +2-> Nw2, +3->Nh1, +4->Nh2, +5 ->hc11, +6-> hc21, +7->hc21,+8->hc22,+9->hct1,+10->hct2
                a[:,base+i].=condition.*y.*a[:,17].+(1 .- condition).*a[:,base+i].*a[:,17]
            end 
        end 
        ################################################     ESTIMATE CV FOR CERTAINTY
        #####    estimate cv 
        Cres[Int(g)+1]=Optim.minimizer(optimize(cvars->certainU(cvars,γ,state),Clower,Cupper,Cc0,
            Fminbox(NelderMead()),Optim.Options(show_trace=false, #show_every=5000, 
            iterations=50))) #x_tol=1e-5,f_tol=1e-5,))
        #Cres[Int(g)]=Optim.minimizer(Cres)
        ######    populate cv 
        @show Cres
        for (i,y) in enumerate(Cres[Int(g)+1])  ##Nw, Nh, hc
            if i<4
                ####   a[:,aoldind+9+1]-> Nw1, +2-> Nw2, +3->Nh1, +4->Nh2, +5 ->hc11, +6-> hc21, +7->hc21,+8->hc22,+9->hct1,+10->hct2
                a[:,base+i].=condition.*y.*a[:,17].+(1 .- condition).*a[:,base+i].*a[:,17]
            end 
        end 
    end 
    #############    build in diff into a 
    for c in 1:CVuncertain-2   ## no hct
        a[:,base2+c]=a[:,c].-a[:,base+c]
    end 
    ########    FEEDS INTO EM TO EST ν, σ 
    @show ν,tB
    #ν,σ=EM(ν,σ,a)  ## state is now apart of state space (assuming observable)
    ULL,CLL=hcat(fill(ν,N),fill(1-ν,N)),ones(N)
    σdic=Dict(1=>1,2=>1,3=>2,4=>2,5=>3,6=>3,7=>3,8=>3,9=>4,10=>4)  ## make nte on the interpretation here, not consump, but Nw here
    error=.01
    ################################################################################
    ##################################################               LOG LIKELIHOOD ESTIMATION 
    ################################################################################

    ###########################     UNCERTAINTY CASE 

    
    Ua=a[a[:,17].==1,:]
    prob=[ν,1-ν]
    CVνdic=Dict(5=>1,6=>1,7=>2,8=>2)
    
    ###  assuming σ the same across mom and dad but different across states
    for c in 1:CVuncertain-2  ## no hct
        if c in keys(CVνdic) 
            ULL[:,CVνdic[c]].*=sum(pdf.(Normal(0,σ[3,Int(floor((c-3)/2))]),Ua[:,base2+c]))  ## probs built into ULL mat
        else 
            for s in 1:2  ##not the prob will be the same for these cvs 
                ULL[:,s]=ULL[:,s].*sum(pdf.(Normal(0,σ[σdic[c],s]),Ua[:,base2+c]))
            end
        end
    end  
    #ULL+=prob*sum(cdf.(Normal.(0,σ[σdic[c]]),Ua[:,c].-Ua[:,base+c].+error)
    #    .-cdf.(Normal.(0,σ[σdic[c]]),Ua[:,c].-Ua[:,base+c].-error))
    ULL.=(ULL./sum(ULL,dims=1)).*ULL  ## weighting by likelohood of that state 
    #ULL+=prob*sum(pdf.(Noraml(0,σ[σdic[c]]),Ua[base2+c]))

    ##########################      CERTAINTY CASE
    Ca=a[a[:,17].==0,:]   ## ALIE RN YOU ARE NOT IMPOSING A DIFFERENT  σ FOR THE CERTAIN CASE
    for c in 1:CVcertain
        CLL= CLL.*sum(pdf.(Normal.(0,σ[σdic[c]]),Ca[:,base2+c]))  ## hcs1 is not touched heere
    end 
    #################################################################################
    ##########################      WRITES LAST a* TO FILE 
    #Ures,Cres=(data=Ures,),(data=Cres,)
    CSV.write("Uastar.csv",DataFrame(x=Ures)),CSV.write("Castar.csv",DataFrame(x=Cres))
    @show "saved to VSC"

    return -log(sum(ULL.+sum(CLL,dims=2)))
    #astar=Dict([key=>subs(value,estdic) for (key,value) in dU])
    ###########################################    

end
###########################################################

###########################################################   numpa
#######################################      MAXIMIZATION STEP 
###########################################################
#cat(β,θ,σ,ν,tB,κ,η,δ,dims=1)

x0=[.5,.7,.9,.9  ##β  (c,ch,hc,hu)
    ,.5,.5,.9,.9   ##θ
    ,.1,.1,.1,.1   ## σ s1 
    ,.05,.05,.05,.05  ## σ s2
    ,5.  #### (tB),κ
    ,2.,.5]   ##,η,δ,(ν)
lower=fill(.01,length(x0))  #  tB,κ,η,δ,ν
upper=[.999,.999,.999,.999  ,.999,.999,.999,.999  ,.999,.999,.999,.999, .999,.999,.999,.999
     ,50.,10.,.99]
#[a[a[:,12].==x,:] for x in unique(a[:,12])] 
#v=[x->loglik(γ,a[a[:,12].==x,:]) for x in unique(a[:,12])]  ## broadcasting over group, one day..
 
res=optimize(γ->loglik(γ,a,ν,tB),lower,upper,x0,Fminbox(NelderMead())
        ,Optim.Options(show_trace=true,show_every=50,iterations=10)) #f_tol=1e-5,x_tol=1e-5,iterations=200))  # , iterations=999999,outer_iterations=99999))  #NelderMead(maxiter=1),change tolerance
#####  get fit of ests 
estfit(res)








res=Optim.minimizer(res)
@show "coeffs",res
#     β,θ,σ,tB,κ,η,δ,ν=γ[1:4],γ[5:8],γ[9:12], γ[13],γ[14],γ[15],γ[16],γ[17]
@show "beta", res[1:4]
@show "theta",res[5:8]
@show "sigma",res[9:16]

@show "kappa",res[17]
@show "eta",res[18]
@show "delta" ,res[19]

###########################################################
#########################################      EM ITERATIONS 
###########################################################
#for n in 1:2   ## why? already max right??
#    @show n ,"--------------------------------"
#γ=maximization(a,group,γ).minimizer
#end

############################################################
##########################################     RUNS THE PROGRAM 
############################################################

