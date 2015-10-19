library('jsonlite')
library('ggplot2')
#
json_file<-'C:/LucMiaz/KG_dev_branch/KG/Measurements_example/MBBMZugExample/results/test_ZischenDetetkt2_2.0s_3000Hz_0dB_19-10-2015_16-55-37.json'
dataraw<-fromJSON(json_file)
falses <-  dataraw$compare$test[[1]][dataraw$compare$disc[[1]]==0 & ! is.nan(dataraw$compare$test[[1]])]#initializes false set
truths<-dataraw$compare$test[[1]][dataraw$compare$disc[[1]]==1& ! is.nan(dataraw$compare$test[[1]])]#initializes True set
for (i in 2:length(dataraw$compare$test)){#take all the true/false values and add them to truths/falses
  falses<-c(falses, dataraw$compare$test[[i]][dataraw$compare$disc[[i]]==0 & ! is.nan(dataraw$compare$test[[i]])])
  truths<-c(truths, dataraw$compare$test[[i]][dataraw$compare$disc[[i]]==1 & ! is.nan(dataraw$compare$test[[i]])])
}
tf<-list('True'=truths,'False'=falses)#make one variable with both truths and falses
bartrue<-ggplot() + aes(tf$True)+ geom_histogram(binwidth=0.01, fill="#a6dba0")
barfalse<-ggplot() + aes(tf$False)+ geom_histogram(binwidth=0.01, fill="#c2a5cf", add=TRUE)
mfalse<-mean(tf$False)
stdfalse<-sqrt(var(tf$False))
curvefalse<-curve(dnorm(x, mean=mfalse, sd=stdfalse), 
      col="#7b3294", lwd=2, add=TRUE, yaxt="n")
mtrue<-mean(tf$True)
stdtrue<-sqrt(var(tf$True))
curvetrue<-curve(dnorm(x, mean=mtrue, sd=stdtrue), 
                  col="#008837", lwd=2, add=TRUE, yaxt="n")

#hist(tf$True, density=20, breaks=20, prob=TRUE, 
#      ylim=c(0, 10), add=TRUE, col='#c2a5cf')
#curve(dnorm(x, mean=m, sd=std), 
#      col="#7b3294", lwd=2, add=TRUE, yaxt="n")
