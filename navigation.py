import formation

#(self, x, y, z, droneSayisi, aralarindakiMesafe, formation_type):
class Navigation:
    def __init__(self, target_x, target_y, target_z, formation):
        self.target_x = target_x
        self.target_y = target_y
        self.target_z = target_z
        self.formation = formation 
        self.new_positions = []  
        print(f"Hedef: {self.target_x}, {self.target_y}, {self.target_z}")


    def goTo(self):
        for drone_position in self.formation.get_formation():
            delta_x = self.target_x - self.formation.x
            delta_y = self.target_y - self.formation.y
            delta_z = self.target_z - self.formation.z
            new_x = drone_position[0] + delta_x
            new_y = drone_position[1] + delta_y
            new_z = drone_position[2] + delta_z
            self.new_positions.append([new_x, new_y, new_z])        
        return self.new_positions



# test
#formation_instance = formation.Formation(0, 0, 0, 5, 10, "arrow")
#navigation = Navigation(100, 50, 30, formation_instance)

#new_positions = navigation.goTo()
#print("Drone'ların yeni pozisyonları:", new_positions)
     


    
