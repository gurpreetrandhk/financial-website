class Person:
    def __init__(self,n,d):
        print("hey I am a peraon")
        self.name = n
        self.occ = d


    def info(self):
        print(f"{self.name} is a {self.occ}")


a = Person("singh","dv")
b = Person("kour","infra")
a.info()
b.info()
        
