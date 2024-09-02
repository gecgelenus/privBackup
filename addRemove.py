import formation

class Navigation:
    def __init__(self, target_x, target_y, target_z, formation):
        self.target_x = target_x
        self.target_y = target_y
        self.target_z = target_z
        self.formation = formation 
        self.new_positions = []  
        self.home_position = [0, 0, 0] 
    
    def goTo(self):
        self.new_positions = []
        for drone_position in self.formation.get_formation():
            delta_x = self.target_x - self.formation.x
            delta_y = self.target_y - self.formation.y
            delta_z = self.target_z - self.formation.z
            new_x = drone_position[0] + delta_x
            new_y = drone_position[1] + delta_y
            new_z = drone_position[2] + delta_z
            self.new_positions.append([new_x, new_y, new_z])
        
        return self.new_positions
    
    def sendDroneHome(self, drone_index):
        if 0 <= drone_index < len(self.formation.formation):
            home_drone = self.formation.formation.pop(drone_index)
            print(f"Drone {drone_index} home pozisyonuna geri gönderildi: {self.home_position}")
            return home_drone
        else:
            print("Geçersiz drone indeksi.")
            return None
    
    def addDroneToFormation(self, drone_position):
        self.formation.formation.append(drone_position)
        print(f"Yeni drone formasyona eklendi: {drone_position}")
    
    def updateFormation(self):
        self.formation.create_formation(self.formation.formation_type)
