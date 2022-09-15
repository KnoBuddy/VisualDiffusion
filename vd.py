import os

def main():
    if os.path.exists('./prs.py'):
        print('PRS Found\n Please specificy which GUI version you want to use\n 1. MakeGUDPics\n 2. PRSGUI')
        choice = input('Choice: ')
        if choice == '1':
            print('starting MakeGUDPics')
            os.system('python visualdiffusion/makegudpics.py')
        elif choice == '2':
            print('starting PRSGUI')
            os.system('python visualdiffusion/prsgui.py')
    elif os.path.exists('./prd.py'):
        print('PRD Found\n Starting PRDGUI')
        os.system('python visualdiffusion/prdgui.py')
    else:
        print('PRS or PRD not found\n Please make sure you are in the correct directory')

main()
