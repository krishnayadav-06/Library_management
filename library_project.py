import mysql.connector as sqlctr
import sys
from datetime import datetime

mycon = sqlctr.connect(host='localhost', user='root', password='krishna')
if mycon.is_connected():
    print('\nSuccessfully connected to localhost')
else:
    print('Error while connecting to localhost')
    sys.exit()

cursor = mycon.cursor()

# Creating database
cursor.execute("CREATE DATABASE IF NOT EXISTS Library")
cursor.execute("USE Library")

# Creating the tables we need

cursor.execute("CREATE TABLE IF NOT EXISTS books(SN INT(5) PRIMARY KEY, Book_Name VARCHAR(50), Quantity_Available INT(10), Price_Per_Day INT(10))")
cursor.execute("CREATE TABLE IF NOT EXISTS BORROWER(SN INT(5), borrowers_name VARCHAR(50), book_lent VARCHAR(50), contact_no BIGINT(11), borrow_date DATE)")


def command(st):
    cursor.execute(st)


def fetch():
    data = cursor.fetchall()
    for i in data:
        print(i)


def all_data(tname):
    li = []
    st = 'DESC ' + tname
    command(st)
    data = cursor.fetchall()
    for i in data:
        li.append(i[0])
    st = 'SELECT * FROM ' + tname
    command(st)
    print('\n')
    print('-------ALL_DATA_FROM_TABLE_'+tname+'_ARE-------\n')
    print(tuple(li))
    fetch()


def detail_borrower(name, contact):
    tup = ('SN', 'borrowers_name', 'book_lent', 'date', 'contact_no')
    print('\n---Details for borrower '+name+'---\n')
    print(tup)
    st = 'SELECT * FROM borrower WHERE borrowers_name LIKE "{}" AND contact_no={}'.format(
        name, contact)
    command(st)
    fetch()


def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    global days
    days = abs((d2 - d1).days)


def price_book(days, book_name):
    st1 = 'SELECT Price_Per_Day FROM books WHERE Book_Name="{}"'.format(
        book_name)
    command(st1)
    data = cursor.fetchall()
    for i in data:
        global t_price
        t_price = int(i[0]) * days
        print('No. of days {} book is kept: {}'.format(book_name, days))
        print('Price per day for book {} is Rs.{}'.format(book_name, i[0]))
        print('Total fare for book '+book_name + '-', t_price)


def lend():
    flag = 'True'
    while flag == 'True':
        print('\n___AVAILABLE BOOKS___\n')
        st0 = 'select Book_Name from books where Quantity_Available>=1'
        command(st0)
        fetch()
        st1 = 'SELECT MAX(SN) FROM borrower'
        command(st1)
        data_sn = cursor.fetchall()
        for i in data_sn:
            if i[0] is not None:
                SN = i[0] + 1
            else:
                SN = 1

        book_selected = str(input('Enter name of book from above list : '))
        borrowers_name = str(input('Enter Borrower Name: '))
        date = str(input('Enter date (YYYY-MM-DD): '))
        contact = int(input('Enter contact no.: '))

        st_insert = 'insert into borrower values({}, "{}", "{}", {}, "{}")'.format(
            SN, borrowers_name, book_selected, contact, date)

        command(st_insert)
        st_quantity = 'select Quantity_Available from books where Book_Name="{}"'.format(
            book_selected)
        command(st_quantity)
        data_quantity = cursor.fetchall()
        for quantity in data_quantity:
            qty = quantity[0] - 1
        st_dec = 'update books set Quantity_Available={} where Book_Name="{}"'.format(
            qty, book_selected)
        command(st_dec)
        dec = str(input('Do you want to add more records (Y/N) : '))
        if dec.upper() == "Y":
            flag = 'True'
        else:
            flag = 'False'
    action_list()


def borrowers():
    print('\n\n___OPTIONS AVAILABLE___\n\nEnter 1 : To Show detail of all borrowers \nEnter 2 : To check detail of a particular borrower \nEnter 3 : To calculate total fee to borrow a book \nEnter 4 : To go Back \nEnter 5 : To commit all the changes and exit')
    dec = input('Enter your choice-')
    if dec == '1':
        all_data('borrower')
    elif dec == '2':
        name = str(input('\nEnter borrower name: '))
        contact = str(input('Enter borrower contact no.: '))
        detail_borrower(name, contact)
    elif dec == '3':
        tfine()
    elif dec == '4':
        action_list()
    elif dec == '5':
        close()
    borrowers()


def tfine():
    name = str(input('\nEnter borrower name: '))
    contact = input('Enter borrower contact_no: ')
    detail_borrower(name, contact)
    st1 = 'SELECT book_lent FROM borrower WHERE borrowers_name ="{}" AND contact_no={}'.format(
        name, contact)
    command(st1)
    data = cursor.fetchall()
    for i in data:
        book_name = i[0]
        st2 = 'select borrow_date from borrower where borrowers_name="{}" and book_lent="{}"'.format(
            name, book_name)
        command(st2)

        data1 = cursor.fetchall()
        for date in data1:
            date_taken = date[0]
            date_return = str(input(
                '\nEnter returning date for book "{}" (YYYY-MM-DD), Press ENTER to skip: '.format(book_name)))
            while date_return != '':
                days_between(str(date_return), str(date_taken))
                price_book(days, i[0])
                print('\nEnter Y : If Rs.{} is paid and book is returned.\nEnter N : If fare is not paid and book is not returned.'.format(t_price))
                dec = str(input('Enter (Y?N): '))
                if dec.upper() == "Y":
                    st = 'SELECT SN , Quantity_Available FROM books WHERE Book_Name ="{}"'.format(
                        i[0])
                    command(st)
                    data2 = cursor.fetchall()
                    for price in data2:
                        st_del = 'DELETE FROM borrower WHERE borrowers_name="{}" AND book_lent="{}"'.format(
                            name, book_name)
                        command(st_del)
                        update('books', 'Quantity_Available',
                               price[1] + 1, price[0])
                        break
                else:
                    print("\n\nPLEASE PAY THE FARE AND RETURN BOOK AFTER READING.\n\n")
                    break


def insert():
    flag = 'true'
    while flag == 'true':
        licol = []
        li1 = []
        li_val = []
        command('DESC books')
        data = cursor.fetchall()
        for i in data:
            licol.append(i[0])
        command('SELECT MAX(SN) FROM books')
        dta = cursor.fetchall()
        for j in dta:
            if j[0] is not None:
                li_val.append(j[0] + 1)
            else:
                li_val.append(1)

        for k in range(1, 4):
            val = str(input('Enter '+licol[k]+': '))
            li_val.append(val)
        li1.append(tuple(li_val))
        values = ', '.join(map(str, li1))
        st1 = "INSERT INTO books VALUES {}".format(values)
        command(st1)
        all_data('books')
        print('\n')
        print("\nDATA INSERTED SUCCESSFULLY\n")
        dec = str(input('Do you want to insert more data? (Y/N): '))
        if dec.upper() == "Y":
            flag = 'true'
        else:
            flag = 'false'
    action_list()


def update(tname, col1, post_value, pre_value):
    st = str('UPDATE %s SET %s=%s WHERE SN=%s') % (
        tname, col1, "'%s'", "'%s'") % (post_value, pre_value)
    command(st)
    all_data(tname)
    print('\nVALUE UPDATED SUCCESSFULLY\nPLEASE COMMIT CHANGES')
    action_list()


def close():
    mycon.commit()
    mycon.close()
    if mycon.is_connected():
        print('Still connected to localhost')
    else:
        print('\n\nConnection closed successfully.')
    sys.exit()


def action_list():
    print('\n')
    print('#### WELCOME TO LIBRARY MANAGEMENT SYSTEM ####\n\nEnter 1 : To View details of all available Books\nEnter 2 : To check detail of a particular book\nEnter 3 : To lend a book \nEnter 4 : To add new books in the list \nEnter 5 : To update data \nEnter 6 : To view details of borrowers \nEnter 7 : To commit all changes and exit')
    dec = input('\nEnter your choice: ')
    if dec == '1':
        all_data('books')
    elif dec == '2':
        tup = ('SN', 'Book_Name', 'Quantity_Available', 'Price_Per_Day')
        tup1 = ('SN', 'borrowers_name', 'book_lent', 'contact_no')
        in1 = str(input('Enter first name, last name, or middle name of a book: '))
        print('\n---ALL DATA OF BOOKS HAVING "{}" IN THEIR NAME FROM BOTH TABLE---'.format(in1))
        st = str(
            'SELECT * FROM books WHERE book_name LIKE "{}"'.format('%' + in1 + '%'))
        st1 = str(
            'SELECT * FROM borrower WHERE book_lent LIKE "{}"'.format('%' + in1 + '%'))
        print('\n---DATA FROM TABLE BOOKS---\n')
        command(st)
        print(tup)
        fetch()
        print('\n---DATA FROM TABLE BORROWER---\n')
        command(st1)
        print(tup1)
        fetch()
        print()
    elif dec == '3':
        lend()
    elif dec == '4':
        insert()
    elif dec == '5':
        flag = 'true'
        while flag == 'true':
            tname = 'books'
            li = []
            st1 = 'DESC '+tname
            command(st1)
            data = cursor.fetchall()
            for i in data:
                li.append(i[0])
            all_data(tname)
            print('\nColumns in table '+tname+' are:')
            print(li)
            col1 = str(
                input('Enter the column name for modification from the above list: '))
            lipo = ['SN']
            lipo.append(col1)
            print(tuple(lipo))
            st0 = 'SELECT SN , %s FROM books' % (col1)
            command(st0)
            fetch()
            pre_value = str(
                input('Enter the corresponding SN for the data to be changed: '))
            post_value = str(
                input('Enter the new value for column %s having SN %s: ' % (col1, pre_value)))
            update(tname, col1, post_value, pre_value)
            dec = str(input('Do you want to change more data? (Y/N): '))
            if dec == 'y' or dec == 'Y':
                flag = 'true'
            else:
                flag = 'false'
    elif dec == '6':
        borrowers()
    elif dec == '7':
        close()


action_list()