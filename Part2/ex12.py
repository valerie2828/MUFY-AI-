def check_string(text):
    
    if text.startswith("The"):
        return "Found it!"

    else:
        return "Nope."

string1 = "The"
string2 = "Thumbs up"
string3 = "Theatre can be boring"

print(check_string(string1))
print(check_string(string2))
print(check_string(string3))
