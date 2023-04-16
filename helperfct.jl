################################################### 
################                        JULIA HELPER FUNCTIONS : UTILITY 
################################################### 

using Optim, NLSolversBase, Random,Symbolics,CSV,DataFrames,Distributions, IterTools 
using LinearAlgebra: diag
using Symbolics: Sym
###################################################
########################         IMPORT DATA 
###################################################
function dfobs()
    df=CSV.read("a.csv",DataFrame)  ##  hh level 
    df=coalesce.(df,0)
    #df=df[shuffle(1:end)[1:2],:]

    #obs=Dict([(x,df[:,x]) for x in obsparams])
    #########   redefine obs to a (assuming relation of model -- c, ch)
    #obs=Dict{Any,Any}(obs)
    #df[!,:"ch"]=Any[]
    #obs["ch"]=η.*(obs["Nhs0"]+obs["Nhs1"])
    N=length(df[:,"Nws0"])
    #df=select(df,[:"hus0",:"hus1",:"hcs0",:"hcs1",
    #    :"Nhs0",:"Nhs1",:"Nws0",:"Nws1",:"ws0",:"ws1",:"y"])
    df=select(df,[:"Nws0",:"Nws1",:"Nhs0",:"Nhs1",:"hcs0",:"hcs1",:"hus0",:"hus1",
        :"ws0",:"ws1",:"y",:"group",:"gws0",:"gws1",:"gy",:"totalive",:"D"])
    group=CSV.read("group.csv",DataFrame)
    group=select(group,[:"group",:"gws0",:"gws1","gy"])
    #a=  collect(df.hus0),collect(df.hus1),
    #    collect(df.hcs0),collect(df.hcs1),
    #    collect(df.Nws0),collect(df.Nws1),
    #    collect(df.Nhs0),collect(df.Nhs1),
    #    #collect(df[:,"ch"]),
    #    collect(df.ws0),collect(df.ws1),
    #    collect(df[:,"y"])
    ##############   test: making a key \forall hh with ^^ structure 
    #adic=Dict()
    #[push!(adic,i=>values(x)) for (i,x) in enumerate(eachrow(df))]
    df=Matrix(df[:,names(df)])
    group=Matrix(group)
    return N,df  ###  return our df observables 
end
####################################################

####################################################
####################################   INIT GUESSES FOR TIME ALLOC 
function initguess(a,nvar)
    #Nw[1],Nw[2],Nh[1],Nh[2],hc[1],hc[2],hc[3],hc[4],hct[1],hct[2]=cvars 
    init=zeros(nvar)  ## hc in states + hct
    for i in 1:nvar
        if i<=6  ##Nw0,Nw1,Nh0,Nh1,hc00,hc01,hc10,hc11,hct0,hct1
            init[i]=mean(a[:,i])
        else 
            init[i]=mean(a[:,6])
        end 
    end 
    return init 
end 
####################################################