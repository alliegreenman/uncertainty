#Eu needds to be first right? 

###########################################################
######################################  DEFINING UTILITY 
###########################################################
function certainU(cvars,γ,state)  ## all variables are globals 
    ###  mom is 1,3 (for hc )
    ###################################
    ## initiate variables
    Nw,Nh,hc,w=zeros(2),zeros(2),zeros(2),zeros(2)
    β,θ,σ=zeros(6),zeros(6),zeros(2)
    ###################################
    ##  unpacking  (generalize this with no magic numbers)
    ###   take group state vars to solve utility 
    w[1],w[2],y=state[1:3]   ## 'group','gws0','gws1','gy',

    Nw[1],Nw[2],Nh[1],Nh[2],hc[1],hc[2]=cvars  ## unpacking guesses 
    β,θ,σ,tB,κ,η,δ,ν=γ[1:4],γ[5:8],γ[9:12],γ[13],γ[14],γ[15],γ[16],γ[17]
    U=zeros(1)
    ####################################
    ###########################    SUBSTITUTED CHOICE VARS
    ####   sub in c, hu
    subvars=[(y./365 .+w[1].*Nw[1].+w[2].*Nw[2],η.*(Nh[1].+Nh[2])),hc,
        vcat(24 .-(Nw[1].+Nh[1].+hc[1]),  ### time (sub ut hu)
        24 .-(Nw[2].+Nh[2].+hc[2]))]  ## hu mom,dad s==1 || hu mom,dad s==2
    ####################################    BODY OF UTILITY 
    for (i,x) in enumerate(subvars)  ## separate from stage 1 due to consump diff 
        for (n,x2) in enumerate(x)
            if x2<0 
                value=0.0001
            else 
                value=β[i].*x2.^(θ[i])/θ[i]
            end
            U[1]+=value
        end 
    end 
    ####################################    RETURN UTILITY 
    if Nw[1].+Nh[1].+hc[1]>24 || Nw[2].+Nh[2].+hc[2]>24             
        return (24-Nw[1]-hc[1]-Nh[1])^100+(24-Nw[2]-hc[2]-Nh[2])^100
    else
        return -log(U[1]) 
    end 
end 
###########################################################
 