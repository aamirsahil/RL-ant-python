import cellular
import random
import qlearn
import backprop
from multiprocessing import Pool
import pickle

# Simulation Parameters
map='food.txt' # food to home separation file
height=30 # world height
width=30 # world width
randomize = False
experiment = 0

antCount=10 # ant count
time=1000 # total time of simulation

dispersionRate=0.04     # rate of spread of pheromone
evaporationRate=0.99    # rate of disappearance of pheromone

#remember 1 ---5
#remember -1 ---6
# Mixed Case
# actions=[0,1,2,3,4,5,6]    # set to [2,3,4] for not structure generation
# Purely External
actions=[0,1,2,3,4]    # set to [2,3,4] for not structure generation

# rewards
posReward=10			# reward for completing a trip
negReward=-1            # reward for moving

# q learning paramerters
qEpsilon=0.4			# Q-Learning exploration rate
qLambda=0.95			# Q-Learning future discount rate
qAlpha=0.2				# Q-Learning learning rate
qDecayTill=0           #Q decay till
qEpsilon_decay = 0.01 # decay rate

# probably for plotting 
displaySize=0			# how big to make the display (set to 0 for no display)

# NN details
learningRate=0.2
nnHidden=5
updateTimes=100
trainingTimes=10
memStaet=[]

# agentsDict = {}
# for tracking how often different actions are chosen
count=[0,0,0,0,0,0,0]

# whats the purpose
isPher_Lev_NN =False
isIhIt_NN=True

# class representing each cell of the world grid
class Cell:
  # constructor
  def __init__(self):
    self.isHome=0 # home cell
    self.isFood=0 # target cell
    self.homePher=0 # level of home pheromone
    self.foodPher=0 # level of target pheromone
  
  # update the pheromone level(due to dispersion and evoporation)
  def update(self,around):
    htotal=0
    ftotal=0

    # look up pheromone level of surrounding cell 
    for c in around:
      htotal+=c.homePher
      ftotal+=c.foodPher

    # calculate home and food pheromone
    havg=htotal/len(around)
    favg=ftotal/len(around)
    # phermone move out/in depending on concentration
    self.homePher+=(havg-self.homePher)*dispersionRate
    self.foodPher+=(favg-self.foodPher)*dispersionRate
    # pheromone evoporartes off
    self.homePher*=evaporationRate
    self.foodPher*=evaporationRate

    # saturation and depeltion of pheromone
    if self.homePher>1: self.homePher=1
    if self.foodPher>1: self.foodPher=1
    if self.homePher<0.001: self.homePher=0
    if self.foodPher<0.001: self.foodPher=0

  # color for plotting cell
  def colour(self):
    if self.isHome: return '#FF0000'     # red
    if self.isFood: return '#0000FF'     # blue
    # if it isn't one of these two cases, we need to make a colour that's
    # a combination of red and blue
    r=min(self.homePher,1)
    b=min(self.foodPher,1)
    retVal = '#%02x00%02x'%(int(r*255),int(b*255))
    return retVal

  # copies the value of different cell
  def copy(self,other):
    self.isHome=other.isHome
    self.isFood=other.isFood
    self.homePher=other.homePher
    self.foodPher=other.foodPher

  # sets home and target level by taking text from txt file
  def load(self,text):
    self.isHome=0
    self.isFood=0
    if text=='H': self.isHome=1
    if text=='F': self.isFood=1

# agent class(child of cellular.Agent)
class Agent(cellular.Agent):
  def __init__(self,mem,isPher_Lev_NN=True,isIhIt_NN=False,actions=[0,1,2,3,4,5,6],q=None,id=0):
    self.id = id
    self.hasFood=0
    self.foodCount=0
    self.reward=0
    self.pherTime=0
    self.ai=qlearn.QLearn(epsilon=qEpsilon,lambd=qLambda,alpha=qAlpha,epsilon_decay=qEpsilon_decay,q=q)
    self.decayTill = qDecayTill
    self.isPher_Lev_NN=isPher_Lev_NN
    self.isIhIt_NN =isIhIt_NN
    if self.isIhIt_NN and self.isPher_Lev_NN :
      self.internal=backprop.NN(5,7,1)
    else:
      self.internal = backprop.NN(3,3,1)
    self.ai.setActions(actions)
    self.actionList=[]
    self.foodArray=[]
    self.mem=mem
    self.is_droper = True
    #self.MemState=[]
  # checks if the agent is droper not
  def checkDroper(self):
    if 0 in self.actionList[-1000:-1] or 1 in self.actionList[-1000:-1]:
      self.is_droper = True
    else:
      self.is_droper = False
  def getmemState(self,pher_Lev=True,IhIt=False,):
      states=[]
      if self.isIhIt_NN:
        states.append(-1)
        states.append(-1)
        here = self.getLocation()
        if here.isHome:states[0]=1
        if here.isFood:states[1]=1
      if self.isPher_Lev_NN:
        states.append(((2*self.getHomePherLevel())/3 )- 1)
        states.append(((2*self.getFoodPherLevel())/3 )- 1)
      states.append(self.internal.ao[0])
      return states

  def update(self, time, exper):
    here=self.getLocation()
    if time%1000 == 0:
      self.checkDroper()
    reward=negReward
    # change state if we've reached what we are looking for
    #when reached to home and reached to target this turned around nature should emergent
    self.foodArray.append(0)
    if self.hasFood:
      if here.isHome:
        self.hasFood=0
        self.turnAround()
        self.foodCount+=1
        self.foodArray[len(self.foodArray)-1]=1
        reward=posReward
    else:
      if here.isFood:
        self.hasFood=1
        self.turnAround()
    if self.pherTime<5:
        self.pherTime+=1
    self.reward=reward

    # Mixed Case
    #what is use of this loop? may be some what randomizing memory
    # for i in range(updateTimes):
    #    i=self.getmemState()
    #    self.internal.update(i)

    #why mem is sometimes 2,3
    # mem=round((self.internal.ao[0]+1.0)*self.mem/2)
    #self.MemState.append({"state":self.getmemState(),"memory":mem})
    #mem=int(self.internal.ao[0])

    # Mixed Case
    # state=(self.getHomePherLevel(),self.getFoodPherLevel(),self.pherTime,mem)

    # self.x, self.y = 0,0
    # External Case
    state=(self.getHomePherLevel(),self.getFoodPherLevel(),self.pherTime)

    if (time<50000 or exper!="TurnedOffDeath") and exper!="QPass":
      self.ai.learn(state,reward)
    choice=self.ai.do(state)
    # print(self.id,self.getHomePherLevel())
    # choice=0
    self.actionList.append(choice)

    if self.world.age>100:
      count[choice]+=1

    if choice==0:
      self.dropHomePher()
    elif choice==1:
      self.dropFoodPher()
    elif choice==2:
      self.followHomePher()
    elif choice==3:
      self.followFoodPher()
    elif choice==4:
      self.moveRandomly()
    elif choice==5:
      self.doChange(-1)
    elif choice==6:
      self.doChange(1)



  def dropFoodPher(self):
    here=self.getLocation()
    here.foodPher+=0.2
    self.pherTime=0
  def dropHomePher(self):
    here=self.getLocation()
    here.homePher+=0.2
    self.pherTime=0
  def getPherLevel(self,p):
    if p==0: return 0
    elif p<0.1: return 1
    elif p<0.25: return 2
    else: return 3
  def getFoodPherLevel(self):
    return self.getPherLevel(self.getLocationNow().foodPher)
  def getHomePherLevel(self):
    return self.getPherLevel(self.getLocationNow().homePher)

  def followFoodPher(self):
    c=self.getCellAhead()
    self.turn(-1)
    l=self.getCellAhead()
    self.turn(2)
    r=self.getCellAhead()
    self.turn(-1)


    if c.isFood: c=1
    else: c=c.foodPher
    if l.isFood: l=1
    else: l=l.foodPher
    if r.isFood: r=1
    else: r=r.foodPher

    self.followPher(l,c,r)
  def followHomePher(self):
    c=self.getCellAhead()
    self.turn(-1)
    l=self.getCellAhead()
    self.turn(2)
    r=self.getCellAhead()
    self.turn(-1)

    if c.isHome: c=1
    else: c=c.homePher
    if l.isHome: l=1
    else: l=l.homePher
    if r.isHome: r=1
    else: r=r.homePher

    self.followPher(l,c,r)
  def followPher(self,l,c,r):
    m=(l,c,r)
    max_m=max(m)
    max_ind=[]
    for i in range(len(m)):
      if max_m == m[i]:
        max_ind.append(i)
    i = random.choice(max_ind)
    if i == 0:
      self.turnLeft()
    elif i == 2:
      self.turnRight()
    self.goForward()

  def moveRandomly(self):
    self.turn(random.choice([0,1,-1]))
    self.goForward()

  def colour(self):
    if self.hasFood: return '#0000FF'   # blue
    else: return '#FF0000'              # red
  
  def doChange(self,value):
    i=self.getmemState()
    for x in range(trainingTimes):
      self.internal.trainOne(i,[value],learningRate)




def run(mem, exper, morphNum=0, morphTime=0, morphType="", morphPlace="", percent=50):
  global isPher_Lev_NN,isIhIt_NN
  # importing past agents Q
  # flname = f'./data/study_1/TurnedOffDeath/20/TurnedOffDeath_t_100000_20_droper_iter4_5.dat'
  # file = open(flname, "rb")
  # prevData = pickle.load(file)
  # prevData = prevData[-1]["agents"]
  # file.close()
  # 
  id = 0
  world=cellular.World(Cell,width,height)
  world.load(map)
  # figure out where to put the ants (they should start at home)
  homes=[]
  for i in range(width):
    for j in range(height):
      if world.grid[i][j].isHome: homes.append((i,j))
  for i in range(antCount):
    # q = prevData[i]["q"]
    q = {}
    ant=Agent(mem,isPher_Lev_NN,isIhIt_NN,actions=actions,q=q,id=id)
    i,j=random.choice(homes)
    world.addAgent(ant,x=i,y=j)
    id+=1

  if displaySize:
    world.display(size=displaySize)
  data=[{} for i in range(len(world.agents))]
  data = setDataInit(world, data)
  # run the simulation
  for i in range(time):
    print(i)
    if i == morphTime:
      if exper == "death":
        #death
        if morphType=="first":
          for i in range(morphNum):
            world.removeAgent(world.agents[0])
        elif morphType=="last":
          for i in range(morphNum):
            world.removeAgent(world.agents[-1])
        elif morphType=="droper":
          world.droperList()
          if len(world.droper_list) < morphNum:
            morphNum = len(world.droper_list)
          for i in range(morphNum):
            world.droperList()
            print(world.droper_list)
            world.removeAgent(world.agents[world.droper_list[0]])
        elif morphType=="free":
          world.freeList()
          if len(world.free_list) < morphNum:
            morphNum = len(world.free_list)
          for i in range(morphNum):
            world.freeList()
            print(world.free_list)
            world.removeAgent(world.agents[world.free_list[0]])
      elif exper == "TurnedOffDeath":
        #death of dropers
        world.droperList()
        if len(world.droper_list) < morphNum:
          morphNum = len(world.droper_list)
        for i in range(morphNum):
          world.droperList()
          print(world.droper_list)
          world.removeAgent(world.agents[world.droper_list[0]])
      # deathPercent
      elif exper == "deathPercent":
        #death
        world.droperList()
        droper_num = len(world.droper_list)
        morphNum = int(droper_num*percent/100)
        for i in range(morphNum):
          world.droperList()
          print(world.droper_list)
          world.removeAgent(world.agents[world.droper_list[0]])
      # birth
      elif exper == "birth":
        #death
        if morphType=="first":
          index = 0
          bornAgent = world.agents[index]
          newAgent = Agent(mem,isPher_Lev_NN,isIhIt_NN,actions=actions,q=bornAgent.ai.q)
          for i in range(morphNum):
            if morphPlace=="home":
              x,y=random.choice(homes)
              world.addAgent(newAgent,x,y)
            elif morphPlace=="location":
              world.addAgent(newAgent, bornAgent.x, bornAgent.y, bornAgent.dir)
        elif morphType=="last":
          index = -1
          bornAgent = world.agents[index]
          newAgent = Agent(mem,isPher_Lev_NN,isIhIt_NN,actions=actions,q=bornAgent.ai.q)
          for i in range(morphNum):
            if morphPlace=="home":
              x,y=random.choice(homes)
              world.addAgent(newAgent,x,y)
            elif morphPlace=="location":
              world.addAgent(newAgent, bornAgent.x, bornAgent.y, bornAgent.dir)
        elif morphType=="droper":
          world.droperList()
          if len(world.droper_list) < morphNum:
            morphNum = len(world.droper_list)
          for i in range(morphNum):
            world.droperList()
            print(world.droper_list)
            bornAgent = world.agents[world.droper_list[0]]
            newAgent = Agent(mem,isPher_Lev_NN,isIhIt_NN,actions=actions,q=bornAgent.ai.q)
            if morphPlace=="home":
              x,y=random.choice(homes)
              world.addAgent(newAgent,x,y)
            elif morphPlace=="location":
              world.addAgent(newAgent, bornAgent.x, bornAgent.y, bornAgent.dir)
        elif morphType == "free":
          world.freeList()
          if len(world.free_list) < morphNum:
            morphNum = len(world.free_list)
          for i in range(morphNum):
            world.freeList()
            print(world.free_list)
            bornAgent = world.agents[world.free_list[0]]
            newAgent = Agent(mem,isPher_Lev_NN,isIhIt_NN,actions=actions,q=bornAgent.ai.q)
            if morphPlace=="home":
              x,y=random.choice(homes)
              world.addAgent(newAgent, x, y)
            elif morphPlace=="location":
              world.addAgent(newAgent, bornAgent.x, bornAgent.y, bornAgent.dir)  
      # rbirth
      elif exper == "rebirth":
        #death
        if morphType=="firstWlast":
          deadAgent = []
          for i in range(morphNum):
            deadAgent.append(world.agents[0])
            world.removeAgent(world.agents[0])
          for i in range(morphNum):
            index = 0
            bornAgent = world.agents[-(i+1)]
            newAgent = Agent(mem,isPher_Lev_NN,isIhIt_NN,actions=actions,q=bornAgent.ai.q)
            
            if morphPlace=="home":
              x,y=random.choice(homes)
              world.insertAgent(newAgent, index, x, y)
            elif morphPlace=="location":
              world.insertAgent(newAgent, index, deadAgent[i].x, deadAgent[i].y, deadAgent[i].dir)
            else:
              world.insertAgent(newAgent,index)
        elif morphType=="lastWfirst":
          deadAgent = []
          for i in range(morphNum):
            deadAgent.append(world.agents[-1])
            world.removeAgent(world.agents[-1])
          for i in range(morphNum):
            index = len(world.agents)
            bornAgent = world.agents[i]
            newAgent = Agent(mem,isPher_Lev_NN,isIhIt_NN,actions=actions,q=bornAgent.ai.q)
            
            if morphPlace=="home":
              x,y=random.choice(homes)
              world.insertAgent(newAgent, index, x, y)
            elif morphPlace=="location":
              world.insertAgent(newAgent, index, deadAgent[i].x, deadAgent[i].y, deadAgent[i].dir)
            else:
              world.insertAgent(newAgent,index)
        elif morphType=="droperWfree":
          world.droperList()
          if len(world.droper_list) < morphNum:
            morphNum = len(world.droper_list)
          for i in range(morphNum):
            world.droperList()
            world.freeList()
            deadAgent = world.agents[world.droper_list[0]]
            index = world.droper_list[0]
            bornAgent = world.agents[random.choice(world.free_list)]
            world.removeAgent(deadAgent)
            newAgent = Agent(mem,isPher_Lev_NN,isIhIt_NN,actions=actions,q=bornAgent.ai.q)
            if morphPlace=="home":
              x,y=random.choice(homes)
              world.insertAgent(newAgent,index,x,y)
            elif morphPlace=="location":
              world.insertAgent(newAgent, index, deadAgent.x, deadAgent.y, deadAgent.dir)
            elif morphPlace=="random":
              world.insertAgent(newAgent, index)
        elif morphType=="freeWdroper":
          world.freeList()
          if len(world.free_list) < morphNum:
            morphNum = len(world.free_list)
          for i in range(morphNum):
            world.droperList()
            world.freeList()
            deadAgent = world.agents[world.free_list[0]]
            bornAgent = world.agents[random.choice(world.droper_list)]
            index = world.free_list[0]
            world.removeAgent(deadAgent)
            newAgent = Agent(mem,isPher_Lev_NN,isIhIt_NN,actions=actions,q=bornAgent.ai.q)
            if morphPlace=="home":
              x,y=random.choice(homes)
              world.insertAgent(newAgent,index,x,y)
            elif morphPlace=="location":
              world.insertAgent(newAgent, index, deadAgent.x, deadAgent.y, deadAgent.dir)
            elif morphPlace=="random":
              world.insertAgent(newAgent, index)
      # seq -> rand
      elif exper == "SeqToRand":
        global randomize
        randomize = True
    world.update(randomize, i, exper)

    # check = True
    # sum = 0
    # sum2 = 0
    # for w in range(world.width):
    #   for h in range(world.height):
    #     check = check and (world.grid[w][h].homePher==world.grid2[w][h].homePher)
    #     sum += world.grid[w][h].homePher
    #     sum2 += world.grid2[w][h].homePher
    # print(check)
    # print(sum)
    # print(sum2)

    data=setData(world, data)
  return data
def setDataInit(world, data):
  for i in range(len(world.agents)):
    data[i]["id"] = [world.agents[i].id]
    data[i]["x"], data[i]["y"] = [world.agents[i].x], [world.agents[i].y]
    data[i]["action"], data[i]["sense"] = [0], [(1,0,0)]
    data[i]["food"], data[i]["q"] = [0], [world.agents[i].ai.q]
    data[i]["reward"], data[i]["dropper"] =  [0], [world.agents[i].is_droper]
  return data
def setData(world, data):
  for i in range(len(world.agents)):
    id = world.agents[i].id
    agent = world.agents[i]
    data[id]["id"].append(id)
    data[id]["x"].append(agent.x)
    data[id]["y"].append(agent.y)
    data[id]["action"].append(agent.actionList[-1])
    data[id]["sense"].append((agent.getHomePherLevel(),agent.getFoodPherLevel(),agent.pherTime))
    data[id]["food"].append(agent.foodArray[-1])
    data[id]["q"].append(agent.ai.q)
    data[id]["reward"].append(agent.reward)
    data[id]["dropper"].append(agent.is_droper)
  return data
def multiProcessSimulation(nProcess,lst_args,func_ToProcess):
    p= Pool(nProcess)
    result = p.map(func_ToProcess,lst_args)
    p.close()
    p.join()

  

#objToDump should be dict
# def pickleDumpToTheFile(flName,objToDump):
#   fl = None
#   if os.path.exists(flName):
#       fl = open(flName,'rb+')
#       oldObjData=pickle.load(fl)
#       objToDump.update(oldObjData)
#   else:
#       fl = open(flName,"wb+")
#   pickle.dump(objToDump,fl)
#   fl.close()