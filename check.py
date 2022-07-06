from flask import Flask, request, flash, session, url_for, redirect, render_template  
from sql import Employees
from base import Base,engine,Session

#sqlalchemy  
app = Flask(__name__)  

app.config['SECRET_KEY'] = "secret key"  
    
Base.metadata.create_all(engine)
session=Session()  

@app.route('/')  
def list_employees():  
   return render_template('list_employees.html', Employees = session.query(Employees).all() )  
 
@app.route('/add', methods = ['GET', 'POST'])  
def addEmployee():  
   if request.method == 'POST':  
      if not request.form['name'] or not request.form['salary'] or not request.form['age']:  
         flash('Please enter all the fields', 'error')  
      else:  

         employee = Employees(request.form['name'], request.form['salary'], request.form['age'], request.form['pin'])  
           
         session.add(employee)  
         session.commit()  
         flash('Record was successfully added')  
         return redirect(url_for('list_employees'))  
   return render_template('add.html')  
  
if __name__ == '__main__':  
   app.run(debug = True)  