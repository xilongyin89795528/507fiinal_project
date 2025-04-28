import pandas as pd
from collections import deque

file_path = '/Users/yinxilong/Desktop/507/merged_output.csv'
df = pd.read_csv(file_path)

df['name'] = df['name'].str.strip()
df['games'] = df['games'].str.strip()
df['friends'] = df['friends'].str.strip()
df['enemies'] = df['enemies'].str.strip()
df['locations'] = df['locations'].str.strip()
df['concepts'] = df['concepts'].str.strip()
df['objects'] = df['objects'].str.strip()
df['deck'] = df['deck'].str.strip()

df['deck'] = df['deck'].fillna('No description.')
df['games'] = df['games'].apply(lambda x: x.split(';') if isinstance(x, str) else [])
df['friends'] = df['friends'].apply(lambda x: x.split(';') if isinstance(x, str) else [])
df['enemies'] = df['enemies'].apply(lambda x: x.split(';') if isinstance(x, str) else [])
df['locations'] = df['locations'].apply(lambda x: x.split(';') if isinstance(x, str) else [])
df['concepts'] = df['concepts'].apply(lambda x: x.split(';') if isinstance(x, str) else [])
df['objects'] = df['objects'].apply(lambda x: x.split(';') if isinstance(x, str) else [])

def find_closely_related_characters(character_name,df):
    character_rows = df[df['name'] == character_name]
    
    if character_rows.empty:
        return f"Character '{character_name}' not found in the dataset."
    
    character = character_rows.iloc[0]
    
    similarity_scores = {}
    for _, row in df.iterrows():
        if row['name'] == character_name:
            continue  
        
        shared_games = set(character['games']).intersection(set(row['games']))
        shared_friends = set(character['friends']).intersection(set(row['friends']))
        shared_enemies = set(character['enemies']).intersection(set(row['enemies']))
        shared_locations = set(character['locations']).intersection(set(row['locations']))

        score = 2*len(shared_games) + len(shared_friends) + 0.5*len(shared_enemies) + 0.2*len(shared_locations)

        if character_name in row['friends']: 
            score += 1 
        if character_name in row['enemies']:  
            score += 1  

        similarity_scores[row['name']] = {
            'score': score,
            'is_friend': character_name in row['friends'],
            'is_enemy': character_name in row['enemies'],
            'shared_games': len(shared_games),
            'shared_friends': len(shared_friends),
            'shared_enemies': len(shared_enemies),
            'shared_locations': len(shared_locations)
        }
    sorted_characters = sorted(similarity_scores.items(), key=lambda x: x[1]['score'], reverse=True)
    
    top_related_characters = sorted_characters[:5]
    
    return top_related_characters



def build_graph(df):
    """ Build the graph where nodes are characters and edges exist if two characters share a game """
    graph = {}
    
    for _, row in df.iterrows():
        character = row['name']
        if character not in graph:
            graph[character] = {}
        
        for game in row['games']:
            co_appearing_characters = df[df['games'].apply(lambda x: game in x)]['name']
            
            for co_character in co_appearing_characters:
                if co_character != character: 
                    if co_character not in graph[character]:
                        graph[character][co_character] = []
                    graph[character][co_character].append(game)
    
    return graph

def find_shortest_path(character1, character2, graph):
    """ Use BFS to find the shortest path between two characters in the graph, including co-appearing games """
    if character1 == character2:
        return [character1]  
    
    queue = deque([(character1, [character1], [])]) 
    visited = set([character1])
    
    while queue:
        current_node, path, games_path = queue.popleft()
        
        for neighbor, games in graph.get(current_node, {}).items():
            for game in games:
                if neighbor not in visited:
                    if neighbor == character2:
                        return path + [neighbor], games_path + [game]
                    
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor], games_path + [game]))
    
    return None  


def find_most_connected_node(df):
    """Find the most connected character by counting direct connections (games, friends, enemies)."""
    connections = {}

   
    for _, row in df.iterrows():
        character = row['name']
        connected_characters = set()

       
        for game in row['games']:
            co_appearing_characters = df[df['games'].apply(lambda x: game in x)]['name']
            connected_characters.update(co_appearing_characters)
        
        
        connected_characters.update(row['friends'])
        
        
        connected_characters.update(row['enemies'])

       
        connected_characters.discard(character)

     
        connections[character] = len(connected_characters)


    most_connected_character = max(connections, key=connections.get)
    return most_connected_character, connections[most_connected_character]

def show_node_stat(character_name, df):
    
    character_row = df[df['name'] == character_name]

    if character_row.empty:
        return f"Character '{character_name}' not found in the dataset."
    
    character = character_row.iloc[0]

    stats = {
        'name': character['name'],
        'description': character['deck'],
        'games': ", ".join(character['games']),  
        'friends': ", ".join(character['friends']),  
        'enemies': ", ".join(character['enemies']), 
        'locations': ", ".join(character['locations']) if character['locations']!= [] else "No locations available." 
    }

    for key, value in stats.items():
        print(f"{key.capitalize()}: {value}")




def main_menu():
    print("Choose an option:")
    print("1. View character information")
    print("2. View the shortest path between two characters")
    print("3. View the most connected characters for a given character")
    print("4. View the most connected character in the dataset")

    choice = input("Enter your choice (1-4): ")

    if choice == '1':
        input_character = input("Enter the character's name: ")
        show_node_stat(input_character, df)

    elif choice == '2':
        input_character1 = input("Enter the name of the first character: ")
        input_character2 = input("Enter the name of the second character: ")
        graph = build_graph(df)
        shortest_path, game_path = find_shortest_path(input_character1, input_character2, graph)
        if shortest_path:
            print(f"Shortest path from {input_character1} to {input_character2}:")
            for i in range(len(shortest_path) - 1):
                print(f"{shortest_path[i]} -> [{game_path[i]}] -> {shortest_path[i + 1]}")
        else:
            print(f"No path found between {input_character1} and {input_character2}.")

    elif choice == '3':
        input_character = input("Enter the character's name: ")
        related_characters = find_closely_related_characters(input_character, df)
        if isinstance(related_characters, str):
            print(related_characters)
        else:
            for character, details in related_characters:
                print(f"Character: {character}, Similarity Score: {details['score']}")
                print(f"  Friend: {details['is_friend']}, Enemy: {details['is_enemy']}")
                print(f"  Shared Games: {details['shared_games']}, Shared Friends: {details['shared_friends']}, "
                      f"Shared Enemies: {details['shared_enemies']}, Shared Locations: {details['shared_locations']}")
                print("-" * 50)

    elif choice == '4':
        most_connected_character, num_connections = find_most_connected_node(df)
        print(f"The most connected character in the dataset is {most_connected_character} with {num_connections} direct connections.")
    else:
        print("Invalid choice. Please try again.")


main_menu()