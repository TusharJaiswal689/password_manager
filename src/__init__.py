from crypto import pass_generator


try:
    x = int(input("Enter the length of the password: "))
    s = int(input("Enter the number of special characters: "))
    n = int(input("Enter the number of numeric characters: "))
    if s + n > x:
        print("The sum of special and numeric characters cannot exceed the total length.")
    else:
        x-=s+n
        password = pass_generator(x, s, n)
        print("Your password is successfully generated: ", password)
except ValueError:
    print("Please enter valid integers.")