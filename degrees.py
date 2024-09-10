import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass

def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")



def compare(person_id, target, explored):
    """
    Checks if a person_id is connected to the target.
    Returns a tuple where:
    - The first element is the target person_id if found.
    - The second element is the list of (movie_id, person_id) pairs excluding explored persons.
    """
    if person_id==target:
        a=[person_id,None]
        return(a)
    z=[]
    
    neighbors = neighbors_for_person(person_id, explored)
    for movie, actor in neighbors:      
        z.append(actor)
    return (None, z)  # Not found, return filtered neighbors


def shortest_path(source, target):

    explored = set()
    explored.add(source)
    if source == target:
        return []

    array_counter = 1
    arrays = {}
    length = []
    ch=[]
    for m,a in neighbors(source):
        ch.append(a)
    while True:
        if not ch:
            return None
        z = []
        l = f"s{array_counter}"
        arrays[l] = []
        for person_id in ch:
            
            # Check neighbors and whether we found the target
            x = compare(person_id, target, explored)
            explored.add(person_id)
            arrays[l].append(person_id)
            if x[0] is not None:
                
                if array_counter==1:
                    
                    for m0,a0 in neighbors(source):
                        if a0==target:
                            path=[(m0,a0)] 
                            return path               
                return reconstruct_path(arrays,source, target)
            
            z.extend(x[1])
            
    
        length.append(len(ch))
        ch = z
        array_counter += 1

def reconstruct_path(arrays, source, target):
    """
    Reconstruct the path from source to target using the arrays dictionary.
    """

        
    path = []
    current_person = target
    i=0
    l=len(arrays)

    while current_person != source:


        level=l
        found = False

   
        i+=1
        j=0
        key = f"s{level}"



        if current_person in arrays.get(key, []):
            
            if l==2:
                temp=current_person
            
            j+=1
            movie_id, next_person = find_connection(arrays, level, current_person)
     
            
            if movie_id is None:
                continue
            path.insert(0, (movie_id, current_person))
            current_person = next_person
            found = True
            

             
        if not found:
            return []  # Path reconstruction failed
        l=l-1
        if l==1:
            flag=False
            for m,a in neighbors(source):
                for m1,a1 in neighbors(a):
                    if a1==temp:
                        flag=True
                        break
                if flag:
                    break
            path.insert(0, (m, a))
            break
    
    return path

def find_connection(arrays, level, person_id):
    """
    Find the movie and the next person_id at the given level that connects to person_id.
    """
    key = f"s{level -1}"
    a=arrays.get(key, [])
    for movie_id, neighbor_id in neighbors(person_id):
        # Check if the neighbor_id exists in the previous level of arrays


        if neighbor_id in a:
            return (movie_id, neighbor_id)
    return (None, None)

def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person and are not in the explored set.
    """
    movie_ids = people.get(person_id, {}).get("movies", set())
    neighbors = set()

    for movie_id in movie_ids:
        for neighbor_id in movies[movie_id]["stars"]:
            if neighbor_id != person_id:
                neighbors.add((movie_id, neighbor_id))
    
    return list(neighbors)

def neighbors_for_person(person_id, explored):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person and are not in the explored set.
    """
    
    # Retrieve the set of movies the person has starred in
    movie_ids = people.get(person_id, {}).get("movies", set())
    neighbors = set()
    
    # Iterate over each movie the person has starred in
    for movie_id in movie_ids:
        # Get all stars in the current movie
        for neighbor_id in movies[movie_id]["stars"]:
            # Ensure the neighbor is not in the explored set
            if neighbor_id not in explored:
                neighbors.add((movie_id, neighbor_id))
                
    return list(neighbors)


if __name__ == "__main__":
    main()
