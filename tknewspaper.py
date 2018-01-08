__VERSION__ = 0.3

'''
TO DO:
    Update the newspaper toplevel after submit
    Make submit ask if it wants to update if data already exists
    Newspaper level finish delete button function
    Newspaper level finish delete button function
    Newspapers data communicates with the customer fields.
    getid function and corresponding connection change to combobox and then move the get data id retrieve line in to separate function
'''

from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
from tinydb import *

db = TinyDB('people.json')
newsdb = TinyDB('newspaper.json')

class AppEntry(Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.name = StringVar()
        self.address = StringVar()
        self.paperName = StringVar()
        self.paperPrice = StringVar()
        self.satPaperPrice = StringVar()
        self.sunPaperPrice = StringVar()
        self.selectedcombovalue = StringVar().set("search News paper")
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
    Create all the widgets for the main menu such as 
    submitting data viewing data and newspaper date.
    '''
    def createwidgets(self):
        self.master.geometry("{}x{}".format(360,160))
        self.mainframe = Frame(self).pack(side="top")

        Label(self.mainframe, text="Newspapers V.{}".format(__VERSION__)).pack(side='top')
        Button(self.mainframe, text="Deliveries", command=self.deliveriesbutton).pack()
        Button(self.mainframe, text="Newspapers", command=self.newspaperbutton).pack()
        Button(self.mainframe, text="New Customers", command=self.ceditwindow).pack()

    '''
    Setup The Toplevel for the newspaper window
    '''
    def newspaperbutton(self):
        self.newswindow = Toplevel()
        self.newswindow.title("Newspapers")
        self.newswindow.focus_set()
        self.newspaperwidgets()

    '''
    Get the data that is search for
    Using the value recieved from the Combobox 
    retrieve all the necessary data and insert it to the appropriate fields
    '''
    def getdata(self, event):
        data = newsdb.all()[self.combobox.current()]

        self.paperName.set(data["Name"])
        self.paperPrice.set(data["Normal Price"])
        self.satPaperPrice.set(data["Saturday Price"])
        self.sunPaperPrice.set(data["Sunday Price"])
    '''
    Push the data back to the json.
    If the data is exist then replace using confirmation
    otherwise simply enter new data
    '''
    def sendnewspaperdata(self):
        if str(self.paperName.get().lower() )not in self.readdata('Name', True, database=newsdb):
            newsdb.insert({'Name' : self.paperName.get(), 'Normal Price' : self.paperPrice.get(), 'Saturday Price' : self.satPaperPrice.get(), 'Sunday Price' : self.sunPaperPrice.get() })
        else:
            messagebox.showerror('Error', "Data already exists")

    '''
    If data already exist then delete that data using
    confirmation otherwise state that there is nothing to
    delete. 
    '''
    def deletenewspaperdata(self):
        pass

    '''
    Widgets for the newspaper window
    all of the gui elements should be located here.
    When an item is selected via combo box the "getdata" function will get called
    When "Delete" button is pressed the deletenewspaperdata function will get called
    when "Submit" button is pressed the sendnewspaperdata function will get called
    '''
    def newspaperwidgets(self):
        Label(self.newswindow, text='Paper Name: ').grid(row=0, column=2)
        Entry(self.newswindow, textvariable=self.paperName).grid(row=0,column=3)

        Label(self.newswindow, text="Price").grid(row=1, column=2)
        Entry(self.newswindow, textvariable=self.paperPrice).grid(row=1, column=3)

        Label(self.newswindow, text="Saturday Price").grid(row=2, column=2)
        Entry(self.newswindow, textvariable=self.satPaperPrice).grid(row=2, column=3)

        Label(self.newswindow, text="Sunday Price").grid(row=3, column=2)
        Entry(self.newswindow, textvariable=self.sunPaperPrice).grid(row=3, column=3)

        Button(self.newswindow, text="Submit", command=self.sendnewspaperdata).grid(row=4, column=3, sticky='e')
        Button(self.newswindow, text="Delete",command=self.deletenewspaperdata).grid(row=4, column=3, sticky='w')

        self.combobox = Combobox(self.newswindow, values=self.readdata('Name', True, newsdb))
        self.combobox.grid(row=0)
        self.combobox.bind("<<ComboboxSelected>>", self.getdata)

    '''
    Create the toplevel for the edit window
    so that you can submit data of new address.
    '''
    def ceditwindow(self):
        self.editwindow = Toplevel()
        self.editwindow.title("Edit")
        self.editwindow.focus_set()
        self.editwidgets()

    '''
    Creates all the widgets for the submit application.
    Such as Name label and entry and so on...
    '''
    def editwidgets(self):

        self.nameLabel = Label(self.editwindow, text="Full Name:").grid(row=0)
        self.nameEntry = Entry(self.editwindow, textvariable=self.name).grid(row=0, column=1)

        self.addressLabel = Label(self.editwindow, text="Address:").grid(row=1)
        self.addressEntry = Entry(self.editwindow, textvariable=self.address).grid(row=1, column=1)

        self.submit = Button(self.editwindow, text="Submit", command=self.submitbutton).grid(row=0, column=2, padx=5)

    '''
    Reads the desired Key of data in the database
    and then returns all the values for that desired field
    '''
    def readdata(self, nameofdata, lower, database=db):
        if lower == True:
            return [str(data[nameofdata]).lower() for data in database.all()]
        else:
            return [data[nameofdata] for data in database.all()]

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
    def deliveriesbutton(self):
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
