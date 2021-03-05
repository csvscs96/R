



  ################################################################################################################
  ## PROGRAMMER   Han-Tian Guo															                                                  
  ## Affiliation	Iowa State University Bioformatics and Computational Biology Undergraduate Program            
  ## STUDY        NHLBI Twin Study 													
  ## PURPOSE      Twin study data frame/layout conversion from long to wide format   			  
  ## DATE         June 6th, 2020	
  ## Email        hantianguo94@gmail.com													                                               
  ################################################################################################################

  
  #install a new packages "tidyverse"
  
  install.packages("tidyverse")
  require(tidyverse)
  
  
  # load the installed "tidyverse" package
  library(tidyverse)
  
  
  #reads the file, change directory here
  twinFile <- read_csv("~/R/twinData_EX0_long_CW.csv")
  
  
  #gets unqiue pairs
  pairUnique <- unique(twinFile[1])%>% drop_na()
  #get column names
  #use the below colName if you want all column to be outputed
  #colName <- colnames(twinFile)
  #colName <- colName[-1]
  
  #use the below colName if you want selected column to be outputed, input the column label in the format of colName <- c("col_1","col_2",...,"col_x")
  colName <- c("ID","twinid","BMI_0")
  
  #gets unqiue twinIDS
  twinID <- unique(twinFile[3]) %>% drop_na()
  #initialize empty list to store new col names
  colName_vec <- rep(NA, nrow(twinID)*(length(colName)+1))
  
  #create new colnames
  count=1
  for(i in 1:nrow(twinID)){
    for(j in colName){
      colName_vec[count]=paste(j,i,sep="_")
      count=count+1
      if(j=="BMI_EX1"){
        colName_vec[count]=paste("BMI_CAT",i,sep="_")
        count=count+1
      }
    }
  }
  
  #initalize dataframe with lenght = number of colnames, and width=number of unqiue pairs
  newFile <- data.frame(matrix(ncol=length(colName_vec),nrow=nrow(pairUnique)))
  colnames(newFile) <- colName_vec
  newFile <- cbind(pairUnique,newFile)
  
  #copy and paste the values
  for(i in 1:nrow(twinFile[1])){
    #gets the pair ID
    rowIDX <- which(newFile$pair == pull(twinFile[i,1]))
    
    for(j in 1:length(colName)){
      #gets the twinid
      targetCol = paste(colName[j], pull(twinFile[i,3]),sep="_")
      colIDX <- which(colnames(newFile)==targetCol)
      newFile[rowIDX,colIDX]=twinFile[i,which(colnames(twinFile)==colName[j])]
      if(colName[j]=="BMI_EX1"){
        BMIVal=twinFile[i,which(colnames(twinFile)==colName[j])]
        targetCol=paste("BMI_CAT", pull(twinFile[i,3]),sep="_")
        colIDX <- which(colnames(newFile)==targetCol)
        if(is.na(BMIVal[[1]])){
          newFile[rowIDX,colIDX]=BMIVal
        }else if(BMIVal[[1]]<30){
          newFile[rowIDX,colIDX]=0
        }else{
          newFile[rowIDX,colIDX]=1
        }
      }
    }
  }
  
  #view(newFile)
  #view(twinFile)
  
  #export, rewrite the filepath/filename here
  pathname <- "E:/DMU_Backup_03132020/Jdai_R_Online_Drive/Home_Part_Files03132020/Chaseton_2020/"
  filename <- "filename_here"
  filepath=file.path(pathname,paste(filename,".csv",sep=""))
  write_csv(newFile, filepath)
  