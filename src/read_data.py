import json


def get_person_data():

    file=open("data\person_db.json")
    person_data=json.load(file) 
    return person_data

def get_person_names():

    names_list = [] 
    #gib mir die Liste der Namen aus der JSON-Datei zurück
    person_dict = get_person_data() 
    #geh durch die Liste
    for person_data in person_dict:
        #Jeder eintrag ist ein dict mit den feldern (first_name, last_name)
        names_list.append(person_data["lastname"]+ ", "+ person_data["firstname"])
        #hänge das an die namensliste an

    return names_list   



def get_person_data_by_name(personname):
    all_persons = get_person_data()
    first_name = personname.split(", ")[1]
    last_name = personname.split(", ")[0]

    for person_data in all_persons:
        if person_data["firstname"]==first_name and person_data["lastname"]==last_name:
            return person_data
        
def get_person_image_by_name(personname):
    picture_path = get_person_data_by_name(personname)["picture_path"]
    return picture_path


    

if __name__=="__main__":
#Example usage
    person_data = get_person_data()
    print(person_data)

    person_names = get_person_names()
    print(person_names)
    
    person_name = "Huber, Julian"
    person_dict = get_person_data_by_name(person_name)
    person_picture = get_person_image_by_name(person_name)
    print(person_dict)
   

