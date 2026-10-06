import random

# World class
class World:
  # 8 directions to move(0 to 7 = looking up and going clockwise)
  directions8=[(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1)]
  directions4=[(0,-1),(1,0),(0,1),(-1,0)]

  # constructor
  def __init__(self,Cell,width,height,directions=8,calcAround=1,cellUpdate=1):
    # direction possible for the agent to move
    if directions==8:
      self.directions=World.directions8
    elif directions==4:
      self.directions=World.directions4
    else:
      print('Unknown number of directions:',directions)
    
    # 
    self.calcAround=calcAround
    self.cellUpdate=cellUpdate
    if not hasattr(Cell,'update'): self.cellUpdate=0
    
    # world parameters and cell objects
    self.Cell=Cell
    self.width=width
    self.height=height

    # what the agent sees
    self.grid=[[Cell() for j in range(height)] for i in range(width)] 
    # keep track of update
    self.grid2=[[Cell() for j in range(height)] for i in range(width)]
    
    # 
    self.agents=[]
    self.age=0
    # 
    self.droper_list = []
    self.free_list = []
  # no randomize member function for Cell class
  def randomize(self):
    for i in range(self.width):
      for j in range(self.height):
        self.grid[i][j].randomize()
    self.age=0
  ###########################################
  def droperList(self):
    self.droper_list = []
    for i in range(len(self.agents)):
      if self.agents[i].is_droper == True:
        self.droper_list.append(i)
  def freeList(self):
    self.free_list = []
    for i in range(len(self.agents)):
      if self.agents[i].is_droper == False:
        self.free_list.append(i)

  def reincDroper(self, num=1):
    self.droperList()
    self.freeList()
    if num > len(self.droper_list):
      num = len(self.droper_list)
    free_riders = self.free_list
    for i in range(num):
      j = random.choice(free_riders)
      # q = self.agents[j].ai.q
      here = {
        'x':self.agents[self.droper_list[i]].x,
        'y':self.agents[self.droper_list[i]].y,
        'dir':self.agents[self.droper_list[i]].dir,
        }
      self.removeAgent(self.agents[self.droper_list[i]])
      self.insertAgent(self.agents[j], self.droper_list[i],**here)

  def reincFree(self, num=1):
    self.freeList()
    self.droperList()
    if num > len(self.free_list):
      num = len(self.free_list)
    dropers = self.droper_list
    for i in range(num):
      j = random.choice(dropers)
      # q = self.agents[j].ai.q
      here = {
        'x':self.agents[self.free_list[i]].x,
        'y':self.agents[self.free_list[i]].y,
        'dir':self.agents[self.free_list[i]].dir,
        }
      self.removeAgent(self.agents[self.free_list[i]])
      self.addAgent(self.agents[j], self.free_list[i],**here)
  def reincFirst(self, num=1):
    N = len(self.agents)
    for i in range(num):
      j = random.choice(range(num,N))
      # q = self.agents[j].ai.q
      here = {
        'x':self.agents[i].x,
        'y':self.agents[i].y,
        'dir':self.agents[i].dir,
        }
      self.removeAgent(self.agents[i])
      self.insertAgent(self.agents[j],i, **here)
  def reincLast(self, num=1):
    N = len(self.agents)
    for i in range(num):
      j = random.choice(range(0,N-num))
      # q = self.agents[j].ai.q
      here = {
        'x':self.agents[N-(i+1)].x,
        'y':self.agents[N-(i+1)].y,
        'dir':self.agents[N-(i+1)].dir,
        }
      self.removeAgent(self.agents[N-(i+1)])
      self.insertAgent(self.agents[j],N-(i+1), **here)
  ##############################################
  # save the state of the world(no save member function for Cell class)
  def save(self,filename):
    f=open(filename,'w')
    for j in range(self.height):
      line=''
      for i in range(self.width):
        line+=self.grid[i][j].save()
      f.write('%s\n'%line)
    f.close()

  # get cell at sx+dir.x and sy+dir.y
  def getCell(self,sx,sy,dir):
    dx,dy=dir
    x=(sx+dx)%self.width
    y=(sy+dy)%self.height
    return self.grid[x][y]

  def update(self, randomize, time, exper=""):
    if randomize:
      random.shuffle(self.agents)
    # for agent in self.agents:
      # if agent.id == 1:
      # print(agent.id)
    self.age+=1
    if self.cellUpdate:
      for i in range(self.width):
        for j in range(self.height):
          c=self.grid2[i][j]
          c.__dict__=dict(self.grid[i][j].__dict__)
          if self.calcAround:
            around=[self.getCell(i,j,d) for d in self.directions]
            c.update(around)
          else:
            c.update(None)

          if self.displaying:
            c=self.grid2[i][j].colour()
            if self.grid[i][j].colour()!=c:
              self.canvas.itemconfig(self.pixelGrid[i][j],fill=c,outline=c)
      self.grid,self.grid2=self.grid2,self.grid

    for a in self.agents:
      x,y=a.x,a.y
      a.update(time, exper)

      # check = True
      # sum = 0
      # sum2 = 0
      # for w in range(self.width):
      #   for h in range(self.height):
      #     check = check and (self.grid[w][h].homePher==self.grid2[w][h].homePher)
      #     sum += self.grid[w][h].homePher
      #     sum2 += self.grid2[w][h].homePher
      # print(check)
      # print(sum)
      # print(sum2)
      
      if self.displaying:
        c=self.grid[x][y].colour()
        self.canvas.itemconfig(self.pixelGrid[x][y],fill=c,outline=c)
        x,y=a.x,a.y
        c=a.colour()
        self.canvas.itemconfig(self.pixelGrid[x][y],fill=c,outline='black')

    if self.displaying:
      self.canvas.update()

  def redraw(self):
    if self.displayInit:
      for i in range(self.width):
        for j in range(self.height):
          c=self.grid[i][j].colour()
          self.canvas.itemconfig(self.pixelGrid[i][j],fill=c,outline=c)
      for a in self.agents:
        x,y=a.x,a.y
        c=a.colour()
        self.canvas.itemconfig(self.pixelGrid[x][y],fill=c,outline='black')
      self.canvas.update()


  def displayPause(self):
    self.displaying=0
  def displayResume(self):
    if self.displayInit:
      self.displaying=1
      self.redraw()

  displaying=0
  displayInit=0
  def display(self,size=5,title='Cognitive agents'):
    if not World.displayInit or self.width!=len(World.pixelGrid) or self.height!=len(World.pixelGrid[0]):
      import tkinter

      World.root=tkinter.Tk()
      World.root.title(title)
      World.canvas=tkinter.Canvas(self.root)
      World.canvas.pack(side=tkinter.LEFT,fill=tkinter.BOTH,expand=1)
      World.pixelGrid=[[None for j in range(self.height)] for i in range(self.width)]
      xoff=5
      yoff=5
      for i in range(self.width):
        for j in range(self.height):
          c=self.grid[i][j].colour()
          World.pixelGrid[i][j]=self.canvas.create_rectangle((xoff+i*size,yoff+j*size,xoff+i*size+size-1,yoff+j*size+size-1),fill=c,outline=c)
      World.root.geometry('%dx%d'%(xoff*2+self.width*size,yoff*2+self.height*size))
      World.root.update()
      World.displayInit=1
    self.displaying=1
    self.redraw()
  def load(self,file):
    lines=open(file).readlines() # reads the food.txt file
    lines=[x.strip('\n') for x in lines] # remove '\n' from each line
    fh=len(lines)
    fw=max([len(x) for x in lines])
    if fh>self.height:
      fh=self.height
      starty=0
    else:
      starty=(self.height-fh)/2
    if fw>self.width:
      fw=self.width
      startx=0
    else:
      startx=(self.width-fw)/2
    for j in range(fh):
      line=lines[j]
      # print("********")
      # print(self)
      for i in range(min(fw,len(line))):
        self.grid[int(startx+i)][int(starty+j)].load(line[i])
    self.age=0

  def addAgent(self,agent,x=None,y=None,dir=None):
    if x==None: x=random.randrange(self.width)
    if y==None: y=random.randrange(self.height)
    if dir==None: dir=random.randrange(len(self.directions))

    agent.x=x
    agent.y=y
    agent.dir=dir
    agent.world=self
    self.agents.append(agent)
  def insertAgent(self,agent,index,x=None,y=None,dir=None):
    if x==None: x=random.randrange(self.width)
    if y==None: y=random.randrange(self.height)
    if dir==None: dir=random.randrange(len(self.directions))

    agent.x=x
    agent.y=y
    agent.dir=dir
    agent.world=self
    self.agents.insert(index,agent)
  def removeAgent(self,agent):
    self.agents.remove(agent)
    del agent.world

  def countChanges(self):
    count=0
    for i in range(self.width):
      for j in range(self.height):
        if self.grid[i][j].colour()!=self.grid2[i][j].colour():
          count+=1
    return float(count)/(self.width*self.height)

  def isAgentAt(self,x,y):
    for a in self.agents:
      if a.x==x and a.y==y:
        return 1
    return 0

  def quit(self):
    self.root.destroy()





# Agent parent object
class Agent:
  # turn a certain amount
  def turn(self,amount):
    self.dir=(self.dir+amount)%len(self.world.directions)
  def turnLeft(self):
    self.turn(-1)
  def turnRight(self):
    self.turn(1)
  def turnAround(self):
    self.turn(len(self.world.directions)/2)
  
  # move 1 step towards the direction facing
  def goForward(self):
    # print(self.dir)
    dx,dy=self.world.directions[int(self.dir)]
    self.x=(self.x+dx)%self.world.width
    self.y=(self.y+dy)%self.world.height
  # reverse step taken
  def goBackward(self):
    self.turnAround()
    self.goForward()
    self.turnAround()
  # reflect

  # get cell object of current position
  def getLocation(self):
    return self.world.grid[self.x][self.y]
  # get cell object of current position
  def getLocationNow(self):
    return self.world.grid2[self.x][self.y]
  
  # check if agent is infront
  def seesAgentAhead(self):
    x,y=self.x,self.y
    self.goForward()
    x2,y2=self.x,self.y
    self.x,self.y=x,y
    return self.world.isAgentAt(x2,y2)

  # get cell object right infront of agent
  def getCellAhead(self):
    x,y=self.x,self.y
    self.goForward()
    cell=self.getLocationNow()
    self.x,self.y=x,y
    return cell

  # get cell object data for positions nearby
  def getNearbyLocations(self):
    dirs=self.world.directions[self.dir:]+self.world.directions[self.dir:]
    return [self.world.getCell(self.x,self.y,d) for d in dirs]
