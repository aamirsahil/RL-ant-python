import json
import os
import pickle
import sys
import internal_external_multi

def setUpStudy(study):
    if study == 1:
        internal_external_multi.isIhIt_NN = True
        internal_external_multi.isPher_Lev_NN=False
        internal_external_multi.actions=[0,1,2,3,4]
    elif study == 2:
        internal_external_multi.isIhIt_NN = True
        internal_external_multi.isPher_Lev_NN=False
        internal_external_multi.actions=[0,1,2,3,4,5,6]
    elif study == 3:
        internal_external_multi.isIhIt_NN = False
        internal_external_multi.isPher_Lev_NN=True
        internal_external_multi.actions=[0,1,2,3,4,5,6]
    elif study == 4:
        internal_external_multi.isIhIt_NN = True
        internal_external_multi.isPher_Lev_NN=True
        internal_external_multi.actions=[0,1,2,3,4,5,6]

def case(i,study,folder1):
    flName=f"/data/study_1/{folder1}/{folder1}_t_{internal_external_multi.time}_iter{i}.dat"
    return flName

def main(iter):
    internal_external_multi.displaySize= 0
    internal_external_multi.antCount = 20
    internal_external_multi.evaporationRate = 0.99
    internal_external_multi.qEpsilon_decay = 0.01
    internal_external_multi.time = 100000
    internal_external_multi.randomize = 0

    internal_external_multi.experiment = "QPass"
    #########################################################################################
    relative = "./"
    path=os.path.abspath(relative)
    #########################################################################################
    study = 1
    setUpStudy(study)
    #########################################################################################
    # folder1, folder2 = getFolder(internal_external_multi.experiment)
    folder1 = "QPass"
    flName = path+case(iter,study, folder1)
    data=internal_external_multi.run(4.0, exper=internal_external_multi.experiment)
    fl = open(flName,'wb+')
    pickle.dump(data,fl)
    fl.close()

def getParam():
    param = {}
    for i in range(len(sys.argv)//2):
        param[sys.argv[2*i]] = sys.argv[2*i+1]
    return param

if __name__ == "__main__":
    # for all other cases
    # import external as internal_external_multi # to run case 6
    lst=list(range(5))
    internal_external_multi.multiProcessSimulation(os.cpu_count(),lst,main)
    # createParamFile()
    print("done")
# def createParamFile():
#     param = {}
#     param['width'] = internal_external_multi.width
#     param['height'] = internal_external_multi.height

#     param['evp_rate'] = internal_external_multi.evaporationRate
#     param['disp_rate'] = internal_external_multi.dispersionRate
    
#     param['exp_rate'] = internal_external_multi.qEpsilon_decay
#     param['starting_exp'] = internal_external_multi.qEpsilon
#     param['exp_decay_till'] = internal_external_multi.qDecayTill
#     param['lambda'] = internal_external_multi.qLambda
#     param['alpha'] = internal_external_multi.qAlpha
    
#     param['time'] = internal_external_multi.time
#     with open("./data/study_1/agent_no/param.txt", "w") as f:
#         json.dump(param, f)

# def getFolder(i):
#     exp_type1 = (i-1)//3
#     exp_type2 = (i-1)%3
#     if exp_type1==0:
#         folder1 = "death/first"
#     elif exp_type1==1:
#         folder1 = "death/last"
#     elif exp_type1==2:
#         folder1 = "death/droper"
#     elif exp_type1==3:
#         folder1 = "death/free"
#     elif exp_type1==4:
#         folder1 = "rebirth/firstWlast"
#     elif exp_type1==5:
#         folder1 = "rebirth/lastWfirst"
#     elif exp_type1==6:
#         folder1 = "rebirth/droperWfree"
#     else:
#         folder1 = "rebirth/freeWdroper"
#     if exp_type2==0:
#         folder2 = "5"
#     elif exp_type2==1:
#         folder2 = "10"
#     else:
#         folder2 = "20"
#     return folder1, folder2