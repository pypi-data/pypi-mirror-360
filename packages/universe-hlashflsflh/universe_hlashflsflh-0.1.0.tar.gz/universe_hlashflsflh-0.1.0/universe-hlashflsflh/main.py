from world.main import main 
world = main()
# print("inside universe")
def universe_entry():
    result = main()
    print("inside universe")
    return result

def happy():
    print("Done")

