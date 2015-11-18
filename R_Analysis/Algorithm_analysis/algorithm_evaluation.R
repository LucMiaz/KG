library('jsonlite')
library('ggplot2')
#
json_file<-'C:/LucMiaz/KG_dev_branch/KG/Measurements_example/MBBMZugExample/results/test_ZischenDetetkt2_2.0s_3000Hz_0dB_20-10-2015_14-59-39.json'
dataraw<-fromJSON(json_file)
tf<-dataraw$R
authors=paste(unique(tf$author), sep=", ")
bartrue<-hist(subset(tf,tf$disc==1)$BPR, density=200, breaks=50, prob=TRUE, col='#a6dba0', main=unique(tf$author), xlab='BPR')
mtrue<-mean(subset(tf,tf$disc==1&!is.nan(tf$BPR))$BPR)
stdtrue<-sqrt(var(subset(tf,tf$disc==1&!is.nan(tf$BPR))$BPR))
curvetrue<-curve(dnorm(x, mean=mtrue, sd=stdtrue), 
                 col="#008837", lwd=2, add=TRUE, yaxt="n")

barfalse<-hist(subset(tf,tf$disc==0)$BPR, density=200, breaks=50, prob=TRUE, col='#c2a5cf', xlim=c(-2,4),main=unique(tf$author), xlab='BPR')
#barfalse<-ggplot() + aes(tf$False)+ geom_histogram(binwidth=0.05, fill="#c2a5cf", add=TRUE)
mfalse<-mean(subset(tf,tf$disc==0 & !is.nan(tf$BPR))$BPR)
stdfalse<-sqrt(var(subset(tf,tf$disc==0 & !is.nan(tf$BPR))$BPR))
curvefalse<-curve(dnorm(x, mean=mfalse, sd=stdfalse), 
      col="#7b3294", lwd=2, add=TRUE, yaxt="n")

curvefalse<-curve(dnorm(x, mean=mfalse, sd=stdfalse), 
                  col="#7b3294", xlim=c(-6,16),lwd=2, main=authors, xlab="BPR", ylab="Normalized number of items")
curvetrue<-curve(dnorm(x, mean=mtrue, sd=stdtrue), 
                 col="#008837", lwd=2, add=TRUE, yaxt="n")
legend(0.01,0.03, # places a legend at the appropriate place 
       c('False','True'), # puts text in the legend
       
       lty=c(1,1), # gives the legend appropriate symbols (lines)
       
       lwd=c(1,1),col=c('#7b3294','#008837')) # gives the legend lines the correct color and width
#hist(tf$True, density=20, breaks=20, prob=TRUE, 
#      ylim=c(0, 10), add=TRUE, col='#c2a5cf')
#curve(dnorm(x, mean=m, sd=std), 
#      col="#7b3294", lwd=2, add=TRUE, yaxt="n")
#select a range of threshold that will be tested
threshold<-seq(0,4,0.01)
#create a table with x\threshold and corresponding boolean for x>threshold
a <- tf$BPR
nf<- length(tf$BPR[tf$disc==0])
np<- length(tf$BPR[tf$disc==1])
xf<-vector(NA,length=length(threshold))
xf <- vector(t(xf),length=nf)
for(i in length(threshold)){
  xf[[i]]<- tf$BPR[tf$disc==0]<threshold[[i]]
}
tf<-mutate(tf, leqBPR=BPR<i)
len<-length(tf$i[!is.na(tf$leqBPR)])
row<-c(sum(tf$leqBPR[tf$disc==1 & !is.na(tf$leqBPR)])/len, sum(tf$leqBPR[tf$disc==0 &!is.na(tf$leqBPR)])/len, i)
tf <- rbind(tprfpr,row)



date<-"21-10-2015"
thres<-"2"
datamaous<-data.frame(time=double(),mID=character(),NoiseT=character(),author=character(), mic=integer(),location=character(),BPR=double(),quality=character(),disc=integer())
for (dt in c("0.01","0.02","0.1")){
  for (fc in c("3000","2000","1000")){
    json_file<-paste('C:/LucMiaz/KG_dev_branch/KG/Measurements_example/MBBMZugExample/results/test_ZischenDetetkt2_',dt,"s_",fc,"Hz_",thres,"dB_",date,"_14.json", sep="")
    dataraw<-fromJSON(json_file)
    tf<-dataraw$R
    datamaous<-rbind(datamaous,tf)
  }
}
remove(fc)
remove(dt)
remove(thres)
remove(date)
remove(json_file)
remove(dataraw)
tf<-datamaous
tf <- filter(tf, !is.nan(BPR))
tprfpr <- data.frame(TPR=double(), FPR=double(),threshold=double())
authors=paste(unique(tf$author), sep=", ")
algorithms=unique(tf$Alg)
len<-nrow(tf)
for(i in seq(0.1,1,0.1)){
  result<- tf$BPR>i
  tf<-tf %>% mutate_(leqBPR=paste(as.numeric(result)))
  tprfpr <- rbind(tprfpr,data.frame(TPR=sum(tf$leqBPR[tf$disc==1])/len, FPR=sum(tf$leqBPR[tf$disc==0])/len, threshold=i))
  print(i)
}
tf$leqBPR<- NULL
