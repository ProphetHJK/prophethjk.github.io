import sqlite3,sys

class COSEM_Class:
    def __init__(self):
        self.value = 0
        self.leaf = []

class ObisA:
    def __init__(self):
        self.value = 0
        self.leaf = []

class ObisB:
    def __init__(self):
        self.value = 0
        self.leaf = []
# 按功能区分存储位置
class ObisC:
    def __init__(self):
        self.value = 0
        self.base_address = 0
        self.leaf = []

class ObisD:
    def __init__(self):
        self.class_id = 0
        self.value = 0
        self.leaf = []

class ObisE:
    def __init__(self):
        self.sub_class_id = 0
        self.value = 0
        self.leaf = []

class ObisF:
    def __init__(self):
        self.leaf = []

class Root:
    leaf = []
    
root = Root()
alist = []
blist = []
clist = []
dlist = []
elist = []
flist = []

# a1 = ObisA()
# b1 = ObisB()
# c1 = ObisC()
# d1 = ObisD()
# e1 = ObisE()
# f1 = ObisF()

# a1.leaf.append(b1)
# b1.leaf.append(c1)
# c1.leaf.append(d1)
# d1.leaf.append(e1)
# e1.leaf.append(f1)

# b1.father = a1
# c1.father = b1
# d1.father = c1
# e1.father = d1
# f1.father = e1

# alist.append(a1)
# for a in alist:   
#     root.leaf.append(a)

# for a in root.leaf:
#     print(a.leaf[0].leaf[0].value)

switchflag = 1

tablename = "idis" # idis or sanxing
objname_list = ["root","A","B","C","D","E","F"]

# 方式一：D携带类型信息
def generateTree(father_obj,father_name_id,where_string,conn):
    global objname_list
    global tablename
    if father_name_id == len(objname_list)-1:
        return
    c = conn.cursor()
    if where_string == "start":
        where_string = ""
    elif where_string == "":
        where_string = "where " + where_string + " %s=%d" % (objname_list[father_name_id],father_obj.value)
    else:
        where_string = where_string + " and %s=%d" % (objname_list[father_name_id],father_obj.value)
    if father_name_id == 3:
        groupstr = ",class"
    else:
        groupstr = ""
    if father_name_id == 4:
        wherestr = " and class=%d" % father_obj.class_id
    else:
        wherestr = ""
    sql = "select %s,class from %s %s%s group by %s%s" % (objname_list[father_name_id+1],tablename,where_string,wherestr,objname_list[father_name_id+1],groupstr)
    # print(sql)
    cursor = c.execute(sql)
    for row in cursor:
        if father_name_id == 0:
            obj = ObisA()
        elif  father_name_id == 1:
            obj = ObisB()
        elif  father_name_id == 2:
            obj = ObisC()
        elif  father_name_id == 3:
            obj = ObisD()
            obj.class_id = row[1]
        elif  father_name_id == 4:
            obj = ObisE()
        elif  father_name_id == 5:
            obj = ObisF()
        
        obj.value = row[0]
        father_obj.leaf.append(obj)
        generateTree(obj,father_name_id+1,where_string,conn)

objname_list2 = ["root","class","A","B","C","D","E","F"]
# 方式2：加一层类层
def generateTree2(father_obj,father_name_id,where_string,conn):
    global objname_list2
    global tablename
    if father_name_id == len(objname_list)-1:
        return
    c = conn.cursor()
    if where_string == "start":
        where_string = ""
    elif where_string == "":
        where_string = "where " + where_string + " %s=%d" % (objname_list[father_name_id],father_obj.value)
    else:
        where_string = where_string + " and %s=%d" % (objname_list[father_name_id],father_obj.value)

    sql = "select %s from %s %s group by %s" % (objname_list[father_name_id+1],tablename,where_string,objname_list[father_name_id+1])
    # print(sql)
    cursor = c.execute(sql)
    for row in cursor:
        if father_name_id == 0:
            obj = COSEM_Class()
        elif  father_name_id == 1:
            obj = ObisA()
        elif  father_name_id == 2:
            obj = ObisB()
        elif  father_name_id == 3:
            obj = ObisC()
        elif  father_name_id == 4:
            obj = ObisD()
        elif  father_name_id == 5:
            obj = ObisE()
        elif  father_name_id == 6:
            obj = ObisF()
        
        obj.value = row[0]
        father_obj.leaf.append(obj)
        generateTree(obj,father_name_id+1,where_string,conn)

conn = sqlite3.connect("obis.db")

if switchflag == 1:
    generateTree(root,0,"start",conn)
elif switchflag == 2:
    generateTree2(root,0,"start",conn)
    tablename = tablename + "2"

counter = 0
def filewrite(obis_id,obj,file,fathername):
    global counter
    counter = counter + 1
    myname = "%s%d" % (obis_id,counter)
    file.write("object %s{\n" % (myname))
    file.write("    value=%s\n" % (obj.value))
    if obis_id == 'd' and switchflag == 1:
       file.write("    class_id=%d\n" % (obj.class_id))
    if obis_id == 'c':
        file.write("    base_address=???\n")
    file.write("}\n")
    file.write("%s --> %s\n" % (fathername, myname))
    return myname

usespace = 0

file = open("%s.puml" % tablename,"w+")
file.write("@startuml\n")
usespace = usespace + len(root.leaf)*4

if switchflag == 1:
    for a in root.leaf:
        usespace = usespace + len(a.leaf)*1 + 1
        aname = filewrite("a",a,file,"root")
        # print(a.value,' ')
        for b in a.leaf:
            usespace = usespace + len(b.leaf)*1 + 1
            bname = filewrite("b",b,file,aname)
            # print(a.value,' ',b.value)
            for c in b.leaf:
                usespace = usespace + len(c.leaf)*1 + 1 + 4
                cname = filewrite("c",c,file,bname)
                # print(a.value,' ',b.value,' ',c.value)
                for d in c.leaf:
                    usespace = usespace + len(d.leaf)*1 + 1 + 2
                    dname = filewrite("d",d,file,cname)
                    for e in d.leaf:
                        usespace = usespace + len(e.leaf)*1 + 1
                        ename = filewrite("e",e,file,dname)
                        for f in e.leaf:
                            usespace = usespace + 1
                            filewrite("f",f,file,ename)
elif switchflag == 2:
    for cosem_class in root.leaf:
        usespace = usespace + len(cosem_class.leaf)*1 + 1
        classname = filewrite("class",cosem_class,file,"root")
        for a in cosem_class.leaf:
            usespace = usespace + len(a.leaf)*1 + 1
            aname = filewrite("a",a,file,classname)
            # print(a.value,' ')
            for b in a.leaf:
                usespace = usespace + len(b.leaf)*1 + 1
                bname = filewrite("b",b,file,aname)
                # print(a.value,' ',b.value)
                for c in b.leaf:
                    usespace = usespace + len(c.leaf)*1 + 1
                    cname = filewrite("c",c,file,bname)
                    # print(a.value,' ',b.value,' ',c.value)
                    for d in c.leaf:
                        usespace = usespace + len(d.leaf)*1 + 1 + 2
                        dname = filewrite("d",d,file,cname)
                        for e in d.leaf:
                            usespace = usespace + len(e.leaf)*1 + 1
                            ename = filewrite("e",e,file,dname)
                            for f in e.leaf:
                                usespace = usespace + 1
                                filewrite("f",f,file,ename)

print("usespace:%d" % usespace)                        
file.write("@enduml\n")
file.close()
# conn.commit()
conn.close()
