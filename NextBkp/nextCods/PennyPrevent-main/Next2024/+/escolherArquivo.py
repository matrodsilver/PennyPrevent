from tkinter import Tk, filedialog

root = Tk()
root.title('Escolha o arquivo')

filename = filedialog.askopenfilename(initialdir='/', title='Selecione o arquivo', filetypes=(('todos os arquivos', '*.*'),))
