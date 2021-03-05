################################################################################################################
## PROGRAMMER   Han-Tian Guo															                                                  
## STUDY        NHLBI Twin Study 													
## PURPOSE      Twin study data 450K PCA			  
## DATE         Feburary 10th, 2020	
## Email        hantianguo94@gmail.com													                                               
################################################################################################################

library(tidyverse)
library(ggbiplot)
library(stringr)
library(data.table)


#read file
victr_450 <- read.table("~/R/450K_Vandy_VICTR_sample/3088-JD_norm_data_autosomes - Copy.txt", header = FALSE, sep = "", dec = ".")
twinDataEx1 <- read.csv("~/R/450K_Vandy_VICTR_sample/Copy of 3088-JD_CHDCVDOutcome_06212017_jd.csv", header=T, sep=",", quote="\"") 
#select column used
twinDataEx1.highlight<-twinDataEx1[,c(2,9,15)]
#transform ID format to match the ID format in the txt file
twinDataEx1.highlight[,1]<-str_replace_all(twinDataEx1.highlight[,1],"-",".")
twinDataEx1.highlight[,1]<-paste0("X",twinDataEx1.highlight[,1])
#find column that would be removed
victr_450.colNum<-list()
n<-1

for(i in 1:nrow(twinDataEx1.highlight)){
  for(j in 1:ncol(victr_450)){
    if(twinDataEx1.highlight[i,1]==victr_450[1,j]){
      if(twinDataEx1.highlight[i,3]==0){
        victr_450.colNum[n]<-j
        n<-n+1
      }
    }
  }
}

#select Data that matches criteria
victr_450.colDf <- data.frame(matrix(unlist(victr_450.colNum), nrow=length(victr_450.colNum), byrow=TRUE))
victr_450.selected<-victr_450[,c(1:17,19:22,25:28,30:43)]

twinDataEx1.selected<-twinDataEx1.highlight

for(i in nrow(twinDataEx1.highlight):1){
  if(twinDataEx1.highlight[i,3]==0){
    twinDataEx1.selected <- twinDataEx1.selected[-c(i),]
  }
}

v_row <- nrow(victr_450.selected)
v_col <- ncol(victr_450.selected)
victr_450.DNE<-list()
n<-1

#replace NA values with its twins value or the average value if both twin have NA value
for(i in 2:v_col){
  colID <- victr_450.selected[1,i]
  rowNum <- which(grepl(colID, twinDataEx1.selected$Sample_ID))
  if(is_empty(rowNum)){
    victr_450.DNE[n]<-colID
    n<-n+1
  }else{
    if((as.integer(rowNum) %% 2)==0){
      pairID <-twinDataEx1.selected[rowNum-1,1]
    }else{
      pairID <-twinDataEx1.selected[rowNum+1,1]
    }
    pairLocation<-which(grepl(pairID,  victr_450.selected[1,]))
    for(j in 1:v_row){
      if(is.na(victr_450.selected[j,i])){
        if(is.na(victr_450.selected[j,pairLocation])){
          victr_450.selected[j,i]<- mean(as.numeric(victr_450.selected[j,c(2:v_col)]),na.rm = TRUE)
          victr_450.selected[j,c(2:v_col)] <-victr_450.selected[j,i]
        }else{
          victr_450.selected[j,i]<-victr_450.selected[j,pairLocation]
        }
      }
    }
  }
}

#save the selected data to csv file in case it need further usage
pathname <- "~/R/450K_Vandy_VICTR_sample/"
filename <- "victr_450_selected"
filepath=file.path(pathname,paste(filename,".csv",sep=""))
write_csv(victr_450, filepath)

#load the saved selected data if need
victr_450.selected <- read.csv("~/R/450K_Vandy_VICTR_sample/victr_450_selected.csv", header=T, sep=",", quote="\"") 
#transpose the data so it is in the right format for pca
victr_450.transposed <-transpose(victr_450.selected)
victr_450 <- victr_450.transposed[c(2:39),]

#set row name and colnames for the transposed data
victr_450_name <- colnames(victr_450.selected[,c(2:39)])
row.names(victr_450)<-victr_450_name
victr_450_name <- victr_450.selected[,1]
colnames(victr_450)<-victr_450_name

victr_450.numeric = as.data.frame(sapply(victr_450,as.numeric))

#pca
victr_450.pca <- prcomp(victr_450.numeric)
victr_450_name <- rownames(victr_450)

#covariance and eigen value
victr_450.S<-cov(victr_450.numeric)
victr_450.S_eigen <- eigen(victr_450.S)

#plot(victr_450.S_eigen$values, xlab = 'Eigenvalue Number', ylab = 'Eigenvalue Size', main = 'Scree Graph')
#lines(victr_450.S_eigen$values)

summary(victr_450.pca)

screeplot(victr_450.pca, main="Scree Plot", xlab="Components")
screeplot(victr_450.pca,type="line",main="Scree Plot")

biplot(victr_450.pca)
biplot(victr_450.pca,choices=c(1,2),labels=victr_450_name)

#varimax, selecting first 12 components
loading <- victr_450.pca$rotation
varimax.pca <- varimax(loading[,c(1:12)])

victr_450.rotated <- scale(victr_450.transposed) %*% varimax.pca$loadings