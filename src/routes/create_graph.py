def read_files(file1,file2):
	df1=pd.read_csv(file1)
	df2=pd.read_csv(file2)
	result = pd.concat([df1,df2])
	result.drop_duplicates("repository_syllabus",'first',True)
	result = result.reset_index(drop=True)
	return result

def getBoard(s):
	a=s.split(">>")[0]
	return a

def check(s,classes,subject):
	s=s.upper()
	t=list(map(str,s.split(">>")))
	if len(t)>=4 and (t[1] in classes) and (t[2] in subject):
		return True
	else:
		return False

def numcheck(s):
	s=s.upper()
	t=list(map(str,s.split(">>")))
	if len(t)>4:
		return True
	else:
		return False

def add_to_graph(graph,info1,info2):
	meta1=info1[4]
	meta2=info2[4]
	a=Node(info1[0],ID=info1[2],Name=info1[1],Board=info1[3],Metadata=meta1,Class=info1[5])
	a.__primarylabel__=info1[0]
	a.__primarykey__="ID"
	b=Node(info2[0],ID=info2[2],Name=info2[1],Board=info2[3],Metadata=meta2,Class=info2[5])
	b.__primarylabel__=info2[0]
	b.__primarykey__="ID"
	ab=Relationship(a,"HAS",b)
	ab['Weight']=1
	graph.merge(ab)

def input_list(index,topic,board,Class,Subject,last,meta):
	if index==1:
		label="SUBJECT"
		ID=str(topic).upper()
		data=""
	elif index==2:
		label="CLASS"
		ID=str(Subject).upper()+" "+str(topic).upper()
		data=""
	elif index==last:
		label="TOPIC"
		ID=str(Subject).upper()+" "+str(Class).upper()+" "+str(topic).upper()
		data=meta
	else:
		label="INTERMEDIATE"
		ID=str(Subject).upper()+" "+str(Class).upper()+" "+str(topic).upper()
		data=meta
	return [label,topic,ID,board,data,Class]

def generate_graph(graph,subject,classes):
	topics=[]
	board=[]
	metadata=[]
	result=read_files("question_data_chapter.csv","question_data_concept.csv")
	for i in range(len(result['board_syllabus'])):
		if ord(result['board_syllabus'][i][0])<126 and check(result['board_syllabus'][i],classes,subject) and numcheck(result['repository_syllabus'][i]):
			topics.append(result['repository_syllabus'][i].upper())
			board.append(getBoard(result['board_syllabus'][i].upper()))
			metadata.append(str(result['question'][i])+" "+str(result['answer'][i]))
	for i in range(len(topics)):
		topics[i]=re.sub("CLASS ","",topics[i])

	nodes=NodeMatcher(graph)
	for i in range(len(topics)):
		l=topics[i].split(">>")
		tmp=l[1]
		l[1]=l[2]
		l[2]=tmp
		meta=metadata[i]
		for j in range(1,len(l)-1):
			add_to_graph(graph,input_list(j,l[j],board[i],l[2],l[1],len(l)-1,meta),input_list(j+1,l[j+1],board[i],l[2],l[1],len(l)-1,meta))

def preprocess_edges(file):
	double=[]
	new_edges=[]
	for i in file:
		tmp=[]
		words=i[0].split("->")
		if words[0][-5:]=="_CBSE":
			words[0]=words[0][:-5]
		if words[1][-5:]=="_CBSE":
			words[1]=words[1][:-5]
		tmp.append(words[0].upper()+"->"+words[1].upper())
		tmp.append(i[1])
		if words[0].upper()+"->"+words[1].upper() not in double:
			double.append(words[0].upper()+"->"+words[1].upper())
			double.append(words[1].upper()+"->"+words[0].upper())
			new_edges.append(tmp)
	return new_edges

def add_edges(graph,file):
	file=preprocess_edges(file)
	count=0
	for k in file:
		words=k[0].split("->")
		one=nodes.match("TOPIC",Name=words[0]).first()
		two=nodes.match("INTERMEDIATE",Name=words[0]).first()
		if one!=None:
			count+=1
			c1=nodes.match("TOPIC",Name=words[1]).first()
			c2=nodes.match("INTERMEDIATE",Name=words[1]).first()
			if c1!=None:
				onec=Relationship(one,"HAS PREREQ",c1)
				onec["Weight"]=float(k[1])
				graph.merge(onec)
			elif c2!=None:
				onec=Relationship(one,"HAS PREREQ",c2)
				onec["Weight"]=float(k[1])
				graph.merge(onec)
		elif two!=None:
			count+=1
			c1=nodes.match("TOPIC",Name=words[1]).first()
			c2=nodes.match("INTERMEDIATE",Name=words[1]).first()
			if c1!=None:
				onec=Relationship(two,"HAS PREREQ",c1)
				onec["Weight"]=float(k[1])
				graph.merge(onec)
			elif c2!=None:
				onec=Relationship(two,"HAS PREREQ",c2)
				onec["Weight"]=float(k[1])
				graph.merge(onec)
