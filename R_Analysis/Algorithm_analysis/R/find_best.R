TPFP_func<-function(df, threshold){
  
  TP<-tally(filter(df, spec>threshold & disc==1))
  FP<-tally(filter(df, spec>threshold & disc==0))
  totP<-tally(filter(df,disc==1))
  totF<-tally(filter(df,disc==0))
  if (totP>0 & totF>0){
    FPR<-FP/totF
    TPR=TP/totP
    d_ax<-(TPR+FPR)/2
    dist_ax<-sqrt( (d_ax-FPR)**2 + (d_ax-TPR)**2 )
    return(data.frame('TPR'=TPR,'FPR'=FPR,'thd'=threshold,'totP'=totP, 'totF'=totF,'dist_ax'=dist_ax,'d_ax'=d_ax))
  }else{
    return(data.frame('TPR'=double(),'FPR'=double(),'thd'=double(),'totP'=double(), 'totF'=double(),'dist_ax'=double(),'d_ax'=double()))
  }
}

find_best<-function(tff, authors=list(), qualities=list(),fixedthreshold=FALSE, bw=200){
  if (length(qualities)==0){
    qualities<-unique(tf$quality)
  }
  if(length(authors)==0){
    authors<-levels(unique(tf$author))
  }
  print(authors)
  print(qualities)
  bestones<-data.frame('TPR'=double(),'FPR'=double(),'thd'=double(),'totP'=double(), 'totF'=double(),'dist_ax'=double(),'d_ax'=double(),'alg'=character(),'algprop'=character(), 'delta'=double())
  #iterate on algorithms
  for (al in unique(tff$alg)){
  #iterate on parameters
    for (alp in unique(tff$algprop)){
      sums<-data.frame('TPR'=double(),'FPR'=double(),'thd'=double(),'totP'=double(), 'totF'=double(),'dist_ax'=double(),'d_ax'=double())
      algtf<-filter(tff, algprop==alp & alg==al & author %in% authors & quality %in% qualities)
      #iterate on thresholds
      if (fixedthreshold){
        thresholds<-seq(-1,25,1/bw)}
      else{
        thresholds<-seq(min(algtf$spec),max(algtf$spec),(max(algtf$spec)-min(algtf$spec))/bw)
      }
      delta<-thresholds[[2]]-thresholds[[1]]
      for (i in thresholds){
          tpfp=TPFP_func(algtf, i)
          sums[nrow(sums)+1,]<-tpfp
          
      }
      thresmax<-which.max(sums$dist_ax)
#       filtre<-filter(sums, thd!=sums$thd[thresmax])
#       thressec<-which.min(abs(filtre$TPR/filtre$TPR))
#       filtre<-filter(filtre, thd!=filtre$thd[thressec])
#       thresthree<- which.min(abs(filtre$TPR/filtre$FPR))
#       thresmin<-which.min(abs(sums$TPR/sums$FPR))
      bestones <-rbind(bestones,data.frame('TPR'=sums$TPR[thresmax],'FPR'=sums$FPR[thresmax],'thd'=sums$thd[thresmax],'totP'=sums$totP[thresmax],'totF'=sums$totF[thresmax],'dist_ax'=sums$dist_ax[thresmax],'d_ax'=sums$d_ax[thresmax], 'alg'=al[[1]],'algprop'=as.character(alp[1]),'delta'=delta))
#       bestones <-rbind(bestones,data.frame('TPR'=sums$TPR[thressec],'FPR'=sums$FPR[thressec],'thd'=sums$thd[thressec],'totP'=sums$totP[thressec],'totF'=sums$totF[thressec], 'alg'=al[[1]],'algprop'=as.character(alp[1]),'delta'=delta))
#       bestones <-rbind(bestones,data.frame('TPR'=sums$TPR[thresthree],'FPR'=sums$FPR[thresthree],'thd'=sums$thd[thresthree],'totP'=sums$totP[thresthree],'totF'=sums$totF[thresthree], 'alg'=al[[1]],'algprop'=as.character(alp[1]),'delta'=delta))
      remove(sums,thresmax)
    }
  }
  bestones<-cbind(bestones, data.frame('col'=as.integer(bestones$algprop)))
  
  bestones<-cbind(bestones, data.frame('dif'=bestones$TPR-bestones$FPR))
  #geom_point(aes(sums$n[thd==thres],sums$n.1[thd==thres]), colour="#7b3294", size=3, label=thres)
  #geom_text(data=filter(sums,thd==thres),aes(label=thd))
  remove(authors, qualities, delta, fixedthreshold)
  return(bestones)
}