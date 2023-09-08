from mesa import Agent, Model
from mesa.model import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import random, time, os, math



class Pedestrian(Agent): 
    def __init__(self, unique_id, model ):
        super().__init__(unique_id, model)
    
    def move(self):
        x,y = self.pos

        semaforo1Derecha = self.model.grid.get_cell_list_contents((11,9))
        semaforo2Arriba = self.model.grid.get_cell_list_contents((14,9))
        semaforo3Abajo = self.model.grid.get_cell_list_contents((11,12))
        semaforo4Izquierda = self.model.grid.get_cell_list_contents((14,12))

        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=False) # obtengo sus posiciones vecinas 
        new_position = random.choice(possible_steps) # consigo una posicion random 
        alrededor = self.model.grid.get_cell_list_contents((new_position)) # guardo la variable para checar abajo si se puede caminar en esa posicion

        if(semaforo1Derecha == "red" and semaforo2Arriba == "red" and semaforo3Abajo == "red" and semaforo4Izquierda == "red"):
            # Solo se mueven si todos los semaforos están en rojo
            for agents in alrededor:
                if(isinstance(agents, TurnSign) or isinstance(agents, CrossRoad)): # Si estan en el area de caminar, se mueven
                    self.model.grid.move_agent(self, new_position)



class Car(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.termino = False

    def move(self):
        # Obtenemos posicion del carro y los agentes que se encuentran en su grid
        x,y = self.pos
        agent_list = self.model.grid.get_cell_list_contents((x, y))

        # Declarar agentes de semaforos para cada lado. 
        def haySemaforo(list):
            for x in list:
                if(isinstance(x, TrafficLight)):
                    return x

        semaforo1Derecha = haySemaforo(self.model.grid.get_cell_list_contents((11,9)))
        semaforo2Arriba = haySemaforo(self.model.grid.get_cell_list_contents((14,9)))
        semaforo3Abajo = haySemaforo(self.model.grid.get_cell_list_contents((11,12)))
        semaforo4Izquierda = haySemaforo(self.model.grid.get_cell_list_contents((14,12)))


        # Aqui iniciamos los movimientos del carro.
        # Checamos si ya llego a la meta, de lo contrario vamos descartando movimientos, primero checamos que
        # el semaforo este en verde. Despues, dependiendo de si se encuentra en una vuelta, un cruce o tiene un carro adelante
        for agent in agent_list:
            if(isinstance(agent, Finish)):
                print("El auto termino")
                self.model.carrosLlegaron += 1
                self.model.grid.remove_agent(self)
                self.model.schedule.remove(self)
            elif(isinstance(agent, GoRight)):
                agent_listDerechaGR = self.model.grid.get_cell_list_contents((x+1, y))
                for nextAgent in agent_listDerechaGR:
                    if(isinstance(agent, GoRight) and isinstance(nextAgent, Finish)):
                                self.model.grid.move_agent(self, (x + 1, y))
                    elif(isinstance(agent, GoRight) and isinstance(nextAgent, Car)):
                                print("Carro ID: "+ str(self.unique_id)+  "Hay un carro adelante, no puedo avanzar")
                    else:
                        print("Carro ID: "+ str(self.unique_id)+  "Avanzó 1 posición a la derecha")
                        self.model.grid.move_agent(self, (x + 1, y))

            elif(isinstance(agent, RightStreet)):
                agent_listDerecha = self.model.grid.get_cell_list_contents((x+1, y))
                if(semaforo1Derecha.state == "green"):
                    for nextAgent in agent_listDerecha:
                        if(isinstance(agent, RightStreet) and isinstance(nextAgent, Finish)):
                            self.model.grid.move_agent(self, (x + 1, y))
                        elif(isinstance(agent, RightStreet) and isinstance(nextAgent, Car)):
                            print("Carro ID: "+ str(self.unique_id)+  "Hay un carro adelante, no puedo avanzar")

                        elif(isinstance(agent, RightStreet) and isinstance(nextAgent, CrossRoad)): # Si llega a la interseccion y no está para dar vuelta, que siga su camino
                            x = x + 5
                            self.model.grid.move_agent(self, (x, y)) # Se salta los tiles y llega a la calle
                        elif(isinstance(agent, CrossRoad)):
                            x =x + 4
                            self.model.grid.move_agent(self, (x, y)) # Se salta los tiles y llega a la calle


                        elif(isinstance(agent, RightStreet) and isinstance(nextAgent, TurnSign)): # Si llega a la interseccion y detecta el tile de vuelta, este da vuelta. 
                            # checar la casilla a la que va, si hay carro, nel
                            agent_vuelta = self.model.grid.get_cell_list_contents((x+1, y-1))
                            for agent2 in agent_vuelta:
                                if(isinstance(agent2, Car)):
                                    print("Carro ID: "+ str(self.unique_id)+  "Hay un carro en la vuelta, no puedo avanzar")
                                else:
                                    y = y-1
                                    self.model.grid.move_agent(self, (x,y)) # Cambia de direccion por vuelta a la derecha 
                        else:
                            print("Carro ID: "+ str(self.unique_id)+  "Avanzó 1 posición a la derecha")
                            self.model.grid.move_agent(self, (x + 1, y))

            elif(isinstance(agent, GoLeft)):
                agent_listIzquierdaGL = self.model.grid.get_cell_list_contents((x-1, y))
                for nextAgent in agent_listIzquierdaGL:
                    if(isinstance(agent, GoLeft) and isinstance(nextAgent, Finish)):
                                self.model.grid.move_agent(self, (x - 1, y))
                    elif(isinstance(agent, GoLeft) and isinstance(nextAgent, Car)):
                                print("Carro ID: "+ str(self.unique_id)+  "Hay un carro adelante, no puedo avanzar")
                    else:
                        print("Carro ID: "+ str(self.unique_id)+  "Avanzó 1 posición a la izquierda")
                        self.model.grid.move_agent(self, (x - 1, y))

            elif(isinstance(agent, LeftStreet)):
                    agent_listIzquierda = self.model.grid.get_cell_list_contents((x-1, y))
                    if(semaforo4Izquierda.state == "green"):
                        for nextAgent in agent_listIzquierda:
                            if(isinstance(agent, LeftStreet) and isinstance(nextAgent, Finish)):
                                 self.model.grid.move_agent(self, (x - 1, y))
                            elif(isinstance(agent, LeftStreet) and isinstance(nextAgent, Car)):
                                print("Carro ID: "+ str(self.unique_id)+  "Hay un carro adelante, no puedo avanzar")

                            elif(isinstance(agent, LeftStreet) and isinstance(nextAgent, CrossRoad)): # Si llega a la interseccion y no está para dar vuelta, que siga su camino
                                x = x-5
                                self.model.grid.move_agent(self, (x , y)) # Se salta los tiles y llega a la calle
                            elif(isinstance(agent, CrossRoad)):
                                x =x - 4
                                self.model.grid.move_agent(self, (x, y)) # Se salta los tiles y llega a la calle

                            elif(isinstance(agent, LeftStreet) and isinstance(nextAgent, TurnSign)): # Si llega a la interseccion y detecta el tile de vuelta, este da vuelta. 
                                agent_vuelta = self.model.grid.get_cell_list_contents((x-1, y+1))
                                for agent2 in agent_vuelta:
                                    if(isinstance(agent2, Car)):
                                        print("Carro ID: "+ str(self.unique_id)+  "Hay un carro en la vuelta, no puedo avanzar")
                                    else:
                                        y = y+1
                                        self.model.grid.move_agent(self, (x,y)) # Cambia de direccion por vuelta a la derecha 
                                        print("Se movio arriba")
                            else:
                                print("Carro ID: "+ str(self.unique_id)+  "Avanzó 1 posición a la izqiuerda")
                                self.model.grid.move_agent(self, (x - 1, y))

            elif(isinstance(agent, GoUp)):
                agent_listArribaGU = self.model.grid.get_cell_list_contents((x, y+1))
                for nextAgent in agent_listArribaGU:
                    if(isinstance(agent, GoUp) and isinstance(nextAgent, Finish)):
                                self.model.grid.move_agent(self, (x, y+1))
                    elif(isinstance(agent, GoUp) and isinstance(nextAgent, Car)):
                                print("Carro ID: "+ str(self.unique_id)+  "Hay un carro adelante, no puedo avanzar")
                    else:
                        print("Carro ID: "+ str(self.unique_id)+  "Avanzó 1 posición arriba")
                        self.model.grid.move_agent(self, (x, y+1))

            elif(isinstance(agent, UpStreet)):
                    agent_listArriba= self.model.grid.get_cell_list_contents((x, y+1))
                    if(semaforo2Arriba.state == "green"):
                        for nextAgent in agent_listArriba:
                            if(isinstance(agent, UpStreet) and isinstance(nextAgent, Finish)):
                                self.model.grid.move_agent(self, (x, y+1))
                            elif(isinstance(agent, UpStreet) and isinstance(nextAgent, Car)):
                                print("Carro ID: "+ str(self.unique_id)+  "Hay un carro adelante, no puedo avanzar")

                            elif(isinstance(agent, UpStreet) and isinstance(nextAgent, CrossRoad)): # Si llega a la interseccion y no está para dar vuelta, que siga su camino
                                y = y + 5
                                self.model.grid.move_agent(self, (x, y)) # Se salta los tiles y llega a la calle
                            elif(isinstance(agent, CrossRoad)):
                                y = y + 4
                                self.model.grid.move_agent(self, (x, y)) # Se salta los tiles y llega a la calle

                            elif(isinstance(agent, UpStreet) and isinstance(nextAgent, TurnSign)): # Si llega a la interseccion y detecta el tile de vuelta, este da vuelta.
                                agent_vuelta = self.model.grid.get_cell_list_contents((x + 1, y+1))
                                for agent2 in agent_vuelta:
                                    if(isinstance(agent2, Car)):
                                        print("Carro ID: "+ str(self.unique_id)+  "Hay un carro en la vuelta, no puedo avanzar")
                                    else:
                                        x = x +1
                                        self.model.grid.move_agent(self, (x,y)) # Cambia de direccion por vuelta a la derecha
                                
                            else:
                                print("Carro ID: "+ str(self.unique_id)+  "Avanzó 1 posición arriba")
                                self.model.grid.move_agent(self, (x, y+1))

            elif(isinstance(agent, GoDown)):
                agent_listAbajoGD = self.model.grid.get_cell_list_contents((x, y-1))
                for nextAgent in agent_listAbajoGD:
                    if(isinstance(agent, GoDown) and isinstance(nextAgent, Finish)):
                                self.model.grid.move_agent(self, (x , y-1))
                    elif(isinstance(agent, GoDown) and isinstance(nextAgent, Car)):
                                print("Carro ID: "+ str(self.unique_id)+  "Hay un carro adelante, no puedo avanzar")
                    else:
                        print("Carro ID: "+ str(self.unique_id)+  "Avanzó 1 posición abajo")
                        self.model.grid.move_agent(self, (x , y-1))

            elif(isinstance(agent, DownStreet)):
                    agent_listAbajo= self.model.grid.get_cell_list_contents((x, y-1))
                    if(semaforo2Arriba.state == "green"):
                        for nextAgent in agent_listAbajo:
                            if(isinstance(agent, DownStreet) and isinstance(nextAgent, Finish)):
                                self.model.grid.move_agent(self, (x, y+1))
                            elif(isinstance(agent, DownStreet) and isinstance(nextAgent, Car)):
                                print("Carro ID: "+ str(self.unique_id)+  "Hay un carro adelante, no puedo avanzar")

                            elif(isinstance(agent, DownStreet) and isinstance(nextAgent, CrossRoad)): # Si llega a la interseccion y no está para dar vuelta, que siga su camino
                                y = y - 5
                                self.model.grid.move_agent(self, (x, y)) # Se salta los tiles y llega a la calle
                            elif(isinstance(agent, CrossRoad)):
                                y = y - 4
                                self.model.grid.move_agent(self, (x, y)) # Se salta los tiles y llega a la calle

                            elif(isinstance(agent, DownStreet) and isinstance(nextAgent, TurnSign)): # Si llega a la interseccion y detecta el tile de vuelta, este da vuelta.
                                agent_vuelta = self.model.grid.get_cell_list_contents((x - 1, y-1))
                                for agent2 in agent_vuelta:
                                    if(isinstance(agent2, Car)):
                                        print("Carro ID: "+ str(self.unique_id)+  "Hay un carro en la vuelta, no puedo avanzar")
                                    else:
                                        x = x -1
                                        self.model.grid.move_agent(self, (x,y)) # Cambia de direccion por vuelta a la derecha
                                
                            else:
                                print("Carro ID: "+ str(self.unique_id)+  "Avanzó 1 posición abajo")
                                self.model.grid.move_agent(self, (x, y-1))
        
    def step(self):
        self.move()

class TrafficLight(Agent):
    def __init__(self, unique_id, model, duration, estado, funcion):
        super().__init__(unique_id, model)
        self.duration = duration
        self.state = estado
        self.lastPosition = 0
        self.time_remaining = duration[0]
        self.firstState = estado
        self.funcion = funcion
    # Aqui creamos los estados del semaforo 
    def move(self):
        print("Estado del semaforo ID: "+str(self.unique_id) + " " + str(self.state)+ " Duracion: " + str(self.time_remaining) )
        self.time_remaining -= 1 

        if(self.time_remaining <0):
            self.model.done = True
        if(self.time_remaining == 0):
            if(self.state == "green"):
                self.state = "red"
            else: 
                self.state = "green"
            if(self.lastPosition == 0):
                self.lastPosition = 1
            elif(self.lastPosition == 1):
                self.lastPosition = 2
                self.state = "red"
            else:
                self.lastPosition = 0
                self.state = self.firstState
                if(self.funcion != None):
                    self.funcion()
            
            self.time_remaining = self.duration[self.lastPosition]


        
    def step(self):
        self.move()
        
        

# Aqui declaramos a los agentes de identificacion en el grid

class GoRight(Agent): # >
    def __init__(self, unique_id, model ):
        super().__init__(unique_id, model)

class GoLeft(Agent): # <
    def __init__(self, unique_id, model ):
        super().__init__(unique_id, model)

class GoUp(Agent): # u
    def __init__(self, unique_id, model ):
        super().__init__(unique_id, model)


class GoDown(Agent): # d
    def __init__(self, unique_id, model ):
        super().__init__(unique_id, model)


class LeftStreet(Agent): # %
    def __init__(self, unique_id, model ):
        super().__init__(unique_id, model)

    
class RightStreet(Agent): # +
    def __init__(self, unique_id, model ):
        super().__init__(unique_id, model)

class UpStreet(Agent): # #
    def __init__(self, unique_id, model ):
        super().__init__(unique_id, model)

class DownStreet(Agent): # *
    def __init__(self, unique_id, model ):
        super().__init__(unique_id, model)

class TurnSign(Agent): # $
    def __init__(self, unique_id, model ):
        super().__init__(unique_id, model)

class PedestrianWait(Agent): # /
    def __init__(self, unique_id, model ):
        super().__init__(unique_id, model)
    
class CrossRoad(Agent): # -
    def __init__(self, unique_id, model ):
        super().__init__(unique_id, model)

class Finish(Agent): # =
    def __init__(self, unique_id, model ):
        super().__init__(unique_id, model)


class ModelNew(Model):
    def __init__(self, num_cars):
        self.num_cars = num_cars
        self.carrosLlegaron = 0
        self.schedule = RandomActivation(self)
        self.carrosTotales = 0
        self.modelStep = 0
        self.done = False

        """ Esta es una representación del grid creado, con los agentes que identifican las calles y sus orientaciones correspondientes
        """
        """
        self.ejemplo = [
["0","0","0","0","0","0","0","0","0","0","0","*","*","=","=","0","0","0","0","0","0","0","0","0","0","0"],
["0","0","0","0","0","0","0","0","0","0","0","*","*","U","U","0","0","0","0","0","0","0","0","0","0","0"],
["0","0","0","0","0","0","0","0","0","0","0","*","*","U","U","0","0","0","0","0","0","0","0","0","0","0"],
["0","0","0","0","0","0","0","0","0","0","0","*","*","U","U","0","0","0","0","0","0","0","0","0","0","0"],
["0","0","0","0","0","0","0","0","0","0","0","*","*","U","U","0","0","0","0","0","0","0","0","0","0","0"],
["0","0","0","0","0","0","0","0","0","0","0","*","*","U","U","0","0","0","0","0","0","0","0","0","0","0"],
["0","0","0","0","0","0","0","0","0","0","0","*","*","U","U","0","0","0","0","0","0","0","0","0","0","0"],
["0","0","0","0","0","0","0","0","0","0","0","*","*","U","U","0","0","0","0","0","0","0","0","0","0","0"],
["0","0","0","0","0","0","0","0","0","0","/","*","*","U","U","/","0","0","0","0","0","0","0","0","0","0"],
["=","<","<","<","<","<","<","<","<","<","<","$","-","-","$","%","%","%","%","%","%","%","%","%","%","%"],
["=","<","<","<","<","<","<","<","<","<","<","-","-","-","-","%","%","%","%","%","%","%","%","%","%","%"],
["+","+","+","+","+","+","+","+","+","+","+","-","-","-","-",">",">",">",">",">",">",">",">",">",">","="],
["+","+","+","+","+","+","+","+","+","+","+","$","-","-","$",">",">",">",">",">",">",">",">",">",">","="],
["0","0","0","0","0","0","0","0","0","0","/","D","D","#","#","/","0","0","0","0","0","0","0","0","0","0"],
["0","0","0","0","0","0","0","0","0","0","0","D","D","#","#","0","0","0","0","0","0","0","0","0","0","0"],
["0","0","0","0","0","0","0","0","0","0","0","D","D","#","#","0","0","0","0","0","0","0","0","0","0","0"],
["0","0","0","0","0","0","0","0","0","0","0","D","D","#","#","0","0","0","0","0","0","0","0","0","0","0"],
["0","0","0","0","0","0","0","0","0","0","0","D","D","#","#","0","0","0","0","0","0","0","0","0","0","0"],
["0","0","0","0","0","0","0","0","0","0","0","D","D","#","#","0","0","0","0","0","0","0","0","0","0","0"],
["0","0","0","0","0","0","0","0","0","0","0","D","D","#","#","0","0","0","0","0","0","0","0","0","0","0"],
["0","0","0","0","0","0","0","0","0","0","0","D","D","#","#","0","0","0","0","0","0","0","0","0","0","0"],
["0","0","0","0","0","0","0","0","0","0","0","=","=","#","#","0","0","0","0","0","0","0","0","0","0","0"],
]
        
        """

       
        self.grid = MultiGrid(26,22,True)

        # /
        self.grid.place_agent(PedestrianWait(1,self),(10,8))
        self.grid.place_agent(PedestrianWait(2, self),(15,8))
        self.grid.place_agent(PedestrianWait(3, self),(10,13))
        self.grid.place_agent(PedestrianWait(4, self),(15,13))
        # $

        self.grid.place_agent(TurnSign(1, self),(11,9))
        self.grid.place_agent(TurnSign(2, self),(14,9))
        self.grid.place_agent(TurnSign(3, self),(11,12))
        self.grid.place_agent(TurnSign(4, self),(14,12))



        # /
        self.grid.place_agent(CrossRoad(1,self),(12,9))
        self.grid.place_agent(CrossRoad(2, self),(12,10))
        self.grid.place_agent(CrossRoad(3, self),(12,11))
        self.grid.place_agent(CrossRoad(4, self),(12,12))

        self.grid.place_agent(CrossRoad(5,self),(13,9))
        self.grid.place_agent(CrossRoad(6, self),(13,10))
        self.grid.place_agent(CrossRoad(7, self),(13,11))
        self.grid.place_agent(CrossRoad(8, self),(13,12))

        self.grid.place_agent(CrossRoad(9, self),(11,10))
        self.grid.place_agent(CrossRoad(10, self),(11,11))

        self.grid.place_agent(CrossRoad(11, self),(14,10))
        self.grid.place_agent(CrossRoad(12, self),(14,11))

        # = 

        self.grid.place_agent(Finish(1, self),(11,0))
        self.grid.place_agent(Finish(2, self),(12,0))

        self.grid.place_agent(Finish(3, self),(13, 21))
        self.grid.place_agent(Finish(4, self),(14,21))

        self.grid.place_agent(Finish(5, self),(0,11))
        self.grid.place_agent(Finish(6, self),(0,12))

        self.grid.place_agent(Finish(7, self),(25,9))
        self.grid.place_agent(Finish(8, self),(25,10))

        

         # +
        self.grid.place_agent(RightStreet(1, self),(0,9))
        self.grid.place_agent(RightStreet(2, self),(1,9))
        self.grid.place_agent(RightStreet(3, self),(2,9))
        self.grid.place_agent(RightStreet(4, self),(3,9))
        self.grid.place_agent(RightStreet(5, self),(4,9))
        self.grid.place_agent(RightStreet(6, self),(5,9))
        self.grid.place_agent(RightStreet(7, self),(6,9))
        self.grid.place_agent(RightStreet(8, self),(7,9))
        self.grid.place_agent(RightStreet(9, self),(8,9))
        self.grid.place_agent(RightStreet(10, self),(9,9))
        self.grid.place_agent(RightStreet(11, self),(10,9))
     
        self.grid.place_agent(RightStreet(12, self),(0,10))
        self.grid.place_agent(RightStreet(13, self),(1,10))
        self.grid.place_agent(RightStreet(14, self),(2,10))
        self.grid.place_agent(RightStreet(15, self),(3,10))
        self.grid.place_agent(RightStreet(16, self),(4,10))
        self.grid.place_agent(RightStreet(17, self),(5,10))
        self.grid.place_agent(RightStreet(18, self),(6,10))
        self.grid.place_agent(RightStreet(19, self),(7,10))
        self.grid.place_agent(RightStreet(20, self),(8,10))
        self.grid.place_agent(RightStreet(21, self),(9,10))
        self.grid.place_agent(RightStreet(22, self),(10,10))

    

        #>
        self.grid.place_agent(GoRight(1, self),(15,9))
        self.grid.place_agent(GoRight(3, self),(16,9))
        self.grid.place_agent(GoRight(4, self),(17,9))
        self.grid.place_agent(GoRight(5, self),(18,9))
        self.grid.place_agent(GoRight(6, self),(19,9))
        self.grid.place_agent(GoRight(7, self),(20,9))
        self.grid.place_agent(GoRight(8, self),(21,9))
        self.grid.place_agent(GoRight(9, self),(22,9))
        self.grid.place_agent(GoRight(10, self),(23,9))
        self.grid.place_agent(GoRight(11, self),(24,9))


        self.grid.place_agent(GoRight(12, self),(15,10))
        self.grid.place_agent(GoRight(13, self),(16,10))
        self.grid.place_agent(GoRight(14, self),(17,10))
        self.grid.place_agent(GoRight(15, self),(18,10))
        self.grid.place_agent(GoRight(16, self),(19,10))
        self.grid.place_agent(GoRight(17, self),(20,10))
        self.grid.place_agent(GoRight(18, self),(21,10))
        self.grid.place_agent(GoRight(19, self),(22,10))
        self.grid.place_agent(GoRight(20, self),(23,10))
        self.grid.place_agent(GoRight(21, self),(24,10))


        # %

        self.grid.place_agent(LeftStreet(2, self),(15,11))
        self.grid.place_agent(LeftStreet(3, self),(16,11))
        self.grid.place_agent(LeftStreet(4, self),(17,11))
        self.grid.place_agent(LeftStreet(5, self),(18,11))
        self.grid.place_agent(LeftStreet(6, self),(19,11))
        self.grid.place_agent(LeftStreet(7, self),(20,11))
        self.grid.place_agent(LeftStreet(8, self),(21,11))
        self.grid.place_agent(LeftStreet(9, self),(22,11))
        self.grid.place_agent(LeftStreet(10, self),(23,11))
        self.grid.place_agent(LeftStreet(11, self),(24,11))
        self.grid.place_agent(LeftStreet(12, self),(25,11))

        self.grid.place_agent(LeftStreet(13, self),(15,12))
        self.grid.place_agent(LeftStreet(14, self),(16,12))
        self.grid.place_agent(LeftStreet(15, self),(17,12))
        self.grid.place_agent(LeftStreet(16, self),(18,12))
        self.grid.place_agent(LeftStreet(17, self),(19,12))
        self.grid.place_agent(LeftStreet(18, self),(20,12))
        self.grid.place_agent(LeftStreet(19, self),(21,12))
        self.grid.place_agent(LeftStreet(20, self),(22,12))
        self.grid.place_agent(LeftStreet(21, self),(23,12))
        self.grid.place_agent(LeftStreet(22, self),(24,12))
        self.grid.place_agent(LeftStreet(23, self),(25,12))
    

        # <
        self.grid.place_agent(GoLeft(2, self),(1,11))
        self.grid.place_agent(GoLeft(3, self),(2,11))
        self.grid.place_agent(GoLeft(4, self),(3,11))
        self.grid.place_agent(GoLeft(5, self),(4,11))
        self.grid.place_agent(GoLeft(6, self),(5,11))
        self.grid.place_agent(GoLeft(7, self),(6,11))
        self.grid.place_agent(GoLeft(8, self),(7,11))
        self.grid.place_agent(GoLeft(9, self),(8,11))
        self.grid.place_agent(GoLeft(10, self),(9,11))
        self.grid.place_agent(GoLeft(11, self),(10,11))

        self.grid.place_agent(GoLeft(12, self),(1,12))
        self.grid.place_agent(GoLeft(13, self),(2,12))
        self.grid.place_agent(GoLeft(14, self),(3,12))
        self.grid.place_agent(GoLeft(15, self),(4,12))
        self.grid.place_agent(GoLeft(16, self),(5,12))
        self.grid.place_agent(GoLeft(17, self),(6,12))
        self.grid.place_agent(GoLeft(18, self),(7,12))
        self.grid.place_agent(GoLeft(19, self),(8,12))
        self.grid.place_agent(GoLeft(20, self),(9,12))
        self.grid.place_agent(GoLeft(21, self),(10,12))


        # #
        self.grid.place_agent(UpStreet(2, self),(13,0))
        self.grid.place_agent(UpStreet(3, self),(13,1))
        self.grid.place_agent(UpStreet(4, self),(13,2))
        self.grid.place_agent(UpStreet(5, self),(13,3))
        self.grid.place_agent(UpStreet(6, self),(13,4))
        self.grid.place_agent(UpStreet(7, self),(13,5))
        self.grid.place_agent(UpStreet(8, self),(13,6))
        self.grid.place_agent(UpStreet(9, self),(13,7))
        self.grid.place_agent(UpStreet(10, self),(13,8))

        self.grid.place_agent(UpStreet(11, self),(14,0))
        self.grid.place_agent(UpStreet(12, self),(14,1))
        self.grid.place_agent(UpStreet(13, self),(14,2))
        self.grid.place_agent(UpStreet(14, self),(14,3))
        self.grid.place_agent(UpStreet(15, self),(14,4))
        self.grid.place_agent(UpStreet(16, self),(14,5))
        self.grid.place_agent(UpStreet(17, self),(14,6))
        self.grid.place_agent(UpStreet(18, self),(14,7))
        self.grid.place_agent(UpStreet(19, self),(14,8))
    

        # U

        self.grid.place_agent(GoUp(11, self),(14,13))
        self.grid.place_agent(GoUp(12, self),(14,14))
        self.grid.place_agent(GoUp(13, self),(14,15))
        self.grid.place_agent(GoUp(14, self),(14,16))
        self.grid.place_agent(GoUp(15, self),(14,17))
        self.grid.place_agent(GoUp(16, self),(14,18))
        self.grid.place_agent(GoUp(17, self),(14,19))
        self.grid.place_agent(GoUp(18, self),(14,20))

        self.grid.place_agent(GoUp(11, self),(13,13))
        self.grid.place_agent(GoUp(12, self),(13,14))
        self.grid.place_agent(GoUp(13, self),(13,15))
        self.grid.place_agent(GoUp(14, self),(13,16))
        self.grid.place_agent(GoUp(15, self),(13,17))
        self.grid.place_agent(GoUp(16, self),(13,18))
        self.grid.place_agent(GoUp(17, self),(13,19))
        self.grid.place_agent(GoUp(18, self),(13,20))


         # *

        self.grid.place_agent(DownStreet(11, self),(11,13))
        self.grid.place_agent(DownStreet(12, self),(11,14))
        self.grid.place_agent(DownStreet(13, self),(11,15))
        self.grid.place_agent(DownStreet(14, self),(11,16))
        self.grid.place_agent(DownStreet(15, self),(11,17))
        self.grid.place_agent(DownStreet(16, self),(11,18))
        self.grid.place_agent(DownStreet(17, self),(11,19))
        self.grid.place_agent(DownStreet(18, self),(11,20))
        self.grid.place_agent(DownStreet(18, self),(11,21))

        self.grid.place_agent(DownStreet(11, self),(12,13))
        self.grid.place_agent(DownStreet(12, self),(12,14))
        self.grid.place_agent(DownStreet(13, self),(12,15))
        self.grid.place_agent(DownStreet(14, self),(12,16))
        self.grid.place_agent(DownStreet(15, self),(12,17))
        self.grid.place_agent(DownStreet(16, self),(12,18))
        self.grid.place_agent(DownStreet(17, self),(12,19))
        self.grid.place_agent(DownStreet(18, self),(12,20))
        self.grid.place_agent(DownStreet(18, self),(12,21))
        
   
  

        # D
        self.grid.place_agent(GoDown(1, self),(11,1))
        self.grid.place_agent(GoDown(2, self),(11,2))
        self.grid.place_agent(GoDown(3, self),(11,3))
        self.grid.place_agent(GoDown(4, self),(11,4))
        self.grid.place_agent(GoDown(5, self),(11,5))
        self.grid.place_agent(GoDown(6, self),(11,6))
        self.grid.place_agent(GoDown(7, self),(11,7))
        self.grid.place_agent(GoDown(8, self),(11,8))

        self.grid.place_agent(GoDown(9, self),(12,1))
        self.grid.place_agent(GoDown(10, self),(12,2))
        self.grid.place_agent(GoDown(11, self),(12,3))
        self.grid.place_agent(GoDown(12, self),(12,4))
        self.grid.place_agent(GoDown(13, self),(12,5))
        self.grid.place_agent(GoDown(14, self),(12,6))
        self.grid.place_agent(GoDown(15, self),(12,7))
        self.grid.place_agent(GoDown(16, self),(12,8))

     
        
        # Crear carros
      
        for i in range(self.num_cars):
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            for c in self.grid.get_cell_list_contents((x,y)):
                if(isinstance(c, Car)):
                    print("Carro ya ahí")
                elif(isinstance(c, RightStreet) or isinstance(c, LeftStreet) or isinstance(c, UpStreet) or isinstance(c, DownStreet) or isinstance(c, GoRight)
                     or isinstance(c, GoLeft) or isinstance(c, GoUp) or isinstance(c, GoDown)):
                    print("Carro colocado")
                    car = Car("car"+str(i+4), self)
                    self.grid.place_agent(car, (x, y))
                    self.schedule.add(car)
                    self.carrosTotales +=1

  
        

        def semaforosFun():
            def restart():
                for x in range(26):
                    for y in range(22):
                        agent = self.grid.get_cell_list_contents((x,y))
                        for semf in agent:
                            if(isinstance(semf, TrafficLight)):
                                self.grid.remove_agent(semf)
                                self.schedule.remove(semf)
                semaforosFun()

            def hay(list, tipo):
                for x in list:
                    if(isinstance(x, tipo)):
                        return True
                return False
        
            def contadorCarros(calle):
                contador = 0
                for x in range(26):
                    for y in range(22):
                        agent = self.grid.get_cell_list_contents((x,y))
                        if(hay(agent, Car) and hay(agent, calle)):
                            contador += 1
                return contador
        
            carrosX = contadorCarros(LeftStreet) + contadorCarros(RightStreet)

            carrosY = contadorCarros(UpStreet) + contadorCarros(DownStreet)

            self.carrosTotales = carrosX + carrosY
            def TimeXY(cuentaX, cuentaY, tiempoTotal):
                mayor = 0
                print("Cuenta x"+str(cuentaX))
                print("Cuenta y"+str(cuentaY))
                if(cuentaX> cuentaY):
                    mayor = cuentaX
                else: 
                    mayor = cuentaY
                print("Mayor"+ str(mayor))
                total = cuentaX+cuentaY
                if(total != 0): 
                    verde = math.ceil((mayor/total) * tiempoTotal)
                    rojo = tiempoTotal - verde
                    print("Verde" + str(verde))
                    return (verde, rojo)
                else:
                    return (0,0)

            green = "green"
            red = "red"
            estadoX = ""
            estadoY = ""
            if(carrosX> carrosY):
                estadoX = green
                estadoY = red
            else:
                estadoX = red
                estadoY = green

            (duracionVerde, duracionRojo) = TimeXY(carrosX, carrosY, 15)
            duracionPeaton = 10

            
                


            # Colocar semáforos 
            semaforo1 = TrafficLight(1, self, [duracionVerde,duracionRojo, duracionPeaton] , estadoX, restart)
            semaforo2 = TrafficLight(2, self, [duracionVerde,duracionRojo, duracionPeaton] , estadoY, None)
            semaforo3 = TrafficLight(3, self, [duracionVerde,duracionRojo, duracionPeaton] ,estadoY, None)
            semaforo4 = TrafficLight(4, self, [duracionVerde,duracionRojo , duracionPeaton] ,estadoX, None)

            self.grid.place_agent(semaforo1,(11,9))
            self.grid.place_agent(semaforo2,(14,9))
            self.grid.place_agent(semaforo3,(11,12))
            self.grid.place_agent(semaforo4,(14,12))
            self.schedule.add(semaforo1)
            self.schedule.add(semaforo2)
            self.schedule.add(semaforo3)
            self.schedule.add(semaforo4)

            

    

            print("Duracion verde primero:" + str(duracionVerde))
            print("Duracion rojo primero:" + str(duracionRojo))
                
            # Contar carros y poner fórmula del tiempo para cuando transcurra x numero de steps y se reinicie 
            
            # Add the agent to a random grid cell
            
        semaforosFun() # Si se prueba con semaforos normales, comentar estar parte 

        # Probar con la simulacion con semaforos normales 
        """
        semaforo1 = TrafficLight(1, self, [7,7, 8] , "green", None)
        semaforo2 = TrafficLight(2, self, [7,7, 8] , "red", None)
        semaforo3 = TrafficLight(3, self, [7,7, 8] ,"red", None)
        semaforo4 = TrafficLight(4, self, [7,7 , 8] ,"green", None)

        self.grid.place_agent(semaforo1,(11,9))
        self.grid.place_agent(semaforo2,(14,9))
        self.grid.place_agent(semaforo3,(11,12))
        self.grid.place_agent(semaforo4,(14,12))
        self.schedule.add(semaforo1)
        self.schedule.add(semaforo2)
        self.schedule.add(semaforo3)
        self.schedule.add(semaforo4)
        """

    def step(self):
        def hay(list, tipo):
            for x in list:
                if(isinstance(x, tipo)):
                    return True
            return False 
        
        def pintar(lista):
            
            if(hay(lista, Car)):
                return "@"
            if(hay(lista, Finish)):
                return "="
            if(hay(lista, LeftStreet)):
                return "%"
            if(hay(lista, RightStreet)):
                return "+"
            if(hay(lista, UpStreet)):
                return "#"
            if(hay(lista, DownStreet)):
                return "*"
            if(hay(lista, GoLeft)):
                return "<"
            if(hay(lista, GoRight)):
                return ">"
            if(hay(lista, GoUp)):
                return "U"
            if(hay(lista, GoDown)):
                return "D"
            if(hay(lista, CrossRoad)):
                return "-"
            if(hay(lista, TurnSign)):
                return "$"
            return " "

        self.schedule.step()
        #os.system("cls")
        #for y in range(25):

        self.modelStep +=1
        for y in range(21,-1,-1):
            string = ""
            for x in range(0, 26,1):
            #for x in range(25):  
                lista = self.grid.get_cell_list_contents((x,y))
                size = len(lista)
                string = string + pintar(lista)
            print(string)
  

# Parámetros de la simulación
num_cars = 60
model = ModelNew(num_cars)

# Ejecutar la simulación
for _ in range(50):
    time.sleep(1)  # Ejecutar 100 pasos de tiempo // Habilitar esto para ver la impresion y movimientos de los agentes
    model.step()
    if(model.carrosLlegaron == model.carrosTotales or model.done == True):
        break

print("Totales: " + str(model.carrosTotales))
print("Llegaron: " + str(model.carrosLlegaron))
print("En un total de: " + str(model.modelStep) + "Steps")