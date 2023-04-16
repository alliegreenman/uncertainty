#Eu needds to be first right? 

###########################################################
######################################  DEFINING UTILITY 
###########################################################
function uncertainU(cvars,γ,state)  ## all variables are globals 
    ###  mom is 1,3 (for hc )
    ###################################
    ## initiate variables
    Nw,Nh,hc,hct,hu,w=zeros(2),zeros(2),zeros(4),zeros(2),zeros(2),zeros(2)
    hcn=zeros(4)  ##hc with no UNCERTAINTY
    β,θ,σ=zeros(6),zeros(6),zeros(2)
    ###################################
    ##  unpacking  (generalize this with no magic numbers)
    ###   take group state vars to solve utility 
    w[1],w[2],y=state[1:3]   ## 'group','gws0','gws1','gy',

    Nw[1],Nw[2],Nh[1],Nh[2],hc[1],hc[2],hc[3],hc[4],hct[1],hct[2]=cvars  ## unpacking guesses 
    β,θ,σ,κ,η,δ=γ[1:4],γ[5:8],γ[9:12],γ[13],γ[14],γ[15]
    U=zeros(3)
    ####################################
    ###########################    UNCERTAINTY
    ####   sub in c, hu
    subvars=[(y./365 .+w[1].*Nw[1].+w[2].*Nw[2].-κ.*((hc[[1,2]].-hct[1]).^2  ## consum across states
       .+(hc[[3,4]].-hct[2]).^2)),η.*(Nh[1].+Nh[2]),hc,
        vcat(24 .-(tB.*[1,0].*δ.+Nw[1].+Nh[1].+hc[[1,3]]),  ### time (sub ut hu)
        24 .-(tB.*[1,0].*(1 .-δ).+Nw[2].+Nh[2].+hc[[2,4]]))]  ## hu mom,dad s==1 || hu mom,dad s==2
    ####################################    BODY OF UTILITY W UNCERTAINTY (stage 2)
    for (i,x) in enumerate(subvars)  ## separate from stage 1 due to consump diff 
        n2=2
        for (n,x2) in enumerate(x)
            if n==1||n==3
                n2=1
            else 
                n2=2
            end 
            if x2<0 
                value=0.0001
            else 
                value=β[i].*x2.^(θ[i])/θ[i]
            end
            U[n2]+=value
        end 

    end 
    ######################################    DEFININING EU
    for s in 1:2 
        cbind=y+w[1]*Nw[1]+w[2]*Nw[2]-κ*((hc[(s-1)+1]-hct[1])^2+
            (hc[(s-1)+1+2]-hct[2])^2)
        chbind=η*(Nh[1]+Nh[2])
        tbind=Vector{Sym}(undef,2)
        for i in [(1,cbind),(2,chbind),(3,subvars[3][(s-1)+1]),(3,subvars[3][(s-1)+3]),(4,subvars[4][(s-1)+1]),(4,subvars[4][(s-1)+3])]
            if i[2]<0
                value=.00001
            else 
                value=i[2]^(θ[i[1]])
            end 
            U[3]+=ν^(2-s)*(1-ν)^(s-1)*(β[i[1]]*value)/θ[i[1]]
        end 
    end
    ##  weights penatly the same
    penalty=0
    for i in subvars[4]
        for j in i 
            if j<0 
                penalty+=sum(24 .-(tB.*(1 .-δ).+Nw[2].+Nh[2].+hc[[2,4]]))^100000
            end
        end
    end
    #penalty=((Nw[1]+Nh[1]+hc[1]+tB*δ)-)^2 ##  shock mom  (clean up ), but still no hu!!
    #         +((Nw[1]+Nh[1]+hc[3])-24)^2   ##no shock mom
    #         +((Nw[2]+Nh[2]+hc[2]+tB*(1-δ))-24)^2 ##  shock dad
    #         +((Nw[2]+Nh@[2]+hc[4])-24)^2   ##no shock dad
 
    if tB*δ+Nw[1].+Nh[1].+hc[1]>24 || tB*(1-δ)* Nw[2].+Nh[2].+hc[2]>24             
        return (24-tB*δ-Nw[1]-hc[1]-Nh[1])^100+(24-tB*(1-δ)-Nw[2]-hc[2]-Nh[2])^100
    else
        return -log(U[1]+U[2]) 
    end 
    
end 
###########################################################
 