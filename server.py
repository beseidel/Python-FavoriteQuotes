from flask import Flask, render_template, redirect, request, session, flash

from flask_bcrypt import Bcrypt

import re	# the regex module
# create a regular expression object that we'll use later   
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 

from MySQLconnection import connectToMySQL 
# import the function that will return an instance of a connection

app = Flask(__name__)
app.secret_key = "keep it secret"
app.secret_key ="keep it secret"
bcrypt = Bcrypt(app)

#flash require a secret key as well as session

# show a page with a form to create a new user


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index_total():
    return render_template('/index-total.html')

@app.route('/register', methods=['POST'])
def register():
    is_valid = True

    mysql = connectToMySQL('quotes2')
    query = 'SELECT * FROM users_table WHERE email = %(em)s;'
    data = {
    'em': request.form['email']
    }
    email_result = mysql.query_db(query, data)
    
    if len(email_result) >= 1:
      is_valid = False
      flash("email already registered in database")
    print(email_result)
    
    if len(request.form['name']) < 1:
      is_valid = False
      flash("Please enter a first name")

    if len(request.form['alias']) < 1:
      is_valid = False
      flash("Please enter an alias name")
   
    if len(request.form['email']) < 1:
      is_valid = False
      flash("Email cannot be blank.")

    if len(request.form['pw']) < 8:
      is_valid = False
      flash('Password must be atleast 8 characters')

    if (request.form['pw'] != request.form['cpw']):
      is_valid = False
      flash('Passwords do NOT match')
 
    if not EMAIL_REGEX.match(request.form['email']):
      # test whether a field matches the pattern.  If it does not fit the pattern, then redirect. if email fits pattern, continue.
      is_valid = False
      flash("email cannot be blank or invalid")
   
    ##### at this point, I have checked every field
    ##### if any of the fields weren't valid, is_valid will be False
    ##### if all the fields are valid, is_valid will be True
    if not is_valid:
      return redirect('/')
      # return render_template('/') could use also in this case
    else:
        pw_hash = bcrypt.generate_password_hash(request.form['pw'])
        # pw_hash can be called anything including mickey
        print(pw_hash)   
        # put the pw_hash in our data dictionary, NOT the password the user provided
        # prints something like b'$2b$12$sqjyok5RQccl9S6eFLhEPuaRaJCcH3Esl2RWLm/cimMIEnhnLb7iC'
        # be sure you set up your database so it can store password hashes this long (60 characters)
      
        mysql = connectToMySQL("quotes2")
    
        query = "INSERT INTO users_table (name, alias, email, password,b_date) VALUES (%(n)s, %(a)s, %(em)s, %(pw)s,%(bd)s);"
    # put the pw_hash in our data dictionary, NOT the password the user provided
    
        data = {
          "n": request.form['name'],
          "a": request.form['alias'],
          "em": request.form['email'],
          "pw": pw_hash,
          'bd': request.form['b_dat'],
          
        }
    #make the call of the function to the database. 
        result = mysql.query_db(query, data)
        session['id_mickey_user']=result
    # never render on a post, always redirect!
        flash("Login info successfuly added.  Please login!")
        
      # either way the application should return to the index and display the messag
      #   never render on a post, always redirect!
        return redirect("/")

# login the database  
@app.route('/login', methods = ['POST'])
def login():
    mysql = connectToMySQL('quotes2')
    query = 'SELECT * FROM users_table WHERE email = %(em)s;'
    data = {
    'em': request.form['email']
    }
    result = mysql.query_db(query, data)
   
    if len(result)>0:
   
      if bcrypt.check_password_hash(result[0]['password'], request.form['pw']):
        session['id_mickey_user'] = result[0]['id_user']
# This is setting id_mickey_user to session which is equal the id_user logged in.
      session['mickeys_first_name'] = result[0]['name']
      #look in session and result the first name at login
      return redirect('/dashboard')
      flash("You could not be logged in")
    return redirect ('/')

@app.route('/logout')
def logout():
    print(session)
    session.clear()
    flash("You've been logged out")
    return redirect('/')


@app.route('/dashboard', methods=['GET'])
def show_all_quotes_dashboard():
    if 'id_mickey_user' not in session:
      flash("You need to be logged in to view this page")
      return redirect('/')
    else:
      flash("welcome to the dashboard")
        
      MySQL = connectToMySQL('quotes2')

      query_show_quotes = 'SELECT * FROM quotes_table JOIN users_table ON quotes_table.id_contributor = users_table.id_user ORDER By quotes_table.id_quote;'
      # Add DESC to order in reverse order backwards
      # toorderbyid_bookuseORDERBYbooks_table.id_quote;

      quotes = MySQL.query_db(query_show_quotes)
      print('show page hitting 0')
      return render_template('dashboard.html', all_quotes=quotes)
      print('show page before Hitting 1')

@app.route('/add_quote', methods = ['POST'])
def process_quote_dashboard():
    print("Hitting 1")
    print(request.form)
    print(session['id_mickey_user'])
    print("Hitting 2")
    print(request.form)
    if len(request.form['q_name']) < 3:
      if len(request.form['q_cont']) < 10:
    # post_content is the name in the form on the dashboard.html
        print("Hitting if")
        flash('Input Needs to be longer')
      return redirect('/dashboard')
    else:
      print(request.form)
    db = connectToMySQL('quotes2')
    print("Hitting 4")

# #  # #this is telling the computer to find the table name posts 

    query = 'INSERT INTO quotes_table (q_author, id_content,id_contributor, created_at, updated_at) VALUES (%(qa)s, %(idc)s,%(id_cont)s, NOW(), NOW());'
    print("Hitting 5")

    data = {
        'qa': request.form['q_name'],
        'idc': request.form['q_cont'],
        'id_cont': session['id_mickey_user'],
    }
    print("hitting 6")
    add_book = db.query_db(query, data)
    print(add_book)
#     print(request.form)
    print("hitting 7")
    return redirect ('/dashboard')

# # # # show the form to show user added quotes
@app.route('/show_one_quote/<id>', methods=["GET"])
def show_quotes_by(id):
    # print(id)
  # showthebooktitle
  # showaddedbyuserx
  # addedoncreated_at
  # lastupdated_at
  # description:
    # if session: ['id_mickey_user'] != 'id_contributor';
    #   return redirect('/dashboard');
    #   flash("You can not edit this entry");
    #     else:

    # if 'golds' in session:
    #     print('*****************')
    #     print("I am counting the money")
    #     session['id_contributer'] += golds
       
    if "golds" not in session:
        session['golds']=0
    print("key 'gold' does NOT exist")
        
    if 'count' in session:
        print('*************************')
        print('count exists')
        print('*************************')
        session['count'] = session['count'] + 1
    else:
        print("key 'count' does NOT exist")
        session['count'] = 0
    
    db = connectToMySQL('quotes2')

    query = 'SELECT COUNT(*)FROM quotes_table JOIN users_table ON quotes_table.id_contributor = users_table.id_user WHERE quotes_table.id_contributor = %(idc)s ;'
    
    data = {
      'idc': ['id_contributor'],
    }
    print("hitting before gold")
    gold = db.query_db(query,data)
    print('The query total is', gold)

    MySQL = connectToMySQL ("quotes2")
    print('hitting mysql')
    query = "SELECT * FROM quotes_table JOIN users_table ON quotes_table.id_contributor = users_table.id_user WHERE id_contributor=%(idc)s;"
    print(id)
    
    data = {
          'idc': id
      }

    quotes = MySQL.query_db(query, data)
    print('we made it through quotes')
    return render_template('show_quotes_by.html', all_quotes=quotes, golds=gold)

    # DO NOT NEED TO USE THE STR(ID) for render template
    # ONly pass in the str(ID) when doing a url or redirect
    

# @app.route('/show_one_user/<id>', methods=['GET'])
# def show_one_user(id):
    #to get info about a specific user, you need to pass in an id through the browser

    # return render_template (show_one_user.html)
    #for temporary solution use this render_template

    # MySQL = connectToMySQL("quotes")
    #connect to to the MySQL schema name
 
    # query = "(SELECT * FROM users_table WHERE id_user= %(mickey_id)s);"  
    # id_user is the variable name found in the database that intiates a user_id
    # print(id)
    #printing the blue id in shown above is id passed in through the browser and not the database.
    
    # data = {
    #      'mickey_id': session['id_mickey_user']
    # }  #data is required when we need to define specific data.
    # In this case, id_user in table users_table, there is data for the query to get and this is this data called id which is in blue and it is passed through the both the URL as well as the function above. 
   
    # data_id_call = MySQL.query_db(query, data)
    # this is the call to run the function to get the ID in the database where the database will then pass results to the browser page. This database_id is database_id and it will be set to the browswer in orange which will be written in jinja

    # MySQL = connectToMySQL('quotes')

    # query_show_quotes = 'SELECT * FROM quotes_table JOIN users_table ON quotes_table.user_added_by = users_table.id_user;'

    # quotes = MySQL.query_db(query_show_quotes)
    # print('show page hitting 0')
    
    # print('show page before Hitting 1')

    # return render_template ("show_one_user.html", all_users=data_id_call, all_quotes=quotes) 

# @app.route('/edit/<id>', methods=["GET", "POST"])
# def show_edit_form(id):
   
    
#     MySQL = connectToMySQL("quotes2")

#     # query = 'SELECT * FROM quotes_table JOIN users_table ON quotes_table.id_contributor = users_table.id_user;'

#     query = "(SELECT * FROM quotes_table JOIN users_table ON quotes_table.id_contributor = users_table.id_user WHERE id_quote = %(idq)s);"

#     print(id)  
#     data = {
#         'idq': id

#     } 
#     # # # # #run query
#     quotes = MySQL.query_db(query, data)
#     print('hitting show edit page')
#     print(quotes)
#     return render_template("edit.html", quote=quotes)

# @app.route('/update_quote/<id>', methods=['POST'])
# def process_edit_form(id):
#     print(id)
#     # #connect to db to show users info in the form
#     print('hittingprocessingeditpage')
    
#     MySQL = connectToMySQL("quotes2")
#     # # # # # #write query for getting specific users
#     print('connecting to the server')
   
#     query = "UPDATE quotes_table SET book_title = %(bt)s,book_description=%(bd)s, id_contributor=%(idc)s, created_at = NOW(), updated_at = NOW() WHERE id_quote = %(idq)s;"
# # 
#     data = {
#     'qn': request.form['q_name'],
#     'qc': request.form['q_cont'],
#     'idc': session['id_mickey_user'],
#     'idq': id
#     }
#     # #possibly a value from the url,
#     print('hitting query')
#     MySQL.query_db(query, data)

#     print("hitting 6")
#     # #possibly a value from the url,
   
#    # where to go after this is complete
#     return redirect('/edit/' + str(id))

@app.route('/delete/<id>', methods=['GET'])
def delete_book(id):
    #     print('user to ??')
    MySQL = connectToMySQL("quotes2")

    # #write an UPDATE query
    query = "DELETE from quotes_table WHERE id_quote = %(idq)s;"
    print(id)
    
    data = {
        'idq': id
    }
    MySQL.query_db(query, data)
    flash("removed")
    return redirect('/dashboard')

if __name__ == "__main__":
  app.run(debug=True)


# data={
    #           "id_user": session['id_mickey_user'],
              
    #           # 'bd': ['book_description'],
    #           # "addby":session['id_mickey_user']
    # }

 # all_recipients = MySQL.query_db(query_all_recipients, data)
      
    # MySQL=connectToMySQL('quotes')
        
    # query_count_incoming_posts = 'SELECT COUNT(*) FROM posts_table WHERE id_receiver = %(id_rec)s'
        
    # data = {
    # 'id_rec': session['id_mickey_user'] 
    # }
    # print('your id is', id)
      
    # total_message_count = MySQL.query_db(query_count_incoming_posts, data)
    # print('You have messages', total_message_count)

        
    # db = connectToMySQL('quotes')

    # query_inbox_messages = 'SELECT * FROM posts_table JOIN users_table ON posts_table.id_sender = users_table.id_user WHERE id_receiver= %(id_rec)s;'

    # data = {
    # 'id_rec': session['id_mickey_user']

    # }
    # print('id_rec')
       
    # print('id_sender says', {query_inbox_messages})
        
    # incoming_messages = db.query_db(query_inbox_messages, data)

    # print('id_sender says', incoming_messages)
    
    
    # return render_template('/dashboard.html', id_receivers=all_recipients,counts=total_message_count, all_messages=incoming_messages)