from mesa import Agent, Model
from mesa.model import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import random


class Pedestrian(Agent): 
    def __init__(self, unique_id, model ):
        super().__init__(unique_id, model)
    
    def move(self):
        x,y = self.pos

        semaforo1Derecha = self.model.get_cell_list_contents((6,6))
        semaforo2Arriba = self.model.get_cell_list_contents((9,6))
        semaforo3Abajo = self.model.get_cell_list_contents((6,9))
        semaforo4Izquierda = self.model.get_cell_list_contents((9,9))

        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=False) # obtengo sus posiciones vecinas 
        new_position = random.choice(possible_steps) # consigo una posicion random 
        alrededor = self.model.get_cell_list_contents((new_position)) # guardo la variable para checar abajo si se puede caminar en esa posicion

        if(semaforo1Derecha == "red" and semaforo2Arriba == "red" and semaforo3Abajo == "red" and semaforo4Izquierda == "red"):
            # Solo se mueven si todos los semaforos están en rojo
            for agents in alrededor:
                if(isinstance(agents, TurnSign) or isinstance(agents, CrossRoad)): # Si estan en el area de caminar, se mueven
                    self.model.grid.move_agent(self, new_position)



class Car(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def move(self):
        # Mover el carro en la dirección actual
        
        x, y = self.pos
        agent_list = self.model.get_cell_list_contents((x, y))
        agent_listDerecha = self.model.get_cell_list_contents((x+1, y))
        agent_listIzquierda = self.model.get_cell_list_contents((x-1, y))
        agent_listArriba = self.model.get_cell_list_contents((x, y+1))
        agent_listAbajo  = self.model.get_cell_list_contents((x, y-1))


        # Declarar agentes de semaforos para cada lado. 

        semaforo1Derecha = self.model.get_cell_list_contents((6,6))
        semaforo2Arriba = self.model.get_cell_list_contents((9,6))
        semaforo3Abajo = self.model.get_cell_list_contents((6,9))
        semaforo4Izquierda = self.model.get_cell_list_contents((9,9))

        for agent in agent_list:
            for nextAgent in agent_listDerecha:
                if(semaforo1Derecha.state == "green"): # Si esta verde, puede buscar avanzar

                    if(isinstance(agent, RightStreet) and isinstance(nextAgent, Car)): # Si hay carro adelante, no avanza
                        print("Carro adelante, no puedo avanzar")
                    elif(isinstance(agent, RightStreet) and isinstance(nextAgent, CrossRoad)): # Si llega a la interseccion y no está para dar vuelta, que siga su camino
                        self.model.grid.move_agent(self, (x + 5, y)) # Se salta los tiles y llega a la calle

                    elif(isinstance(agent, RightStreet) and isinstance(nextAgent, TurnSign)): # Si llega a la interseccion y detecta el tile de vuelta, este da vuelta. 
                        self.model.grid.move_agent(self, (x + 1, y-1)) # Cambia de direccion por vuelta a la derecha 
                    else:
                        print("Carro avanzó 1 posición a la derecha")
                        self.model.grid.move_agent(self, (x + 1, y))

                
            
            for nextAgent in agent_listIzquierda:
                if(semaforo4Izquierda.state == "green"): # Si esta verde, puede buscar avanzar
                    if(isinstance(agent, LeftStreet) and isinstance(nextAgent, Car)): # Si hay carro adelante, no avanza
                        print("Carro adelante, no puedo avanzar")

                    elif(isinstance(agent, LeftStreet) and isinstance(nextAgent, CrossRoad)): # Si llega a la interseccion y no está para dar vuelta, que siga su camino
                        self.model.grid.move_agent(self, (x - 5, y)) # Se salta los tiles y llega a la calle

                    elif(isinstance(agent, LeftStreet) and isinstance(nextAgent, TurnSign)): # Si llega a la interseccion y detecta el tile de vuelta, este da vuelta. 
                        self.model.grid.move_agent(self, (x - 1, y+1)) # Cambia de direccion por vuelta a la derecha 
                    else:
                        print("Carro avanzó 1 posición a la izquierda")
                        self.model.grid.move_agent(self, (x -1, y))


            for nextAgent in agent_listArriba:
                if(semaforo2Arriba.state == "green"): # Si esta verde, puede buscar avanzar

                    if(isinstance(agent, UpStreet) and isinstance(nextAgent, Car)): # Si hay carro adelante, no avanza
                        print("Carro adelante, no puedo avanzar")
                    
                    elif(isinstance(agent, UpStreet) and isinstance(nextAgent, CrossRoad)): # Si llega a la interseccion y no está para dar vuelta, que siga su camino
                        self.model.grid.move_agent(self, (x, y+5)) # Se salta los tiles y llega a la calle

                    elif(isinstance(agent, UpStreet) and isinstance(nextAgent, TurnSign)): # Si llega a la interseccion y detecta el tile de vuelta, este da vuelta. 
                        self.model.grid.move_agent(self, (x +1, y+1)) # Cambia de direccion por vuelta a la derecha 

                    else:
                        print("Carro avanzó 1 posición arriba")
                        self.model.grid.move_agent(self, (x , y+1))

            for nextAgent in agent_listAbajo:
                if(semaforo3Abajo.state == "green"): # Si esta verde, puede buscar avanzar

                    if(isinstance(agent, DownStreet) and isinstance(nextAgent, Car)): # Si hay carro adelante, no avanza
                        print("Carro adelante, no puedo avanzar")

                    elif(isinstance(agent, DownStreet) and isinstance(nextAgent, CrossRoad)): # Si llega a la interseccion y no está para dar vuelta, que siga su camino
                        self.model.grid.move_agent(self, (x, y-5)) # Se salta los tiles y llega a la calle

                    elif(isinstance(agent, DownStreet) and isinstance(nextAgent, TurnSign)): # Si llega a la interseccion y detecta el tile de vuelta, este da vuelta. 
                        self.model.grid.move_agent(self, (x - 1, y-1)) # Cambia de direccion por vuelta a la derecha 

                    else:
                        print("Carro avanzó 1 posición abajo")
                        self.model.grid.move_agent(self, (x, y-1))

class TrafficLight(Agent):
    def __init__(self, unique_id, model, green_duration, red_duration, estado):
        super().__init__(unique_id, model)
        self.green_duration = green_duration
        self.red_duration = red_duration
        self.state = estado
        self.time_remaining = green_duration
        
    def step(self):
        if self.state == "green":
            self.time_remaining -= 1 
            if self.time_remaining == 0:
                self.state = "yellow"
            elif self.time_remaining == 0:
                self.state = "red"
                self.time_remaining = self.red_duration
        else:
            self.time_remaining -= 1
            if self.time_remaining == 0:
                self.state = "green"
                self.time_remaining = self.green_duration




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
        self.schedule = RandomActivation(self)

        """ Esta es una representación del grid creado, con los agentes que identifican las calles y sus orientaciones correspondientes
        ejemplo = [
            [ "0","0","0","0","0","0","*","*","=","=","0","0","0","0","0","0"],

            [ "0","0","0","0","0","0","*","*","#","#","0","0","0","0","0","0"],

            [ "0","0","0","0","0","0","*","*","#","#","0","0","0","0","0","0"],

            ["0", "0","0","0","0","0","*","*","#","#","0","0","0","0","0","0"],

            ["0", "0","0","0","0","0","*","*","#","#","0","0","0","0","0","0"],
            
            ["0", "0","0","0","0","/","*","*","#","#","/","0","0","0","0","0"],

            ["=", "%","%","%","%","%","$","-","-","$","%","%","%","%","%","%"],

            ["=", "%","%","%","%","%","-","-","-","-","%","%","%","%","%","%"],

            ["+", "+","+","+","+","+","-","-","-","-","+","+","+","+","+","="],

            ["+", "+","+","+","+","+","$","-","-","$","+","+","+","+","+","="],

            ["0", "0","0","0","0","/","*","*","#","#","/","0","0","0","0","0"],

            ["0", "0","0","0","0","0","*","*","#","#","0","0","0","0","0","0"],

            ["0", "0","0","0","0","0","*","*","#","#","0","0","0","0","0","0"],

            ["0", "0","0","0","0","0","*","*","#","#","0","0","0","0","0","0"],

            ["0", "0","0","0","0","0","*","*","#","#","0","0","0","0","0","0"],
            
            ["0", "0","0","0","0","0","=","=","#","#","0","0","0","0","0","0"]
        ]
        """
        self.grid = MultiGrid(16,16,True)


        # /

        self.grid.place_agent(PedestrianWait(1,self),(5,5))
        self.grid.place_agent(PedestrianWait(2, self),(10,5))
        self.grid.place_agent(PedestrianWait(3, self),(5,10))
        self.grid.place_agent(PedestrianWait(4, self),(10,10))
        # $

        self.grid.place_agent(TurnSign(1, self),(6,6))
        self.grid.place_agent(TurnSign(2, self),(9,6))
        self.grid.place_agent(TurnSign(3, self),(6,9))
        self.grid.place_agent(TurnSign(4, self),(9,9))



        # /
        self.grid.place_agent(CrossRoad(1,self),(7,6))
        self.grid.place_agent(CrossRoad(2, self),(7,7))
        self.grid.place_agent(CrossRoad(3, self),(7,8))
        self.grid.place_agent(CrossRoad(4, self),(7,9))

        self.grid.place_agent(CrossRoad(5, self),(8,6))
        self.grid.place_agent(CrossRoad(6, self),(8,7))
        self.grid.place_agent(CrossRoad(7, self),(8,8))
        self.grid.place_agent(CrossRoad(8, self),(8,9))

        self.grid.place_agent(CrossRoad(9, self),(6,7))
        self.grid.place_agent(CrossRoad(10, self),(6,8))

        self.grid.place_agent(CrossRoad(11, self),(9,7))
        self.grid.place_agent(CrossRoad(12, self),(9,8))

        # = 

        self.grid.place_agent(Finish(1, self),(6,0))
        self.grid.place_agent(Finish(2, self),(7,0))

        self.grid.place_agent(Finish(3, self),(15,6))
        self.grid.place_agent(Finish(4, self),(15,7))

        self.grid.place_agent(Finish(5, self),(8,15))
        self.grid.place_agent(Finish(6, self),(9,15))

        self.grid.place_agent(Finish(7, self),(0,8))
        self.grid.place_agent(Finish(8, self),(0,9))

        # %

        self.grid.place_agent(LeftStreet(1, self),(15,9))
        self.grid.place_agent(LeftStreet(2, self),(14,9))
        self.grid.place_agent(LeftStreet(3, self),(13,9))
        self.grid.place_agent(LeftStreet(4, self),(12,9))
        self.grid.place_agent(LeftStreet(5, self),(11,9))
        self.grid.place_agent(LeftStreet(6, self),(10,9))

        self.grid.place_agent(LeftStreet(7, self),(15,8))
        self.grid.place_agent(LeftStreet(8, self),(14,8))
        self.grid.place_agent(LeftStreet(9, self),(13,8))
        self.grid.place_agent(LeftStreet(10, self),(12,8))
        self.grid.place_agent(LeftStreet(11, self),(11,8))
        self.grid.place_agent(LeftStreet(12, self),(10,8))

        self.grid.place_agent(LeftStreet(13, self),(1,9))
        self.grid.place_agent(LeftStreet(14, self),(2,9))
        self.grid.place_agent(LeftStreet(15, self),(3,9))
        self.grid.place_agent(LeftStreet(16, self),(4,9))
        self.grid.place_agent(LeftStreet(17, self),(5,9))
        
        self.grid.place_agent(LeftStreet(18, self),(1,8))
        self.grid.place_agent(LeftStreet(19, self),(2,8))
        self.grid.place_agent(LeftStreet(20, self),(3,8))
        self.grid.place_agent(LeftStreet(21, self),(4,8))
        self.grid.place_agent(LeftStreet(22, self),(5,8))

         # +

        self.grid.place_agent(RightStreet(1, self),(0,6))
        self.grid.place_agent(RightStreet(2, self),(1,6))
        self.grid.place_agent(RightStreet(3, self),(2,6))
        self.grid.place_agent(RightStreet(4, self),(3,6))
        self.grid.place_agent(RightStreet(5, self),(4,6))
        self.grid.place_agent(RightStreet(6, self),(5,6))

        self.grid.place_agent(RightStreet(7, self),(14,6))
        self.grid.place_agent(RightStreet(8, self),(13,6))
        self.grid.place_agent(RightStreet(9, self),(12,6))
        self.grid.place_agent(RightStreet(10, self),(11,6))
        self.grid.place_agent(RightStreet(11, self),(10,6))

        self.grid.place_agent(RightStreet(12, self),(14,7))
        self.grid.place_agent(RightStreet(13, self),(13,7))
        self.grid.place_agent(RightStreet(14, self),(12,7))
        self.grid.place_agent(RightStreet(15, self),(11,7))
        self.grid.place_agent(RightStreet(16, self),(10,7))

        self.grid.place_agent(RightStreet(17, self),(0,7))
        self.grid.place_agent(RightStreet(18, self),(1,7))
        self.grid.place_agent(RightStreet(19, self),(2,7))
        self.grid.place_agent(RightStreet(20, self),(3,7))
        self.grid.place_agent(RightStreet(21, self),(4,7))
        self.grid.place_agent(RightStreet(22, self),(5,7))


         # #

        self.grid.place_agent(UpStreet(1, self),(8,0))
        self.grid.place_agent(UpStreet(2, self),(8,1))
        self.grid.place_agent(UpStreet(3, self),(8,2))
        self.grid.place_agent(UpStreet(4, self),(8,3))
        self.grid.place_agent(UpStreet(5, self),(8,4))
        self.grid.place_agent(UpStreet(6, self),(8,5))

        self.grid.place_agent(UpStreet(7, self),(8,10))
        self.grid.place_agent(UpStreet(8, self),(8,11))
        self.grid.place_agent(UpStreet(9, self),(8,12))
        self.grid.place_agent(UpStreet(10, self),(8,13))
        self.grid.place_agent(UpStreet(11, self),(8,14))


        self.grid.place_agent(UpStreet(12, self),(9,0))
        self.grid.place_agent(UpStreet(13, self),(9,1))
        self.grid.place_agent(UpStreet(14, self),(9,2))
        self.grid.place_agent(UpStreet(15, self),(9,3))
        self.grid.place_agent(UpStreet(16, self),(9,4))
        self.grid.place_agent(UpStreet(17, self),(9,5))

        self.grid.place_agent(UpStreet(18, self),(9,10))
        self.grid.place_agent(UpStreet(19, self),(9,11))
        self.grid.place_agent(UpStreet(20, self),(9,12))
        self.grid.place_agent(UpStreet(21, self),(9,13))
        self.grid.place_agent(UpStreet(22, self),(9,14))


         # *

        self.grid.place_agent(DownStreet(1, self),(6,15))
        self.grid.place_agent(DownStreet(2, self),(6,14))
        self.grid.place_agent(DownStreet(3, self),(6,13))
        self.grid.place_agent(DownStreet(4, self),(6,12))
        self.grid.place_agent(DownStreet(5, self),(6,11))
        self.grid.place_agent(DownStreet(6, self),(6,10))

        self.grid.place_agent(DownStreet(7, self),(6,1))
        self.grid.place_agent(DownStreet(8, self),(6,2))
        self.grid.place_agent(DownStreet(9, self),(6,3))
        self.grid.place_agent(DownStreet(10, self),(6,4))
        self.grid.place_agent(DownStreet(11, self),(6,5))

        self.grid.place_agent(DownStreet(12, self),(7,15))
        self.grid.place_agent(DownStreet(13, self),(7,14))
        self.grid.place_agent(DownStreet(14, self),(7,13))
        self.grid.place_agent(DownStreet(15, self),(7,12))
        self.grid.place_agent(DownStreet(16, self),(7,11))
        self.grid.place_agent(DownStreet(17, self),(7,10))

        self.grid.place_agent(DownStreet(18, self),(7,1))
        self.grid.place_agent(DownStreet(19, self),(7,2))
        self.grid.place_agent(DownStreet(20, self),(7,3))
        self.grid.place_agent(DownStreet(21, self),(7,4))
        self.grid.place_agent(DownStreet(22, self),(7,5))

        estadoX = "red"
        estadoY = "red"
        duracionVerde = 300 # Agregar formula
        duracionRojo =  200 # Agregar formula 
        # Colocar semáforos 
        semaforo1 = TrafficLight(1, self, duracionVerde,duracionRojo , estadoX)
        semaforo2 = TrafficLight(2, self, duracionVerde,duracionRojo , estadoY)
        semaforo3 = TrafficLight(3, self, duracionVerde,duracionRojo ,estadoY)
        semaforo4 = TrafficLight(4, self, duracionVerde,duracionRojo ,estadoX)

        self.grid.place_agent(semaforo1,(6,6))
        self.grid.place_agent(semaforo2,(9,6))
        self.grid.place_agent(semaforo3,(6,9))
        self.grid.place_agent(semaforo4,(9,9))
        
        # Crear carros
        for i in range(self.num_cars):
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            for c in self.grid.get_cell_list_contents((x,y)):
                if(isinstance(c, Car)):
                    print("Carro ya ahí")
                elif(isinstance(c, RightStreet) or isinstance(c, LeftStreet) or isinstance(c, UpStreet) or isinstance(c, DownStreet)):
                    print("Carro colocado")
                    car = Car(i + 1, self)
                    self.grid.place_agent(car, (x, y))
                    self.schedule.add(car)

                
            # Contar carros y poner fórmula del tiempo para cuando transcurra x numero de steps y se reinicie 
            
            # Add the agent to a random grid cell
            
            
    def step(self):
        self.schedule.step()

# Parámetros de la simulación
num_cars = 100
model = ModelNew(num_cars)

# Ejecutar la simulación
for _ in range(100):  # Ejecutar 100 pasos de tiempo
    model.step()
