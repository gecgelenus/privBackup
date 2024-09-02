class Formation:# yukseklik = y eksenindeki yükseklik
    def __init__(self, x, y, z, droneSayisi, aralarindakiMesafe, formation_type):
        self.x = x # sagsol
        self.y = y # yukseklik
        self.z = z # derinlik
        self.droneSayisi = droneSayisi
        self.aralarindakiMesafe = aralarindakiMesafe
        self.formation_type = formation_type
        self.formation = []
        print(f"Formasyon: {self.droneSayisi} drone, aralarındaki mesafe: {self.aralarindakiMesafe} ve formasyon tipi: {self.formation_type}") 
        self.create_formation(formation_type)

    def lineFormation(self):
        formation = []
        for i in range(self.droneSayisi):
            formation.append([self.x - (self.droneSayisi-1)/2 * self.aralarindakiMesafe + self.aralarindakiMesafe*i , self.y, self.z])
        return formation

    

    def VFormation(self):
        formation = []
        middle_index = self.droneSayisi // 2  # Ortadaki drone'un indeksi
        for i in range(self.droneSayisi):
            dx = (i - middle_index) * self.aralarindakiMesafe / 2
            dz = abs(i - middle_index) * self.aralarindakiMesafe        
            # Ortaya yakın dronelar merkezde, uçlara doğru ilerliyor
            formation.append([self.x + dx, self.y , self.z - dz])
        return formation

    def arrowFormation(self):
        formation = []
        middle_index = self.droneSayisi // 2  # Ortadaki drone'u bul
        for i in range(self.droneSayisi):
            if i < middle_index:
                # Sol taraftaki droneları yerleştir
                dx = -(middle_index - i) * self.aralarindakiMesafe / 2  # X ekseninde sola kayma
                dz = (middle_index - i) * self.aralarindakiMesafe  # Z ekseninde yukarı kayma
                formation.append([self.x + dx, self.y, self.z + dz])
            elif i > middle_index:
                # Sağ taraftaki droneları yerleştir
                dx = (i - middle_index) * self.aralarindakiMesafe / 2  # X ekseninde sağa kayma
                dz = (i - middle_index) * self.aralarindakiMesafe  # Z ekseninde yukarı kayma
                formation.append([self.x + dx, self.y, self.z + dz])
            else:
                # Ortadaki drone sabit kalır
                formation.append([self.x, self.y, self.z])

        return formation

    
    def create_formation(self, formation_type):
        if formation_type == "line":
            self.formation = self.lineFormation()
        elif formation_type == "V":
            self.formation = self.VFormation()
        elif formation_type == "arrow":
            self.formation = self.arrowFormation()
        else:
            raise ValueError(f"Bilinmeyen formasyon türü: {formation_type}")
    
    def get_formation(self):
        return self.formation
# def __init__(self, x, y, z, droneSayisi, aralarindakiMesafe, formation_type):
"""

formation = Formation(0, 0, 0, 5 ,10 ,"arrow")
print("Drone Formasyonu:", formation.formation)

"""


