# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 16:40:01 2019

@author: Aishwarya
"""
import copy
import time

queries=[]
KB=[]
dictionary={}
max_limit=8000

class Sentence():
    def __init__(self,sentence):
        self.sentence=sentence
        all_predicates=sentence.split("|")
        self.predicates=[]
        for predicate in all_predicates:
            predicate=Predicate(predicate)
            #print (predicate.predicate_name)
            self.predicates.append(predicate)
        #print ("sentence",self.sentence)
        
            
            
class Predicate():
    def __init__(self,predicate):
        self.predicate=predicate
        temp=predicate.split('(')
        if temp[0][0]=='~':
            self.negation=True
            self.predicate_name=temp[0][1:]
        else:
            self.negation=False
            self.predicate_name=temp[0]
        #self.predicate_name=temp[0]
        #print ("predicate name",self.predicate_name)
        temp=temp[1][:-1]
        #print (temp)
        self.arguments=temp.split(",")
        #print ("arguments",self.arguments)
        



#reading the input form the file
def read_input():
    queries_list=[]
    sentences_list=[]
    file=open("input_31.txt", "r")
    contents=file.readlines()
    
    no_of_queries=int(contents[0])
    for i in range(no_of_queries):
        query=contents[1+i].rstrip()
        if " " in query:
            query=query.replace(" ","")
        queries_list.append(query)
    
    no_of_sentences=int(contents[no_of_queries+1])
    for i in range(no_of_sentences):
        sentence=contents[no_of_queries+2+i].rstrip()
        if " " in sentence:
            sentence=sentence.replace(" ","")
        if '&' in sentence and '=>' not in sentence:
            temp=sentence.split("&")
            for i in temp:
                sentences_list.append(i)
        else:
            sentences_list.append(sentence)
    
    return queries_list,sentences_list
    

def convert_to_cnf(fol_sentence):
    #print ()
    #print (fol_sentence)
    s=eliminate_implications(fol_sentence)
    #print ("s",s)
    s=move_negation_inwards(s)
    #print (s)
    
    return s

def eliminate_implications(fol_sentence):
    #print ("eliminating implications")
    if not "=>" in fol_sentence:
        return fol_sentence
    else:
        parts=fol_sentence.split('=>')
        a=parts[0]
        b=parts[1]
        s="~("+a+")|"+b
        return s
    
def move_negation_inwards(s):
    #print ("moving negation inward")
    #print (s)
    st=""
    if s[0]!='~':
        #print ('hello')
        return s
    else:
        a=s.find('&')
        
        if a==-1:
            if s[2]=='~':
                s=s.replace("~(~","")
                s=s.replace("))",")")
            else:
                s=s.replace("~(","~")
                s=s.replace("))",")")
            return s
        else:
            s=s[2:len(s)]
            #print (a)
            s_list=s.split('&')
            #print (s_list)
            for i in s_list:
                #print (i)
                if i[0]=='~':
                    st=st+i[1:]+'|'
                else:
                    st=st+"~"+i+'|'
            st=st.replace("))",")")
            st=st[0:len(st)-1]
            return st
        
def standardize(KB):
    standardized_KB=[]
    for index in range(len(KB)):
        sentence=""
        argument_list=set()
        predicate_argument=[]
        argument_dict={}
        #print ("----")
        #print (KB[index])
        if '|' in KB[index]:
            predicates=KB[index].split('|')
        else:
            predicates=[]
            predicates.append(KB[index])
        #print (predicates)
        for p in predicates:
            x=[]
            predicate_name=p.split("(")[0]
            temp=p[p.index('(')+1:-1]
            arguments=temp.split(',')
            x.append(predicate_name)
            x.extend(arguments)
            #print (temp)
            predicate_argument.append(x)
            argument_list=argument_list.union(arguments)
        #print (predicate_argument)
        #print (argument_list)
        for a in argument_list:
            if a[0].islower():
                argument_dict[a]=a+str(index)
        #print (argument_dict)
        for s in range(len(predicate_argument)):
            for i in range(len(predicate_argument[s])):
                if i==0:
                    sentence+=predicate_argument[s][i] + '('
                    
                elif predicate_argument[s][i] in argument_dict:
                    if i==len(predicate_argument[s])-1:
                        sentence+=argument_dict[predicate_argument[s][i]] + ')'
                    else:
                        sentence+=argument_dict[predicate_argument[s][i]] + ','
                
                elif i==len(predicate_argument[s])-1:
                        sentence+=predicate_argument[s][i] + ')'
                else:
                    sentence+=predicate_argument[s][i] + ','
            if s!=len(predicate_argument)-1:
                sentence+='|'
        standardized_KB.append(sentence)
        #print (sentence)
        
    return standardized_KB
                
                    
        
            

def unification(p1,p2):
    if p1.predicate_name==p2.predicate_name:
        theta={}
        return unify(p1.arguments,p2.arguments,theta)
    else:
        return False
    
def unify(p1_arguments,p2_arguments,theta):
    if theta==False:
        return False
    elif p1_arguments==p2_arguments:
        return theta
    elif isinstance(p1_arguments,str) and p1_arguments.islower():
        return unify_variable(p1_arguments,p2_arguments,theta)
    elif isinstance(p2_arguments,str) and p2_arguments.islower():
        return unify_variable(p2_arguments,p1_arguments,theta)
    elif isinstance(p1_arguments,list) and isinstance(p2_arguments,list):
        return unify(p1_arguments[1:],p2_arguments[1:],unify(p1_arguments[0],
                     p2_arguments[0],theta))
    else:
        return False
    
def unify_variable(variable,x,theta):
    if variable in theta:
        return unify(theta[variable],x,theta)
    elif x in theta:
        return unify(variable,theta[x],theta)
    else:
        theta[variable]=x
        return theta
   

def resolution_sentences(query,knowledge,dictionary):
    #print(";;;;;;performing resolution")
    #print(query.sentence)
    #print (query)
    knowledge.sort(key=lambda x:len(x.sentence))
    #for i in knowledge:
        #print (i.sentence)
    knowledge.insert(0,query)
    for i in query.predicates:
        if i.predicate_name in dictionary:
            dictionary[i.predicate_name].add(query)
        else:
            dictionary[i.predicate_name]=set([query])
    start_time=time.time()
    while(1):
        seen={}
        new_sentences=set()
        #resolving each query
        #print(time.clock()-tt)
        current_time=time.time()
        if (current_time-start_time)>30:
            return False
# =============================================================================
#         if len(knowledge)>max_limit:
#             return False
# =============================================================================
        for l in range(len(knowledge)):
            #s=query
    # =============================================================================
    #         if (l==2):
    #             break
    # =============================================================================
            s=knowledge[l]
            #find all sentences that can resolve the current sentence
            #print("\n.....")
            list_sentences=set()
            #print (s.sentence)
            for p in s.predicates:
                #print ("-------")
                #print (p.predicate_name)
                #for i in dictionary[p.predicate_name]:
                    #print (i.sentence)
                if p.predicate_name in dictionary:
                    list_sentences=list_sentences.union(dictionary[p.predicate_name])
            #for i in list_sentences:
                #print ("i",i.sentence)
            for t in list_sentences:
                #print ("\ns",s.sentence)
                #print ("t",t.sentence)
                if (s==t):
                    #print ("same sentence")
                    continue
                if t.sentence in seen:
                    if s.sentence in seen[t.sentence]:
                        seen[t.sentence].discard(s.sentence)
                        continue
                if s.sentence in seen:
                    if t.sentence in seen[s.sentence]:
                        seen[s.sentence].discard(t.sentence)
                        continue
                    else:
                        seen[s.sentence].add(t.sentence)
                else:
                    seen[s.sentence]=set([t.sentence])
                
                for p1 in s.predicates:
                    for p2 in t.predicates:
                        #knowledge2=copy.deepcopy(knowledge)
                        #print ("p1",p1.predicate)
                        #print ("p2",p2.predicate)
                        unified_values=False
                        if (p1.negation!=p2.negation) and (p1.predicate_name==p2.predicate_name):
                            #print ("starting unification")
                            unified_values=unification(p1,p2)
                            #print ("u",unified_values)
                        if unified_values==False:
                            #print ("cannot unify")
                            continue
# =============================================================================
#                         if len(unified_values)==0:
#                             continue
#                             #print ('blahhh', p1.predicate,p2.predicate)
# =============================================================================
                        else:
                            #print ("continuing unification")
                            remaining_first=[]
                            remaining_second=[]
                            for a in s.predicates:
                                if a==p1:
                                    continue
                                else:
                                    remaining_first.append(a)
                            #print ("remaining first",len(remaining_first))
                            #for i in remaining_first:
                                #print (i.predicate)
                            for b in t.predicates:
                                if b==p2:
                                    continue
                                else:
                                    remaining_second.append(b)
                            #print ("remaining second",len(remaining_second))
                            #for i in remaining_second:
                                #print (i.predicate)
                            if len(remaining_first)==0 and len(remaining_second)==0:
                                #print ("no more remaining values")
                                return True
                            else:
                                r1=copy.deepcopy(remaining_first)
                                r2=copy.deepcopy(remaining_second)
                                if len(r1)!=0:
                                    #print ("substituting in p1")
                                    for c in r1:
                                        for index in range(len(c.arguments)):
                                            if c.arguments[index] in unified_values:
                                                c.arguments[index]=unified_values[c.arguments[index]]
                                        c.predicate=c.predicate.split("(")[0] + "(" + ','.join(c.arguments) + ")"
                                        #print ("first predicate after substitution",c.predicate)
                                if len(r2)!=0:
                                    #print ("substituting in p2")
                                    for d in r2:
                                        #print (d.arguments)
                                        for index in range(len(d.arguments)):
                                            #print (d.arguments[index])
                                            if d.arguments[index] in unified_values:
                                                d.arguments[index]=unified_values[d.arguments[index]]
                                        d.predicate=d.predicate.split("(")[0] + "(" + ','.join(d.arguments) + ")"
                                        #print ("second predicate after substitution",d.predicate)
                                r1.extend(r2)
                                #print ("total",remaining_first)
                                temp=[]
                                for i in r1:
                                    temp.append(i.predicate)
                                #print (temp)
                                new_sentence="|".join(temp)
                                #print ("new sentence",new_sentence)
                                new_sentence=Sentence(new_sentence)
                                new_sentences.add(new_sentence)
                                #print (new_sentences)
                                c=time.time()
                                if (c-start_time)>20:
                                    break
                                #print (new_sentences)
                            c=time.time()
                            if (c-start_time)>20:
                                break
                        c=time.time()
                        if (c-start_time)>20:
                            break
                    c=time.time()
                    if (c-start_time)>20:
                        break
                c=time.time()
                if (c-start_time)>20:
                    break
            c=time.time()
            if (c-start_time)>20:
                break
            
        
        
        if new_sentences.issubset(knowledge):
            print ("here")
            return False
    
        #k=set(knowledge)
        #print (len(new_sentences))
        new_sentences=new_sentences.difference(knowledge)
        #print ("...",len(new_sentences))
        for sen in new_sentences:
            #print ("added to kb\n",sen.sentence)
            knowledge.append(sen)
            for i in sen.predicates:
                if i.predicate_name in dictionary:
                    dictionary[i.predicate_name].add(sen)
                else:
                    dictionary[i.predicate_name]=set([sen])
            #for mm in knowledge:
                #print (mm.sentence)
            
    
    
    



queries,fol=read_input()

# =============================================================================
# print ("-----Queries-----")
# for i in queries:
#     print (i)
# print("\n------Sentences-----")
# for i in fol:
#     print (i)
# 
# print ("\n------CNF-----")
# =============================================================================
for i in fol:
    cnf_sentence=convert_to_cnf(i)
# =============================================================================
#     print (cnf_sentence)
# =============================================================================
    
    #st=Sentence(cnf_sentence)
    #print (st)
    KB.append(cnf_sentence)
#print ("\n-----Standardize-----")
temp=standardize(KB)
KB=[]
for st in temp:
    #print (st)
    st=Sentence(st)
    KB.append(st)
    for i in st.predicates:
        if i.predicate_name in dictionary:
            dictionary[i.predicate_name].add(st)
        else:
            dictionary[i.predicate_name]=set([st])
#print (dictionary)
#print (KB)
    
# =============================================================================
# p1=Predicate("Alert(Alice,VitE)")
# p2=Predicate("Alert(x,VitE)")
# u={}
# u=unification(p1,p2)
# print (u)
# =============================================================================




# =============================================================================
# print ("\n-----Resolution-----")
# =============================================================================
#query=queries[0]
output=open("output.txt","w")
for query in queries:
    #print (query)
    #negating the query
    if query[0]=='~':
        query=query[1:]
    else:
        query='~'+query
    
    #creating an object of the query
    query=Sentence(query)
    #print (query)
    
    knowledge=copy.deepcopy(KB)
    
    d=copy.deepcopy(dictionary)
    #print (type(knowledge))
    solution=resolution_sentences(query,knowledge,d)
    if solution:
        solution='TRUE'
    else:
        solution='FALSE'
    output.write(solution)
    output.write('\n')
    print (solution)
output.close()

    
	

	
    
  
    
