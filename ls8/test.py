string = "hey this is a string\n"
string_copy = "hey this is a string\n"

print(string)
new_string = string.replace('\n', '')
print(string_copy == string)
print(string == new_string)
