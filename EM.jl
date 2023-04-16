####################################################
####################################################
##################################     EM ESTIMATION FOR STATE 
####################################################

###  a[base] ≡ [Nw,Nh,hc,hu,w,y,group,gw,gy,totalive,D] (17), [Nw,Nh,hcs0,hcs1,hct] (10) (27 now)
##  a[base2] :: uncertainty + certainty case ≡ [Nw-Nwstar,Nh-Nhstar,hc-hcs0state,hc-hcs1star]  (18,19),(20,21),(22,23),(<-- 24,25 --> only applicable for uncertainty case)

function EM(ν,σ,a) 
    Ua=a[a[:,17].==1,:]
    N=size(Ua,1)
    ULL=hcat(fill(ν,N),fill(1-ν,N))   ## hh level ll of state 
    for n in 1:10
        CVνdic=Dict(5=>1,6=>1,7=>2,8=>2)
        #####################################     E STEP
        ###  assuming σ the same across mom and dad but different across states
        for c in 1:CVuncertain-2  ## no hct
            if c in keys(CVνdic)   ## grabs hc  (5,6,7,8)
                ULL[:,CVνdic[c]].=ULL[:,CVνdic[c]].*sum(pdf.(Normal(0,σ[3,Int(floor((c-3)/2))]),Ua[:,base2+c]))  ## probs built into ULL mat
            else   ## grabs Nw,Nh (1,2,3,4)
                for s in 1:2 
                    ULL[:,s]=ULL[:,s].*sum(pdf.(Normal(0,σ[Int(floor(c/2))+1,s]),Ua[:,base2+c]))
                end 
            end
        end  
        ####################################       M STEP 
        ULL.=(ULL./sum(ULL,dims=2))
        ν=mean(ULL[1])  ## update ν  

        for (i,y) in enumerate([(1,2),(3,4),(5,6),(7,8)])
            
            if i<3
                for s in 1:2   ## update σ
                    σ[i,s]=sum(sum(ULL[:,s]).*(Ua[:,base2+y[1]]).^2 .*Ua[:,base2+y[2]].^2)./sum(ULL[:,s])
                end 
            else 
                σ[i,Int(i-2)]=sum(ULL[:,Int(i-2)].*(Ua[:,base2+y[1]]).^2 .*(Ua[:,base2+y[2]]).^2)./sum(ULL[:,Int(i-2)])
            end 
        end 

    end   ### end of iterations 
    return ν,σ
end 


