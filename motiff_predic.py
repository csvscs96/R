import Bio
from Bio import SeqIO
from Bio import pairwise2
from Bio import Seq
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.pairwise2 import format_alignment
from Bio import Align
import numpy as np

def loadseq(input, qscore = 0, filetype = "fastq"): #load the sequence file into a readable format, 0 and else input to determine the need to load qscore instead of the sequence
	seqlist=[] 
	with open(input,"rU") as fp:
		for record in SeqIO.parse(fp, filetype): #append sequences in a loop to a list
			sequences = record
			if qscore == 0: # if = 0 load sequences
				seqlist.append(str(sequences.seq))
			else: #load quality score
				seqlist.append(sequences.letter_annotations["phred_quality"])
	fp.close()
	return seqlist #return a list of sequence

def setupAligner(match, mismatch,open,extend): #create an aligner to attempt to simulate a semi-global aligment, as it is some what more accurate than pairwise2.globalms
	a = Align.PairwiseAligner() #the aligner  itself
	a.match_score = match #set the aligner score based on the given condition 
	a.mismatch_score = mismatch
	a.internal_open_gap_score = open #internal gap open
	a.internal_extend_gap_score = extend #internal extending gap 
	a.target_left_open_gap_score = open #left gap open
	a.target_left_extend_gap_score = extend #left extend 
	return a
	
def splitseq(seq, strand): #strand 0,1,or 2, split the aligned read to something that can be processed 
	sequence = str(seq)
	splitted = sequence.split('\n')
	return splitted[strand]
	
def findIDX(seq):
	sequence = seq
	idx = 0
	for i in range(len(sequence)):
		if sequence[i] != "-":
			idx = i
			break
	return idx
	
def mle(seqA,seqB,pA,pB,pC): #calculate the mle, give pA,pB,pC, as the probablity of error for match, mismatch, and gap
	sequenceA = seqA
	sequenceB = seqB
	p_num = [1-pA* np.power(10,-.05),pB* np.power(10,-.05)] #the inside of the product formula
	q_score = []
	for i in range(len(seqA)): #calculate for all nucleotide in the sequnce
		if sequenceB[i] == '-': #making sure when merging, the nucleotide will be choosen over -
			q_score.append([0,38])
		elif sequenceA[i] =='-':
			q_score.append([38,0])
		else:
			q_score.append([cal_mle(sequenceA[i],sequenceB[i],sequenceA[i],p_num),cal_mle(sequenceA[i],sequenceB[i],sequenceB[i],p_num)])
	return q_score

def cal_mle(nucA,nucB,nucZ,pnum): #calculate true N
	nucList = [nucA,nucB]
	ArgR = 1
	for i in nucList:
		if i == nucZ:
			ArgR *= pnum[0]
		else:
			ArgR *= pnum[1]
	return int(round(np.log10(ArgR)*-10+.5))
	
def merge(seqA,seqB,q_score): #merge read based on q_score
	sequenceA = seqA
	sequenceB = seqB
	qScore = q_score
	sequenceMerged = ""
	for i in range(len(qScore)):
		if i < 318:
			if qScore[i][0] < qScore[i][1]: #the smaller the quality score the better the data, use the nucleotide with lowest q_score
				sequenceMerged += sequenceA[i]
			else:
				sequenceMerged += sequenceB[i]
	return sequenceMerged

def scoreC(seq, num): #statment to check if is qualif as an good align
	symbals = 0
	for i in seq:
		if i == '|':
			symbals+=1
	if symbals > num:
		return True
	return False
	
def seqMerge(file): #merging all sequences
	unused_seq = []
	seqM = file[0]
	for i in range(1,6): #len(file)
		a=aligner.align(seqM,file[i])
		if scoreC(splitseq(a[0],1),3): #more than 3 nucleotide aligned count as a good align, due to i have seen where it so happens to only 1,2 bp being aligned and it was consider good
			seqA = splitseq(a[0],0)
			seqB = splitseq(a[0],2)
			seqN = mle(seqA,seqB,.63,.38,.00016)
			seqM = merge(seqA,seqB,seqN)
		else:
			unused_seq.append(file[i])
	
	if len(seqN) < 318:
		rangeQ = len(seqN)
	else:
		rangeQ = 318
		
		qscore=[0]*rangeQ
		
	for i in range(rangeQ):
		if seqN[i][0] < seqN[i][1]:
			qscore[i]= seqN[i][0]
		else:
			qscore[i]= seqN[i][1]
	
	return seqM,unused_seq,qscore #return merged sequence and unsued sequence
	
def exportFile(file,seqA,qscore,id_r):
	output_name = file + ".fastq"
	record = SeqRecord(Seq(seqA),id=id_r,description="merged read")
	record.letter_annotations["phred_quality"]=qscore
	SeqIO.write(record,output_name,"fastq")
	
def exportUnused(file,seqA,id_r):
	output_name = file + ".fastq"
	if len(seqA) > 0:
		with open(output_name,"a") as output_handle:
			for i in seqA:
				record = SeqRecord(Seq(i),id=id_r,description="merged read")
				record.letter_annotations["phred_quality"]=[0]*len(seqA)
				SeqIO.write(record,output_handle,"fastq")
	
def startHW(fileA,fileB,fileC):	
	f_file = fileA #forward read
	r_file = fileB #reverse read
	output_name = fileC #outputname
	f_seq = loadseq(f_file) #forward sequence
	r_seq = loadseq(r_file) #reverse sequence
	aligner = setupAligner(1,-.5,-8,-8) #the high negative score on the gap is due to the sequencing matching is unlikely to produce a gap 
	merge_f,unused_f,qS_f = seqMerge(f_seq)
	merge_r,unused_r,qS_r = seqMerge(r_seq)
	seqM = mle(merge_f,merge_r,.63,.38,.00016)
	global seqF
	seqF = merge(merge_f,merge_r,seqM )
	
	if len(seqM) < 318:
		rangeQ = len(seqM)
	else:
		rangeQ = 318
		
	qscore=[0]*rangeQ
	for i in range(rangeQ):
		if seqM[i][0] < seqM[i][1]:
			qscore[i]= seqM[i][0]
		else:
			qscore[i]= seqM[i][1]
	
	exportFile(output_name+"_merged",seqF,qscore,'forward')
	exportUnused(output_name+"_unmerged_1",unused_f,'forward')
	exportUnused(output_name+"_unmerged_2",unused_r,'reverse')
	
def alignKnown(fileA,Output): 
	global seqF
	mergedSeq = seqF
	knownSeq= loadseq(fileA,filetype = "fasta") # amplicon2.fsa
	outputfile = Output+".txt" # output
	aligner = setupAligner(1,-.5,-8,-8)
	alig1 =aligner.align(knownSeq,mergedSeq)
	with open(outputfile, "a") as f:
		f.write("Merged forward and Reverse Read" + "	")
		print(alig1[0],file=f)
	
#-----------Sample Code-----------------
#startHW("SRR3561198_1.fastq","SRR3561198_2.fastq","output1")
#alignKnown("amplicon2.fsa","output2")

	


