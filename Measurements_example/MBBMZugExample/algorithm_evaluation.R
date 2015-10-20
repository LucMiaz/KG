library('jsonlite')
library('ggplot2')
#
json_file<-'C:/LucMiaz/KG_dev_branch/KG/Measurements_example/MBBMZugExample/results/test_ZischenDetetkt2_2.0s_3000Hz_0dB_19-10-2015_22-13-01.json'
dataraw<-fromJSON(json_file)
for (author in names(dataraw$compare)){
for (i in 1:length(dataraw$compare$author$test)){#take all the true/false values and add them to truths/falses
  falses<-c(falses, dataraw$compare$author$test[[i]][dataraw$compare$author$disc[[i]]==0 & ! is.nan(dataraw$compare$author$test[[i]])])
  truths<-c(truths, dataraw$compare$author$test[[i]][dataraw$compare$author$disc[[i]]==1 & ! is.nan(dataraw$compare$author$test[[i]])])
}}
tf<-list('True'=truths,'False'=falses)#make one variable with both truths and falses
bartrue<-hist(tf$True, density=200, breaks=50, prob=TRUE, 
      ylim=c(0, 10), col='#a6dba0')
mtrue<-mean(tf$True)
stdtrue<-sqrt(var(tf$True))
curvetrue<-curve(dnorm(x, mean=mtrue, sd=stdtrue), 
                 col="#008837", lwd=1, add=TRUE, yaxt="n")

bartrue<-hist(tf$False, density=200, breaks=50, prob=TRUE, 
              ylim=c(0, 4), col='#c2a5cf', xlim=c(-2,4))
#barfalse<-ggplot() + aes(tf$False)+ geom_histogram(binwidth=0.05, fill="#c2a5cf", add=TRUE)
mfalse<-mean(tf$False)
stdfalse<-sqrt(var(tf$False))
curvefalse<-curve(dnorm(x, mean=mfalse, sd=stdfalse), 
      col="#7b3294", lwd=1, add=TRUE, yaxt="n")

curvefalse<-curve(dnorm(x, mean=mfalse, sd=stdfalse), 
                  col="#7b3294", lwd=1, yaxt="n", xlim=c(-2,4))
curvetrue<-curve(dnorm(x, mean=mtrue, sd=stdtrue), 
                 col="#008837", lwd=1, add=TRUE, yaxt="n")
#hist(tf$True, density=20, breaks=20, prob=TRUE, 
#      ylim=c(0, 10), add=TRUE, col='#c2a5cf')
#curve(dnorm(x, mean=m, sd=std), 
#      col="#7b3294", lwd=2, add=TRUE, yaxt="n")
threshold<-seq(0,4,0.01)
x<-sum(tf$false>threshold)
