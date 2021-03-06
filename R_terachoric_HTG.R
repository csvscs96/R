################################################################################################################
## PROGRAMMER   Han-Tian Guo															                                                  
## STUDY        NHLBI Twin Study 													
## PURPOSE      Twin study data terachoric correlation 			  
## DATE         July 22nd, 2020	
## Email        hantianguo94@gmail.com													                                               
################################################################################################################

library(psych)
library(tidyverse)

#change the file location here
twinDataEx1 <- read.csv("~/R/twinData_Ex1_dichot_CW.csv", header=T, sep=",", quote="\"") 

#make sure the column name are matching
binData <- data.frame(bbmi1= twinDataEx1[,'BMI2CAT_EX1_1'],
                      bbmi2= twinDataEx1[,'BMI2CAT_EX1_2'],
                      zyg=twinDataEx1[,'zyg'])

#directly using the data to get correlation this way it will output 3 correlation, use the one that is bbmi1 vs bbmi2
mzData <- subset(binData, zyg==1)
dzData <- subset(binData, zyg==2)
result<-tetrachoric(dzData)$rho

#create a 2x2 matrix of counts, this way it will only output 1 correlation rather than 3
ZeroZeroCount<-0
ZeroOneCount<-0
OneZeroCount<-0
OneOneCount<-0
for(i in 1:nrow(mzData[1])){
  if(is.na(mzData[i,1])||is.na(mzData[i,2])){
    next
  }else if(mzData[i,1]==0 && mzData[i,2]==0){
    ZeroZeroCount<-ZeroZeroCount+1
  }else if(mzData[i,1]==0 && mzData[i,2]==1){
    ZeroOneCount<-ZeroOneCount+1
  }else if(mzData[i,1]==1 && mzData[i,2]==0){
    OneZeroCount<-OneZeroCount+1
  }else if(mzData[i,1]==1 && mzData[i,2]==1){
    OneOneCount<-OneOneCount+1
  }
}

dzM<-matrix(c(ZeroZeroCount,ZeroOneCount,OneZeroCount,OneOneCount),ncol=2,byrow=TRUE)
colnames(dzM) <- c("BMI2_0","BMI2_1")
rownames(dzM) <- c("BMI1_0","BMI1_1")
tetrachoric(dzM)$rho