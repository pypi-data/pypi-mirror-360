def create_hero(name, power, city):
    return f"Captain {name} has the {power} of fire and protects New {city}"
message = create_hero("Flames", "power","York") 
print(message)

def hero_intro(hero_description):
    return message
new_message = hero_intro(message)
print(new_message)