from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
from tinydb import *

db = TinyDB('newspaper.json')


class AppEntry(Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.name = StringVar()
        self.address = StringVar()
        self.daynames = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.weeklist = []
        for i in range(7):
            self.weeklist.append(BooleanVar())
        self.createwidgets()

    '''
    Reset the week list. This is mainly used in exception handling
    and initialisation
    '''
    def weekreset(self):
        for i in range(7):
            self.weeklist[i].set(False)

    '''
    Creates all the widgets for the main application.
    Such as Name label and entry and so on...
    '''
    def createwidgets(self):
        self.topParent = Frame(self).pack(side="top")

        self.nameLabel = Label(self.topParent, text="Full Name:").grid(row=0)
        self.nameEntry = Entry(self.topParent, textvariable=self.name).grid(row=0, column=1)

        self.addressLabel = Label(self.topParent, text="Address:").grid(row=1)
        self.addressEntry = Entry(self.topParent, textvariable=self.address).grid(row=1, column=1)

        self.buttonFrame = Frame(self.topParent).grid(row=3,column=1)

        self.submit = Button(self.buttonFrame, text="Submit", command=self.submitbutton).grid(row=0, column=2, padx=5)
        self.show = Button(self.buttonFrame, text="Show", command=self.showbutton).grid(row=1, column=2, padx=5)

    '''
    Reads the desired field of data in the database
    and then returns all the values for that desired field
    '''
    def readdata(self, nameofdata, lower):
        if lower == True:
            return [str(data[nameofdata]).lower() for data in db.all()]
        else:
            return [data[nameofdata] for data in db.all()]

    '''
    Submits data after checking it and clears the entry fields.
    The checks include checking if the data is already present and
    if the entry fields are not empty
    '''
    def submitbutton(self):
        if self.name.get() != '' and self.address.get() != '':
            if str(self.name.get()).lower() not in self.readdata('Name', True) or str(self.address.get()).lower() not in self.readdata('Address', True):
                db.insert({"Name": self.name.get(), "Address": self.address.get()})
                self.updatedatawindow()
                self.name.set('')
                self.address.set('')
            else:
                messagebox.showerror("Error", "Data already in the database")

    '''
    Shows data that is in the database by opening a new window
    and displaying the data
    '''
    def showbutton(self):
        self.dataWindow = Toplevel()
        self.dataWindow.title("Data")
        self.dataWindow.focus_set()
        self.datawidgets()

    '''
    Creates the widgets for the dataWindow 
    '''
    def datawidgets(self):
        self.datalist = Listbox(self.dataWindow)
        self.datalist.bind("<<ListboxSelect>>", self.getid)
        self.datalist.grid(row=0)

        Button(self.dataWindow, text="Submit", command=self.datasubmit).grid(row=0, column=7, sticky='s')
        Button(self.dataWindow, text="Delete", command=self.datadelete).grid(row=0, column=4, columnspan=3, sticky='se')

        for data in db.all():
            self.datalist.insert('end', "{}. {}, {}".format(data.doc_id, data['Address'], data['Name']))

    '''
    Gets the ID of the selected field by using regex and then
    stores this value which can be accessed by any other function
    that will need it. The variable stays the same until a new field
    is selected
    '''
    def getid(self, event):
        self.dataid = int(re.compile('.*(?=\.)').search(self.datalist.get(self.datalist.curselection())).group(0))
        self.updatedata()

    '''
    Check if the window is open and update the window if it is
    otherwise do nothing and let the program operate as usual
    '''
    def updatedatawindow(self):
        try:
            if self.dataWindow.state() == 'normal':
                self.datawidgets()
        except Exception:
            pass

    '''
    Update the list by checking the json file and retrieving 
    data of the appropriate user
    '''
    def updateweeklist(self):
        self.userdata = db.get(doc_id=self.dataid)
        try:
            for i in range(len(self.daynames)):
                if not self.userdata[self.daynames[i]]:
                    self.weeklist[i].set(False)
                elif KeyError:
                    self.weeklist[i].set(True)
        except KeyError:
            self.weekreset()

    '''
    Update the checkbox for the appropriate user after
    getting their id and corresponding week values
    '''
    def updatedata(self):
        self.updateweeklist()
        for i in range(len(self.weeklist)):
            Checkbutton(self.dataWindow, text=i + 1, variable=self.weeklist[i], onvalue=True,
                        offvalue=False).grid(row=0, column=i + 1, sticky='nw')

    '''
    Submits the week data to the json file so that it can be stored 
    permanently for that user
    '''
    def datasubmit(self):
        for i in range(len(self.weeklist)):
            db.update({str(self.daynames[i]): self.weeklist[i].get()}, doc_ids=[int(self.dataid)])

    '''
    Deletes the selected data from the json file and after which
    the window is updated to represent the changes
    '''
    def datadelete(self):
        if messagebox.askyesno("Confirmation", "Are you sure you want to delete {} record ?".format(self.userdata['Name'])):
            db.remove(doc_ids=[self.dataid])
        self.datawidgets()


root = Tk()
app = AppEntry(master=root)

app.mainloop()