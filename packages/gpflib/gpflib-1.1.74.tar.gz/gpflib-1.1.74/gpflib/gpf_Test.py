from gpflib import GPF
gpf=GPF()
Lua='''
Speedup(1)
OriOn()
Handle0=GetAS("<manner","","","","","","","","","")
Handle3=Freq(Handle0,"$Q",0)
Ret=Output(Handle3,1000)
return Ret

'''
Ret=gpf.Parse("我们今天去上学学物理",Structure="Tree")
print(Ret)
def GetBCC1():
    ret=gpf.BCC("man")
    print(ret)
    


