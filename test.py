import msvcrt


if __name__ == '__main__':
   print ('Press s or n to continue:\n')
   for i in range(59):
      input_char = msvcrt.getch().decode('utf-8')
      print(input_char)